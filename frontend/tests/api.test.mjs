import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire, stripTypeScriptTypes } from 'node:module'
import test from 'node:test'
import vm from 'node:vm'

function load(name, fetch = async () => { throw new TypeError('offline') }, env = {}) {
  const url = new URL(`../src/${name}.ts`, import.meta.url)
  const source = readFileSync(url, 'utf8').replaceAll('import.meta.env', JSON.stringify(env))
  const stripped = stripTypeScriptTypes(source)
  const names = [...stripped.matchAll(/export (?:const|function|class) (\w+)/g)].map(match => match[1])
  const outputText = stripped.replace(/^import (\w+) from ('[^']+')/gm, 'const $1 = require($2)').replace(/export (?=const|function|class)/g, '') + `\nObject.assign(exports, { ${names.join(', ')} })`
  const exports = {}
  vm.runInNewContext(outputText, { exports, require: createRequire(url), fetch, FormData, File, Blob, AbortSignal, structuredClone }, { filename: url.pathname })
  return exports
}
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
const fixture = JSON.parse(readFileSync(new URL('../src/mocks/fixed.json', import.meta.url)))

test('live catalog and demo POST use the local API and preserve the actual verdict', async () => {
  const calls = []
  const live = { ...fixture, id: 'r_live', verdict: 'NOT_FIXED', percent_resolved: 0 }
  const client = load('api', async (url, init) => { calls.push([url, init]); return json(url.endsWith('/api/demo') ? [{ case_id: 'real-case' }] : live) })
  assert.equal((await client.api.demos())[0].case_id, 'real-case')
  assert.equal((await client.api.demoVerify('real/case')).verdict, 'NOT_FIXED')
  assert.equal(calls[0][0], 'http://localhost:8000/api/demo')
  assert.equal(calls[1][0], 'http://localhost:8000/api/demo/real%2Fcase/verify')
  assert.equal(calls[1][1].method, 'POST')
  assert.equal(client.isOffline(), false)
})

test('suggestion posts the before file and returns its normalized ROI', async () => {
  const roi = [[.1, .2], [.4, .2], [.4, .6], [.1, .6]]
  const client = load('api', async (url, init) => {
    assert.equal(url, 'http://localhost:8000/api/suggest-roi')
    assert.equal(init.method, 'POST')
    assert.equal(init.body.get('before').name, 'before.jpg')
    assert.equal(init.headers, undefined)
    return json({ roi, confidence: .8 })
  })
  assert.deepEqual((await client.api.suggest(new File(['photo'], 'before.jpg', { type: 'image/jpeg' }))).roi, roi)
})

test('upload forwards multipart files, complaint ID, ROI JSON and GPS without forcing a content type', async () => {
  const body = new FormData()
  body.append('before', new File(['before'], 'before.jpg'))
  body.append('after', new File(['after'], 'after.jpg'))
  body.append('complaint_id', 'BLR-42'); body.append('roi', JSON.stringify(fixture.roi))
  body.append('before_lat', '12.9'); body.append('before_lon', '77.6')
  const client = load('api', async (url, init) => {
    assert.equal(url, 'http://localhost:8000/api/verify'); assert.equal(init.method, 'POST')
    assert.equal(init.body, body); assert.equal(init.headers, undefined)
    assert.equal(init.body.get('complaint_id'), 'BLR-42')
    assert.deepEqual(JSON.parse(init.body.get('roi')), fixture.roi)
    assert.equal(init.body.get('before_lat'), '12.9')
    return json({ ...fixture, id: 'r_upload', simulated: false })
  })
  assert.equal((await client.api.verify(body)).id, 'r_upload')
})

test('missing ROI 422 is distinguishable from other validation errors', async () => {
  const missing = load('api', async () => json({ detail: 'Mark the pothole on the before photo' }, 422))
  await assert.rejects(missing.api.verify(new FormData()), error => error instanceof missing.ApiError && error.status === 422 && error.roiRequired)
  const invalid = load('api', async () => json({ detail: [{ loc: ['body', 'before_lat'], msg: 'Invalid latitude' }] }, 422))
  await assert.rejects(invalid.api.verify(new FormData()), error => error.status === 422 && !error.roiRequired && /before_lat: Invalid latitude/.test(error.message))
})

test('offline demos fall back to labeled fixtures but upload verification still fails', async () => {
  const client = load('api')
  assert.equal((await client.api.demos()).length, 5)
  assert.equal(client.isOffline(), true)
  assert.equal(client.isFixture(await client.api.demoVerify('case_01')), true)
  await assert.rejects(client.api.verify(new FormData()), error => error.status === 0)
})

test('network fallback preserves a previously received real result and reconnect clears offline state', async () => {
  let available = true
  const client = load('api', async () => { if (!available) throw new TypeError('offline'); return json({ ...fixture, id: 'r_cached' }) })
  assert.equal((await client.api.demoVerify('case_01')).id, 'r_cached')
  available = false
  assert.equal((await client.api.demoVerify('case_01')).id, 'r_cached')
  assert.equal(client.isOffline(), true)
  available = true
  await client.api.health()
  assert.equal(client.isOffline(), false)
})

test('HTTP errors are shown rather than replaced with a successful fixture', async () => {
  const client = load('api', async () => json({ detail: 'Processing failed' }, 500))
  await assert.rejects(client.api.demoVerify('case_01'), error => error.status === 500 && error.message === 'Processing failed')
  assert.equal(client.isOffline(), false)
})

test('image URLs honor a configured API base while keeping local and absolute sources intact', () => {
  const client = load('api', undefined, { VITE_API_URL: 'http://localhost:9000/' })
  assert.equal(client.imageUrl('/files/r_1/heatmap.jpg'), 'http://localhost:9000/files/r_1/heatmap.jpg')
  assert.equal(client.imageUrl('/demo-files/case_01/before.jpg'), 'http://localhost:9000/demo-files/case_01/before.jpg')
  for (const url of ['/mock/before.svg', 'blob:example', 'data:image/svg+xml,test', 'https://example.test/photo.jpg']) assert.equal(client.imageUrl(url), url)
})

test('explicit mock mode does not call the backend', async () => {
  const client = load('api', async () => { assert.fail('Unexpected fetch') }, { VITE_MOCK: '1' })
  assert.equal((await client.api.demos()).length, 5)
  assert.equal(client.isFixture(await client.api.demoVerify('case_05')), true)
})

test('keyboard shortcuts accept 1–7, H and K but ignore editing, repeated keys and browser commands', () => {
  const { shortcutKey } = load('shortcuts')
  const event = { key: '1', target: { closest: () => null } }
  for (const key of ['1', '2', '3', '4', '5', '6', '7', 'H', 'K']) assert.equal(shortcutKey({ ...event, key }), key.toLowerCase())
  for (const extra of [{ key: '8' }, { repeat: true }, { isComposing: true }, { ctrlKey: true }, { metaKey: true }, { altKey: true }, { target: { isContentEditable: true } }, { target: { closest: () => ({ tagName: 'INPUT' }) } }]) assert.equal(shortcutKey({ ...event, ...extra }), null)
})

test('ledger reads the live results endpoint without substituting demo fixtures', async () => {
  const client = load('api', async (url, init) => {
    assert.equal(url, 'http://localhost:8000/api/results')
    assert.equal(init.method, undefined)
    return json([{ ...fixture, id: 'r_record', simulated: false }])
  })
  const results = await client.api.results()
  assert.equal(results.length, 1)
  assert.equal(results[0].id, 'r_record')
})

test('ward rates use the latest result per complaint and count pending reviews separately', () => {
  const { summarizeWards } = load('ledgerMetrics')
  const record = (complaint_id, verdict, created_at, ward = 'Ward A') => ({ ...fixture, complaint_id, verdict, created_at, location: { ...fixture.location, ward } })
  const rows = [
    record('one', 'NOT_FIXED', '2026-11-01T08:00:00Z'),
    record('one', 'FIXED', '2026-11-01T10:00:00Z'),
    record('two', 'PARTIAL', '2026-11-01T09:00:00Z'),
    record('three', 'SUSPICIOUS', '2026-11-01T09:00:00Z'),
    record('four', 'NEEDS_REVIEW', '2026-11-01T09:00:00Z'),
    record('five', 'NOT_FIXED', '2026-11-01T09:00:00Z', 'Ward B'),
  ]
  const summaries = summarizeWards(rows)
  const a = summaries.find(summary => summary.ward === 'Ward A')
  assert.equal(a.total, 4)
  assert.equal(a.failed, 2)
  assert.equal(a.pending, 1)
  assert.equal(a.failurePercent, 50)
  assert.equal(summaries[0].ward, 'Ward B')
  assert.equal(summaries[0].failurePercent, 100)
})

test('ward summaries handle missing locations and empty results without inventing coordinates', () => {
  const { summarizeWards, hasCoordinates } = load('ledgerMetrics')
  assert.equal(summarizeWards([]).length, 0)
  const missing = { ...fixture, location: null }
  assert.equal(summarizeWards([missing])[0].ward, 'Unassigned ward')
  assert.equal(hasCoordinates(missing), false)
  assert.equal(hasCoordinates({ ...fixture, location: { lat: 0, lon: 0 } }), true)
  for (const location of [{ lat: 91, lon: 10 }, { lat: 20, lon: -181 }, { lat: NaN, lon: 10 }, { lat: null, lon: 10 }]) assert.equal(hasCoordinates({ ...fixture, location }), false)
})

test('friendly errors never display raw service messages or private details', () => {
  const { friendlyError } = load('presentation')
  for (const context of ['demos', 'verify', 'ledger', 'reconnect']) {
    for (const error of [new Error('private traceback /private/internal/file'), { status: 500, message: 'database exception: secret' }, null]) {
      const copy = friendlyError(error, context)
      assert.ok(copy.length > 20)
      assert.doesNotMatch(copy, /traceback|private|secret|database|exception/)
    }
  }
  assert.match(friendlyError({ status: 0 }, 'verify'), /connection/)
  assert.match(friendlyError({ status: 422 }, 'verify'), /photos, complaint ID/)
})

test('the offline catalog matches the real demo stories, including reused evidence', async () => {
  const client = load('api')
  const demos = await client.api.demos()
  assert.deepEqual(demos.map(demo => demo.title), ['Pothole marked resolved – honest repair', 'Only half the pothole repaired', 'Pothole still unrepaired', 'Photo from a different road', 'Reused photo'])
  assert.deepEqual(demos.map(demo => demo.expected), ['FIXED', 'PARTIAL', 'NOT_FIXED', 'SUSPICIOUS', 'SUSPICIOUS'])
  const reused = await client.api.demoVerify('case_05')
  assert.equal(reused.verdict, 'SUSPICIOUS')
  assert.equal(reused.checks.duplicate.status, 'fail')
  assert.equal(reused.checks.duplicate.matched_complaint_id, 'DEMO-0001')
})

test('live demo cards preserve server titles and thumbnails with the requested reused-photo label', async () => {
  const catalog = [{ case_id: 'case_01', title: 'Real repair title', before_url: '/demo-files/case_01/before.jpg', expected: 'FIXED' }, { case_id: 'case_05', title: 'Repair photo reused for another complaint', before_url: '/demo-files/case_05/before.jpg', expected: 'SUSPICIOUS' }]
  const client = load('api', async () => json(catalog))
  const demos = await client.api.demos()
  assert.equal(demos[0].title, catalog[0].title)
  assert.equal(demos[0].before_url, catalog[0].before_url)
  assert.equal(demos[1].title, 'Reused photo')
  assert.equal(demos[1].expected, 'SUSPICIOUS')
  assert.equal(demos[1].before_url, catalog[1].before_url)
})


test('live catalog accepts seven cases and preserves real photo tags and image URLs', async () => {
  const catalog = Array.from({ length: 7 }, (_, i) => ({ case_id: `case_0${i + 1}`, title: `Repair ${i + 1}`, expected: 'FIXED', simulated: i < 5, ward: 'Ward A', before_url: `/demo-files/case_0${i + 1}/before.jpg`, after_url: `/demo-files/case_0${i + 1}/after.jpg` }))
  const client = load('api', async () => json(catalog))
  const demos = await client.api.demos()
  assert.equal(demos.length, 7)
  for (const i of [5, 6]) {
    assert.equal(demos[i].simulated, false)
    assert.equal(demos[i].title, catalog[i].title)
    assert.equal(demos[i].before_url, catalog[i].before_url)
  }
})

test('light theme text and verdict chip labels meet AA contrast on their surfaces', () => {
  const css = readFileSync(new URL('../src/index.css', import.meta.url), 'utf8')
  const tokens = Object.fromEntries([...css.matchAll(/--([\w-]+):#([0-9a-f]{6})/gi)].map(([, name, hex]) => [name, [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)]))
  function luminance(rgb) { return rgb.reduce((sum, value, i) => sum + [.2126, .7152, .0722][i] * (value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4), 0) }
  function contrast(a, b) { const values = [luminance(a), luminance(b)].sort((x, y) => x - y); return (values[1] + .05) / (values[0] + .05) }
  for (const foreground of ['text', 'muted', 'primary']) for (const background of ['bg', 'surface', 'surface-2']) assert.ok(contrast(tokens[foreground], tokens[background]) >= 4.5, `${foreground} on ${background}`)
  assert.ok(contrast(tokens['on-primary'], tokens.primary) >= 4.5)
  for (const verdict of ['fixed', 'partial', 'not-fixed', 'suspicious', 'needs-review']) {
    const ink = tokens[verdict].map((value, i) => .9 * value + .1 * tokens.text[i])
    const tint = tokens[verdict].map((value, i) => .1 * value + .9 * tokens.surface[i])
    assert.ok(contrast(ink, tint) >= 4.5, `${verdict} chip contrast`)
  }
})


test('invalid boxes are treated as absent for optional automatic measurement', () => {
  const { isValidRoi } = load('api')
  assert.equal(isValidRoi(fixture.roi), true)
  for (const box of [null, [], [[.7,.2],[.2,.2],[.2,.8],[.7,.8]], [[.2,.8],[.7,.8],[.7,.2],[.2,.2]], [[.2,.2],[.2,.2],[.2,.8],[.2,.8]], [[-.1,0],[1,0],[1,1],[-.1,1]], [[NaN,0],[1,0],[1,1],[0,1]]]) assert.equal(isValidRoi(box), false)
})

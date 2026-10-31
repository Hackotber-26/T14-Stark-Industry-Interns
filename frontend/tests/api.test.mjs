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

test('keyboard shortcuts accept 1–5, H and K but ignore editing, repeated keys and browser commands', () => {
  const { shortcutKey } = load('shortcuts')
  const event = { key: '1', target: { closest: () => null } }
  for (const key of ['1', '2', '3', '4', '5', 'H', 'K']) assert.equal(shortcutKey({ ...event, key }), key.toLowerCase())
  for (const extra of [{ key: '6' }, { repeat: true }, { isComposing: true }, { ctrlKey: true }, { metaKey: true }, { altKey: true }, { target: { isContentEditable: true } }, { target: { closest: () => ({ tagName: 'INPUT' }) } }]) assert.equal(shortcutKey({ ...event, ...extra }), null)
})

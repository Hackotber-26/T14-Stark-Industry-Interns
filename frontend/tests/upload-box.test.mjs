import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

// Set PLAYWRIGHT_MODULE to an installed package path to run against local services.
const playwrightModule = process.env.PLAYWRIGHT_MODULE
const before = fileURLToPath(new URL('../../data/real/real_before.jpg', import.meta.url))
const after = fileURLToPath(new URL('../../data/real/real_after_fixed.jpg', import.meta.url))

async function upload(page) {
  await page.goto(process.env.FRONTEND_URL ?? 'http://localhost:5173')
  await page.getByPlaceholder('e.g. BLR-2026-0042').fill('INPUT-CHECK')
  const suggestion = page.waitForResponse(response => response.url().endsWith('/api/suggest-roi'))
  await page.locator('.upload-zone input').nth(0).setInputFiles(before)
  await page.locator('.upload-zone input').nth(1).setInputFiles(after)
  assert.equal((await suggestion).status(), 200)
  await page.getByRole('button', { name: 'Clear box', exact: true }).click()
  await page.locator('.editor').scrollIntoViewIfNeeded()
  assert.equal(await page.getByRole('button', { name: 'Verify repair', exact: true }).isEnabled(), true)
  assert.equal(await page.getByText('Optional: mark the problem area for a more precise measurement. Without it, we find the changed area automatically.', { exact: true }).isVisible(), true)
}

async function assertBox(page, left = .3, top = .5, right = .7, bottom = .8) {
  await page.waitForFunction(() => !!document.querySelector('.editor .roi') && !document.querySelector('button[type="submit"]').disabled, null, { timeout: 5000 })
  assert.equal(await page.locator('.editor .roi').count(), 1)
  const coordinates = await page.locator('.coordinate-grid input').evaluateAll(inputs => inputs.map(input => Number(input.value)))
  for (const [i, expected] of [left, top, right, bottom].entries()) assert.ok(Math.abs(coordinates[i] - expected) < .01, `${coordinates} expected ${[left, top, right, bottom]}`)
  assert.equal(await page.getByText('Optional: mark the problem area for a more precise measurement. Without it, we find the changed area automatically.', { exact: true }).count(), 1)
}

test('real uploads support drag, fast release, two clicks, box movement and touch', { skip: !playwrightModule }, async t => {
  const { chromium } = await import(playwrightModule)
  const browser = await chromium.launch({ headless: true })
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    await page.route('**/*', route => /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(route.request().url()) ? route.continue() : route.abort())
    page.setDefaultTimeout(10000)
    const errors = []; page.on('pageerror', error => errors.push(error.message))
    await upload(page)
    const editor = page.locator('.editor')
    await t.test('normal mouse or trackpad drag', async () => {
      await editor.scrollIntoViewIfNeeded()
      const r = await editor.boundingBox()
      await page.mouse.move(r.x + r.width * .3, r.y + r.height * .5)
      await page.mouse.down()
      await page.mouse.move(r.x + r.width * .7, r.y + r.height * .8, { steps: 12 })
      await page.mouse.up()
      await assertBox(page)
    })
    await t.test('release coordinates commit even without a final move event', async () => {
      await page.getByRole('button', { name: 'Clear box', exact: true }).click()
      await editor.scrollIntoViewIfNeeded()
      const r = await editor.boundingBox()
      await page.mouse.move(r.x + r.width * .3, r.y + r.height * .5)
      await page.mouse.down()
      await editor.dispatchEvent('pointerup', { pointerId: 1, button: 0, clientX: r.x + r.width * .7, clientY: r.y + r.height * .8 })
      await page.mouse.up()
      await assertBox(page)
    })
    await t.test('move and release in one event batch do not use stale state', async () => {
      await page.getByRole('button', { name: 'Clear box', exact: true }).click()
      await editor.scrollIntoViewIfNeeded()
      const r = await editor.boundingBox()
      await page.mouse.move(r.x + r.width * .3, r.y + r.height * .5)
      await page.mouse.down()
      await editor.evaluate((element, rect) => {
        element.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, pointerId: 1, clientX: rect.x + rect.width * .301, clientY: rect.y + rect.height * .501 }))
        element.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, clientX: rect.x + rect.width * .7, clientY: rect.y + rect.height * .8 }))
      }, r)
      await page.mouse.up()
      await assertBox(page)
    })
    await t.test('two clicks set opposite corners', async () => {
      await page.getByRole('button', { name: 'Clear box', exact: true }).click()
      await editor.scrollIntoViewIfNeeded()
      const r = await editor.boundingBox()
      await page.mouse.click(r.x + r.width * .3, r.y + r.height * .5)
      assert.equal(await page.locator('.corner-marker').count(), 1)
      assert.equal(await page.getByRole('button', { name: 'Verify repair', exact: true }).isEnabled(), true)
      await page.mouse.click(r.x + r.width * .7, r.y + r.height * .8)
      await assertBox(page)
      assert.equal(await page.locator('.corner-marker').count(), 0)
    })
    await t.test('an existing box can still be moved', async () => {
      await editor.scrollIntoViewIfNeeded()
      const r = await editor.boundingBox()
      await page.mouse.move(r.x + r.width * .5, r.y + r.height * .65)
      await page.mouse.down()
      await page.mouse.move(r.x + r.width * .6, r.y + r.height * .75, { steps: 5 })
      await page.mouse.up()
      await assertBox(page, .4, .6, .8, .9)
    })
    await t.test('touch users can tap two corners at 390px', async () => {
      const touchPage = await browser.newPage({ viewport: { width: 390, height: 900 }, hasTouch: true, isMobile: true })
      await touchPage.route('**/*', route => /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(route.request().url()) ? route.continue() : route.abort())
      await upload(touchPage)
      const r = await touchPage.locator('.editor').boundingBox()
      await touchPage.touchscreen.tap(r.x + r.width * .3, r.y + r.height * .5)
      await touchPage.touchscreen.tap(r.x + r.width * .7, r.y + r.height * .8)
      await assertBox(touchPage)
      assert.equal(await touchPage.evaluate(() => document.documentElement.scrollWidth), 390)
      await touchPage.close()
    })
    await t.test('missing and invalid boxes remain optional and are omitted from uploads', async () => {
      const optionalPage = await browser.newPage({ viewport: { width: 1440, height: 900 } })
      await optionalPage.route('**/*', route => /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(route.request().url()) ? route.continue() : route.abort())
      const sentBodies = []
      const result = JSON.parse(readFileSync(new URL('../src/mocks/fixed.json', import.meta.url), 'utf8'))
      result.roi_source = 'auto_change'
      await optionalPage.route('**/api/verify', async route => {
        sentBodies.push(route.request().postDataBuffer().toString())
        await route.fulfill({ json: result })
      })
      await upload(optionalPage)
      const verify = optionalPage.getByRole('button', { name: 'Verify repair', exact: true })
      await optionalPage.getByPlaceholder('e.g. BLR-2026-0042').fill('')
      assert.equal(await verify.isEnabled(), false)
      await optionalPage.getByPlaceholder('e.g. BLR-2026-0042').fill('OPTIONAL-BOX')
      await verify.click()
      await optionalPage.getByText('Detected change area', { exact: true }).waitFor()
      assert.equal(sentBodies.length, 1)
      assert.doesNotMatch(sentBodies[0], /name="roi"/)
      await optionalPage.getByRole('button', { name: 'Verify another repair' }).click()
      await optionalPage.getByText('Use coordinates instead', { exact: true }).click()
      await optionalPage.getByLabel('Left box coordinate', { exact: true }).fill('0.7')
      await optionalPage.getByLabel('Right box coordinate', { exact: true }).fill('0.2')
      assert.equal(await optionalPage.getByLabel('Left box coordinate', { exact: true }).inputValue(), '0.7')
      assert.equal(await optionalPage.getByLabel('Right box coordinate', { exact: true }).inputValue(), '0.2')
      assert.equal(await optionalPage.locator('.editor .roi').count(), 0)
      assert.equal(await verify.isEnabled(), true)
      await verify.click()
      await optionalPage.getByText('Detected change area', { exact: true }).waitFor()
      assert.equal(sentBodies.length, 2)
      assert.doesNotMatch(sentBodies[1], /name="roi"/)
      await optionalPage.close()
    })
    assert.deepEqual(errors, [])
  } finally { await browser.close() }
})

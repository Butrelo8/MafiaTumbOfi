#!/usr/bin/env node
// Is the wheel / roof-rack group (camion_extras.glb) really absent from stop 1? Shoots parada1 with that request aborted (waits for the
// cast, which loads first, not for `cargado`), at 1440 and 390, same framing as vivo-tomas.mjs; diff them against a full-load shot with diff.py.
//   PW=... CHROME=... WSLENV=PW:CHROME node.exe scripts/g63/sin_extras.mjs <url> <out_dir (Windows)>   -> <out>/1440-parada1.png, 390-parada1.png
import { createRequire } from 'node:module'
import { mkdirSync } from 'node:fs'
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out] = process.argv.slice(2)
mkdirSync(out, { recursive: true })
const SIZES = { 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } } }
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] })
for (const w of [1440, 390]) {
  const ctx = await browser.newContext(SIZES[w])
  const page = await ctx.newPage()
  await page.route('**/camion_extras.glb', (r) => r.abort())
  await page.goto(`${url}?f=0&sinpantalla&parada=0`, { waitUntil: 'load' })
  await page.waitForFunction(() => window.__vivo?.fases?.reparto > 0, null, { timeout: 120000 })
  const ruedas = await page.evaluate(() => window.__vivo.ruedas)
  await page.waitForTimeout(1500)
  await page.locator('nav, h1, #creditos, header, .apertura').evaluateAll((els) => els.forEach((e) => (e.style.visibility = 'hidden')))
  await page.waitForTimeout(500)
  await page.screenshot({ path: `${out}/${w}-parada1.png` })
  console.log(w, 'ruedas en la escena:', ruedas)
  await ctx.close()
}
await browser.close()

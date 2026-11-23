#!/usr/bin/env node
// Stills of the opening for a before/after pair (ticket 01-pagina-primero, Done-check 3): the writing at 1.6 s from navigation, and the
// clip 1 s after it starts to play (#apertura.con-video). One run per width, no throttling. Writes <out>/<ancho>-escritura.png, <ancho>-clip.png.
//   PW=<dir of playwright-core> node scripts/fotos-apertura.mjs <url> <out dir> [chromium path]
import { createRequire } from 'node:module'
import { mkdirSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out, exe = '/snap/bin/chromium'] = process.argv.slice(2)
mkdirSync(out, { recursive: true })
const browser = await chromium.launch({ executablePath: exe, args: ['--ignore-gpu-blocklist', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] })
for (const [w, opc] of Object.entries({ 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } } })) {
  const page = await (await browser.newContext(opc)).newPage()
  await page.goto(url, { waitUntil: 'commit' })
  const t0 = Date.now()
  await page.waitForTimeout(1600)
  await page.screenshot({ path: `${out}/${w}-escritura.png` })
  console.log(w, 'escritura at', Date.now() - t0, 'ms')
  await page.waitForFunction(() => document.getElementById('apertura')?.classList.contains('con-video'), null, { timeout: 30000, polling: 100 })
  await page.waitForTimeout(1000)
  await page.screenshot({ path: `${out}/${w}-clip.png` })
  console.log(w, 'clip at', Date.now() - t0, 'ms')
  await page.close()
}
await browser.close()

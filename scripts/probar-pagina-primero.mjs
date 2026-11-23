#!/usr/bin/env node
// Page-first test (ticket 01-pagina-primero, Done-check 2): at first paint + 500 ms, with the opening still playing and the phone
// conditions of medir-lcp.mjs, (a) a wheel and a touch drag reach the page and nothing cancels them, (b) the topmost thing under the
// nav and the h1 is the control itself, nothing is inert, (c) Tab lands on the nav buttons, (d) a nav click is taken and ends the
// opening. The page itself has nothing to scroll (the home is a fixed scene driven by the nav); the test says so instead of faking it.
//   PW=<dir of playwright-core> node scripts/probar-pagina-primero.mjs <url> <out.json> [chromium path]
import { createRequire } from 'node:module'
import { writeFileSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out, exe = '/snap/bin/chromium'] = process.argv.slice(2)
const UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
const browser = await chromium.launch({ executablePath: exe, args: ['--ignore-gpu-blocklist', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] })
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: UA })
const page = await ctx.newPage()
await page.addInitScript(() => {
  const w = window
  w.__p = { wheel: 0, wheelCancelado: 0, touchmove: 0, touchmoveCancelado: 0 }
  for (const [t, a, b] of [['wheel', 'wheel', 'wheelCancelado'], ['touchmove', 'touchmove', 'touchmoveCancelado']])
    document.addEventListener(t, (e) => { w.__p[a]++; setTimeout(() => { if (e.defaultPrevented) w.__p[b]++ }, 0) }, { passive: true, capture: false })
  new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.name === 'first-contentful-paint') w.__p.fcp = e.startTime })
    .observe({ type: 'paint', buffered: true })
})
const cdp = await ctx.newCDPSession(page)
await cdp.send('Network.enable')
await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 60, downloadThroughput: (9e6 / 8) * 0.9, uploadThroughput: (1.5e6 / 8) * 0.9 })
await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 })
await page.goto(url, { waitUntil: 'commit' })
await page.waitForFunction(() => window.__p?.fcp != null, null, { timeout: 30000 })
await page.waitForTimeout(500) // first paint + 500 ms

const antes = await page.evaluate(() => ({
  apertura: !!document.getElementById('apertura'), scrollable: document.documentElement.scrollHeight - innerHeight,
  inert: [...document.querySelectorAll('nav, h1')].some((e) => e.inert || e.closest('[inert]')),
  tapa: ['h1', '#p-cabina', '#p-placa'].map((s) => { const r = document.querySelector(s).getBoundingClientRect(); const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [s, document.querySelector(s).contains(t)] }),
}))
await page.mouse.move(195, 400)
await page.mouse.wheel(0, 400)
await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 195, y: 600 }] })
for (const y of [560, 500, 440, 380]) await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 195, y }] })
await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
await page.waitForTimeout(200)
const entradas = await page.evaluate(() => ({ ...window.__p, scrollY: scrollY, aperturaSigue: !!document.getElementById('apertura') }))
// keyboard: Tab from the top lands on the nav buttons (the opening's own Saltar may come first; it is one stop)
const tabs = []
for (let i = 0; i < 4; i++) { await page.keyboard.press('Tab'); tabs.push(await page.evaluate(() => { const a = document.activeElement; return a ? (a.id || a.className || a.tagName) : null })) }
// a tap on a nav button is taken and the opening steps aside; the camera follows only if the scene has loaded by then (its handlers attach after the GLB)
await page.tap('#p-caja')
await page.waitForFunction(() => !document.getElementById('apertura'), null, { timeout: 8000 }).catch(() => {}) // the opening steps aside (the canvas may take up to 3 s)
const despues = await page.evaluate(() => ({ aperturaSigue: !!document.getElementById('apertura'), actual: document.querySelector('#escenas [aria-current="true"]')?.id }))
const res = { url, antes, entradas, tabs, despues }
if (out) writeFileSync(out, JSON.stringify(res, null, 1))
console.log(JSON.stringify(res, null, 1))
await browser.close()

#!/usr/bin/env node
// LCP of the home on a phone-like run (ticket 01-pagina-primero): 390x844, mobile UA, 4x CPU throttle, Fast 4G (9 Mbps down, 1.5 up,
// 60 ms), a cold cache per run. Per run: LCP (a PerformanceObserver, last entry before the page settles; no input is sent, so nothing
// freezes it early), its element, FCP, the time the h1 is readable (the topmost element at its centre is the h1 and nothing is inert),
// TTFF (html[data-listo], the live canvas' first frame, as medir-inicio.mjs reads it) and when the heavy files start.
//   PW=<dir of playwright-core> node scripts/medir-lcp.mjs <url> <runs> <out.json> [chromium path, default /snap/bin/chromium]
import { createRequire } from 'node:module'
import { writeFileSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, runs = '5', out, exe = '/snap/bin/chromium'] = process.argv.slice(2)
const UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
const MAX_MS = 40000 // a run ends when the scene has drawn and the page has been quiet 2 s, or here

const sonda = () => {
  const w = window
  w.__m = { lcp: [], h1Legible: null, ttff: null, fcp: null }
  new PerformanceObserver((l) => { for (const e of l.getEntries()) w.__m.lcp.push({ t: Math.round(e.startTime), tag: e.element?.tagName ?? null, id: e.element?.id ?? null, url: e.url ?? '', size: e.size }) })
    .observe({ type: 'largest-contentful-paint', buffered: true })
  new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.name === 'first-contentful-paint') w.__m.fcp = Math.round(e.startTime) })
    .observe({ type: 'paint', buffered: true })
  const tick = () => {
    const h1 = document.querySelector('h1')
    if (h1 && w.__m.h1Legible === null) {
      const r = h1.getBoundingClientRect()
      const alto = document.elementFromPoint(r.left + Math.min(r.width, 40) / 2, r.top + r.height / 2)
      const cs = getComputedStyle(h1)
      if (r.width > 0 && alto && h1.contains(alto) && !h1.closest('[inert]') && cs.visibility === 'visible' && +cs.opacity > 0.9) w.__m.h1Legible = Math.round(performance.now())
    }
    if (w.__m.ttff === null && document.documentElement.dataset.listo === '1') w.__m.ttff = Math.round(performance.now())
    requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

const browser = await chromium.launch({ executablePath: exe, args: ['--ignore-gpu-blocklist', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] })
const res = { url, runs: [], condiciones: { viewport: '390x844 @2x', cpu: '4x', red: 'Fast 4G 9 Mbps / 1.5 Mbps / 60 ms', ua: UA, navegador: await browser.version() } }

for (let i = 0; i < +runs; i++) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: UA })
  const page = await ctx.newPage()
  const errores = []
  page.on('pageerror', (e) => errores.push(e.message))
  await page.addInitScript(sonda)
  const cdp = await ctx.newCDPSession(page)
  await cdp.send('Network.enable')
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 60, downloadThroughput: (9e6 / 8) * 0.9, uploadThroughput: (1.5e6 / 8) * 0.9 })
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 })
  await page.goto(url, { waitUntil: 'commit' })
  const t0 = Date.now()
  let quieto = 0, ultimo = ''
  while (Date.now() - t0 < MAX_MS) {
    await page.waitForTimeout(500)
    const m = await page.evaluate(() => ({ ...window.__m, ahora: Math.round(performance.now()), overlay: !!document.getElementById('apertura') })).catch(() => null)
    if (!m) continue
    const firma = JSON.stringify([m.lcp.length, m.ttff, m.overlay])
    quieto = firma === ultimo ? quieto + 500 : 0
    ultimo = firma
    if (m.ttff !== null && !m.overlay && quieto >= 2000) break
  }
  const f = await page.evaluate(() => {
    const m = window.__m, r = performance.getEntriesByType('resource')
    const ini = (re) => { const e = r.find((x) => re.test(x.name)); return e ? Math.round(e.startTime) : null }
    return { ...m, inicio: { js: ini(/_astro\/index.*\.js/), escenaGlb: ini(/escena\.glb/), aperturaMp4: ini(/apertura\.mp4/), pantallaMp4: ini(/pantalla\.mp4/), poster: ini(/parada-1\.webp/) },
      lcpFinal: m.lcp.at(-1) ?? null, ahora: Math.round(performance.now()) }
  })
  f.errores = errores
  res.runs.push(f)
  console.log(`run ${i + 1}: LCP ${f.lcpFinal?.t} ms (${f.lcpFinal?.tag}#${f.lcpFinal?.id} ${f.lcpFinal?.url.split('/').pop()}), FCP ${f.fcp}, h1 ${f.h1Legible}, TTFF ${f.ttff}, ends ${f.ahora}`)
  await ctx.close()
}
const mediana = (a) => { const s = a.filter((x) => x != null).sort((x, y) => x - y); if (!s.length) return null; const m = s.length >> 1; return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2) }
res.mediana = { lcp: mediana(res.runs.map((r) => r.lcpFinal?.t)), fcp: mediana(res.runs.map((r) => r.fcp)), h1Legible: mediana(res.runs.map((r) => r.h1Legible)), ttff: mediana(res.runs.map((r) => r.ttff)) }
res.elementoLcp = [...new Set(res.runs.map((r) => `${r.lcpFinal?.tag}#${r.lcpFinal?.id} ${r.lcpFinal?.url.split('/').pop()}`))]
if (out) writeFileSync(out, JSON.stringify(res, null, 1))
console.log(JSON.stringify({ mediana: res.mediana, elementoLcp: res.elementoLcp }, null, 1))
await browser.close()

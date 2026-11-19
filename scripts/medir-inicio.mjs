#!/usr/bin/env node
// The home's opening, end to end: the "MTO" writing, the descent clip, the hand-off to the live scene, then a section move.
// Samples the page every 250 ms from navigation (overlay state, the clip's currentTime, the canvas' first frame) and takes
// screenshots at fixed moments. Writes <out>/inicio.json and <out>/<ancho>-<momento>.png.
//   Windows GPU: PW=E:\tmp\pw-vivo\node_modules\playwright-core CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe" \
//     node.exe scripts/medir-inicio.mjs http://127.0.0.1:4433/ <out_dir (Windows)>
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out] = process.argv.slice(2)
mkdirSync(out, { recursive: true })
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] })
const SIZES = { 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } } }
const res = { url, anchos: {} }
const errores = []

for (const [w, opc] of Object.entries(SIZES)) {
  const ctx = await browser.newContext(opc)
  const page = await ctx.newPage()
  page.on('pageerror', (e) => errores.push(`${w}: ${e.message}`))
  page.on('requestfailed', (r) => errores.push(`${w} requestfailed: ${r.url()}`))
  await page.goto(url, { waitUntil: 'commit' })
  const t0 = Date.now()
  const muestras = []
  const fotos = { '0.5s': 500, '1.2s': 1200, '2.2s-escrito': 2200 }
  const hechas = new Set()
  let video0 = null
  for (let i = 0; i < 100; i++) { // up to 25 s
    const m = await page.evaluate(() => {
      const a = document.getElementById('apertura'), v = document.getElementById('apertura-video')
      return { overlay: !!a, conVideo: !!a?.classList.contains('con-video'), seVa: !!a?.classList.contains('se-va'), t: v ? +v.currentTime.toFixed(2) : null,
        dur: v?.duration || null, pausado: v?.paused ?? null, listo: document.documentElement.dataset.listo === '1', inert: document.querySelector('nav')?.inert ?? null }
    }).catch(() => null)
    if (!m) { await page.waitForTimeout(250); continue }
    m.ms = Date.now() - t0
    muestras.push(m)
    for (const [n, ms] of Object.entries(fotos)) if (m.ms >= ms) { await page.screenshot({ path: `${out}/${w}-${n}.png` }); delete fotos[n] }
    if (m.conVideo && video0 === null) { video0 = m.ms }
    if (m.conVideo && !hechas.has('mitad') && m.t >= (m.dur || 6) / 2) { hechas.add('mitad'); await page.screenshot({ path: `${out}/${w}-video-mitad.png` }) }
    if (m.conVideo && !hechas.has('fin') && m.t >= (m.dur || 6) - 0.3) { hechas.add('fin'); await page.screenshot({ path: `${out}/${w}-video-fin.png` }) }
    if (m.overlay && m.seVa && !hechas.has('fundido')) { hechas.add('fundido'); await page.screenshot({ path: `${out}/${w}-fundido.png` }) }
    if (!m.overlay && m.listo) break
    await page.waitForTimeout(250)
  }
  const fin = muestras.at(-1)
  await page.waitForTimeout(800)
  await page.screenshot({ path: `${out}/${w}-escena-1.png` })
  const cam0 = await page.evaluate(() => window.__vivo?.estado().cam)
  await page.click('#p-pantalla')
  await page.waitForTimeout(3500)
  await page.screenshot({ path: `${out}/${w}-escena-pantalla.png` })
  const cam1 = await page.evaluate(() => window.__vivo?.estado().cam)
  const tmax = Math.max(...muestras.map((m) => m.t ?? 0))
  res.anchos[w] = {
    // last sample with the overlay up (the first ones precede the body)
    overlayEnd_ms: muestras.findLast((m) => m.overlay)?.ms ?? null,
    videoStart_ms: video0, clipMaxTime_s: tmax, clipDur_s: muestras.find((m) => m.dur)?.dur ?? null,
    canvasListo_ms: muestras.find((m) => m.listo)?.ms ?? null, navInertDuring: muestras.some((m) => m.overlay && m.inert), navInertAfter: fin?.inert,
    camMovesOnClick: JSON.stringify(cam0) !== JSON.stringify(cam1), cam0, cam1, muestras: muestras.map((m) => [m.ms, m.overlay ? 1 : 0, m.conVideo ? 1 : 0, m.seVa ? 1 : 0, m.t, m.listo ? 1 : 0].join(' ')),
  }
  await ctx.close()
}
res.errores = errores
writeFileSync(`${out}/inicio.json`, JSON.stringify(res, null, 1))
console.log(JSON.stringify(res, null, 1))
await browser.close()

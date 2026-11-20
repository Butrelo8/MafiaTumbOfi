#!/usr/bin/env node
// /vivo-secciones checks and numbers: nav clicks + keys across the six stops, traffic both ways, wheels, video; frame times
// (rAF interval and renderer.render()) at 1440 and 390 (CPU x4) with the video playing and paused; TTFF on throttled 4G;
// one 960x540 still per stop with ?f=0&sinpantalla for the side-by-side sheet. Writes <out>/medir.json and <out>/vivo-N.png.
//   Windows GPU: PW=E:\tmp\pw-vivo\node_modules\playwright-core CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe" \
//     node.exe scripts/medir-vivo.mjs http://127.0.0.1:4411/vivo-secciones <out_dir (Windows)>
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out] = process.argv.slice(2)
mkdirSync(out, { recursive: true })
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] })
const SIZES = { 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } }, 960: { viewport: { width: 960, height: 540 } } }
const res = { url, frames: {}, checks: {}, ttff4g: null }
const pct = (a) => { const s = a.slice(10).sort((x, y) => x - y); return (p) => (s.length ? +s[Math.min(s.length - 1, Math.floor(p * s.length))].toFixed(2) : null) }
const errores = []
const SOLO_TTFF = process.env.SOLO_TTFF === '1' // only block 3 (TTFF and bytes): a run takes ~1 min instead of ~10; list SOLO_TTFF in WSLENV

async function abrir(w, q = '') {
  const ctx = await browser.newContext(SIZES[w])
  const page = await ctx.newPage()
  page.on('pageerror', (e) => errores.push(`${w}${q}: ${e.message}`))
  await page.goto(url + q, { waitUntil: 'load' })
  await page.waitForFunction(() => window.__vivo?.cargado, null, { timeout: 120000 }) // streamed parts in: cast, cars, signs, video
  res.renderer ??= await page.evaluate(() => {
    const g = document.createElement('canvas').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info')
    return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : g.getParameter(g.RENDERER)
  })
  return { ctx, page }
}

async function tiempos(page, nombre) {
  await page.evaluate(() => (window.__vivo.frameMs.length = window.__vivo.renderMs.length = 0))
  await page.waitForTimeout(5000)
  const [ft, rm, calls, tris, dpr, sondeo] = await page.evaluate(() => [[...window.__vivo.frameMs], [...window.__vivo.renderMs], window.__vivo.calls, window.__vivo.tris, window.__vivo.dpr, window.__vivo.sondeo])
  const f = pct(ft), r = pct(rm)
  res.frames[nombre] = { raf_p50: f(0.5), raf_p95: f(0.95), render_p50: r(0.5), render_p95: r(0.95), n: ft.length, calls, tris, dpr, sondeo }
}

// 1) behaviour at 1440: nav clicks, keys, traffic, wheels, video
if (!SOLO_TTFF) {
  const { ctx, page } = await abrir(1440)
  await page.waitForTimeout(2500)
  const c = res.checks
  c.datos = await page.evaluate(() => { const v = window.__vivo; return { clips: v.clips, ruedas: v.ruedas, pantallas: v.pantallas, autos: v.autos, video: v.video, videoListo: v.el.readyState } })
  const e0 = await page.evaluate(() => window.__vivo.estado())
  await page.waitForTimeout(1000)
  const e1 = await page.evaluate(() => window.__vivo.estado())
  c.mundoSeMueve = e0.vias !== e1.vias
  c.ruedasGiran = e0.rueda !== e1.rueda
  c.autos = e0.z.map((z, i) => +(e1.z[i] - z).toFixed(1)) // per car, metres in 1 s along three's z (- = ahead)
  c.clics = []
  const orden = [1, 2, 3, 4, 5, 0, 3, 0, 5, 2]
  for (const i of orden) {
    const antes = await page.evaluate(() => window.__vivo.estado().cam)
    await page.click(`nav button[data-parada="${i}"]`)
    await page.waitForTimeout(400)
    const medio = await page.evaluate(() => window.__vivo.estado().cam)
    await page.waitForTimeout(1900)
    const fin = await page.evaluate(() => window.__vivo.estado().cam)
    const cur = await page.evaluate(() => [...document.querySelectorAll('nav button')].findIndex((b) => b.getAttribute('aria-current') === 'true'))
    c.clics.push({ a: i, current: cur, movio: Math.hypot(...fin.map((v, k) => v - antes[k])).toFixed(2), enCamino: Math.hypot(...medio.map((v, k) => v - antes[k])) > 0.01 })
  }
  await page.focus('nav button[data-parada="2"]')
  const teclas = []
  for (const k of ['ArrowRight', 'ArrowRight', 'ArrowLeft', 'End', 'Home', 'ArrowLeft']) {
    await page.keyboard.press(k)
    await page.waitForTimeout(2200)
    teclas.push(await page.evaluate(() => [document.activeElement.dataset.parada, [...document.querySelectorAll('nav button')].findIndex((b) => b.getAttribute('aria-current') === 'true')].join('/')))
  }
  c.teclas = teclas // expected 3/3 4/4 3/3 5/5 0/0 5/5
  // stop 4's member shots (owner 19:11): the second row shows only at stop 4; clicks and keys move between the four shots
  c.banda = { oculta: await page.evaluate(() => document.getElementById('banda').hidden), clics: [], teclas: [] }
  await page.click('nav button[data-parada="3"]')
  await page.waitForTimeout(2300)
  c.banda.visible = await page.evaluate(() => !document.getElementById('banda').hidden)
  for (const s of [1, 2, 3, 0, 2]) {
    const antes = await page.evaluate(() => window.__vivo.estado().cam)
    await page.click(`#banda button[data-toma="${s}"]`)
    await page.waitForTimeout(2300)
    const e = await page.evaluate(() => window.__vivo.estado())
    const cur = await page.evaluate(() => [...document.querySelectorAll('#banda button')].findIndex((b) => b.getAttribute('aria-current') === 'true'))
    c.banda.clics.push({ a: s, sub: e.sub, current: cur, movio: Math.hypot(...e.cam.map((v, k) => v - antes[k])).toFixed(2), lamparas: e.lamparas.map((x) => +x.toFixed(2)) })
  }
  await page.focus('#banda button[data-toma="2"]')
  for (const k of ['ArrowRight', 'ArrowRight', 'End', 'Home', 'ArrowLeft']) {
    await page.keyboard.press(k)
    await page.waitForTimeout(2300)
    c.banda.teclas.push(await page.evaluate(() => [document.activeElement.dataset.toma, window.__vivo.estado().sub].join('/')))
  } // expected 3/3 0/0 3/3 0/0 3/3
  await page.click('nav button[data-parada="4"]')
  await page.waitForTimeout(2300)
  c.banda.ocultaFuera = await page.evaluate(() => document.getElementById('banda').hidden)
  c.banda.lamparasFuera = await page.evaluate(() => window.__vivo.estado().lamparas)
  c.videoTrasClics = await page.evaluate(() => ({ playing: !window.__vivo.el.paused, t: window.__vivo.el.currentTime.toFixed(1) }))
  await ctx.close()
}

// 2) frame times, video playing and paused, 1440 x1 and 390 CPU x4
for (const w of SOLO_TTFF ? [] : [1440, 390]) {
  const { ctx, page } = await abrir(w)
  const cdp = await ctx.newCDPSession(page)
  if (w === 390) await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 })
  await page.waitForTimeout(3000)
  await tiempos(page, `${w}-video`)
  await page.evaluate(() => window.__vivo.el.pause())
  await tiempos(page, `${w}-pausa`)
  await page.evaluate(() => window.__vivo.el.play())
  await page.click('nav button[data-parada="3"]')
  await tiempos(page, `${w}-video-moviendo`) // includes a 1.2-2 s camera move to the side stop
  await ctx.close()
}

// 3) TTFF and bytes on throttled 4G (DevTools "Fast 4G": 165 ms RTT, 9 Mbps down, 1.5 Mbps up), 390, cold cache
{
  const ctx = await browser.newContext(SIZES[390])
  const page = await ctx.newPage()
  const cdp = await ctx.newCDPSession(page)
  await cdp.send('Network.enable')
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true })
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 165, downloadThroughput: (9e6 / 8), uploadThroughput: (1.5e6 / 8) })
  const bytes = {}
  cdp.on('Network.loadingFinished', (e) => { bytes[e.requestId] = { n: e.encodedDataLength } })
  const urls = {}
  cdp.on('Network.responseReceived', (e) => { urls[e.requestId] = e.response.url })
  const t0 = Date.now()
  await page.goto(url, { waitUntil: 'commit' })
  await page.waitForFunction(() => window.__vivo?.ttff > 0, null, { timeout: 300000, polling: 200 })
  const ttff = await page.evaluate(() => window.__vivo.ttff)
  await page.waitForFunction(() => window.__vivo.cargado, null, { timeout: 300000, polling: 200 })
  const fases = await page.evaluate(() => ({ ...window.__vivo.fases, dpr: window.__vivo.dpr, telefono: window.__vivo.telefono }))
  await page.waitForTimeout(3000) // let the video's first ranges arrive
  const porArchivo = {}
  for (const [id, b] of Object.entries(bytes)) {
    const u = (urls[id] || id).replace(/^https?:\/\/[^/]+/, '').replace(/\?.*/, '')
    porArchivo[u] = (porArchivo[u] || 0) + b.n
  }
  res.ttff4g = { ttff_ms: Math.round(ttff), fases, wall_ms: Date.now() - t0, bytes_total: Object.values(porArchivo).reduce((a, b) => a + b, 0), porArchivo }
  await ctx.close()
}

// 4) stills for the sheet: frozen (?f=0), screen panel flat (?sinpantalla), 960x540
for (let i = 0; i < (SOLO_TTFF ? 0 : 6); i++) {
  const { ctx, page } = await abrir(960, `?f=0&sinpantalla&parada=${i}`)
  await page.waitForTimeout(1500)
  await page.locator('nav, h1, #creditos').evaluateAll((els) => els.forEach((e) => (e.style.visibility = 'hidden')))
  await page.screenshot({ path: `${out}/vivo-${i + 1}.png` })
  await ctx.close()
}

res.errores = errores
writeFileSync(`${out}/medir.json`, JSON.stringify(res, null, 1))
console.log(JSON.stringify({ renderer: res.renderer, frames: res.frames, checks: res.checks, ttff4g: { ...res.ttff4g, porArchivo: undefined }, errores }, null, 1))
await browser.close()

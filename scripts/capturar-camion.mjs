#!/usr/bin/env node
// Shots of each camera stop (390 and 1440, both presets), a recording of the moves, and frame times.
//   node scripts/capturar-camion.mjs <url> <out_dir> [gl=angle-gl|swiftshader]
//   Windows GPU: PW=<dir>\\node_modules\\playwright-core CHROME=<chrome.exe> node.exe capturar-camion.mjs ...
// Frame times: p50/p95 over 5 s of the live scene (?sinrespaldo keeps it live), at 390 with CPU x4 and at 1440 x1.
// The GL backend in use is printed next to every number (a software rasterizer is not a phone).
import { createRequire } from 'node:module'
import { execSync } from 'node:child_process'
import { mkdirSync, writeFileSync, renameSync, readdirSync } from 'node:fs'

const require = createRequire(import.meta.url)
// PW: path to a playwright(-core) package (Windows run: node.exe with Chrome on the real GPU), else the global one.
const { chromium } = require(process.env.PW || `${execSync('npm root -g').toString().trim()}/playwright`)
const [url, out, gl = 'angle-gl'] = process.argv.slice(2)
if (!url || !out) { console.error('uso: node scripts/capturar-camion.mjs <url> <out_dir> [angle-gl|swiftshader]'); process.exit(2) }
mkdirSync(out, { recursive: true })
const args = gl === 'swiftshader' ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] : ['--use-angle=gl', '--ignore-gpu-blocklist', '--enable-gpu']
const browser = await chromium.launch({ args: process.env.CHROME ? ['--ignore-gpu-blocklist'] : args, executablePath: process.env.CHROME, headless: !process.env.HEADFUL })
const SIZES = { 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } } }
const TABS = ['inicio', 'musica', 'grupo', 'contratacion']
const res = { url, gl, shots: [], frames: {} }

async function abrir(w, extra = {}) {
  const ctx = await browser.newContext({ ...SIZES[w], ...extra })
  const page = await ctx.newPage()
  await page.goto(`${url}?sinrespaldo`, { waitUntil: 'load' })
  await page.waitForFunction(() => document.documentElement.dataset.modo === 'vivo', null, { timeout: 60000 })
  res.renderer ??= await page.evaluate(() => {
    const g = document.createElement('canvas').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info')
    return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : g.getParameter(g.RENDERER)
  })
  await page.waitForTimeout(1500)
  return { ctx, page }
}

for (const w of [390, 1440]) {
  const { ctx, page } = await abrir(w)
  for (const preset of ['noche', 'atardecer']) {
    await page.click(`.hora button[data-preset="${preset}"]`)
    await page.waitForTimeout(1200)
    for (const t of TABS) {
      await page.click(`#tab-${t}`)
      await page.waitForTimeout(2200) // move is 1.6 s
      const f = `${out}/${w}-${preset}-${t}.jpg`
      await page.screenshot({ path: f, quality: 82 })
      res.shots.push(f)
    }
  }
  // frame times
  const cdp = await ctx.newCDPSession(page)
  const rate = w === 390 ? 4 : 1
  await cdp.send('Emulation.setCPUThrottlingRate', { rate })
  await page.click('.hora button[data-preset="noche"]')
  await page.click('#tab-inicio')
  await page.waitForTimeout(1000)
  await page.evaluate(() => (window.__escena.frameTimes.length = 0))
  await page.waitForTimeout(5000)
  const ft = await page.evaluate(() => [...window.__escena.frameTimes])
  const s = ft.slice(1).sort((a, b) => a - b), q = (p) => +s[Math.min(s.length - 1, Math.floor(p * s.length))].toFixed(1)
  res.frames[`${w}@cpu${rate}`] = { n: s.length, p50: q(0.5), p95: q(0.95), fallback_would_fire: q(0.5) > 50 }
  await ctx.close()
}

// recording of the moves at 1440, night then dusk
const vdir = `${out}/video-tmp`
const { ctx, page } = await abrir(1440, { recordVideo: { dir: vdir, size: { width: 1440, height: 900 } } })
for (const t of [...TABS.slice(1), 'inicio']) { await page.click(`#tab-${t}`); await page.waitForTimeout(2400) }
await page.click('.hora button[data-preset="atardecer"]'); await page.waitForTimeout(1500)
for (const t of [...TABS.slice(1), 'inicio']) { await page.click(`#tab-${t}`); await page.waitForTimeout(2400) }
await ctx.close()
renameSync(`${vdir}/${readdirSync(vdir)[0]}`, `${out}/movimientos-1440.webm`)
await browser.close()
writeFileSync(`${out}/resultados.json`, JSON.stringify(res, null, 2))
console.log(JSON.stringify({ renderer: res.renderer, frames: res.frames, shots: res.shots.length }, null, 2))

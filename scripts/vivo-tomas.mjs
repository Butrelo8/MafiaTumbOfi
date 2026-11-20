#!/usr/bin/env node
// Live scene check shots: every stop, the four stop-4 member shots, and views that are no stop (the truck's sides, three-quarter
// front and rear, El Manco's feet, Héctor's bottle) framed through window.__vivo.cam / .mira, at 1440 and 390, all with ?f=0.
// Then the emblem drift under the truck's sway: the MT emblem against a hood point, both projected to pixels, over 3 s live.
//   [emblem vertex x,y,z (three.js axes)] enables the drift; SOLO_DERIVA=1 skips the shots.
// Writes <out>/<w>-<name>.png and <out>/tomas.json (page errors, draw calls per shot, drift).
//   Windows GPU: PW=E:\tmp\pw-vivo\node_modules\playwright-core CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe" \
//     node.exe scripts/vivo-tomas.mjs <url> <out_dir (Windows)>
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'

const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, out, vertice] = process.argv.slice(2)
const punto = vertice ? vertice.split(',').map(Number) : null
const SOLO_DERIVA = process.env.SOLO_DERIVA === '1'
mkdirSync(out, { recursive: true })
const SIZES = { 390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }, 1440: { viewport: { width: 1440, height: 900 } } }
// Blender axes (Z up, the truck faces +Y); [query, camera, look-at] (null camera = the stop's own)
const VISTAS = {
  ...Object.fromEntries([0, 1, 2, 3, 4, 5].map((p) => [`parada${p + 1}`, [`parada=${p}`, null, null]])),
  ...Object.fromEntries(['manager', 'hector', 'alejandro', 'diego'].map((m, k) => [`banda-${m}`, [`parada=3&toma=${k}`, null, null]])),
  frente34: ['parada=1', [-1.6, 7.2, 1.7], [1.72, 2.2, 1.25]],
  lado_izq: ['parada=1', [-3.6, 1.6, 1.55], [0.95, 1.0, 1.28]],
  lado_der: ['parada=1', [7.0, 1.6, 1.55], [2.5, 1.0, 1.28]],
  tras34: ['parada=1', [-1.8, -7.6, 3.5], [1.72, -2.1, 1.45]],
  caja_arriba: ['parada=1', [1.72, -4.6, 4.2], [1.72, -2.0, 1.4]],
  manco_pies: ['parada=3&toma=3', [1.78, 1.02, 1.5], [1.3, 0.8, 1.13]],
  hector_botella: ['parada=3&toma=3', [2.45, 1.3, 1.95], [2.15, 0.87, 1.57]],
  cabina_atras: ['parada=3&toma=3', [1.72, -0.2, 2.05], [1.72, 0.9, 1.35]],
  // the cab close-ups for the old-seat leftovers and the console / dash clipping (owner 2026-11-19), and the roof from above
  asiento_izq_lado: ['parada=3&toma=3', [1.30, 1.25, 2.02], [1.33, 0.4, 1.4]],
  asiento_der_lado: ['parada=3&toma=3', [2.10, 1.25, 2.02], [2.11, 0.4, 1.4]],
  tablero: ['parada=3&toma=3', [1.72, 0.35, 1.75], [1.72, 1.2, 1.45]],
  techo: ['parada=1', [1.72, -1.2, 4.6], [1.72, 0.8, 2.1]],
}
const res = { url, errores: [], calls: {}, deriva: null }

async function abrir(w, q) {
  const ctx = await browser.newContext(SIZES[w])
  const page = await ctx.newPage()
  page.on('pageerror', (e) => res.errores.push(`${w} ${q}: ${e.message}`))
  await page.goto(`${url}?${q}`, { waitUntil: 'load' })
  await page.waitForFunction(() => window.__vivo?.cargado, null, { timeout: 120000 })
  await page.waitForTimeout(1500)
  return { ctx, page }
}

const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] })
for (const w of SOLO_DERIVA ? [] : [1440, 390]) {
  for (const [nombre, [q, pos, mira]] of Object.entries(VISTAS)) {
    const { ctx, page } = await abrir(w, `f=0&sinpantalla&${q}`)
    await page.locator('nav, h1, #creditos, header, .apertura').evaluateAll((els) => els.forEach((e) => (e.style.visibility = 'hidden')))
    if (pos) await page.evaluate(([p, m]) => { const v = window.__vivo; v.cam.position.set(p[0], p[2], -p[1]); v.mira.set(m[0], m[2], -m[1]) }, [pos, mira])
    await page.waitForTimeout(500)
    res.calls[`${w}-${nombre}`] = await page.evaluate(() => window.__vivo.calls)
    await page.screenshot({ path: `${out}/${w}-${nombre}.png` })
    await ctx.close()
  }
}
// emblem drift: live (no ?f) at the front stop. The page merges static meshes per rigid parent, so the emblem has no node of its
// own: find the merged mesh holding the emblem's top vertex (argv[3], three.js axes, from the GLB), then track that vertex
// against a hood point held in truck space (0.35 m behind, 0.12 m over it), both in pixels at 1440, over ~90 frames
if (punto) {
  const { ctx, page } = await abrir(1440, 'parada=5&sinpantalla')
  res.deriva = await page.evaluate(async (t) => {
    const v = window.__vivo, cam = v.cam, V3 = cam.position.constructor
    let camion = null, malla = null, idx = -1, dmin = Infinity
    const p = new V3()
    v.escena.updateMatrixWorld(true)
    v.escena.traverse((o) => {
      if (!camion && o.name === 'camion') camion = o
      if (!o.isMesh || o.isSkinnedMesh || o.isInstancedMesh) return
      const a = o.geometry.attributes.position
      for (let i = 0; i < a.count; i++) {
        p.fromBufferAttribute(a, i).applyMatrix4(o.matrixWorld)
        const d = Math.hypot(p.x - t[0], p.y - t[1], p.z - t[2])
        if (d < dmin) { dmin = d; malla = o; idx = i }
      }
    })
    const capo = camion.worldToLocal(new V3(t[0], t[1] + 0.12, t[2] + 0.35))
    const px = (q) => { q.project(cam); return [(q.x + 1) * innerWidth / 2, (1 - q.y) * innerHeight / 2] }
    const muestras = []
    for (let i = 0; i < 90; i++) {
      await new Promise((r) => requestAnimationFrame(r))
      await new Promise((r) => setTimeout(r, 30))
      const a = px(new V3().fromBufferAttribute(malla.geometry.attributes.position, idx).applyMatrix4(malla.matrixWorld))
      const b = px(camion.localToWorld(capo.clone()))
      muestras.push([a[0] - b[0], a[1] - b[1]])
    }
    const m0 = muestras[0]
    const d = muestras.map(([x, y]) => Math.hypot(x - m0[0], y - m0[1]))
    let enCamion = false
    for (let o = malla; o; o = o.parent) if (o === camion) enCamion = true
    return { vertice_a_m: +dmin.toFixed(4), malla_en_camion: enCamion, muestras: muestras.length, max_px: +Math.max(...d).toFixed(3) }
  }, punto)
  await ctx.close()
}
await browser.close()
writeFileSync(`${out}/tomas.json`, JSON.stringify(res, null, 1))
console.log(JSON.stringify({ errores: res.errores.length, deriva: res.deriva, calls: res.calls }))

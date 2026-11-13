// Frame strip of the loop toggle's play/pause morph, sampled from the built page's own rAF (MorphSVG animates `d` from JS,
// which revisar cannot see). Usage: node scripts/morph-tira.mjs <url> <out dir> [--reduce]
import { chromium } from '/home/black/projects/visual-lab/web/skills/diseccion/scripts/node_modules/playwright-core/index.mjs'
import { mkdirSync, writeFileSync } from 'node:fs'
const [url, out] = process.argv.slice(2), reduce = process.argv.includes('--reduce')
mkdirSync(out, { recursive: true })
const b = await chromium.launch()
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: reduce ? 'reduce' : 'no-preference' })
const p = await ctx.newPage()
await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(800)
const muestras = await p.evaluate(() => new Promise((res) => {
  const trazo = document.querySelector('#pausa .icono path'), m = [], t0 = performance.now()
  const paso = () => {
    m.push({ t: Math.round(performance.now() - t0), d: trazo.getAttribute('d'), tf: trazo.getAttribute('transform') || getComputedStyle(trazo).transform })
    performance.now() - t0 < 420 ? requestAnimationFrame(paso) : res(m)
  }
  document.getElementById('pausa').click(); requestAnimationFrame(paso)
}))
writeFileSync(`${out}/muestras${reduce ? '-reduce' : ''}.json`, JSON.stringify(muestras))
const cambia = muestras.filter((s, i) => i && (s.d !== muestras[i - 1].d || s.tf !== muestras[i - 1].tf))
const dur = cambia.length ? cambia.at(-1).t - cambia[0].t : 0
console.log(`${reduce ? 'reduced' : 'normal'}: ${muestras.length} samples, first change ${cambia[0]?.t} ms, last change ${cambia.at(-1)?.t} ms, span ${dur} ms, distinct d: ${new Set(muestras.map((s) => s.d)).size}`)
const pasos = [0, 1, 2, 3, 4, 5, 6].map((i) => muestras[Math.min(muestras.length - 1, Math.round((i * 42) / 16.7))])
const html = `<body style="margin:0;background:#000;display:flex;gap:4px;padding:6px">${pasos.map((s) => `<figure style="margin:0;color:#aaa;font:12px sans-serif;text-align:center"><svg viewBox="0 0 24 24" width="88" height="88" style="background:#0b0b0d"><path d="${s.d}" transform="${/matrix/.test(s.tf) ? `matrix(${s.tf.match(/matrix\(([^)]+)/)[1]})` : ''}" fill="#e8b84a"/></svg>${s.t} ms</figure>`).join('')}</body>`
const q = await ctx.newPage(); await q.setContent(html); await q.screenshot({ path: `${out}/morph${reduce ? '-reduce' : ''}.png`, clip: { x: 0, y: 0, width: 800, height: 150 } })
await b.close()

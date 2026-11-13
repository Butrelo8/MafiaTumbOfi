// Stages the loop toggle's real states on a built page and shoots them (revisar --state cannot stage a failure).
// Usage: node scripts/estados-toggle.mjs <url> <out dir>
import { chromium } from '/home/black/projects/visual-lab/web/skills/diseccion/scripts/node_modules/playwright-core/index.mjs'
import { mkdirSync } from 'node:fs'
const [url, out] = process.argv.slice(2); mkdirSync(out, { recursive: true })
const b = await chromium.launch()
const leer = (p) => p.evaluate(() => { const t = document.getElementById('pausa'); return { oculto: t.hidden, etiqueta: t.textContent.trim(), anillo: !t.querySelector('.anillo').hidden } })
async function caso(nombre, ancho, preparar) {
  const ctx = await b.newContext({ viewport: { width: ancho, height: 844 } }); const p = await ctx.newPage()
  await preparar(p, ctx); await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(1500)
  const s = await leer(p); console.log(nombre, ancho, JSON.stringify(s))
  await p.screenshot({ path: `${out}/${nombre}-${ancho}.png`, clip: { x: 0, y: 0, width: ancho, height: 844 } }); await ctx.close()
}
for (const w of [1440, 390]) {
  // waiting: the loop request is held open, so the video buffers
  await caso('cargando', w, (p) => p.route('**/escena/loop-*.mp4', () => {}))
  // error: the loop source fails for real (aborted request)
  await caso('error-fuente', w, (p) => p.route('**/escena/loop-*.mp4', (r) => r.abort()))
  // refused: iOS Low Power Mode makes play() reject with NotAllowedError
  await caso('play-rechazado', w, (p) => p.addInitScript(() => { HTMLMediaElement.prototype.play = () => Promise.reject(new DOMException('x', 'NotAllowedError')) }))
}
await b.close()

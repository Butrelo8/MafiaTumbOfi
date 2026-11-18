// DOM test for the loop toggle on the BUILT /anterior page (the A Carretera home) (bun test runs it: src/lib/toggleDom.test.ts). The pure state lives in
// estadoBoton.ts; what only a browser shows is that the toggle really is hidden (a scoped `display` once beat [hidden]).
// Usage: node scripts/toggle-dom-test.mjs [dist dir]   exit 0 pass, 1 fail
import { chromium } from '/home/black/projects/visual-lab/web/skills/diseccion/scripts/node_modules/playwright-core/index.mjs'
import { createServer } from 'node:http'
import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { extname, join, normalize } from 'node:path'
const dist = process.argv[2] || fileURLToPath(new URL('../dist', import.meta.url))
if (!existsSync(join(dist, 'index.html'))) { console.error(`no ${dist}/index.html: run bun run build first`); process.exit(1) }
const tipos = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.mp4': 'video/mp4', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2' }
const srv = createServer((q, r) => {
  const f = join(dist, normalize(q.url.split('?')[0]).replace(/\/$/, '/index.html'))
  if (!f.startsWith(dist) || !existsSync(f)) { r.statusCode = 404; return r.end() }
  r.setHeader('content-type', tipos[extname(f)] || 'application/octet-stream'); r.end(readFileSync(f))
}).listen(0)
const url = `http://127.0.0.1:${srv.address().port}/anterior/`
const b = await chromium.launch(); let fallos = 0
const caja = async (p) => { const t = p.locator('#pausa'); return { visible: await t.isVisible(), box: await t.boundingBox() } }
async function caso(nombre, opciones, preparar, espera) {
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, ...opciones }); const p = await ctx.newPage()
  if (preparar) await preparar(p)
  await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(espera)
  const { visible, box } = await caja(p)
  const ok = !visible && !box
  console.log(`${ok ? 'pass' : 'FAIL'} ${nombre}: visible=${visible} box=${JSON.stringify(box)}`); if (!ok) fallos++
  await ctx.close()
}
await caso('sin JavaScript el interruptor no se ve', { javaScriptEnabled: false }, null, 500)
await caso('si el video no carga el interruptor se oculta', {}, (p) => p.route('**/escena/loop-*.mp4', (r) => r.abort()), 1500)
const ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); const p = await ctx.newPage()
await p.goto(url, { waitUntil: 'load' }); await p.waitForTimeout(1000)
const vivo = (await caja(p)).visible; console.log(`${vivo ? 'pass' : 'FAIL'} con JavaScript y video el interruptor se ve: visible=${vivo}`); if (!vivo) fallos++
await b.close(); srv.close(); process.exit(fallos ? 1 : 0)

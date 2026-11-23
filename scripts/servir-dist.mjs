#!/usr/bin/env node
// Serves a built dist/ the way the site is served for measuring: Range requests (worker.js answers them for the videos), brotli for
// text, no caching beyond the browser's own. Usage: node scripts/servir-dist.mjs <dist dir> <port>
import { createServer } from 'node:http'
import { createReadStream, statSync, readFileSync, existsSync } from 'node:fs'
import { join, extname, normalize } from 'node:path'
import { brotliCompressSync } from 'node:zlib'

const [raiz, puerto] = process.argv.slice(2)
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.wasm': 'application/wasm',
  '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.mp4': 'video/mp4', '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.woff': 'font/woff', '.svg': 'image/svg+xml' }
const TEXTO = new Set(['.html', '.js', '.css', '.json', '.svg'])
const cache = new Map()

createServer((req, res) => {
  const url = new URL(req.url, 'http://x')
  let ruta = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, '')
  let f = join(raiz, ruta)
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html')
  if (!existsSync(f)) { res.writeHead(404).end('no'); return }
  const ext = extname(f), tam = statSync(f).size
  const cab = { 'content-type': TIPOS[ext] || 'application/octet-stream', 'accept-ranges': 'bytes', 'cache-control': 'public, max-age=0, must-revalidate' }
  const rango = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range || '')
  if (rango) {
    const a = rango[1] === '' ? tam - +rango[2] : +rango[1], b = rango[1] === '' || rango[2] === '' ? tam - 1 : Math.min(+rango[2], tam - 1)
    res.writeHead(206, { ...cab, 'content-range': `bytes ${a}-${b}/${tam}`, 'content-length': b - a + 1 })
    createReadStream(f, { start: a, end: b }).pipe(res)
  } else if (TEXTO.has(ext) && /\bbr\b/.test(req.headers['accept-encoding'] || '')) {
    if (!cache.has(f)) cache.set(f, brotliCompressSync(readFileSync(f)))
    const cuerpo = cache.get(f)
    res.writeHead(200, { ...cab, 'content-encoding': 'br', 'content-length': cuerpo.length }).end(cuerpo)
  } else {
    res.writeHead(200, { ...cab, 'content-length': tam })
    createReadStream(f).pipe(res)
  }
}).listen(+puerto, '127.0.0.1', () => console.log(`http://127.0.0.1:${puerto}/`))

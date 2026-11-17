#!/usr/bin/env node
// /prototipo en un motor de navegador: los mismos números en Chromium (WSL) y WebKit (Mac), para compararlos.
//   node scripts/prototipo-motor.mjs <url-de-/prototipo/> <chromium|webkit> <salida.json>
// Playwright: PW_DIR=<carpeta con node_modules> si no es el global. Sin capturas: sólo números.
import { createRequire } from 'node:module'
import { execSync } from 'node:child_process'
import fs from 'node:fs'

const [url, motor = 'chromium', salida = 'results.json'] = process.argv.slice(2)
if (!url) { console.error('uso: prototipo-motor.mjs <url> <chromium|webkit> <salida.json>'); process.exit(2) }
const raiz = process.env.PW_DIR ? process.env.PW_DIR + '/' : execSync('npm root -g').toString().trim() + '/'
const pw = createRequire(raiz)('playwright')
const b = await pw[motor].launch()
const R = { motor, url, version: b.version() }
const movil = (o = {}) => ({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, ...o })
const T = (ms) => new Promise((r) => setTimeout(r, ms))

// 1. carga: consola, estado de los dos videos, desborde, objetivos táctiles, alto del hero
async function carga(nombre, opts) {
  const c = await b.newContext(opts); const p = await c.newPage()
  const errores = []; p.on('console', (m) => m.type() === 'error' && errores.push(m.text().slice(0, 120))); p.on('pageerror', (e) => errores.push(String(e).slice(0, 120)))
  await p.goto(url, { waitUntil: 'load' }); await T(4000)
  R[nombre] = await p.evaluate(() => {
    const v = (id) => { const e = document.getElementById(id); return { readyState: e.readyState, w: e.videoWidth, h: e.videoHeight, dur: +e.duration.toFixed(2), err: e.error?.code ?? null } }
    const peq = [...document.querySelectorAll('a,button')].filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.height && (r.height < 44 || r.width < 44) && getComputedStyle(e).visibility !== 'hidden' && !e.closest('.saltar') })
    return {
      ruta: v('ruta'), bucle: v('bucle'),
      scrollW: document.documentElement.scrollWidth, innerW: innerWidth,
      heroH: Math.round(document.getElementById('inicio').getBoundingClientRect().height), innerH: innerHeight,
      masLinks: document.querySelectorAll('.mas-lista a').length, pendientes: document.querySelectorAll('.pendiente').length,
      numero: document.querySelector('.numero')?.textContent ?? null,
      pausaOculto: document.getElementById('pausa').hidden,
      tapPequenos: peq.map((e) => e.textContent.trim().slice(0, 30)),
      fuentes: [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family + ' ' + f.weight).sort(),
    }
  })
  R[nombre].errores = errores
  return { c, p }
}

// 2. escrubeo: ms hasta `seeked` y error de cuadro al saltar el scroll a 8 puntos
async function escrubeo(p) {
  const alto = await p.evaluate(() => document.documentElement.scrollHeight - innerHeight)
  const filas = []
  for (const k of [0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 0.95, 0.3]) {
    await p.evaluate((y) => scrollTo(0, y), Math.round(alto * k)); await T(900)
    filas.push(await p.evaluate(() => { const s = window.__proto, r = document.getElementById('ruta'), l = document.getElementById('bucle'); return { f: +s.f.toFixed(1), t: s.t === null ? null : +s.t.toFixed(1), rutaT: +(r.currentTime * 24).toFixed(1), buclePausado: l.paused, rutaOn: r.classList.contains('on'), bucleOn: l.classList.contains('on') } }))
  }
  return filas
}

// 3. bucle: quieto dentro de La banda debe arrancar solo; tiempo que avanza en 2 s
async function bucle(p) {
  await p.evaluate(() => document.getElementById('integrantes').scrollIntoView({ block: 'center' })); await T(1500)
  const a = await p.evaluate(() => ({ t: document.getElementById('bucle').currentTime, pausado: document.getElementById('bucle').paused }))
  await T(2000)
  const d = await p.evaluate(() => ({ t: document.getElementById('bucle').currentTime, pausado: document.getElementById('bucle').paused, enBucle: window.__proto.t !== null, on: document.getElementById('bucle').classList.contains('on') }))
  // pausa: el botón detiene y cambia la etiqueta
  const antes = await p.textContent('#pausa'); await p.click('#pausa'); await T(500)
  const pausa = await p.evaluate(() => ({ et: document.querySelector('#pausa .et').textContent, pausado: document.getElementById('bucle').paused }))
  return { inicio: a, despues2s: d, avanzo: +(d.t - a.t).toFixed(2), etiquetaAntes: antes.trim(), pausa }
}

{ const { c, p } = await carga('movil', movil()); R.escrubeo = await escrubeo(p); await c.close() }
{ const { c, p } = await carga('movil2', movil()); R.bucle = await bucle(p); await c.close() }
{ const { c, p } = await carga('escritorio', { viewport: { width: 1440, height: 900 } }); await c.close() }
// 4. movimiento reducido: sin bucle, botón oculto
{ const { c, p } = await carga('reducido', movil({ reducedMotion: 'reduce' }))
  await p.evaluate(() => document.getElementById('integrantes').scrollIntoView({ block: 'center' })); await T(2500)
  R.reducidoBucle = await p.evaluate(() => ({ pausado: document.getElementById('bucle').paused, enBucle: window.__proto.t !== null }))
  await c.close() }
// 5. tacto: eventos sintéticos sobre document.body (nunca new Touch(): cierra WebKit)
{ const { c, p } = await carga('tacto', movil())
  R.tacto = await p.evaluate(async () => {
    const e = (t) => document.body.dispatchEvent(new Event(t, { bubbles: true, cancelable: true }))
    e('touchstart'); scrollBy(0, 600); e('touchmove'); e('touchend'); await new Promise((r) => setTimeout(r, 600))
    return { scrollY: Math.round(scrollY), error: null }
  }).catch((x) => ({ error: String(x).slice(0, 120) }))
  await c.close() }
await b.close()
fs.writeFileSync(salida, JSON.stringify(R, null, 1))
console.log(JSON.stringify({ motor, version: R.version, scrollW: R.movil.scrollW, errores: R.movil.errores.length, tapPequenos: R.movil.tapPequenos.length, bucleAvanzo: R.bucle.avanzo }))

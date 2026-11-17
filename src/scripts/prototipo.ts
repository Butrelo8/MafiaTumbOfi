// /prototipo: the scroll drives one fixed stage. Outside the band station it scrubs the run preview (run frame f = currentTime x 24);
// inside it, the loop clip plays by itself when the visitor holds still, and scrolling leaves the loop the way movimiento-plan.md ›
// Band loop says (ruta.ts paso()): move 1 is the run's own stretch, so the exit is jump-free. Sources: references.md › Prototype.
import { FORMAS } from '../lib/formas'
import { bucleInfo, paso, secciones, type Estado } from '../lib/ruta'

const FPS = 24
// Scroll frames per loop frame while the loop is running: the plan's open question "a speed factor" (?gain=N overrides it).
// At 1 the loop needs ~3500 px of scroll to leave; 4 makes it about one screen.
const GANANCIA = Number(new URLSearchParams(location.search).get('gain')) || 4
const REPOSO_MS = 250 // holding still this long inside the station starts the loop
const quieto = matchMedia('(prefers-reduced-motion: reduce)')

const ruta = document.getElementById('ruta') as HTMLVideoElement
const bucle = document.getElementById('bucle') as HTMLVideoElement
const inicial = document.getElementById('escena-f0') as HTMLElement
const boton = document.getElementById('pausa') as HTMLButtonElement
const hud = document.getElementById('hud') as HTMLElement
const barra = document.querySelector('.barra') as HTMLElement
if (new URLSearchParams(location.search).has('hud')) hud.hidden = false

// scroll -> run frame: each section holds its frame range over its own height; the travel between two sections interpolates.
type Clave = { y: number; f: number }
let claves: Clave[] = []
function medir() {
  const vh = innerHeight
  claves = []
  for (const s of secciones) {
    const el = document.getElementById(s.id)
    if (!el) continue
    const r = el.getBoundingClientRect()
    const top = r.top + scrollY, bottom = r.bottom + scrollY
    const y0 = s.id === 'inicio' ? 0 : top - 0.25 * vh
    const y1 = Math.max(y0 + 40, bottom - 0.5 * vh)
    claves.push({ y: y0, f: s.fr[0] }, { y: y1, f: s.fr[1] })
  }
}
function cuadroDeScroll(y: number): number {
  if (y <= claves[0].y) return claves[0].f
  for (let i = 1; i < claves.length; i++) {
    if (y <= claves[i].y) {
      const a = claves[i - 1], b = claves[i]
      return a.f + ((b.f - a.f) * (y - a.y)) / (b.y - a.y)
    }
  }
  return claves[claves.length - 1].f
}

let e: Estado = { f: 0, t: null }
let pausado = quieto.matches
let ultimoY = -1, ultimoF = 0, quietoDesde = performance.now()
let objetivo: { v: HTMLVideoElement; s: number } | null = null

// one seek at a time per video; the latest target wins when it lands
function buscar(v: HTMLVideoElement, s: number) {
  if (v.seeking) { objetivo = { v, s }; return }
  if (Math.abs(v.currentTime - s) > 0.5 / FPS) v.currentTime = s
}
for (const v of [ruta, bucle]) v.addEventListener('seeked', () => { if (objetivo?.v === v) { const o = objetivo; objetivo = null; buscar(o.v, o.s) } })

function ponerEtiqueta() {
  boton.querySelector('.et')!.textContent = pausado ? 'Reproducir video' : 'Pausar video'
  boton.querySelector('.icono path')!.setAttribute('d', FORMAS[pausado ? 'play' : 'pausa'])
}

function pintar(enBucle: boolean, tBucle: number) {
  ruta.classList.toggle('on', !enBucle)
  bucle.classList.toggle('on', enBucle)
  if (enBucle) { if (bucle.paused) buscar(bucle, tBucle / FPS) } else buscar(ruta, e.f / FPS)
}

function tic(ahora: number) {
  requestAnimationFrame(tic)
  const y = scrollY
  const F = cuadroDeScroll(y)
  if (ultimoY < 0) { e = { f: F, t: null }; ultimoY = y; ultimoF = F }
  const dF = F - ultimoF
  ultimoF = F
  const mov = Math.abs(dF) > 1e-6
  if (mov) quietoDesde = ahora
  if (quieto.matches) {
    // reduced motion: poses, not travel: the frame changes in steps and the loop never plays
    if (Math.abs(F - e.f) > 48) e = { f: F, t: null }
    e = { f: e.f, t: null }
  } else if (e.t !== null) {
    if (!bucle.paused) e = { f: e.f, t: bucle.currentTime * FPS }
    if (mov) {
      bucle.pause()
      // the gain only speeds moves 2-3; in move 1 the run takes over at 1:1, so there is no jump ahead and no rewind
      e = paso(e, e.t > bucleInfo.hasta - bucleInfo.desde ? dF * GANANCIA : dF, 0)
    } else if (bucle.paused && !pausado) void bucle.play().catch(() => { pausado = true; ponerEtiqueta() })
  } else {
    const dentro = e.f >= bucleInfo.desde && e.f <= bucleInfo.hasta
    if (!mov && dentro && ahora - quietoDesde > REPOSO_MS && !pausado) {
      e = paso(e, 0, 0.001) // enter the loop where the run stands
      bucle.currentTime = (e.t ?? 0) / FPS
      void bucle.play().catch(() => { pausado = true; ponerEtiqueta() })
    } else {
      // follow the scroll; after a loop exit the run is behind it, so it catches up at up to 3x
      const deuda = F - e.f - dF // how far the run is behind the scroll before this tick (negative: ahead of it)
      const tope = Math.max(3, Math.abs(dF) * 2)
      // behind: fast-forward up to 3x; ahead (after leaving move 1): half speed while scrolling forward, never a rewind
      const mueve = deuda >= 0 ? dF + Math.min(tope, deuda) : dF > 0 ? dF * 0.5 : dF
      e = { f: e.f + mueve, t: null }
    }
  }
  const dentroBucle = e.t !== null || (e.f >= bucleInfo.desde && e.f <= bucleInfo.hasta)
  pintar(dentroBucle, e.t ?? Math.max(0, e.f - bucleInfo.desde))
  inicial.style.visibility = ruta.readyState >= 2 ? 'hidden' : 'visible'
  barra.classList.toggle('solida', y > 8)
  if (!hud.hidden) hud.textContent = `F ${F.toFixed(0)} · f ${e.f.toFixed(0)} · ${e.t === null ? 'ruta' : `bucle t ${e.t.toFixed(0)}`}${bucle.paused ? '' : ' ▶'}`
  ;(window as any).__proto = { f: e.f, t: e.t, F }
}

boton.hidden = false
boton.addEventListener('click', () => {
  pausado = !pausado
  if (pausado) bucle.pause()
  ponerEtiqueta()
})
if (quieto.matches) boton.hidden = true
ponerEtiqueta()

addEventListener('resize', medir)
addEventListener('load', medir)
medir()
requestAnimationFrame(tic)

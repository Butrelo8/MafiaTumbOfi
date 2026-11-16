// The whole run's camera path (src/lib/ruta.json), sampled the same way blender/ruta.py samples it, so what Blender renders is
// what the page can reproduce. Pure math, no three.js: muestra() returns a column-major 4x4 that three's Matrix4.fromArray takes.
import ruta from './ruta.json'

type V3 = [number, number, number]
type Punto = { fr: number }
const PERIODO = 240

// cubic Hermite through the points with monotone tangents over frame time (Fritsch-Carlson style, per component): the Bessel
// slope (h1·d0 + h0·d1) / (h0 + h1), zero where the component turns back, capped at 3x the slower neighbouring slope, so a slow
// section next to a fast move never overshoots backwards. One-sided at the ends unless `ext` gives the end tangents; clamped outside.
function tangentes<T extends Punto>(ps: T[], val: (p: T) => number[], ext?: number[][]) {
  const n = ps.length
  const sec = (i: number) => { const a = val(ps[i]), b = val(ps[i + 1]); return a.map((x, j) => (b[j] - x) / (ps[i + 1].fr - ps[i].fr)) }
  return (i: number) => {
    if (i === 0) return ext ? ext[0] : sec(0)
    if (i === n - 1) return ext ? ext[1] : sec(n - 2)
    const d0 = sec(i - 1), d1 = sec(i), h0 = ps[i].fr - ps[i - 1].fr, h1 = ps[i + 1].fr - ps[i].fr
    return d0.map((a, j) => {
      const b = d1[j]
      if (a * b <= 0) return 0
      const m = (a * h1 + b * h0) / (h0 + h1)
      return Math.sign(m) * Math.min(Math.abs(m), 3 * Math.abs(a), 3 * Math.abs(b))
    })
  }
}

function hermite<T extends Punto>(ps: T[], val: (p: T) => number[], f: number, ext?: number[][]): number[] {
  const n = ps.length
  if (f <= ps[0].fr) return val(ps[0])
  if (f >= ps[n - 1].fr) return val(ps[n - 1])
  let k = 0
  while (ps[k + 1].fr < f) k++
  const tan = tangentes(ps, val, ext)
  const h = ps[k + 1].fr - ps[k].fr, s = (f - ps[k].fr) / h
  const s2 = s * s, s3 = s2 * s
  const h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2
  const p0 = val(ps[k]), p1 = val(ps[k + 1]), m0 = tan(k), m1 = tan(k + 1)
  return p0.map((x, j) => h00 * x + h10 * h * m0[j] + h01 * p1[j] + h11 * h * m1[j])
}

const norm = (v: V3): V3 => { const l = Math.hypot(...v); return [v[0] / l, v[1] / l, v[2] / l] }
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
const ondas = (o: number[][], f: number) => o.reduce((s, [g, c]) => s + g * Math.sin((2 * Math.PI * c * f) / PERIODO), 0) * (Math.PI / 180)

// 3x3 as columns [x, y, z]; r(axis, angle) about the camera's own axis
function girar(cols: V3[], eje: 0 | 1 | 2, a: number): V3[] {
  const c = Math.cos(a), s = Math.sin(a)
  const [u, v] = eje === 0 ? [1, 2] : eje === 1 ? [2, 0] : [0, 1]
  const out = cols.slice() as V3[]
  out[u] = cols[u].map((x, j) => c * x + s * cols[v][j]) as V3
  out[v] = cols[v].map((x, j) => -s * cols[u][j] + c * x) as V3
  return out
}

export interface Pose { pos: V3; mira: V3; mm: number; m: number[] }

type PuntoCam = { fr: number; pos: number[]; mira: number[]; mm: number }
const camVal = (p: PuntoCam) => [...p.pos, ...p.mira, p.mm]

export const muestra = (f: number): Pose => orientar(hermite(ruta.camara, camVal, f), f)

// the camera looks at `mira` with world up; `vibra` (phase = run frame f) turns it in its own axes
function orientar([px, py, pz, mx, my, mz, mm]: number[], f: number): Pose {
  const pos: V3 = [px, py, pz], mira: V3 = [mx, my, mz]
  const z = norm([px - mx, py - my, pz - mz])
  const x = norm(cross([0, 1, 0], z))
  let cols: V3[] = [x, cross(z, x), z]
  const vb = ruta.vibra
  cols = girar(cols, 0, ondas(vb.cabeceo, f)) // pitch about the camera's x
  cols = girar(cols, 1, ondas(vb.giro, f)) // yaw about its y
  cols = girar(cols, 2, ondas(vb.alabeo, f)) // roll about its z
  const m = [...cols[0], 0, ...cols[1], 0, ...cols[2], 0, ...pos, 1]
  return { pos, mira, mm, m }
}

// The band station's loop (owner 2026-11-16 08:45): `largo` frames, three moves. Loop frame t in [0, hasta - desde] is the run's own
// stretch desde..hasta (move 1, the hood slide), so the loop and the run share every pose there. The rest is a Hermite from the run's
// pose at `hasta` through ruta.json's loop points back to its pose at `desde`, with the run's own tangents at both ends, so the
// handovers and the wrap are continuous in position and velocity. `largo` is a multiple of 240, so vibra (phase desde + t) loops too.
const B = ruta.bucles[0]
const L1 = B.hasta - B.desde
const corrida = (fr: number) => ruta.camara.find((p) => p.fr === fr)!
const tanCorrida = tangentes(ruta.camara, camVal)
const ptsBucle: PuntoCam[] = [{ ...corrida(B.hasta), fr: L1 }, ...B.camara.map((p) => ({ ...p, fr: p.t })), { ...corrida(B.desde), fr: B.largo }]
const extBucle = [tanCorrida(ruta.camara.indexOf(corrida(B.hasta))), tanCorrida(ruta.camara.indexOf(corrida(B.desde)))]
export const bucleInfo = { seccion: B.seccion, desde: B.desde, hasta: B.hasta, largo: B.largo, clip: B.clip }

export function bucle(t: number): Pose {
  const u = ((t % B.largo) + B.largo) % B.largo
  if (u <= L1) return muestra(B.desde + u)
  return orientar(hermite(ptsBucle, camVal, u, extBucle), B.desde + u)
}

// One page tick. `f` is the run frame the scroll has carried the camera to; `t` is the loop frame while the camera is in the loop.
// df: run frames the scroll moved since the last tick (0 = holding still); dt: clock frames since the last tick (seconds x fps).
// Holding inside the station starts the loop where the run stands (same pose: move 1 is the run). Scrolling while in move 1 leaves at
// once; scrolling in move 2 or 3 drives the loop's clock in the scroll's direction until it is back on move 1 (forward: through the
// windshield to the hood at `desde`; back: to `hasta`), and the run goes on from there. No blend, so no cut through the cab.
export interface Estado { f: number; t: number | null }

export function paso(e: Estado, df: number, dt: number): Estado {
  if (e.t === null) {
    if (df === 0 && e.f >= B.desde && e.f <= B.hasta) return { f: e.f, t: (e.f - B.desde + dt) % B.largo }
    return { f: e.f + df, t: null }
  }
  if (df === 0) return { f: e.f, t: (e.t + dt) % B.largo }
  if (e.t <= L1) return { f: B.desde + e.t + df, t: null }
  const t = e.t + df
  if (t >= B.largo) return { f: B.desde + t - B.largo, t: null }
  if (t <= L1) return { f: B.desde + t, t: null }
  return { f: e.f, t }
}

export const poseEstado = (e: Estado) => (e.t === null ? muestra(e.f) : bucle(e.t))

// vertical field of view (degrees) for a canvas aspect (w / h): the lens is on a 36 mm horizontal sensor
export const fovVertical = (mm: number, aspecto: number) => (2 * Math.atan(18 / (mm * aspecto)) * 180) / Math.PI

export const pantalla = (f: number) => hermite(ruta.pantalla, (p) => p.pos, f) as V3

export function flash(f: number): number {
  const k = ruta.flash
  if (f <= k[0][0] || f >= k[k.length - 1][0]) return 0
  let i = 0
  while (k[i + 1][0] < f) i++
  return k[i][1] + ((k[i + 1][1] - k[i][1]) * (f - k[i][0])) / (k[i + 1][0] - k[i][0])
}

export const secciones = ruta.secciones
export const ultimo = ruta.camara[ruta.camara.length - 1].fr

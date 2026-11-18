// Camera path between two stop compositions of the live scene (/vivo-secciones), in the truck's own frame, Blender axes
// (x right, y forward, z up, metres). Exterior to exterior: the camera orbits the truck (elliptic polar coordinates around
// its centre, radius and height interpolated), lifted over the roof when the straight orbit would cut through the body.
// A stop inside the cab leaves or enters through the windshield, as the Cycles cab -> outside move does (transicion.CAMINO).
export type V3 = [number, number, number]
export interface Caja { min: V3; max: V3 }
export interface Parada { pos: V3; mira: V3; lens: number }
export interface Ruta { pos: V3[]; mira: V3[]; lens: number[]; largo: number }

const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const lerp3 = (a: V3, b: V3, t: number): V3 => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]
const dist = (a: V3, b: V3) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])
const suave = (t: number) => t * t * (3 - 2 * t)

export const dentro = (p: V3, c: Caja, m = 0) =>
  p[0] > c.min[0] - m && p[0] < c.max[0] + m && p[1] > c.min[1] - m && p[1] < c.max[1] + m && p[2] > c.min[2] - m && p[2] < c.max[2] + m

/** Orbit from a to b around box c (both outside it), n+1 samples, lifted so that no sample comes within `margen` of the box. */
export function orbita(a: V3, b: V3, c: Caja, margen = 0.35, n = 48): V3[] {
  const cx = (c.min[0] + c.max[0]) / 2, cy = (c.min[1] + c.max[1]) / 2
  const ax = (c.max[0] - c.min[0]) / 2 + margen, ay = (c.max[1] - c.min[1]) / 2 + margen
  const polar = (p: V3) => [Math.atan2((p[1] - cy) / ay, (p[0] - cx) / ax), Math.hypot((p[0] - cx) / ax, (p[1] - cy) / ay)]
  const [ta, ra] = polar(a), [tb0, rb] = polar(b)
  let tb = tb0
  while (tb - ta > Math.PI) tb -= 2 * Math.PI
  while (tb - ta < -Math.PI) tb += 2 * Math.PI
  const base: V3[] = []
  for (let i = 0; i <= n; i++) {
    const t = i / n, th = lerp(ta, tb, t), r = lerp(ra, rb, suave(t))
    base.push([cx + Math.cos(th) * r * ax, cy + Math.sin(th) * r * ay, lerp(a[2], b[2], suave(t))])
  }
  // lift: the smallest bump h * sin(pi t) that clears the roof by `margen` wherever a sample is inside the box's footprint
  let h = 0
  base.forEach((p, i) => {
    const s = Math.sin((Math.PI * i) / n)
    if (s > 1e-6 && dentro(p, c, margen)) h = Math.max(h, (c.max[2] + margen - p[2]) / s)
  })
  return base.map((p, i) => [p[0], p[1], p[2] + h * Math.sin((Math.PI * i) / n)])
}

/** The windshield exit for a stop inside the cab: straight ahead to the glass, then out and up over the hood. */
export function salida(p: V3, parabrisas: number, techo: number): V3[] {
  return [p, [p[0], parabrisas - 0.15, p[2]], [p[0], parabrisas + 0.6, p[2] + 0.15], [p[0], parabrisas + 1.4, techo + 0.6]]
}

export function ruta(a: Parada, b: Parada, camion: Caja, cabina: Caja, parabrisas: number): Ruta {
  const ia = dentro(a.pos, cabina), ib = dentro(b.pos, cabina)
  let pos: V3[]
  if (ia && ib) pos = [a.pos, b.pos]
  else {
    const sa = ia ? salida(a.pos, parabrisas, cabina.max[2]) : [a.pos]
    const sb = ib ? salida(b.pos, parabrisas, cabina.max[2]).reverse() : [b.pos]
    pos = [...sa.slice(0, -1), ...orbita(sa.at(-1)!, sb[0], camion), ...sb.slice(1)]
  }
  // densify to even steps so the look-at and lens can follow arc length
  const largos = [0]
  for (let i = 1; i < pos.length; i++) largos.push(largos[i - 1] + dist(pos[i - 1], pos[i]))
  const largo = largos.at(-1)!
  const mira = largos.map((l) => lerp3(a.mira, b.mira, suave(largo ? l / largo : 1)))
  const lens = largos.map((l) => lerp(a.lens, b.lens, suave(largo ? l / largo : 1)))
  return { pos, mira, lens, largo }
}

/** Move time: 1.2 s for a short hop up to 2 s for a long orbit. */
export const duracion = (largo: number) => Math.min(2, Math.max(1.2, 1.2 + largo / 25))

/** Blender lens (mm, 36 mm horizontal sensor) -> three.js vertical fov (degrees) at aspect w/h. */
export const fovVertical = (lens: number, aspecto: number) => (2 * Math.atan(18 / lens / aspecto) * 180) / Math.PI

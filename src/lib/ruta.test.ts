import { describe, expect, test } from 'bun:test'
import ruta from './ruta.json'
import bake from './ruta.bake.json'
import { bucle, bucleInfo as B, flash, muestra, pantalla, paso, poseEstado, type Estado } from './ruta'

const lejos = (a: number[], b: number[]) => Math.max(...a.map((x, j) => Math.abs(x - b[j])))
const vel = (p: (t: number) => number[], t: number, lado: 1 | -1, h = 1e-3) => p(t + lado * h).map((x, j) => (lado * (x - p(t)[j])) / h)
const pb = (t: number) => bucle(t).pos as number[]

describe('ruta', () => {
  test('the path passes through every authored point', () => {
    for (const p of ruta.camara) {
      const s = muestra(p.fr)
      s.pos.forEach((v, j) => expect(v).toBeCloseTo(p.pos[j], 9))
      expect(s.mm).toBeCloseTo(p.mm, 9)
    }
  })

  // blender/ruta.py writes ruta.bake.json from the camera it rendered (matrix_world in three.js axes, lens), the pantalla
  // actor's offset and the flash: the page's sampler must land within 1 mm and 0.001 (about 0.06 degrees) of it
  test('parity with the Blender bake', () => {
    expect(bake.cuadros.length).toBeGreaterThan(100)
    let peor = 0
    for (const c of bake.cuadros) {
      const s = muestra(c.fr)
      s.m.forEach((v, j) => (peor = Math.max(peor, Math.abs(v - c.m[j]))))
      expect(s.mm).toBeCloseTo(c.mm, 4)
      pantalla(c.fr).forEach((v, j) => (peor = Math.max(peor, Math.abs(v - c.pantalla[j]))))
      expect(flash(c.fr)).toBeCloseTo(c.flash, 4)
    }
    expect(peor).toBeLessThan(1e-3)
  })
})

describe('band loop', () => {
  const L1 = B.hasta - B.desde

  test('the run has knots at the loop ends, and the loop length lets vibra loop', () => {
    expect(ruta.camara.some((p) => p.fr === B.desde) && ruta.camara.some((p) => p.fr === B.hasta)).toBe(true)
    expect(B.largo % 240).toBe(0)
    expect(B.clip % 240).toBe(B.desde % 240)
  })

  test('move 1 is the run, and the wrap and both handovers are continuous in pose and velocity', () => {
    for (let t = 0; t <= L1; t += 4) expect(lejos(bucle(t).m, muestra(B.desde + t).m)).toBeLessThan(1e-12)
    expect(lejos(bucle(B.largo).m, bucle(0).m)).toBeLessThan(1e-9)
    const run = (f: number) => muestra(f).pos as number[]
    // velocity in m/frame on each side: hasta (run 743 -> move 2) and the wrap (move 3 -> run 647)
    const vHasta = [vel(run, B.hasta, -1), vel(pb, L1, 1)]
    const vWrap = [vel(pb, B.largo, -1), vel(run, B.desde, 1)]
    console.log('loop handover velocity m/frame', { hasta: vHasta, wrap: vWrap })
    expect(lejos(vHasta[0], vHasta[1])).toBeLessThan(1e-3)
    expect(lejos(vWrap[0], vWrap[1])).toBeLessThan(1e-3)
  })

  // `t` places a point on the approved curve; `reloj` is when the eased loop (scripts/bucle-suave.py) reaches it
  test('the loop passes through its points', () => {
    for (const p of ruta.bucles[0].camara) {
      bucle(p.reloj).pos.forEach((v, j) => expect(v).toBeCloseTo(p.pos[j], 9))
      expect(bucle(p.reloj).mm).toBeCloseTo(p.mm, 9)
    }
  })

  // owner 2026-11-16 16:25: moves 2-3 jerked; the old monotone Hermite's acceleration jumped 0.013-0.079 m/frame² at its knots
  test('moves 2-3 are eased: the acceleration never jumps (knots and both handovers)', () => {
    const acc = (t: number, lado: 1 | -1, h = 1e-2) => {
      const p = [0, 1, 2].map((k) => pb(t + lado * k * h))
      return p[0].map((x, j) => (p[2][j] - 2 * p[1][j] + x) / (h * h))
    }
    let peor = 0
    for (const [t] of ruta.bucles[0].suave.slice(1, -1)) peor = Math.max(peor, lejos(acc(t, 1), acc(t, -1)))
    // handovers: run -> move 2 at L1, move 3 -> run at the wrap
    peor = Math.max(peor, lejos(acc(L1, 1), acc(L1, -1)), lejos(acc(0, 1), acc(B.largo, -1)))
    expect(peor).toBeLessThan(5e-4) // m/frame²; the old knots jumped 0.013-0.079
  })

  test('parity with the Blender bake of the loop clip', () => {
    expect(bake.bucle.length).toBeGreaterThan(100)
    let peor = 0
    for (const c of bake.bucle) {
      peor = Math.max(peor, lejos(bucle(c.t).m, c.m))
      expect(bucle(c.t).mm).toBeCloseTo(c.mm, 4)
    }
    expect(peor).toBeLessThan(1e-3)
  })

  test('scroll: holding loops, scrolling leaves through move 1 with no jump', () => {
    const ir = (e: Estado, df: number, dt: number, n: number) => { for (let i = 0; i < n; i++) e = paso(e, df, dt); return e }
    // holding at 680 starts the loop where the run stands
    let e: Estado = { f: 680, t: null }
    expect(lejos(poseEstado(paso(e, 0, 0)).m, muestra(680).m)).toBe(0)
    e = ir(e, 0, 1, B.largo + 100) // into move 2 of the second cycle
    expect(e.t).toBe(680 - B.desde + 100)
    // forward scroll in move 2 finishes the loop and comes out on the run: every step moves the camera a little, never a jump
    let prev = poseEstado(e).pos as number[], salto = 0
    for (let i = 0; i < 400 && (e.t !== null || e.f < B.hasta + 30); i++) {
      e = paso(e, 2, 1)
      const p = poseEstado(e).pos as number[]
      salto = Math.max(salto, Math.hypot(...p.map((x, j) => x - prev[j])))
      prev = p
    }
    expect(e.t).toBeNull()
    expect(e.f).toBeGreaterThan(B.hasta)
    expect(salto).toBeLessThan(0.5) // m per tick at 2 frames per tick: the fastest stretch of move 2
    // backward scroll from move 3 plays the loop back to hasta, then the run backwards
    e = { f: 700, t: 400 }
    e = ir(e, -2, 1, 200)
    expect(e.t).toBeNull()
    expect(e.f).toBeLessThan(B.hasta)
  })
})

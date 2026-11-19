import { describe, expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'
import { dentro, duracion, fovVertical, ruta, type Caja, type Parada, type V3 } from './vivoRuta'

// public/vivo/ is git-ignored (blender/vivo_secciones_exportar.py writes it): skip on a checkout without the export
const JSON_VIVO = new URL('../../public/vivo/vivo.json', import.meta.url)
const hay = existsSync(JSON_VIVO)
const datos = hay ? JSON.parse(readFileSync(JSON_VIVO, 'utf8')) : { camaras: [], camion: {}, cabina: {}, parabrisas: 0 }
const paradas = datos.camaras as Parada[]
// stop 4 is four member shots (owner 19:11): camaras[3] is the first (4a), datos.banda all four
const banda = (datos.banda ?? []) as Parada[]
const tomas = [...paradas, ...banda.slice(1)]
const nombre = (i: number) => (i === 3 ? '4a' : i < 6 ? `${i + 1}` : `4${'abcd'[i - 5]}`)
const camion = datos.camion as Caja
const cabina = datos.cabina as Caja

// dense samples of the polyline (the page runs a centripetal Catmull-Rom through the same points)
function muestras(pos: V3[], paso = 0.05): V3[] {
  const out: V3[] = []
  for (let i = 1; i < pos.length; i++) {
    const [a, b] = [pos[i - 1], pos[i]]
    const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) / paso))
    for (let k = 0; k < n; k++) out.push([a[0] + ((b[0] - a[0]) * k) / n, a[1] + ((b[1] - a[1]) * k) / n, a[2] + ((b[2] - a[2]) * k) / n])
  }
  return out
}

describe.skipIf(!hay)('vivoRuta', () => {
  test('six stops, and only the cab stops sit inside the cab', () => {
    expect(paradas.length).toBe(6)
    expect(dentro(paradas[0].pos, cabina)).toBe(true)
  })

  test('stop 4 is the four member shots, each with an exit leg that ends outside the body', () => {
    expect(banda.length).toBe(4)
    expect(paradas[3]).toEqual(banda[0])
    for (const t of banda) {
      expect(dentro(t.pos, camion) && !dentro(t.pos, cabina)).toBe(true)
      expect(dentro(t.salida!, camion, 0.35)).toBe(false)
    }
  })

  for (let i = 0; i < tomas.length; i++)
    for (let j = 0; j < tomas.length; j++) {
      if (i === j) continue
      test(`move ${nombre(i)} -> ${nombre(j)} never passes through the truck body`, () => {
        const [a, b] = [tomas[i], tomas[j]]
        const r = ruta(a, b, camion, cabina, datos.parabrisas)
        r.pos[0].forEach((v, k) => expect(v).toBeCloseTo(a.pos[k], 6))
        r.pos.at(-1)!.forEach((v, k) => expect(v).toBeCloseTo(b.pos[k], 6))
        // a member shot's own exit leg may be inside the box (it was checked against the real body in Blender): skip it
        const resto = r.pos.slice(a.salida ? 1 : 0, b.salida ? -1 : undefined)
        const malas = muestras(resto).filter((p) => dentro(p, camion, 0.05) && !dentro(p, cabina) && !(p[1] > datos.parabrisas - 0.3 && p[1] < datos.parabrisas + 0.3))
        expect(malas).toEqual([])
        if (a.salida) r.pos[1].forEach((v, k) => expect(v).toBeCloseTo(a.salida![k], 6))
        if (b.salida) r.pos.at(-2)!.forEach((v, k) => expect(v).toBeCloseTo(b.salida![k], 6))
        // the roof lift stays a lift (an orbit end inside the box once sent it 13.5-14.8 m up)
        expect(Math.max(...r.pos.map((p) => p[2]))).toBeLessThanOrEqual(camion.max[2] + 5)
        expect(duracion(r.largo)).toBeGreaterThanOrEqual(1.2)
        expect(duracion(r.largo)).toBeLessThanOrEqual(2)
      })
    }

  test('lens to vertical fov: 36 mm sensor, 16:9', () => {
    expect(fovVertical(18, 16 / 9)).toBeCloseTo((2 * Math.atan(0.5625) * 180) / Math.PI, 6)
  })
})

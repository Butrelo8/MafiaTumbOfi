import { describe, expect, test } from 'bun:test'
import { existsSync, readFileSync } from 'node:fs'
import { dentro, duracion, fovVertical, ruta, type Caja, type Parada, type V3 } from './vivoRuta'

// public/vivo/ is git-ignored (blender/vivo_secciones_exportar.py writes it): skip on a checkout without the export
const JSON_VIVO = new URL('../../public/vivo/vivo.json', import.meta.url)
const hay = existsSync(JSON_VIVO)
const datos = hay ? JSON.parse(readFileSync(JSON_VIVO, 'utf8')) : { camaras: [], camion: {}, cabina: {}, parabrisas: 0 }
const paradas = datos.camaras as Parada[]
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

  for (let i = 0; i < 6; i++)
    for (let j = 0; j < 6; j++) {
      if (i === j) continue
      test(`move ${i + 1} -> ${j + 1} never passes through the truck body`, () => {
        const r = ruta(paradas[i], paradas[j], camion, cabina, datos.parabrisas)
        r.pos[0].forEach((v, k) => expect(v).toBeCloseTo(paradas[i].pos[k], 6))
        r.pos.at(-1)!.forEach((v, k) => expect(v).toBeCloseTo(paradas[j].pos[k], 6))
        const malas = muestras(r.pos).filter((p) => dentro(p, camion, 0.05) && !dentro(p, cabina) && !(p[1] > datos.parabrisas - 0.3 && p[1] < datos.parabrisas + 0.3))
        expect(malas).toEqual([])
        expect(duracion(r.largo)).toBeGreaterThanOrEqual(1.2)
        expect(duracion(r.largo)).toBeLessThanOrEqual(2)
      })
    }

  test('lens to vertical fov: 36 mm sensor, 16:9', () => {
    expect(fovVertical(18, 16 / 9)).toBeCloseTo((2 * Math.atan(0.5625) * 180) / Math.PI, 6)
  })
})

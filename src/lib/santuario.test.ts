import { describe, expect, test } from 'bun:test'
import { espacios } from '../data/santuario'
import { clavesDelViaje, colaDePrecarga, ejeDelGesto, elegirFuente, planDeViaje } from './santuario'

// Navegadores de prueba: Chrome con AV1, Safari de iPhone anterior al 15 Pro (HEVC y H.264), y uno
// que sólo entiende H.264.
const chrome = () => 'probably'
const safariViejo = (tipo: string) => (tipo.includes('av01') ? '' : 'maybe')
const soloH264 = (tipo: string) => (tipo.includes('avc1') ? 'probably' : '')

describe('elegirFuente', () => {
  const ida = espacios[1].fondo.escritorio.ida

  test('se queda con la primera que el navegador puede reproducir', () => {
    expect(elegirFuente(ida, chrome)?.src).toBe('/video/escritorio/ida-av1.mp4')
    expect(elegirFuente(ida, safariViejo)?.src).toBe('/video/escritorio/ida-hevc.mp4')
    expect(elegirFuente(ida, soloH264)?.src).toBe('/video/escritorio/ida-h264.mp4')
  })

  test('sin ninguna reproducible devuelve null', () => {
    expect(elegirFuente(espacios[1].fondo.escritorio.vuelta, safariViejo)).toBeNull()
    expect(elegirFuente(undefined, chrome)).toBeNull()
  })
})

describe('planDeViaje', () => {
  test('nave → sacristía reproduce la ida; de vuelta, la vuelta', () => {
    expect(planDeViaje(espacios, 'escritorio', 1, 2, false, chrome)).toEqual({ tipo: 'transicion', clave: '1:ida' })
    expect(planDeViaje(espacios, 'vertical', 2, 1, false, chrome)).toEqual({ tipo: 'transicion', clave: '1:vuelta' })
  })

  test('el hero entra a la nave por negro (ticket 08, sin render)', () => {
    expect(planDeViaje(espacios, 'escritorio', 0, 1, false, chrome)).toEqual({ tipo: 'fundido' })
    expect(planDeViaje(espacios, 'escritorio', 1, 0, false, chrome)).toEqual({ tipo: 'fundido' })
  })

  test('los saltos y las secciones sobre negro cruzan por negro', () => {
    expect(planDeViaje(espacios, 'escritorio', 1, 4, false, chrome)).toEqual({ tipo: 'fundido' })
    expect(planDeViaje(espacios, 'vertical', 2, 3, false, chrome)).toEqual({ tipo: 'fundido' })
  })

  test('una vuelta sin códec que sirva cruza por negro en vez de cortar', () => {
    expect(planDeViaje(espacios, 'escritorio', 2, 1, false, safariViejo)).toEqual({ tipo: 'fundido' })
  })

  test('con movimiento reducido siempre corta', () => {
    expect(planDeViaje(espacios, 'escritorio', 1, 2, true, chrome)).toEqual({ tipo: 'corte' })
  })
})

describe('clavesDelViaje', () => {
  test('la transición espera a su archivo y al loop de llegada', () => {
    const viaje = planDeViaje(espacios, 'vertical', 1, 2, false, chrome)
    expect(clavesDelViaje(espacios, 'vertical', viaje, 2, chrome)).toEqual(['1:ida', '2:loop'])
  })

  test('llegar a negro o a una imagen quieta no espera a nada', () => {
    expect(clavesDelViaje(espacios, 'escritorio', { tipo: 'fundido' }, 3, chrome)).toEqual([])
    const viaje = planDeViaje(espacios, 'escritorio', 1, 2, false, chrome)
    expect(clavesDelViaje(espacios, 'escritorio', viaje, 2, chrome)).toEqual(['1:ida'])
  })
})

describe('colaDePrecarga', () => {
  test('desde el hero lo inmediato es sólo el loop de la nave', () => {
    const cola = colaDePrecarga(espacios, 'vertical', 0, chrome)
    expect(cola.inmediato).toEqual(['1:loop'])
    expect(cola.cascada).toEqual(['1:ida', '1:vuelta', '2:loop'])
  })

  test('desde la sacristía: su loop y la vuelta a la nave primero', () => {
    const cola = colaDePrecarga(espacios, 'vertical', 2, chrome)
    expect(cola.inmediato).toEqual(['2:loop', '1:vuelta'])
    expect(cola.cascada).toEqual(['1:loop', '1:ida'])
  })

  test('lo que el navegador no puede reproducir no se baja', () => {
    const cola = colaDePrecarga(espacios, 'escritorio', 1, safariViejo)
    expect([...cola.inmediato, ...cola.cascada]).not.toContain('1:vuelta')
  })
})

describe('ejeDelGesto', () => {
  test('el eje dominante pasado el umbral', () => {
    expect(ejeDelGesto(5, -120)).toBe('y')
    expect(ejeDelGesto(-90, 30)).toBe('x')
  })

  test('un toque corto no es gesto', () => {
    expect(ejeDelGesto(10, 20)).toBeNull()
  })
})

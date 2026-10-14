import { describe, expect, test } from 'bun:test'
import { espacios as todos } from '../data/santuario'
import { clavesDelViaje, colaDePrecarga, ejeDelGesto, elegirFuente, paraPantalla, planDeViaje } from './santuario'

// Una pantalla de hasta 1920 px físicos, la de casi todo lo de abajo; el peldaño de 2560 va aparte.
const espacios = paraPantalla(todos, false)

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

  test('un loop en varios códecs: el H.264 se llama como el espacio', () => {
    const loop = espacios[3].fondo.vertical.loop
    expect(elegirFuente(loop, chrome)?.src).toBe('/video/vertical/vestidor-av1.mp4')
    expect(elegirFuente(loop, safariViejo)?.src).toBe('/video/vertical/vestidor-hevc.mp4')
    expect(elegirFuente(loop, soloH264)?.src).toBe('/video/vertical/vestidor.mp4')
  })

  test('sin ninguna reproducible devuelve null', () => {
    expect(elegirFuente(espacios[1].fondo.escritorio.vuelta, safariViejo)).toBeNull()
    expect(elegirFuente(undefined, chrome)).toBeNull()
  })
})

describe('paraPantalla', () => {
  const grande = paraPantalla(todos, true)

  test('con más de 1920 px físicos, AV1 y HEVC salen del peldaño de 2560; el H.264 se queda en 1920', () => {
    const loop = grande[3].fondo.escritorio.loop
    expect(elegirFuente(loop, chrome)?.src).toBe('/video/escritorio-2560/vestidor-av1.mp4')
    expect(elegirFuente(loop, safariViejo)?.src).toBe('/video/escritorio-2560/vestidor-hevc.mp4')
    expect(elegirFuente(loop, soloH264)?.src).toBe('/video/escritorio/vestidor.mp4')
    expect(elegirFuente(grande[4].fondo.escritorio.ida, chrome)?.src).toBe('/video/escritorio-2560/contratacion-ida-av1.mp4')
  })

  test('hasta 1920 px, y en vertical siempre, nada de 2560', () => {
    expect(elegirFuente(espacios[3].fondo.escritorio.loop, chrome)?.src).toBe('/video/escritorio/vestidor-av1.mp4')
    expect(elegirFuente(grande[3].fondo.vertical.loop, chrome)?.src).toBe('/video/vertical/vestidor-av1.mp4')
    const fuentes = espacios.flatMap((e) => Object.values(e.fondo).flatMap((f) => [f.loop, f.ida, f.vuelta].flat()))
    expect(fuentes.some((f) => f?.grande)).toBe(false)
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

  test('camarín, cripta y atrio (07): idas de escritorio salvo el grupo, que cruza por negro', () => {
    expect(planDeViaje(espacios, 'escritorio', 2, 3, false, chrome)).toEqual({ tipo: 'transicion', clave: '2:ida' })
    expect(planDeViaje(espacios, 'escritorio', 3, 2, false, chrome)).toEqual({ tipo: 'transicion', clave: '2:vuelta' })
    expect(planDeViaje(espacios, 'escritorio', 3, 4, false, chrome)).toEqual({ tipo: 'fundido' })
    expect(planDeViaje(espacios, 'escritorio', 4, 3, false, chrome)).toEqual({ tipo: 'fundido' })
    expect(planDeViaje(espacios, 'escritorio', 4, 5, false, chrome)).toEqual({ tipo: 'transicion', clave: '4:ida' })
    expect(planDeViaje(espacios, 'escritorio', 5, 4, false, chrome)).toEqual({ tipo: 'transicion', clave: '4:vuelta' })
    expect(planDeViaje(espacios, 'vertical', 4, 5, false, chrome)).toEqual({ tipo: 'fundido' })
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

  test('llegar a negro no espera a nada', () => {
    expect(clavesDelViaje(espacios, 'escritorio', { tipo: 'fundido' }, 0, chrome)).toEqual([])
  })

  test('en escritorio la sacristía también espera a su loop', () => {
    const viaje = planDeViaje(espacios, 'escritorio', 1, 2, false, chrome)
    expect(clavesDelViaje(espacios, 'escritorio', viaje, 2, chrome)).toEqual(['1:ida', '2:loop'])
  })
})

describe('colaDePrecarga', () => {
  test('desde el hero lo inmediato es sólo el loop de la nave', () => {
    const cola = colaDePrecarga(espacios, 'vertical', 0, chrome)
    expect(cola.inmediato).toEqual(['1:loop'])
    expect(cola.cascada).toEqual(['1:ida', '2:loop'])
  })

  test('desde la sacristía: su loop y la vuelta a la nave primero', () => {
    const cola = colaDePrecarga(espacios, 'vertical', 2, chrome)
    expect(cola.inmediato).toEqual(['2:loop', '3:loop', '1:vuelta'])
    expect(cola.cascada).toEqual(['4:loop', '1:loop'])
  })

  test('entrar por #cierre y volver: el viaje de vuelta ya está en la cola', () => {
    const cola = colaDePrecarga(espacios, 'escritorio', 5, chrome)
    const viaje = planDeViaje(espacios, 'escritorio', 5, 4, false, chrome)
    expect(viaje).toEqual({ tipo: 'transicion', clave: '4:vuelta' })
    for (const clave of clavesDelViaje(espacios, 'escritorio', viaje, 4, chrome)) {
      expect([...cola.inmediato, ...cola.cascada]).toContain(clave)
    }
    expect(cola.cascada.at(-1)).toBe('4:loop')
  })

  test('la cascada baja sólo los dos viajes siguientes en el sentido de la marcha', () => {
    const cola = colaDePrecarga(espacios, 'escritorio', 4, chrome, -1)
    expect(cola.inmediato).toEqual(['4:loop', '4:ida', '5:loop'])
    expect(cola.cascada).toEqual(['3:loop', '2:vuelta', '2:loop'])
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

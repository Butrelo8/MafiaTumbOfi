import { describe, expect, test } from 'bun:test'
import { cercania, montarCapas, VENTANA } from './capasEstacion'
import { framesDeEstacion } from './scrollScene'
import escena from '../data/scene.json'

const formato = escena.formatos.desktop

describe('cercania', () => {
  test('en la estación vale 1', () => {
    expect(cercania(60, 60)).toBe(1)
  })

  test('a la ventana entera o más allá vale 0, sin extrapolar', () => {
    expect(cercania(60 + VENTANA, 60)).toBe(0)
    expect(cercania(60 - VENTANA, 60)).toBe(0)
    expect(cercania(9999, 60)).toBe(0)
  })

  test('a media ventana vale medio, y da igual el lado', () => {
    expect(cercania(62, 60, 4)).toBeCloseTo(0.5)
    expect(cercania(58, 60, 4)).toBeCloseTo(0.5)
  })

  test('sin ventana sólo enciende el frame exacto', () => {
    expect(cercania(60, 60, 0)).toBe(1)
    expect(cercania(61, 60, 0)).toBe(0)
  })
})

/** DOM mínimo: sólo lo que el módulo consulta. */
function documentoFalso(indices: number[]) {
  const capas = indices.map((i) => ({ dataset: { capaFrente: String(i) }, style: { opacity: '' } }))
  const secciones = indices.map((i) => ({ dataset: { estacion: String(i) } as Record<string, string> }))
  return {
    documento: {
      querySelectorAll: (selector: string) =>
        selector === '[data-capa-frente]' ? capas : secciones,
    } as unknown as Document,
    capas,
    secciones,
  }
}

describe('montarCapas', () => {
  const frames = framesDeEstacion(formato)

  test('la capa de una estación se enciende al llegar a su frame y se apaga fuera', () => {
    const { documento, capas } = documentoFalso([0, 1])
    const pintar = montarCapas({ formato, framesDeEstacion: frames, documento })

    pintar(frames[1])
    expect(capas[1].style.opacity).toBe('1')
    expect(capas[0].style.opacity).toBe('0')

    pintar(frames[1] + VENTANA)
    expect(capas[1].style.opacity).toBe('0')
  })

  test('el titular entra antes que la capa y sigue puesto cuando ella ya se fue', () => {
    const { documento, secciones } = documentoFalso([1])
    const pintar = montarCapas({ formato, framesDeEstacion: frames, documento })

    pintar(frames[1] + VENTANA)
    expect(secciones[0].dataset.cerca).toBe('1')

    pintar(frames[1] + VENTANA * 4)
    expect(secciones[0].dataset.cerca).toBe('0')
  })

  test('sin movimiento deja todo puesto y no hace nada más', () => {
    const { documento, capas, secciones } = documentoFalso([0, 1])
    const pintar = montarCapas({
      formato, framesDeEstacion: frames, documento, sinMovimiento: true,
    })

    expect(capas[0].style.opacity).toBe('1')
    expect(secciones[0].dataset.cerca).toBe('1')

    // Aunque el frame se vaya lejos, no se apaga nada.
    pintar(9999)
    expect(capas[0].style.opacity).toBe('1')
  })

  test('una estación sin capa no rompe el resto', () => {
    // Hoy las seis estaciones tienen capa; se quita la última para cubrir el caso.
    const estaciones = formato.estaciones.map((e, i, todas) => {
      if (i !== todas.length - 1) return e
      const { capaFrente: _, ...sinCapa } = e
      return sinCapa
    })
    expect(estaciones.some((e) => !('capaFrente' in e))).toBe(true)

    const { documento, capas } = documentoFalso([0])
    const pintar = montarCapas({ formato: { ...formato, estaciones } as typeof formato, framesDeEstacion: frames, documento })
    pintar(frames[0])
    expect(capas[0].style.opacity).toBe('1')
  })
})

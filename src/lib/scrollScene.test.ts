import { describe, expect, test } from 'bun:test'
import { formatoParaPantalla, frameEnScroll, rutasDeFrames } from './scrollScene'
import escena from '../data/scene.json'

const formato = escena.formatos.mobile

describe('rutasDeFrames', () => {
  test('una ruta por frame, en orden de scroll', () => {
    const rutas = rutasDeFrames(formato)
    expect(rutas.length).toBe(formato.tramos.reduce((suma, t) => suma + t.frames, 0))
    expect(rutas[0]).toBe('/scene/mobile/tramo-0/000.avif')
    expect(rutas[20]).toBe('/scene/mobile/tramo-1/000.avif')
    expect(rutas.at(-1)).toBe('/scene/mobile/tramo-3/019.avif')
  })
})

describe('frameEnScroll', () => {
  test('los extremos caen en el primer y el último frame', () => {
    expect(frameEnScroll(0, 4000, 80)).toBe(0)
    expect(frameEnScroll(4000, 4000, 80)).toBe(79)
  })

  test('la mitad del recorrido cae a la mitad de los frames', () => {
    expect(frameEnScroll(2000, 4000, 80)).toBe(40)
  })

  test('no se sale del rango por mucho scroll ni por rebote negativo', () => {
    expect(frameEnScroll(99999, 4000, 80)).toBe(79)
    expect(frameEnScroll(-500, 4000, 80)).toBe(0)
  })

  test('sin recorrido no divide por cero', () => {
    expect(frameEnScroll(0, 0, 80)).toBe(0)
  })
})

describe('formatoParaPantalla', () => {
  test('vertical pide mobile y horizontal pide desktop', () => {
    expect(formatoParaPantalla(escena, 390, 844)).toBe('mobile')
    expect(formatoParaPantalla(escena, 1440, 900)).toBe('desktop')
  })
})

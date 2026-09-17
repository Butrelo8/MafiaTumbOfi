import { describe, expect, test } from 'bun:test'
import {
  frameEnAnclas,
  framesDeEstacion,
  formatoParaPantalla,
  frameEnScroll,
  rutasDeFrames,
} from './scrollScene'
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

describe('framesDeEstacion', () => {
  test('cada estación es el primer frame de su tramo, y la última el final', () => {
    expect(framesDeEstacion(formato)).toEqual([0, 20, 40, 60, 79])
  })
})

describe('frameEnAnclas', () => {
  const anclas = [
    { scroll: 0, frame: 0 },
    { scroll: 1000, frame: 20 },
    { scroll: 2000, frame: 40 },
  ]

  test('en el ancla cae el frame exacto de la estación', () => {
    expect(frameEnAnclas(0, anclas)).toBe(0)
    expect(frameEnAnclas(1000, anclas)).toBe(20)
    expect(frameEnAnclas(2000, anclas)).toBe(40)
  })

  test('entre dos anclas interpola', () => {
    expect(frameEnAnclas(500, anclas)).toBe(10)
    expect(frameEnAnclas(1500, anclas)).toBe(30)
  })

  test('fuera del rango se queda en el extremo, no extrapola', () => {
    expect(frameEnAnclas(-800, anclas)).toBe(0)
    expect(frameEnAnclas(99999, anclas)).toBe(40)
  })

  test('dos anclas en el mismo scroll no dividen por cero: gana la primera', () => {
    expect(frameEnAnclas(1000, [{ scroll: 1000, frame: 5 }, { scroll: 1000, frame: 9 }])).toBe(5)
  })

  test('sin anclas devuelve el primer frame', () => {
    expect(frameEnAnclas(300, [])).toBe(0)
  })
})

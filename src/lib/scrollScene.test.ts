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
    // Derivado de scene.json, no escrito a mano: el número de tramos y de
    // frames por tramo cambia cada vez que se re-renderiza la escena, y un
    // test con números fijos sólo avisa de eso, que no es un error.
    const rutas = rutasDeFrames(formato)
    const porTramo = formato.tramos[0].frames
    const ultimo = formato.tramos.length - 1
    expect(rutas.length).toBe(formato.tramos.reduce((suma, t) => suma + t.frames, 0))
    expect(rutas[0]).toBe('/scene/mobile/tramo-0/000.webp')
    expect(rutas[porTramo]).toBe('/scene/mobile/tramo-1/000.webp')
    expect(rutas.at(-1)).toBe(
      `/scene/mobile/tramo-${ultimo}/${String(formato.tramos[ultimo].frames - 1).padStart(3, '0')}.webp`)
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
    const frames = framesDeEstacion(formato)
    const total = formato.tramos.reduce((suma, t) => suma + t.frames, 0)
    expect(frames.length).toBe(formato.tramos.length + 1)
    expect(frames[0]).toBe(0)
    expect(frames.at(-1)).toBe(total - 1)
    let acumulado = 0
    formato.tramos.forEach((tramo, indice) => {
      expect(frames[indice]).toBe(acumulado)
      acumulado += tramo.frames
    })
  })

  test('hay una estación por cada nombre de scene.json', () => {
    expect(framesDeEstacion(formato).length).toBe(formato.estaciones.length)
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

import { describe, expect, test } from 'bun:test'
import {
  acercar,
  anclasDelDocumento,
  frameEnAnclas,
  posicionEnAnclas,
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

describe('posicionEnAnclas', () => {
  const anclas = [
    { scroll: 0, frame: 0 },
    { scroll: 1000, frame: 20 },
  ]

  test('entre dos anclas da el frame con decimales, sin redondear', () => {
    expect(posicionEnAnclas(510, anclas)).toBeCloseTo(10.2)
  })

  test('frameEnAnclas es su versión redondeada', () => {
    expect(frameEnAnclas(510, anclas)).toBe(10)
    expect(frameEnAnclas(530, anclas)).toBe(11)
  })
})

describe('acercar', () => {
  test('sin tiempo no se mueve', () => {
    expect(acercar(10, 20, 0)).toBe(10)
  })

  test('avanza hacia el objetivo sin pasarse', () => {
    const paso = acercar(10, 20, 16)
    expect(paso).toBeGreaterThan(10)
    expect(paso).toBeLessThan(20)
  })

  test('llega en un tiempo finito, en cualquier dirección', () => {
    let pos = 50
    for (let i = 0; i < 120; i += 1) pos = acercar(pos, 0, 16)
    expect(pos).toBe(0)
  })

  test('no depende de los fps: 4 pasos de 4 ms ≈ 1 de 16 ms', () => {
    let a = 0
    for (let i = 0; i < 4; i += 1) a = acercar(a, 10, 4)
    expect(a).toBeCloseTo(acercar(0, 10, 16), 6)
  })
})

describe('anclasDelDocumento', () => {
  // Ventana de 1000 px. Estación 0 sin panel (hero); estación 1 es el titular
  // de una sección con panel que termina en 5000.
  function ventanaFalsa() {
    const titular = (estacion: number, top: number, fondoSeccion?: number) => ({
      dataset: { estacion: String(estacion) },
      getBoundingClientRect: () => ({ top, height: 1000 }),
      parentElement: fondoSeccion === undefined
        ? { classList: { contains: () => false } }
        : { classList: { contains: (c: string) => c === 'estacion' }, getBoundingClientRect: () => ({ bottom: fondoSeccion }) },
    })
    const elementos = [titular(0, 0), titular(1, 2000, 5000), titular(2, 7000)]
    return {
      innerHeight: 1000,
      scrollY: 0,
      document: {
        documentElement: { scrollHeight: 20000 },
        querySelectorAll: () => elementos,
      },
    } as unknown as Window
  }

  test('una estación con panel se queda quieta hasta que el panel acaba', () => {
    const anclas = anclasDelDocumento(formato, ventanaFalsa())
    const f = framesDeEstacion(formato)
    // llegada al centrar el titular, salida cuando el pie del panel toca el pie de la ventana
    expect(anclas).toEqual([
      { scroll: 0, frame: f[0] },
      { scroll: 2000, frame: f[1] },
      { scroll: 4000, frame: f[1] },
      { scroll: 7000, frame: f[2] },
    ])
  })

  test('mientras sube el panel la cámara no se mueve', () => {
    const anclas = anclasDelDocumento(formato, ventanaFalsa())
    expect(posicionEnAnclas(3000, anclas)).toBe(framesDeEstacion(formato)[1])
  })
})

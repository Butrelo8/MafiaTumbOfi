import { describe, expect, test } from 'bun:test'
import { etiqueta, icono, inicial, siguiente } from './estadoBoton'

describe('interruptor del loop', () => {
  test('arranca reproduciendo, o en pausa bajo movimiento reducido', () => {
    expect(etiqueta(inicial(false))).toBe('Pausar video')
    expect(etiqueta(inicial(true))).toBe('Reproducir video')
  })

  test('un toque alterna pausa y reproducción, y el icono sigue a la etiqueta', () => {
    const pausa = siguiente(inicial(false), 'toque')
    expect(etiqueta(pausa)).toBe('Reproducir video')
    expect(icono(pausa)).toBe('play')
    expect(icono(siguiente(pausa, 'toque'))).toBe('pausa')
  })

  test('esperando muestra "Cargando video" con el anillo; reproduciendo lo quita', () => {
    const espera = siguiente(inicial(false), 'esperando')
    expect(etiqueta(espera)).toBe('Cargando video')
    expect(icono(espera)).toBe('anillo')
    expect(etiqueta(siguiente(espera, 'reproduciendo'))).toBe('Pausar video')
  })

  test('en pausa, esperando no cambia nada (el video no se está pidiendo)', () => {
    const p = siguiente(inicial(false), 'toque')
    expect(siguiente(p, 'esperando')).toEqual(p)
  })

  test('listo solo si el usuario inició la reproducción', () => {
    expect(siguiente(inicial(false), 'reproduciendo').hecho).toBe(false)
    const reanuda = siguiente(siguiente(inicial(false), 'toque'), 'toque')
    expect(siguiente(reanuda, 'reproduciendo').hecho).toBe(true)
  })

  test('play() rechazado (modo de bajo consumo de iOS) deja el interruptor en "Reproducir video"', () => {
    const e = siguiente(siguiente(inicial(false), 'esperando'), 'rechazado')
    expect(e.pausado).toBe(true)
    expect(etiqueta(e)).toBe('Reproducir video')
    expect(e.cargando).toBe(false)
  })

  test('error del video oculta el interruptor y no se queda en "Cargando video"', () => {
    const e = siguiente(siguiente(inicial(false), 'esperando'), 'error')
    expect(e.oculto).toBe(true)
    expect(e.cargando).toBe(false)
  })

  test('si el video se detiene mientras esperaba (sale de pantalla), no queda en "Cargando video"', () => {
    const e = siguiente(siguiente(inicial(false), 'esperando'), 'detenido')
    expect(e.cargando).toBe(false)
    expect(e.pausado).toBe(false)
  })
})

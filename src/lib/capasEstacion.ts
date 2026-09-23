/**
 * Profundidad y pop-in en las estaciones.
 *
 * Una sola señal manda sobre las dos cosas: la distancia en frames entre el
 * frame que se está pintando y el frame de la estación. De ahí salen la
 * opacidad de la capa que va DELANTE del texto y el `data-cerca` que dispara
 * la entrada del titular.
 *
 * La capa de frente es una imagen fija y el fondo se está moviendo: fuera de
 * la estación las dos cosas no encajan. La ventana de fundido existe para que
 * nadie vea ese desencaje, y por eso es estrecha.
 */

import type { FormatoEscena } from './scrollScene'

/** Loop de bruma: un <video> con `data-bruma` en lugar de una imagen. */
function esBruma(capa: HTMLElement): capa is HTMLVideoElement {
  return 'bruma' in capa.dataset
}

/** Frames de fundido a cada lado de la estación. Medido en el navegador. */
export const VENTANA = 4

/**
 * 1 en la estación, 0 a `ventana` frames o más de ella.
 *
 * Fuera de rango no extrapola: se queda en 0. Con `ventana` 0 o negativa
 * devuelve 1 sólo en el frame exacto, que es el degenerado razonable.
 */
export function cercania(frame: number, frameEstacion: number, ventana = VENTANA): number {
  const distancia = Math.abs(frame - frameEstacion)
  if (ventana <= 0) return distancia === 0 ? 1 : 0
  return Math.max(0, 1 - distancia / ventana)
}

export type Estacion = {
  nombre: string
  imagen: string
  bytes: number
  capaFrente?: { imagen: string; bytes: number }
  bruma?: { imagen: string; bytes: number }
  relampago?: { imagen: string; bytes: number }
}

type Opciones = {
  formato: FormatoEscena
  /** Frame de cada estación dentro de la secuencia, de `framesDeEstacion`. */
  framesDeEstacion: number[]
  documento: Document
  ventana?: number
  /** Sin movimiento: la capa va opaca y fija, y el titular aparece sin animar. */
  sinMovimiento?: boolean
}

/**
 * Engancha las capas y los titulares a los frames.
 *
 * Devuelve la función que hay que llamar en cada cambio de frame. No escucha
 * el scroll: de eso ya se ocupa `scrollScene`, y tener dos lectores del mismo
 * evento es la forma segura de que se desincronicen.
 */
export function montarCapas({
  formato,
  framesDeEstacion,
  documento,
  ventana = VENTANA,
  sinMovimiento = false,
}: Opciones): (frame: number) => void {
  const capas = new Map<number, HTMLElement>()
  for (const elemento of documento.querySelectorAll<HTMLElement>('[data-capa-frente]')) {
    const indice = Number(elemento.dataset.capaFrente)
    if (Number.isInteger(indice)) capas.set(indice, elemento)
  }

  const secciones = new Map<number, HTMLElement>()
  for (const elemento of documento.querySelectorAll<HTMLElement>('[data-estacion]')) {
    const indice = Number(elemento.dataset.estacion)
    if (Number.isInteger(indice)) secciones.set(indice, elemento)
  }

  if (sinMovimiento) {
    // Sin scrub no hay fundido que valga: cada estación es un still. La capa se
    // deja puesta y el titular visible, que es lo que pide la spec. La bruma
    // es movimiento y nada más: no se muestra.
    for (const capa of capas.values()) capa.style.opacity = esBruma(capa) ? '0' : '1'
    for (const seccion of secciones.values()) seccion.dataset.cerca = '1'
    return () => {}
  }

  return (frame: number) => {
    for (const [indice, capa] of capas) {
      const frameEstacion = framesDeEstacion[indice]
      if (frameEstacion === undefined) continue
      if (esBruma(capa)) {
        // La bruma es aire pegado a la cámara, no una imagen fija sobre un
        // fondo que se mueve: no tiene desencaje que esconder y entra con la
        // ventana ancha del titular. Sólo se reproduce mientras se ve.
        const nivel = cercania(frame, frameEstacion, ventana * 4)
        capa.style.opacity = String(nivel)
        if (nivel > 0 && capa.paused) void capa.play().catch(() => {})
        else if (nivel === 0 && !capa.paused) capa.pause()
        continue
      }
      capa.style.opacity = String(cercania(frame, frameEstacion, ventana))
    }
    for (const [indice, seccion] of secciones) {
      const frameEstacion = framesDeEstacion[indice]
      if (frameEstacion === undefined) continue
      // El titular entra con una ventana más ancha que la capa: la capa se funde
      // para esconder un desencaje y el texto no tiene nada que esconder, así
      // que aparece antes y se queda mientras la sección se lee.
      const cerca = cercania(frame, frameEstacion, ventana * 4) > 0 ? '1' : '0'
      if (seccion.dataset.cerca !== cerca) seccion.dataset.cerca = cerca
    }
  }
}

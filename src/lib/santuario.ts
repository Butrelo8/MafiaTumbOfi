// Lógica sin DOM del santuario (ticket 09): qué fuente se baja, en qué orden y cómo se cruza de un
// espacio a otro. `montarSantuario.ts` la conecta con la página.
import type { Espacio, Formato, Fuente } from '../data/santuario'

/** `canPlayType` del navegador: '' no, 'maybe' o 'probably' sí. */
export type PuedeReproducir = (tipo: string) => string

export type Pieza = 'loop' | 'ida' | 'vuelta'
/** `"1:ida"`: la ida que sale del espacio 1. */
export type Clave = `${number}:${Pieza}`

export type Viaje =
  | { tipo: 'corte' }
  | { tipo: 'fundido' }
  | { tipo: 'transicion'; clave: Clave }

export function elegirFuente(fuentes: Fuente[] | undefined, puede: PuedeReproducir): Fuente | null {
  return fuentes?.find((fuente) => puede(fuente.type) !== '') ?? null
}

export function fuenteDe(
  espacios: Espacio[],
  formato: Formato,
  clave: Clave,
  puede: PuedeReproducir,
): Fuente | null {
  const [indice, pieza] = clave.split(':') as [string, Pieza]
  return elegirFuente(espacios[Number(indice)]?.fondo[formato][pieza], puede)
}

/**
 * Un gesto = una sección (ticket 11). Entre vecinos con transición se reproduce entera; los saltos,
 * los vecinos sin transición y cualquier transición sin códec que sirva cruzan por negro (ticket 05).
 * Con movimiento reducido, corte directo.
 */
export function planDeViaje(
  espacios: Espacio[],
  formato: Formato,
  desde: number,
  hasta: number,
  quieto: boolean,
  puede: PuedeReproducir,
): Viaje {
  if (quieto) return { tipo: 'corte' }
  const clave: Clave | null =
    hasta === desde + 1 ? `${desde}:ida` : hasta === desde - 1 ? `${hasta}:vuelta` : null
  if (clave && fuenteDe(espacios, formato, clave, puede)) return { tipo: 'transicion', clave }
  return { tipo: 'fundido' }
}

/** Lo que tiene que estar bajado para hacer el viaje sin esperar a la red. */
export function clavesDelViaje(
  espacios: Espacio[],
  formato: Formato,
  viaje: Viaje,
  hasta: number,
  puede: PuedeReproducir,
): Clave[] {
  const claves: Clave[] = viaje.tipo === 'transicion' ? [viaje.clave, `${hasta}:loop`] : [`${hasta}:loop`]
  return claves.filter((clave) => fuenteDe(espacios, formato, clave, puede))
}

/**
 * Orden de precarga (ticket 05): lo inmediato es el loop de donde se entra, la ida y el loop del
 * siguiente y la vuelta al anterior; al tenerlo, la cascada baja todo el resto del sitio en orden.
 */
export function colaDePrecarga(
  espacios: Espacio[],
  formato: Formato,
  actual: number,
  puede: PuedeReproducir,
): { inmediato: Clave[]; cascada: Clave[] } {
  const existe = (clave: Clave) => fuenteDe(espacios, formato, clave, puede) !== null
  const inmediato = ([
    `${actual}:loop`,
    `${actual}:ida`,
    `${actual + 1}:loop`,
    `${actual - 1}:vuelta`,
  ] as Clave[]).filter(existe)
  const cascada = espacios
    .flatMap((_, indice) => [`${indice}:loop`, `${indice}:ida`, `${indice}:vuelta`] as Clave[])
    .filter((clave) => existe(clave) && !inmediato.includes(clave))
  return { inmediato, cascada }
}

/** Swipe: el eje que domina, o nada si no pasa del umbral. El vertical es sección; el lateral, pieza. */
export function ejeDelGesto(dx: number, dy: number, umbral = 40): 'x' | 'y' | null {
  if (Math.max(Math.abs(dx), Math.abs(dy)) < umbral) return null
  return Math.abs(dx) > Math.abs(dy) ? 'x' : 'y'
}

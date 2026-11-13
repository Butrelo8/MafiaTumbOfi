// Estado del interruptor del loop (único botón con carga real). Pura: el DOM y GSAP viven en src/scripts/loop.ts.
export type Estado = { pausado: boolean; cargando: boolean; hecho: boolean; oculto: boolean; deToque: boolean }
export type Evento = 'toque' | 'esperando' | 'reproduciendo' | 'rechazado' | 'error' | 'detenido'

export const inicial = (movimientoReducido: boolean): Estado => ({
  pausado: movimientoReducido,
  cargando: false,
  hecho: false,
  oculto: false,
  deToque: false,
})

export function siguiente(e: Estado, ev: Evento): Estado {
  switch (ev) {
    case 'toque':
      return { ...e, pausado: !e.pausado, cargando: false, hecho: false, deToque: e.pausado }
    case 'esperando':
      return e.pausado ? e : { ...e, cargando: true, hecho: false }
    case 'reproduciendo':
      return { ...e, cargando: false, hecho: e.deToque, deToque: false }
    case 'rechazado':
      return { ...e, pausado: true, cargando: false, hecho: false, deToque: false }
    case 'detenido':
      return { ...e, cargando: false, hecho: false }
    case 'error':
      return { ...e, cargando: false, hecho: false, oculto: true }
  }
}

export const etiqueta = (e: Estado) => (e.cargando ? 'Cargando video' : e.pausado ? 'Reproducir video' : 'Pausar video')
export const icono = (e: Estado): 'play' | 'pausa' | 'anillo' => (e.cargando ? 'anillo' : e.pausado ? 'play' : 'pausa')

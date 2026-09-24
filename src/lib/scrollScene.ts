/**
 * Scroll -> frame del santuario.
 *
 * Los frames los renderiza Blender y los describe `src/data/scene.json`; aquí
 * sólo se traduce la posición del scroll a un índice y se dibuja en el canvas.
 * Ni una ruta ni un número de frames está escrito en este archivo: cambiar la
 * animación es re-renderizar y regenerar el JSON.
 */

export type Tramo = {
  desde: string
  hasta: string
  frames: number
  patron: string
  bytes: number
}

export type FormatoEscena = {
  ancho: number
  alto: number
  estaciones: { nombre: string; imagen: string; bytes: number }[]
  tramos: Tramo[]
  bytes: number
}

export type Escena = { formatos: Record<string, FormatoEscena> }

/** Rutas de todos los frames, en orden de scroll. */
export function rutasDeFrames(formato: FormatoEscena): string[] {
  const rutas: string[] = []
  for (const tramo of formato.tramos) {
    for (let i = 0; i < tramo.frames; i += 1) {
      rutas.push(tramo.patron.replace('%03d', String(i).padStart(3, '0')))
    }
  }
  return rutas
}

/**
 * Índice de frame para un scroll dado.
 *
 * `recorrido` es cuánto se puede scrollear (scrollHeight - innerHeight). Si es
 * 0 —contenido más corto que la ventana— se queda en el primer frame en vez de
 * dividir por cero.
 */
export function frameEnScroll(scrollY: number, recorrido: number, total: number): number {
  if (total <= 0) return 0
  if (recorrido <= 0) return 0
  const avance = Math.min(Math.max(scrollY / recorrido, 0), 1)
  return Math.round(avance * (total - 1))
}

/** Formato que le toca a esta pantalla: uno solo, nunca los dos. */
export function formatoParaPantalla(escena: Escena, ancho: number, alto: number): string {
  const vertical = alto >= ancho
  if (vertical && escena.formatos.mobile) return 'mobile'
  if (!vertical && escena.formatos.desktop) return 'desktop'
  return Object.keys(escena.formatos)[0] ?? ''
}

/** Un ancla: en este scroll, este frame. Ordenadas por scroll. */
export type Ancla = { scroll: number; frame: number }

/**
 * Frame de cada estación dentro de la secuencia completa.
 *
 * La estación N es el primer frame del tramo N, y la última es el último
 * frame del último tramo: al llegar abajo la cámara ha terminado el recorrido.
 */
export function framesDeEstacion(formato: FormatoEscena): number[] {
  const frames: number[] = []
  let acumulado = 0
  for (const tramo of formato.tramos) {
    frames.push(acumulado)
    acumulado += tramo.frames
  }
  frames.push(Math.max(acumulado - 1, 0))
  return frames
}

/**
 * Posición en la secuencia entre anclas, con decimales: 30.4 es el frame 30
 * con el 31 fundido al 40 %.
 *
 * Entre dos anclas el avance es lineal, así que el tramo se reproduce mientras
 * se scrollea de una sección a la siguiente y la cámara llega a la estación
 * justo cuando la sección queda centrada. Fuera del rango se queda en el ancla
 * del extremo en vez de extrapolar.
 */
export function posicionEnAnclas(scrollY: number, anclas: Ancla[]): number {
  if (anclas.length === 0) return 0
  if (scrollY <= anclas[0].scroll) return anclas[0].frame
  const ultima = anclas[anclas.length - 1]
  if (scrollY >= ultima.scroll) return ultima.frame

  for (let i = 1; i < anclas.length; i += 1) {
    const previa = anclas[i - 1]
    const actual = anclas[i]
    if (scrollY > actual.scroll) continue
    const tramo = actual.scroll - previa.scroll
    if (tramo <= 0) return actual.frame
    const avance = (scrollY - previa.scroll) / tramo
    return previa.frame + avance * (actual.frame - previa.frame)
  }
  return ultima.frame
}

/** El frame entero más cercano: el que manda sobre las capas y `data-frame`. */
export function frameEnAnclas(scrollY: number, anclas: Ancla[]): number {
  return Math.round(posicionEnAnclas(scrollY, anclas))
}

/** Constante de tiempo del suavizado, en ms. Más alta = más inercia. */
export const INERCIA_MS = 90

/**
 * Un paso del suavizado: acerca `actual` a `objetivo` lo que toque en `dt` ms.
 *
 * Amortiguador exponencial: la fracción que se recorre depende del tiempo
 * transcurrido, no del número de pasos, así que da lo mismo a 60 Hz que a 144.
 * Por debajo de una centésima de frame se engancha, para que el bucle termine.
 */
export function acercar(actual: number, objetivo: number, dt: number, inercia = INERCIA_MS): number {
  const siguiente = actual + (objetivo - actual) * (1 - Math.exp(-dt / inercia))
  return Math.abs(objetivo - siguiente) < 0.01 ? objetivo : siguiente
}

/**
 * Anclas leídas del documento: cada `[data-estacion]` centrada en la ventana.
 *
 * Si faltan secciones o vienen desordenadas se usan las que haya; si no hay
 * ninguna, quien llama se queda con el reparto plano de siempre.
 *
 * ## Para navegar por clicks
 *
 * Las seis estaciones están marcadas con `[data-estacion]` y con un `id`
 * estable: `#inicio`, `#quienes`, `#musica`, `#grupo`, `#contratacion`,
 * `#cierre`. Un botón
 * que quiera saltar a una estación tiene que **centrar** el elemento:
 *
 *     document.querySelector('[data-estacion="3"]')
 *       .scrollIntoView({ block: 'center' })
 *
 * Y no puede usar un enlace `#hash`: el hash deja el borde superior de la
 * sección arriba, no su centro, y la estación vive en el centro. Medido el
 * 2026-09-17 a 390x844: `#musica` cae en el frame 5 y `#grupo` en el 38,
 * cuando sus estaciones son la 20 y la 40. Sólo coinciden cuando la sección
 * mide exactamente una ventana, como pasa hoy con contratación.
 *
 * El menú de cabecera son enlaces `#hash` a propósito: lleva al principio de
 * la sección, que es donde está el titular. Centrar `#musica` dejaría el
 * titular 2500 px por encima del viewport. Son dos navegaciones distintas y no
 * hay que fundirlas: la de contenido va al titular, la de estaciones al frame.
 */
export function anclasDelDocumento(
  formato: FormatoEscena,
  ventana: Window,
): Ancla[] {
  const frames = framesDeEstacion(formato)
  const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
  const anclas: Ancla[] = []
  for (const elemento of ventana.document.querySelectorAll<HTMLElement>('[data-estacion]')) {
    const indice = Number(elemento.dataset.estacion)
    if (!Number.isInteger(indice) || indice < 0 || indice >= frames.length) continue
    const caja = elemento.getBoundingClientRect()
    const centro = caja.top + ventana.scrollY + caja.height / 2
    const limite = (y: number) => Math.min(Math.max(y, 0), Math.max(recorrido, 0))
    const scroll = limite(centro - ventana.innerHeight / 2)
    anclas.push({ scroll, frame: frames[indice] })

    // Salida: si el titular encabeza una sección con panel, la cámara se queda
    // en la estación hasta que el pie del panel toca el pie de la ventana. El
    // panel es opaco y tapa la escena mientras sube, así que la espera no se
    // ve; y el viaje queda en lo que mide el hueco entre secciones más una
    // ventana, igual en todos los tramos sea cual sea el largo del panel.
    const seccion = elemento.parentElement
    if (seccion?.classList.contains('estacion')) {
      const fondo = seccion.getBoundingClientRect().bottom + ventana.scrollY
      const salida = limite(fondo - ventana.innerHeight)
      if (salida > scroll) anclas.push({ scroll: salida, frame: frames[indice] })
    }
  }
  anclas.sort((a, b) => a.scroll - b.scroll)
  return anclas
}

type Opciones = {
  canvas: HTMLCanvasElement
  escena: Escena
  ventana?: Window
  /** Se llama con el índice recién pintado. Lo usa `capasEstacion`. */
  alCambiarFrame?: (indice: number) => void
}

export function mountScrollScene(
  { canvas, escena, ventana = window, alCambiarFrame }: Opciones,
): () => void {
  const sinMovimiento = ventana.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  const clave = formatoParaPantalla(escena, ventana.innerWidth, ventana.innerHeight)
  const formato = escena.formatos[clave]
  if (!formato) return () => {}

  const contexto = canvas.getContext('2d')
  if (!contexto) return () => {}

  canvas.width = formato.ancho
  canvas.height = formato.alto

  // Con reduced-motion no hay scrub: sólo el frame quieto de cada estación,
  // que es lo que pide la spec de accesibilidad.
  const rutas = sinMovimiento
    ? formato.estaciones.map((estacion) => estacion.imagen)
    : rutasDeFrames(formato)

  const cache = new Map<number, HTMLImageElement>()
  let pintado = -1
  let actual = -1
  let ultimoTiempo = 0
  let corriendo = false

  const cargar = (indice: number): Promise<HTMLImageElement> | undefined => {
    if (indice < 0 || indice >= rutas.length) return undefined
    const ya = cache.get(indice)
    if (ya) return Promise.resolve(ya)
    const imagen = new Image()
    imagen.src = rutas[indice]
    imagen.decoding = 'async'
    cache.set(indice, imagen)
    return imagen.decode().then(() => imagen)
  }

  // Pinta una posición con decimales: el frame de abajo entero y el de arriba
  // encima con la fracción como opacidad. Entre dos frames de 30 por tramo la
  // cámara no salta: se funde.
  const pintar = (posicion: number) => {
    if (posicion === pintado) return
    const base = Math.floor(posicion)
    const mezcla = posicion - base
    const abajo = cache.get(base)
    if (!abajo?.complete) {
      void cargar(base)?.then(arrancar)
      return
    }
    contexto.globalAlpha = 1
    contexto.drawImage(abajo, 0, 0, canvas.width, canvas.height)
    if (mezcla > 0.01) {
      const arriba = cache.get(base + 1)
      if (arriba?.complete) {
        contexto.globalAlpha = mezcla
        contexto.drawImage(arriba, 0, 0, canvas.width, canvas.height)
        contexto.globalAlpha = 1
      } else {
        // Se repinta con el fundido en cuanto llegue.
        void cargar(base + 1)?.then(() => { pintado = -1; arrancar() })
      }
    }
    pintado = posicion
    const indice = Math.round(posicion)
    if (canvas.dataset.frame !== String(indice)) {
      canvas.dataset.frame = String(indice)
      alCambiarFrame?.(indice)
    }
  }

  // Las anclas dependen del alto de las secciones, que cambia con la ventana y
  // con las fuentes: se releen en cada cuadro, que es una lectura de layout ya
  // dentro del rAF (medido: 0.01 ms).
  const posicionDeScroll = () => {
    if (sinMovimiento) {
      const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
      return frameEnScroll(ventana.scrollY, recorrido, rutas.length)
    }
    const anclas = anclasDelDocumento(formato, ventana)
    if (anclas.length < 2) {
      const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
      return frameEnScroll(ventana.scrollY, recorrido, rutas.length)
    }
    return posicionEnAnclas(ventana.scrollY, anclas)
  }

  // Un bucle de rAF que persigue al scroll y se apaga al alcanzarlo. La rueda
  // del ratón llega a tirones de 100 px; el suavizado los reparte en cuadros.
  // Sin movimiento no hay inercia ni fundido: salta a la estación.
  const cuadro = (tiempo: number) => {
    const objetivo = posicionDeScroll()
    const dt = ultimoTiempo ? Math.min(tiempo - ultimoTiempo, 100) : 16
    ultimoTiempo = tiempo
    actual = actual < 0 || sinMovimiento ? objetivo : acercar(actual, objetivo, dt)
    pintar(actual)
    for (const cercano of [Math.floor(actual) - 1, Math.ceil(actual) + 1]) void cargar(cercano)
    if (actual !== objetivo) {
      ventana.requestAnimationFrame(cuadro)
    } else {
      corriendo = false
      ultimoTiempo = 0
    }
  }

  function arrancar() {
    if (corriendo) return
    corriendo = true
    ventana.requestAnimationFrame(cuadro)
  }

  const alScroll = () => arrancar()

  // Precarga en orden, sin bloquear el primer pintado: son ~780 KB en total.
  void cargar(0)?.then(() => {
    arrancar()
    let siguiente = 1
    const seguir = () => {
      if (siguiente >= rutas.length) return
      void cargar(siguiente)?.then(seguir)
      siguiente += 1
    }
    seguir()
  })

  ventana.addEventListener('scroll', alScroll, { passive: true })
  alScroll()

  // Girar el teléfono cambia de formato: el juego de frames es otro, así que
  // hay que volver a montar en vez de estirar el que ya está dibujado.
  let remontar: (() => void) | undefined
  const alRedimensionar = () => {
    if (formatoParaPantalla(escena, ventana.innerWidth, ventana.innerHeight) === clave) return
    ventana.removeEventListener('scroll', alScroll)
    ventana.removeEventListener('resize', alRedimensionar)
    remontar = mountScrollScene({ canvas, escena, ventana, alCambiarFrame })
  }
  ventana.addEventListener('resize', alRedimensionar, { passive: true })

  return () => {
    ventana.removeEventListener('scroll', alScroll)
    ventana.removeEventListener('resize', alRedimensionar)
    remontar?.()
  }
}

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
 * Interpola el frame entre anclas.
 *
 * Entre dos anclas el avance es lineal, así que el tramo se reproduce mientras
 * se scrollea de una sección a la siguiente y la cámara llega a la estación
 * justo cuando la sección queda centrada. Fuera del rango se queda en el ancla
 * del extremo en vez de extrapolar.
 */
export function frameEnAnclas(scrollY: number, anclas: Ancla[]): number {
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
    return Math.round(previa.frame + avance * (actual.frame - previa.frame))
  }
  return ultima.frame
}

/**
 * Anclas leídas del documento: cada `[data-estacion]` centrada en la ventana.
 *
 * Si faltan secciones o vienen desordenadas se usan las que haya; si no hay
 * ninguna, quien llama se queda con el reparto plano de siempre.
 *
 * ## Para navegar por clicks
 *
 * Las cinco estaciones están marcadas con `[data-estacion]` y con un `id`
 * estable: `#inicio`, `#musica`, `#grupo`, `#contratacion`, `#cierre`. Un botón
 * que quiera saltar a una estación tiene que **centrar** el elemento:
 *
 *     document.querySelector('[data-estacion="2"]')
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
    const scroll = Math.min(Math.max(centro - ventana.innerHeight / 2, 0), Math.max(recorrido, 0))
    anclas.push({ scroll, frame: frames[indice] })
  }
  anclas.sort((a, b) => a.scroll - b.scroll)
  return anclas
}

type Opciones = {
  canvas: HTMLCanvasElement
  escena: Escena
  ventana?: Window
}

export function mountScrollScene({ canvas, escena, ventana = window }: Opciones): () => void {
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
  let dibujado = -1
  let pedido = -1
  let animando = false

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

  const pintar = (indice: number) => {
    const imagen = cache.get(indice)
    if (!imagen?.complete || dibujado === indice) return
    contexto.drawImage(imagen, 0, 0, canvas.width, canvas.height)
    dibujado = indice
    canvas.dataset.frame = String(indice)
  }

  // Las anclas dependen del alto de las secciones, que cambia con la ventana y
  // con las fuentes: se releen en cada scroll, que es una lectura de layout ya
  // dentro del rAF.
  const indiceDeScroll = () => {
    if (sinMovimiento) {
      const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
      return frameEnScroll(ventana.scrollY, recorrido, rutas.length)
    }
    const anclas = anclasDelDocumento(formato, ventana)
    if (anclas.length < 2) {
      const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
      return frameEnScroll(ventana.scrollY, recorrido, rutas.length)
    }
    return frameEnAnclas(ventana.scrollY, anclas)
  }

  const alScroll = () => {
    if (animando) return
    animando = true
    ventana.requestAnimationFrame(() => {
      animando = false
      const indice = indiceDeScroll()
      if (indice === pedido) return
      pedido = indice
      const carga = cargar(indice)
      if (carga) void carga.then(() => { if (pedido === indice) pintar(indice) })
      // el siguiente, para que el scrub no espere al decode
      void cargar(indice + 1)
    })
  }

  // Precarga en orden, sin bloquear el primer pintado: son ~780 KB en total.
  void cargar(0)?.then(() => {
    pintar(0)
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
    remontar = mountScrollScene({ canvas, escena, ventana })
  }
  ventana.addEventListener('resize', alRedimensionar, { passive: true })

  return () => {
    ventana.removeEventListener('scroll', alScroll)
    ventana.removeEventListener('resize', alRedimensionar)
    remontar?.()
  }
}

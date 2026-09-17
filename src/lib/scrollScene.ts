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

  const alScroll = () => {
    if (animando) return
    animando = true
    ventana.requestAnimationFrame(() => {
      animando = false
      const recorrido = ventana.document.documentElement.scrollHeight - ventana.innerHeight
      const indice = frameEnScroll(ventana.scrollY, recorrido, rutas.length)
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

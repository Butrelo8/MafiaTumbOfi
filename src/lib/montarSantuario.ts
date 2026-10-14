// El santuario en la página: un gesto = una sección (ticket 11), loop → ida/vuelta → loop con la mezcla
// de 0.15 s y la costura de 20 cuadros, cola de precarga por `fetch` → `blob:` (ticket 05), espera con
// aviso si el gesto llega antes que el archivo, fundido a negro para lo demás y corte directo con
// movimiento reducido. Portado de los prototipos `tmp/transicion-4/web/` y `tmp/movil-06/web/`.
import { espacios as todos, type Formato } from '../data/santuario'
import { type Clave, clavesDelViaje, colaDePrecarga, ejeDelGesto, fuenteDe, paraPantalla, planDeViaje } from './santuario'

const MEZCLA = 160 // ms: la transición entra sobre el loop durante el arranque lento del travelling
const COSTURA = 20 / 24 // la ida y la vuelta ya traen los cuadros 0-19 crudos del loop
const FUNDIDO = 300 // ms por mitad: 0.6 s de ida y vuelta al negro (ticket 05)
const INERCIA = 400 // ms después de llegar: absorbe la cola de un trackpad
const PAUSA_RUEDA = 200 // ms sin eventos de rueda para contar un gesto nuevo

const espera = (ms: number) => new Promise((ok) => setTimeout(ok, ms))
const terminado = (video: HTMLVideoElement) =>
  new Promise((ok) => video.addEventListener('ended', ok, { once: true }))
const listo = (video: HTMLVideoElement) =>
  video.readyState >= 2 ? Promise.resolve() : new Promise((ok) => video.addEventListener('loadeddata', ok, { once: true }))

/** Un panel abierto que todavía puede scrollear en esa dirección se lleva el gesto (ticket 03). */
function panelQueScrollea(objetivo: EventTarget | null, dy: number): boolean {
  const panel = objetivo instanceof Element ? objetivo.closest<HTMLElement>('[data-panel-scroll]') : null
  if (!panel || panel.scrollHeight <= panel.clientHeight + 1) return false
  return dy > 0 ? panel.scrollTop + panel.clientHeight < panel.scrollHeight - 1 : panel.scrollTop > 0
}

export function montarSantuario() {
  // El peldaño de 2560 sólo con más de 1920 px físicos de ancho; se decide una vez, al montar.
  const espacios = paraPantalla(todos, screen.width * devicePixelRatio > 1920)
  const raiz = document.documentElement
  // Escritorio o vertical, como el hero. Girar el teléfono o cambiar la ventana de proporción cambia el
  // juego de videos: en el acto si no hay viaje, o al terminar el que esté en curso.
  const consultaFormato = matchMedia('(min-aspect-ratio: 1/1)')
  const formatoDe = (consulta: { matches: boolean }): Formato => (consulta.matches ? 'escritorio' : 'vertical')
  let formato = formatoDe(consultaFormato)
  const quieto = matchMedia('(prefers-reduced-motion: reduce)').matches
  const sonda = document.createElement('video')
  const puede = (tipo: string) => sonda.canPlayType(tipo)

  const secciones = espacios.map((espacio) => document.getElementById(espacio.id) as HTMLElement)
  const enlaces = [...document.querySelectorAll<HTMLAnchorElement>('.indicador [data-ir]')]
  const negro = document.querySelector<HTMLElement>('[data-negro]')!
  const capa = (clave: Clave) =>
    document.querySelector<HTMLVideoElement | HTMLImageElement>(`.escena [data-formato="${formato}"][data-clave="${clave}"]`)

  // ── Precarga ───────────────────────────────────────────────────────────────
  // Por formato y clave: los dos juegos de videos conviven si la pantalla cambia de proporción.
  const llave = (clave: Clave) => `${formato}/${clave}`
  const bajadas = new Map<string, Promise<boolean>>()
  const progreso = new Map<string, number>()
  let avisando: { indice: number; claves: Clave[] } | null = null

  function pintarAviso() {
    if (!avisando) return
    const { indice, claves } = avisando
    const hecho = claves.reduce((suma, clave) => suma + (progreso.get(llave(clave)) ?? 0), 0) / claves.length
    enlaces[indice]?.style.setProperty('--carga', hecho.toFixed(3))
  }

  function bajar(clave: Clave): Promise<boolean> {
    const id = llave(clave)
    const previa = bajadas.get(id)
    if (previa) return previa
    const fuente = fuenteDe(espacios, formato, clave, puede)
    const video = capa(clave)
    if (!fuente || !(video instanceof HTMLVideoElement)) return Promise.resolve(false)
    const bajada = (async () => {
      const respuesta = await fetch(fuente.src)
      if (!respuesta.ok || !respuesta.body) throw new Error(`${fuente.src}: ${respuesta.status}`)
      const total = Number(respuesta.headers.get('content-length')) || 0
      const lector = respuesta.body.getReader()
      const partes: BlobPart[] = [] // los trozos de un fetch siempre son ArrayBuffer, nunca compartidos
      let recibido = 0
      for (;;) {
        const { done, value } = await lector.read()
        if (done) break
        partes.push(value as Uint8Array<ArrayBuffer>)
        recibido += value.length
        if (total) progreso.set(id, Math.min(recibido / total, 0.99))
        pintarAviso()
      }
      video.preload = 'auto'
      video.src = URL.createObjectURL(new Blob(partes, { type: 'video/mp4' }))
      await listo(video)
      progreso.set(id, 1)
      pintarAviso()
      return true
    })().catch(() => {
      bajadas.delete(id) // el siguiente gesto lo vuelve a intentar
      return false
    })
    bajadas.set(id, bajada)
    return bajada
  }

  let sentido: 1 | -1 = 1 // el del último viaje: la cascada baja lo que viene en esa dirección

  async function precargar(desde: number) {
    const { inmediato, cascada } = colaDePrecarga(espacios, formato, desde, puede, sentido)
    await Promise.all(inmediato.map(bajar))
    raiz.dataset.precarga = 'cascada'
    for (const clave of cascada) await bajar(clave)
  }

  // ── Escena ─────────────────────────────────────────────────────────────────
  function ponerImagenes() {
    for (const imagen of document.querySelectorAll<HTMLImageElement>(`.escena img[data-formato="${formato}"]`)) {
      if (!imagen.src) imagen.src = imagen.dataset.src ?? ''
    }
  }

  const mostrar = (elemento: Element | null, on: boolean) => elemento?.classList.toggle('on', on)

  // El hero (ticket 08) trae su propio video en la sección, por streaming y sin precarga: corre sólo
  // mientras se ve y nunca con movimiento reducido (se queda el póster). Entra y sale por negro.
  const heroVideo = document.querySelector<HTMLVideoElement>('[data-hero-video]')

  function apagarFondo(indice: number) {
    if (espacios[indice].hero) return heroVideo?.pause()
    const fondo = capa(`${indice}:loop`)
    mostrar(fondo, false)
    if (fondo instanceof HTMLVideoElement) fondo.pause()
  }

  function encenderFondo(indice: number) {
    if (espacios[indice].hero) {
      if (!quieto) heroVideo?.play().catch(() => {})
      return
    }
    const fondo = capa(`${indice}:loop`)
    if (fondo instanceof HTMLVideoElement) {
      if (!fondo.src) return // llega cuando termine de bajar (ver entrar)
      fondo.currentTime = COSTURA
      if (!quieto) fondo.play().catch(() => {})
    }
    mostrar(fondo, true)
  }

  // ── Secciones ──────────────────────────────────────────────────────────────
  let actual = 0
  let ocupado = false
  let pedido: number | null = null

  function activar(indice: number, enfocar: boolean) {
    secciones.forEach((seccion, k) => {
      seccion.classList.toggle('activa', k === indice)
      seccion.inert = k !== indice
    })
    enlaces.forEach((enlace, k) => {
      if (k === indice) enlace.setAttribute('aria-current', 'true')
      else enlace.removeAttribute('aria-current')
    })
    // Entrar por `/` deja la URL limpia; desde ahí, cada sección deja su ancla.
    if (indice !== 0 || location.hash) history.replaceState(null, '', `#${espacios[indice].id}`)
    if (enfocar) secciones[indice].focus({ preventScroll: true })
    document.dispatchEvent(new Event('santuario:llega'))
  }

  /** La E (ticket 03) pasa de pieza con ←/→ y el swipe lateral; ver montarUi.ts. */
  const pasar = (paso: number) => secciones[actual].dispatchEvent(new CustomEvent('santuario:paso', { detail: paso }))

  function avisar(indice: number | null, claves: Clave[] = []) {
    for (const enlace of enlaces) {
      enlace.removeAttribute('data-cargando')
      enlace.style.removeProperty('--carga')
    }
    avisando = indice === null ? null : { indice, claves }
    if (indice !== null) enlaces[indice]?.setAttribute('data-cargando', '')
    pintarAviso()
  }

  /** Los gestos durante un viaje se ignoran; un `#ancla` pedido a medio viaje se cumple al llegar. */
  async function viajar(hasta: number, encolar = false) {
    if (hasta < 0 || hasta >= espacios.length || hasta === actual) return
    if (ocupado) {
      if (encolar) pedido = hasta
      return
    }
    ocupado = true
    const desde = actual
    let viaje = planDeViaje(espacios, formato, desde, hasta, quieto, puede)

    // El gesto espera a que la transición pueda reproducirse entera (ticket 05, decisión 9).
    const claves = clavesDelViaje(espacios, formato, viaje, hasta, puede)
    if (claves.some((clave) => progreso.get(llave(clave)) !== 1)) {
      avisar(hasta, claves)
      const listos = await Promise.all(claves.map(bajar))
      avisar(null)
      if (viaje.tipo === 'transicion' && !listos[0]) viaje = { tipo: 'fundido' }
    }

    const transicion = viaje.tipo === 'transicion' ? (capa(viaje.clave) as HTMLVideoElement) : null
    if (transicion) {
      secciones[desde].classList.remove('activa')
      transicion.currentTime = 0
      const arranca = await transicion.play().then(() => true, () => false)
      if (arranca) {
        mostrar(transicion, true)
        setTimeout(() => apagarFondo(desde), MEZCLA)
        await terminado(transicion)
        encenderFondo(hasta)
        setTimeout(() => mostrar(transicion, false), MEZCLA)
      } else {
        // Sin autoplay (modo de bajo consumo de iOS): corte directo.
        apagarFondo(desde)
        encenderFondo(hasta)
      }
    } else if (viaje.tipo === 'fundido') {
      negro.classList.add('on')
      await espera(FUNDIDO)
      apagarFondo(desde)
      encenderFondo(hasta)
      negro.classList.remove('on')
    } else {
      apagarFondo(desde)
      encenderFondo(hasta)
    }

    actual = hasta
    activar(hasta, true)
    sentido = hasta > desde ? 1 : -1
    precargar(hasta)
    await espera(viaje.tipo === 'corte' ? 0 : INERCIA)
    if (formatoPendiente) cambiarFormato(formatoPendiente)
    ocupado = false
    if (pedido !== null) {
      const siguiente = pedido
      pedido = null
      viajar(siguiente)
    }
  }

  /** Enciende el fondo del espacio; si su loop aún no baja, aparece en cuanto llega. */
  function entrarEn(indice: number) {
    const enFormato = formato
    encenderFondo(indice)
    bajar(`${indice}:loop`).then(() => {
      const fondo = capa(`${indice}:loop`)
      if (actual === indice && formato === enFormato && !ocupado && !fondo?.classList.contains('on')) encenderFondo(indice)
    })
  }

  // ── Formato ────────────────────────────────────────────────────────────────
  let formatoPendiente: Formato | null = null

  function cambiarFormato(nuevo: Formato) {
    formatoPendiente = null
    if (nuevo === formato) return
    apagarFondo(actual)
    formato = nuevo
    ponerImagenes()
    heroVideo?.load() // el hero vuelve a elegir su <source> por `media`
    entrarEn(actual)
    precargar(actual)
  }

  consultaFormato.addEventListener('change', (cambio) => {
    if (ocupado) formatoPendiente = formatoDe(cambio)
    else cambiarFormato(formatoDe(cambio))
  })

  // ── Entrada ────────────────────────────────────────────────────────────────
  const indiceDelHash = () => espacios.findIndex((espacio) => `#${espacio.id}` === location.hash)
  actual = Math.max(0, indiceDelHash())
  secciones.forEach((seccion) => (seccion.tabIndex = -1))
  activar(actual, false)
  ponerImagenes()
  entrarEn(actual)
  precargar(actual)

  // ── Gestos ─────────────────────────────────────────────────────────────────
  const hayModal = () =>
    document.querySelector('.mobile-menu.is-open') !== null ||
    document.querySelector<HTMLDialogElement>('dialog[open]') !== null

  let ultimaRueda = -Infinity
  let ruedaGastada = false
  addEventListener('wheel', (evento) => {
    // Una racha de rueda (o la inercia de un trackpad) es un solo gesto, aunque dure más que el viaje.
    if (evento.timeStamp - ultimaRueda > PAUSA_RUEDA) ruedaGastada = false
    ultimaRueda = evento.timeStamp
    if (ruedaGastada || hayModal() || Math.abs(evento.deltaY) < 20) return
    ruedaGastada = true
    if (panelQueScrollea(evento.target, evento.deltaY)) return
    viajar(actual + Math.sign(evento.deltaY))
  }, { passive: true })

  addEventListener('keydown', (evento) => {
    if (evento.defaultPrevented || evento.altKey || evento.ctrlKey || evento.metaKey || hayModal()) return
    const objetivo = evento.target instanceof Element ? evento.target : null
    if (objetivo?.closest('input, textarea, select, [contenteditable]')) return
    const sobreControl = objetivo?.closest('a, button') !== null
    const adelante = ['ArrowDown', 'PageDown'].includes(evento.key) || (evento.key === ' ' && !evento.shiftKey && !sobreControl)
    const atras = ['ArrowUp', 'PageUp'].includes(evento.key) || (evento.key === ' ' && evento.shiftKey && !sobreControl)
    if (evento.key === 'ArrowLeft' || evento.key === 'ArrowRight') {
      if (!ocupado) pasar(evento.key === 'ArrowLeft' ? -1 : 1)
      return
    }
    const destino = adelante ? actual + 1 : atras ? actual - 1 : evento.key === 'Home' ? 0 : evento.key === 'End' ? espacios.length - 1 : null
    if (destino === null) return
    if ((adelante || atras) && panelQueScrollea(document.activeElement, adelante ? 1 : -1)) return
    evento.preventDefault()
    viajar(destino)
  })

  let toque: { x: number; y: number; scroll: number } | null = null
  addEventListener('touchstart', (evento) => {
    const panel = evento.target instanceof Element ? evento.target.closest<HTMLElement>('[data-panel-scroll]') : null
    toque = { x: evento.touches[0].clientX, y: evento.touches[0].clientY, scroll: panel?.scrollTop ?? 0 }
  }, { passive: true })
  addEventListener('touchend', (evento) => {
    if (!toque || hayModal()) return
    const dx = toque.x - evento.changedTouches[0].clientX
    const dy = toque.y - evento.changedTouches[0].clientY
    const panel = evento.target instanceof Element ? evento.target.closest<HTMLElement>('[data-panel-scroll]') : null
    const scrolleo = panel !== null && panel.scrollTop !== toque.scroll
    toque = null
    const eje = ejeDelGesto(dx, dy)
    if (eje === 'y' && !scrolleo) viajar(actual + Math.sign(dy))
    if (eje === 'x' && !ocupado) pasar(Math.sign(dx))
  })

  addEventListener('hashchange', () => {
    const indice = indiceDelHash()
    if (indice >= 0) viajar(indice, true)
  })
}

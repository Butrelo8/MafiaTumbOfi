// The opening: "MTO" is written while apertura.mp4 buffers, the video plays once, and the overlay fades into the live scene (first
// stop) once the canvas has drawn its first frame. Markup and styles: src/components/Apertura.astro.
// Writing time: at least MIN (the draw and the fill take 2.1 s, plus a short hold so it reads), at most MAX (a slow connection
// gives up the video and lands on the page). Reduced motion, a #anchor link, ?f/?parada/?toma and a return visit in the same tab
// never get here (the inline gate in the component hides the overlay before the first paint).
const MIN = 2400
const MAX = 7000
const ESCENA_MAX = 3000 // how long to wait for the live canvas' first frame before fading anyway
const CLAVE = 'mto-apertura'

const html = document.documentElement
const el = document.getElementById('apertura')
const video = document.getElementById('apertura-video') as HTMLVideoElement | null
const saltar = document.getElementById('apertura-saltar')
const bloqueados = [...document.querySelectorAll<HTMLElement>('nav, h1')]

if (el && video && !html.classList.contains('sin-apertura')) {
  try { sessionStorage.setItem(CLAVE, '1') } catch {}
  for (const b of bloqueados) b.inert = true

  // The source is set here, not in the markup: a skipped opening (reduced motion, return visit, anchor link) downloads nothing.
  if (video.dataset.poster) video.poster = video.dataset.poster
  video.src = video.dataset.src!
  const t0 = performance.now()
  let fin = false
  let reproduciendo = false
  let listo = video.readyState >= 4

  function terminar() {
    if (fin) return
    fin = true
    video!.pause()
    const teniaFoco = document.activeElement === saltar
    html.classList.add('entra')
    for (const b of bloqueados) b.inert = false
    if (teniaFoco) document.querySelector<HTMLElement>('#escenas button[aria-current="true"]')?.focus()
    el!.classList.add('se-va')
    // a timer, not transitionend: in a hidden tab the event never arrives
    setTimeout(() => { el!.remove(); video!.removeAttribute('src'); video!.load() }, 600)
    setTimeout(() => html.classList.remove('entra'), 1100)
  }

  // Hand over: fade only once the live canvas shows its first frame, so the overlay never lifts onto an empty page.
  function empalmar() {
    const hasta = performance.now() + ESCENA_MAX
    const espera = () => {
      if (html.dataset.listo === '1' || performance.now() > hasta) terminar()
      else requestAnimationFrame(espera)
    }
    espera()
  }

  function reproducir() {
    if (fin || reproduciendo) return
    reproduciendo = true
    video!.play().then(
      () => {
        el!.classList.add('con-video')
        // a stalled or missing "ended" must not keep the visitor out of the page
        setTimeout(empalmar, (video!.duration || 10) * 1000 + 3000)
      },
      empalmar, // autoplay refused (Low Power Mode): the page, without the video
    )
  }

  function revisar() {
    if (fin || reproduciendo) return
    const t = performance.now() - t0
    if (listo && t >= MIN) reproducir()
    else if (t >= MAX) empalmar() // the video never buffered in time
  }

  video.addEventListener('canplaythrough', () => { listo = true; revisar() })
  video.addEventListener('ended', empalmar)
  video.addEventListener('error', () => setTimeout(empalmar, Math.max(0, MIN - (performance.now() - t0))))
  setTimeout(revisar, MIN)
  setTimeout(revisar, MAX)

  saltar?.addEventListener('click', terminar)
  addEventListener('keydown', (e) => { if (e.key === 'Escape') terminar() })
}

// The hero loop and its toggle. The loop plays only while visible and never under reduced motion; the poster (= loop frame 0)
// stays otherwise (references.md › hero arraisballet + landonorris; contacto teamusa toggle, placed on the hero it controls).
// The toggle's play/pause morph is GSAP MorphSVG: it animates the path's `d` from JS on a 24 px SVG, the one exception to
// "transform and opacity only" (DESIGN.md › Motion). Under reduced motion the icon swaps in one frame.
import gsap from 'gsap'
import { MorphSVGPlugin } from 'gsap/MorphSVGPlugin'
import { etiqueta, icono, inicial, siguiente, type Evento } from '../lib/estadoBoton'
import { BLOQUE, FORMAS } from '../lib/formas'

gsap.registerPlugin(MorphSVGPlugin)

const v = document.getElementById('loop') as HTMLVideoElement
const boton = document.getElementById('pausa') as HTMLButtonElement
const trazo = boton.querySelector('.icono path') as SVGPathElement
const svg = boton.querySelector('.icono') as SVGElement
const anillo = boton.querySelector('.anillo') as HTMLElement
const et = boton.querySelector('.et') as HTMLElement
const quieto = matchMedia('(prefers-reduced-motion: reduce)')

let e = inicial(quieto.matches)
let forma: 'play' | 'pausa' = e.pausado ? 'play' : 'pausa'
let visible = true
trazo.setAttribute('d', FORMAS[forma])

// 250 ms in all: 60 ms anticipation (shrink to .88); 90 ms closing the two bars into one block (or opening it back); 100 ms
// from the block to the other glyph while the scale overshoots 1 and settles. The overshoot is on the scale, not on the points
// (an overshoot on the points opened a wedge between the two halves of the play shape).
function morfar(a: 'play' | 'pausa') {
  gsap.killTweensOf(trazo)
  if (quieto.matches) {
    trazo.setAttribute('d', FORMAS[a])
    gsap.set(trazo, { scale: 1 })
    return
  }
  gsap
    .timeline()
    .to(trazo, { scale: 0.88, svgOrigin: '12 12', duration: 0.06, ease: 'power1.in' })
    .to(trazo, { morphSVG: BLOQUE, duration: 0.09, ease: 'power2.in' })
    .to(trazo, { morphSVG: FORMAS[a], duration: 0.1, ease: 'power3.out' })
    .to(trazo, { scale: 1, svgOrigin: '12 12', duration: 0.1, ease: 'back.out(2.4)' }, '<')
}

function pintar() {
  const i = icono(e)
  et.textContent = etiqueta(e)
  boton.hidden = e.oculto
  anillo.hidden = i !== 'anillo'
  svg.style.display = i === 'anillo' ? 'none' : ''
  if (i !== 'anillo' && i !== forma) {
    forma = i
    morfar(i)
  }
  if (e.hecho) {
    boton.classList.remove('hecho')
    void boton.offsetWidth
    boton.classList.add('hecho')
    boton.addEventListener('animationend', () => boton.classList.remove('hecho'), { once: true })
  }
}

const aplicar = (ev: Evento) => {
  e = siguiente(e, ev)
  pintar()
}

const tocar = () => {
  if (e.pausado) return v.pause()
  v.play()
    .then(() => v.classList.add('on'))
    .catch((err) => {
      // a pause() that interrupts play() is an AbortError, not a refusal; iOS Low Power Mode refuses with NotAllowedError
      if (err?.name === 'NotAllowedError') aplicar('rechazado')
    })
}

new IntersectionObserver(([en]) => {
  visible = en.isIntersecting
  visible ? tocar() : v.pause()
}).observe(v)

v.addEventListener('waiting', () => aplicar('esperando'))
v.addEventListener('playing', () => aplicar('reproduciendo'))
v.addEventListener('pause', () => aplicar('detenido'))
v.querySelectorAll('source').forEach((s) => s.addEventListener('error', () => aplicar('error')))
v.addEventListener('error', () => aplicar('error'))

boton.addEventListener('click', () => {
  aplicar('toque')
  if (!e.pausado) v.preload = 'auto'
  if (visible) tocar()
})

if (!e.pausado) v.preload = 'auto'
pintar()

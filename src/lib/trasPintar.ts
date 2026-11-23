/** Runs `fn` once the page has painted: after `load`, then a frame and a task later. The heavy downloads (three.js, the GLBs,
 *  apertura.mp4) start here, so the h1 and the nav are never queued behind them (page-first rule, wayfinder escenas ticket 01). */
export function trasPintar(fn: () => void) {
  const luego = () => requestAnimationFrame(() => setTimeout(fn, 0))
  if (document.readyState === 'complete') luego()
  else addEventListener('load', luego, { once: true })
}

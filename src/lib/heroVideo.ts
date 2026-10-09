export function shouldLoadHeroVideo(win: Window): boolean {
  if (win.matchMedia('(prefers-reduced-motion: reduce)').matches) return false
  const conn = (win.navigator as Navigator & { connection?: { saveData?: boolean; effectiveType?: string } }).connection
  if (conn?.saveData === true) return false
  if (conn?.effectiveType && ['slow-2g', '2g'].includes(conn.effectiveType)) return false
  return true
}

export function mountHeroVideo(doc: Document): void {
  if (!shouldLoadHeroVideo(window)) return
  const video = doc.querySelector<HTMLVideoElement>('.hero-video')
  if (!video) return
  video.querySelectorAll('source[data-src]').forEach((s) => {
    s.setAttribute('src', s.getAttribute('data-src')!)
    s.removeAttribute('data-src')
  })
  video.load()
  video.addEventListener(
    'loadeddata',
    () => {
      video.setAttribute('data-loaded', '')
    },
    { once: true },
  )
  // Autoplay: the element has no `autoplay` attr, and `preload="none"` means
  // some browsers won't fire `loadeddata` until a decode is requested. Calling
  // play() here forces the load + starts playback (muted = allowed unattended).
  const p = video.play()
  if (p && typeof p.catch === 'function') p.catch(() => {})
}

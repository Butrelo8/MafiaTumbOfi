/**
 * Click events for POST /e (Workers Analytics Engine, see e.js). No cookies, no ids: the body is
 * { event, net, page, placement } and nothing else. Names match the other sites' plan.
 */

export type ClickEvent = { event: 'wa_click' | 'contact_click' | 'follow_click'; net: string }

const NETS: Record<string, string> = {
  'open.spotify.com': 'spotify',
  'instagram.com': 'instagram',
  'youtube.com': 'youtube',
  'youtu.be': 'youtube',
  'tiktok.com': 'tiktok',
  'facebook.com': 'facebook',
  'music.apple.com': 'apple_music',
}

/** What a link is, by its href. Null for anything we do not count (nav anchors, video thumbnails to other hosts). */
export function classifyLink(href: string, pageHost: string): ClickEvent | null {
  if (href.startsWith('tel:') || href.startsWith('mailto:')) return { event: 'contact_click', net: '' }
  let url: URL
  try {
    url = new URL(href, `https://${pageHost}`)
  } catch {
    return null
  }
  if (url.host === pageHost && url.pathname.startsWith('/wa/')) return { event: 'wa_click', net: '' }
  const host = url.hostname.replace(/^(www|m)\./, '')
  const net = NETS[host]
  return net ? { event: 'follow_click', net } : null
}

export function trackClicks(doc: Document, endpoint = '/e'): void {
  const send = (event: ClickEvent, placement: string) => {
    const body = JSON.stringify({ ...event, page: location.pathname, placement })
    try {
      if (!navigator.sendBeacon?.(endpoint, body)) void fetch(endpoint, { method: 'POST', body, keepalive: true }).catch(() => {})
    } catch {}
  }
  const onClick = (e: Event) => {
    const link = (e.target as Element | null)?.closest?.('a[href]')
    if (!link) return
    const event = classifyLink(link.getAttribute('href') ?? '', location.host)
    if (event) send(event, link.closest<HTMLElement>('[data-placement]')?.dataset.placement ?? '')
  }
  doc.addEventListener('click', onClick)
  doc.addEventListener('auxclick', onClick)
}

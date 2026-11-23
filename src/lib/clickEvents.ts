/**
 * Page views and clicks for POST /e (Workers Analytics Engine, see e.js). No ids, nothing identifies a visitor:
 * {"t":"pv","p":path} per page load (plus nd/nm: first visit of the day/month on this device) and {"t":"click","id":...,"p":path} per tracked link (same contract on every site).
 * The only cookie is the owner's opt-out, nolog=1 (?nolog=1 sets it for a year, ?nolog=0 clears it); /e drops those requests.
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

/** The click id sent to /e: event, net and placement joined, e.g. follow_click:spotify:hero. Matches /^[a-z0-9_:-]{1,60}$/. */
export function clickId(event: ClickEvent, placement: string): string {
  return [event.event, event.net, placement].filter(Boolean).join(':')
}

/** Cookie to write for a query string: set for ?nolog=1, clear for ?nolog=0, none otherwise. */
export function nologCookie(search: string): string | null {
  const flag = new URLSearchParams(search).get('nolog')
  if (flag === '1') return 'nolog=1; Max-Age=31536000; Path=/; SameSite=Lax'
  if (flag === '0') return 'nolog=; Max-Age=0; Path=/; SameSite=Lax'
  return null
}

function beacon(endpoint: string, payload: object): void {
  const body = JSON.stringify(payload)
  try {
    if (!navigator.sendBeacon?.(endpoint, body)) void fetch(endpoint, { method: 'POST', body, keepalive: true }).catch(() => {})
  } catch {}
}

/**
 * First visit of the day / month from this device, from two dates kept in localStorage (ev_d: YYYY-MM-DD, ev_m: YYYY-MM, local time).
 * Returns { nd: 1 } when today differs from ev_d, { nm: 1 } when the month differs from ev_m, and stores today. No id is created or sent;
 * a storage that throws (private mode) gives {}.
 */
export function visitFlags(storage: Pick<Storage, 'getItem' | 'setItem'>, now: Date = new Date()): { nd?: 1; nm?: 1 } {
  const pad = (n: number) => String(n).padStart(2, '0')
  const month = `${now.getFullYear()}-${pad(now.getMonth() + 1)}`
  const day = `${month}-${pad(now.getDate())}`
  const flags: { nd?: 1; nm?: 1 } = {}
  try {
    if (storage.getItem('ev_d') !== day) { flags.nd = 1; storage.setItem('ev_d', day) }
    if (storage.getItem('ev_m') !== month) { flags.nm = 1; storage.setItem('ev_m', month) }
  } catch {
    return {}
  }
  return flags
}

/** One page view per load. A ?nolog flag updates the opt-out cookie; the owner's own visit with ?nolog=1 is not sent. */
export function trackPageview(doc: Document, endpoint = '/e'): void {
  const cookie = nologCookie(location.search)
  if (cookie) doc.cookie = cookie
  if (new URLSearchParams(location.search).get('nolog') === '1') return
  let flags = {}
  try { flags = visitFlags(localStorage) } catch {}
  beacon(endpoint, { t: 'pv', p: location.pathname, ...flags })
}

export function trackClicks(doc: Document, endpoint = '/e'): void {
  const send = (event: ClickEvent, placement: string) =>
    beacon(endpoint, { t: 'click', id: clickId(event, placement), p: location.pathname })
  const onClick = (e: Event) => {
    const link = (e.target as Element | null)?.closest?.('a[href]')
    if (!link) return
    const event = classifyLink(link.getAttribute('href') ?? '', location.host)
    if (event) send(event, link.closest<HTMLElement>('[data-placement]')?.dataset.placement ?? '')
  }
  doc.addEventListener('click', onClick)
  doc.addEventListener('auxclick', onClick)
}

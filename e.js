// POST /e: one event from the page, written to Workers Analytics Engine (binding MTO_EVENTS, dataset mto_events).
// Two body shapes, nothing else is stored (no IP, no user agent, no country, no cookie value):
//  - contract (all sites): {"t":"pv","p":"/path"} or {"t":"click","id":"<button-id>","p":"/path"}
//    Row: index1 = t; blob1 = t, blob2 = p, blob3 = id or "", double1 = 1, double2 = nd, double3 = nm.
//    nd / nm (pv only) are 1 when the page says it is this device's first visit of the day / month (kept in its localStorage as two
//    dates, no id): unique visitors per day = sum(double2), per month = sum(double3), over t = 'pv'. Anything but 1 counts as 0.
//  - legacy clicks: {event, net, page, placement}. Row: index1 = event; blob1 = event, blob2 = net, blob3 = page, blob4 = placement.
//    Kept so rows already in the dataset and older pages keep their shape; a reader tells them apart by blob1 ('pv'|'click' vs *_click).
// Always answers 204 so the beacon never retries or errors the page.
// Not counted: non-POST (405), empty user agent, a crawler/headless/tool user agent, the cookie nolog=1 (the owner's own devices),
// a foreign Origin, a body over 512 bytes, names or paths off the lists.
import { BOT } from './wa.js'

const EXCLUDE_UA = /HeadlessChrome|Playwright|puppeteer|bot|crawler|spider|curl|wget|python|node-fetch|lighthouse/i
const NOLOG = /(?:^|;\s*)nolog=1(?:;|$)/
const EVENTS = new Set(['wa_click', 'contact_click', 'follow_click'])
const NETS = new Set(['spotify', 'instagram', 'youtube', 'tiktok', 'facebook', 'apple_music'])
const PLACEMENT = /^[a-z_]{1,20}$/
const PAGE = /^\/[a-z0-9\-/]{0,60}$/
const CLICK_ID = /^[a-z0-9_:\-]{1,60}$/

function record(env, event, { net = '', page = '/', placement = '' } = {}) {
  env.MTO_EVENTS?.writeDataPoint({ indexes: [event], blobs: [event, net, page, placement] })
}

function recordContract(env, t, p, id, nd, nm) {
  env.MTO_EVENTS?.writeDataPoint({ indexes: [t], blobs: [t, p, id], doubles: [1, nd, nm] })
}

export async function e(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } })
  const ua = request.headers.get('User-Agent') || ''
  const origin = request.headers.get('Origin')
  if (!ua || BOT.test(ua) || EXCLUDE_UA.test(ua) || NOLOG.test(request.headers.get('Cookie') || '') ||
    (origin && origin !== new URL(request.url).origin)) return new Response(null, { status: 204 })
  let d
  try {
    const text = await request.text()
    if (text.length > 512) return new Response(null, { status: 204 })
    d = JSON.parse(text)
  } catch {
    return new Response(null, { status: 204 })
  }
  if (d?.t !== undefined) {
    const id = typeof d.id === 'string' ? d.id : ''
    if (typeof d.p === 'string' && PAGE.test(d.p) &&
      ((d.t === 'pv' && id === '') || (d.t === 'click' && CLICK_ID.test(id)))) {
      const pv = d.t === 'pv'
      recordContract(env, d.t, d.p, id, pv && d.nd === 1 ? 1 : 0, pv && d.nm === 1 ? 1 : 0)
    }
    return new Response(null, { status: 204 })
  }
  const net = typeof d?.net === 'string' ? d.net : ''
  const page = typeof d?.page === 'string' ? d.page : '/'
  const placement = typeof d?.placement === 'string' ? d.placement : ''
  if (EVENTS.has(d?.event) && (net === '' || NETS.has(net)) && PAGE.test(page) && (placement === '' || PLACEMENT.test(placement))) {
    record(env, d.event, { net, page, placement })
  }
  return new Response(null, { status: 204 })
}

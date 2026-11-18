// POST /e: one click event from the page, written to Workers Analytics Engine (binding MTO_EVENTS, dataset mto_events).
// Row: index1 = event; blob1 = event, blob2 = net, blob3 = page, blob4 = placement. Nothing else is stored:
// no IP, no user agent, no country, no cookie. Always answers 204 so the beacon never retries or errors the page.
// Not counted: non-POST (405), crawlers or empty user agent, a foreign Origin, a body over 512 bytes, names off the lists.
import { BOT } from './wa.js'

const EVENTS = new Set(['wa_click', 'contact_click', 'follow_click'])
const NETS = new Set(['spotify', 'instagram', 'youtube', 'tiktok', 'facebook', 'apple_music'])
const PLACEMENT = /^[a-z_]{1,20}$/
const PAGE = /^\/[a-z0-9\-/]{0,60}$/

function record(env, event, { net = '', page = '/', placement = '' } = {}) {
  env.MTO_EVENTS?.writeDataPoint({ indexes: [event], blobs: [event, net, page, placement] })
}

export async function e(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } })
  const ua = request.headers.get('User-Agent') || ''
  const origin = request.headers.get('Origin')
  if (!ua || BOT.test(ua) || (origin && origin !== new URL(request.url).origin)) return new Response(null, { status: 204 })
  let d
  try {
    const text = await request.text()
    if (text.length > 512) return new Response(null, { status: 204 })
    d = JSON.parse(text)
  } catch {
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

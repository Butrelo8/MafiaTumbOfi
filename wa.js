// /wa/<number>?<query>: counts one tap on a WhatsApp button and 302s to https://wa.me/<number>?<query> (query as is).
// Count: KV binding WA_CLICKS, key wa:<YYYY-MM> (Mexico City month), value a bare integer. Nothing else is stored:
// no IP, no user agent, no cookie. The redirect never waits on KV and still happens if KV is missing or fails.
// Not counted: non-GET, prefetch, crawlers, empty user agent.
// ponytail: read-modify-write, two taps in the same instant may count once; fine at this volume (Durable Object if not).
const BOT = /bot|crawl|spider|slurp|facebookexternalhit|headless|curl|wget|python/i

export function wa(request, env, ctx) {
  const url = new URL(request.url)
  const m = /^\/wa\/(\d{8,15})\/?$/.exec(url.pathname)
  if (!m) return new Response('Not found', { status: 404 })
  const h = request.headers
  const ua = h.get('User-Agent') || ''
  const prefetch = /prefetch/i.test(`${h.get('Sec-Purpose') || ''} ${h.get('Purpose') || ''}`) ||
    h.has('Next-Router-Prefetch') || h.has('RSC')
  if (request.method === 'GET' && !prefetch && ua && !BOT.test(ua) && env.WA_CLICKS) {
    ctx.waitUntil(count(env.WA_CLICKS).catch(() => {}))
  }
  return Response.redirect(`https://wa.me/${m[1]}${url.search}`, 302)
}

export const month = (d = new Date()) =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Mexico_City', year: 'numeric', month: '2-digit' }).format(d)

async function count(kv) {
  const key = `wa:${month()}`
  await kv.put(key, String((parseInt(await kv.get(key), 10) || 0) + 1))
}

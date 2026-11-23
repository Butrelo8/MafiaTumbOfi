// node --test e.test.mjs : POST /e (e.js) against a stub Analytics Engine binding.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { e } from './e.js'

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Instagram 300.0'
const ae = () => { const rows = []; return { rows, writeDataPoint: (r) => rows.push(r) } }
const post = (body, { ua = UA, origin, cookie, method = 'POST', env } = {}) =>
  e(new Request('https://mafiatumbada.com/e', { method, body: typeof body === 'string' ? body : JSON.stringify(body),
    headers: { ...(ua ? { 'User-Agent': ua } : {}), ...(origin ? { Origin: origin } : {}), ...(cookie ? { Cookie: cookie } : {}) } }), env)

test('a click writes one row: event, net, page, placement and nothing else', async () => {
  const env = { MTO_EVENTS: ae() }
  const res = await post({ event: 'follow_click', net: 'spotify', page: '/', placement: 'hero' }, { env })
  assert.equal(res.status, 204)
  assert.deepEqual(env.MTO_EVENTS.rows, [{ indexes: ['follow_click'], blobs: ['follow_click', 'spotify', '/', 'hero'] }])
  await post({ event: 'wa_click', page: '/', placement: 'footer', ip: '1.2.3.4' }, { env, origin: 'https://mafiatumbada.com' })
  assert.deepEqual(env.MTO_EVENTS.rows[1].blobs, ['wa_click', '', '/', 'footer'])
})

test('bots, empty UA, foreign origin, other names, big or broken bodies write nothing', async () => {
  const env = { MTO_EVENTS: ae() }
  const ok = { event: 'wa_click', page: '/', placement: 'hero' }
  for (const [b, o] of [[ok, { ua: 'curl/8' }], [ok, { ua: 'Googlebot/2.1' }], [ok, { ua: '' }], [ok, { origin: 'https://evil.example' }],
    [{ ...ok, event: 'signup' }, {}], [{ ...ok, event: 'x' }, {}], [{ ...ok, net: 'myspace' }, {}], [{ ...ok, page: 'https://x' }, {}],
    [{ ...ok, placement: '<b>' }, {}], ['{nope', {}], ['x'.repeat(600), {}], [null, {}]]) {
    assert.equal((await post(b, { ...o, env })).status, 204)
  }
  assert.equal(env.MTO_EVENTS.rows.length, 0)
})

test('GET is 405 and a missing binding still answers 204', async () => {
  const get = await e(new Request('https://mafiatumbada.com/e', { headers: { 'User-Agent': UA } }), {})
  assert.equal(get.status, 405)
  assert.equal((await post({ event: 'wa_click', page: '/' }, { env: {} })).status, 204)
})

test('contract: a page view and a click write t, path, id, a count of 1 and no unique flags', async () => {
  const env = { MTO_EVENTS: ae() }
  assert.equal((await post({ t: 'pv', p: '/anterior-home', ip: '1.2.3.4' }, { env })).status, 204)
  assert.equal((await post({ t: 'click', id: 'follow_click:spotify:hero', p: '/' }, { env })).status, 204)
  assert.deepEqual(env.MTO_EVENTS.rows, [
    { indexes: ['pv'], blobs: ['pv', '/anterior-home', ''], doubles: [1, 0, 0] },
    { indexes: ['click'], blobs: ['click', '/', 'follow_click:spotify:hero'], doubles: [1, 0, 0] },
  ])
})

test('contract payload validation: bad t, path, id, or an id on a pv write nothing', async () => {
  const env = { MTO_EVENTS: ae() }
  for (const b of [{ t: 'view', p: '/' }, { t: 'pv' }, { t: 'pv', p: 'https://x' }, { t: 'pv', p: '/<b>' }, { t: 'pv', p: '/', id: 'x' },
    { t: 'click', p: '/' }, { t: 'click', id: '', p: '/' }, { t: 'click', id: '<b>', p: '/' }, { t: 'click', id: 'a'.repeat(61), p: '/' },
    { t: 1, p: '/' }, { t: 'pv', p: '/'.padEnd(80, 'a') }]) {
    assert.equal((await post(b, { env })).status, 204)
  }
  assert.equal(env.MTO_EVENTS.rows.length, 0)
})

test('exclusion: automation and tool user agents write nothing, a phone browser does', async () => {
  const env = { MTO_EVENTS: ae() }
  for (const ua of ['Mozilla/5.0 HeadlessChrome/131.0', 'Mozilla/5.0 Playwright/1.50', 'puppeteer', 'Googlebot/2.1', 'crawler', 'spider',
    'curl/8.5', 'Wget/1.21', 'python-requests/2.31', 'node-fetch/3', 'Chrome-Lighthouse', 'HEADLESSCHROME']) {
    assert.equal((await post({ t: 'pv', p: '/' }, { ua, env })).status, 204, ua)
  }
  assert.equal(env.MTO_EVENTS.rows.length, 0)
  await post({ t: 'pv', p: '/' }, { ua: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1', env })
  assert.equal(env.MTO_EVENTS.rows.length, 1)
})

test('exclusion: cookie nolog=1 writes nothing, other cookies and nolog=0 do', async () => {
  const env = { MTO_EVENTS: ae() }
  for (const cookie of ['nolog=1', 'a=b; nolog=1', 'nolog=1; a=b']) await post({ t: 'pv', p: '/' }, { cookie, env })
  assert.equal(env.MTO_EVENTS.rows.length, 0)
  for (const cookie of ['nolog=0', 'xnolog=1', 'nolog=10', 'a=b']) await post({ t: 'pv', p: '/' }, { cookie, env })
  assert.equal(env.MTO_EVENTS.rows.length, 4)
})

test('unique flags: nd and nm of 1 land in double2 and double3 on a pv; other values, strings and clicks count 0', async () => {
  const env = { MTO_EVENTS: ae() }
  const doubles = () => env.MTO_EVENTS.rows.map((r) => r.doubles)
  await post({ t: 'pv', p: '/', nd: 1, nm: 1 }, { env })
  await post({ t: 'pv', p: '/', nd: 1 }, { env })
  await post({ t: 'pv', p: '/', nm: 1 }, { env })
  await post({ t: 'pv', p: '/', nd: '1', nm: 2 }, { env })
  await post({ t: 'click', id: 'wa_click', p: '/', nd: 1, nm: 1 }, { env })
  assert.deepEqual(doubles(), [[1, 1, 1], [1, 1, 0], [1, 0, 1], [1, 0, 0], [1, 0, 0]])
})

test('unique flags: bots and nolog are dropped even with nd and nm', async () => {
  const env = { MTO_EVENTS: ae() }
  await post({ t: 'pv', p: '/', nd: 1, nm: 1 }, { ua: 'HeadlessChrome', env })
  await post({ t: 'pv', p: '/', nd: 1, nm: 1 }, { cookie: 'nolog=1', env })
  assert.equal(env.MTO_EVENTS.rows.length, 0)
})

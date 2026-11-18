// node --test e.test.mjs : POST /e (e.js) against a stub Analytics Engine binding.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { e } from './e.js'

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Instagram 300.0'
const ae = () => { const rows = []; return { rows, writeDataPoint: (r) => rows.push(r) } }
const post = (body, { ua = UA, origin, method = 'POST', env } = {}) =>
  e(new Request('https://mafiatumbada.com/e', { method, body: typeof body === 'string' ? body : JSON.stringify(body),
    headers: { ...(ua ? { 'User-Agent': ua } : {}), ...(origin ? { Origin: origin } : {}) } }), env)

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

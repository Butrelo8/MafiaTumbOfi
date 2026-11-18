// node --test signup.test.mjs : POST /signup (signup.js) against stub D1, Rate Limiting and Analytics Engine bindings.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { signup, parseContact, CONSENT_VERSION } from './signup.js'

const stack = (limit = true) => {
  const inserts = [], events = []
  return { inserts, events, env: {
    DB: { prepare: (sql) => ({ bind: (...args) => ({ run: async () => { inserts.push({ sql, args }) } }) }) },
    SIGNUP_LIMIT: { limit: async () => ({ success: limit }) },
    MTO_EVENTS: { writeDataPoint: (r) => events.push(r) },
  } }
}
const post = (fields, env, headers = {}) => signup(new Request('https://mafiatumbada.com/signup', { method: 'POST', body: new URLSearchParams(fields), headers }), env)

test('parseContact: email lowercased, WhatsApp digits with 52, junk rejected', () => {
  assert.deepEqual(parseContact(' Ana@Correo.MX '), { kind: 'email', contact: 'ana@correo.mx' })
  assert.deepEqual(parseContact('228 353 8827'), { kind: 'whatsapp', contact: '522283538827' })
  assert.deepEqual(parseContact('+52 (228) 353-8827'), { kind: 'whatsapp', contact: '522283538827' })
  for (const bad of ['', 'ana@', 'a b@c.mx', '12345', 'hola', 'x'.repeat(300) + '@a.mx']) assert.equal(parseContact(bad), null)
})

test('a valid sign-up inserts one row (no IP) and writes a signup event without the contact', async () => {
  const { env, inserts, events } = stack()
  const res = await post({ contacto: 'ana@correo.mx', ciudad: ' Xalapa ', consent: 'on', web: '' }, env, { 'CF-Connecting-IP': '9.9.9.9' })
  assert.deepEqual(await res.json(), { ok: true })
  assert.deepEqual(inserts[0].args, ['ana@correo.mx', 'email', 'Xalapa', CONSENT_VERSION])
  assert.doesNotMatch(JSON.stringify(inserts), /9\.9\.9\.9/)
  assert.deepEqual(events, [{ indexes: ['signup'], blobs: ['signup', '', '/', 'lista'] }])
})

test('honeypot answers ok and stores nothing; no consent, bad contact and rate limit are refused', async () => {
  let s = stack()
  assert.deepEqual(await (await post({ contacto: 'ana@correo.mx', consent: 'on', web: 'http://spam' }, s.env)).json(), { ok: true })
  assert.equal(s.inserts.length, 0)
  assert.equal((await post({ contacto: 'ana@correo.mx' }, s.env)).status, 400)
  assert.equal((await post({ contacto: 'nope', consent: 'on' }, s.env)).status, 400)
  assert.equal((await post({ contacto: 'ana@correo.mx', consent: 'on' }, s.env, { Origin: 'https://evil.example' })).status, 403)
  s = stack(false)
  const res = await post({ contacto: 'ana@correo.mx', consent: 'on' }, s.env)
  assert.equal(res.status, 429)
  assert.equal(s.inserts.length, 0)
  assert.equal(s.events.length, 0)
})

test('D1 failure is a 500 and no event; GET is 405', async () => {
  const s = stack()
  s.env.DB = { prepare: () => ({ bind: () => ({ run: async () => { throw new Error('d1') } }) }) }
  assert.equal((await post({ contacto: 'ana@correo.mx', consent: 'on' }, s.env)).status, 500)
  assert.equal(s.events.length, 0)
  assert.equal((await signup(new Request('https://mafiatumbada.com/signup'), s.env)).status, 405)
})

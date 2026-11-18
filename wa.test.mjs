// node --test wa.test.mjs : the /wa click counter (wa.js) against a stub KV.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { wa, month } from './wa.js'

const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Instagram 300.0'
const kv = () => { const m = new Map(); return { m, get: async (k) => m.get(k) ?? null, put: async (k, v) => { m.set(k, v) } } }
async function hit(path, { headers = { 'User-Agent': UA }, method = 'GET', env } = {}) {
  const pending = []
  const res = wa(new Request(`https://example.com${path}`, { method, headers }), env, { waitUntil: (p) => pending.push(p) })
  await Promise.all(pending)
  return res
}

test('a tap counts once and redirects to wa.me with the same query', async () => {
  const env = { WA_CLICKS: kv() }
  const q = '?text=Hola%20quiero%20%5Bfecha%5D'
  const res = await hit(`/wa/5212283538827${q}`, { env })
  assert.equal(res.status, 302)
  assert.equal(res.headers.get('Location'), `https://wa.me/5212283538827${q}`)
  await hit('/wa/5212283538827', { env })
  assert.deepEqual([...env.WA_CLICKS.m], [[`wa:${month()}`, '2']])
})

test('crawlers, prefetch, HEAD and empty user agent redirect but do not count', async () => {
  const env = { WA_CLICKS: kv() }
  for (const o of [{ headers: { 'User-Agent': 'facebookexternalhit/1.1' } }, { headers: { 'User-Agent': 'Googlebot/2.1' } },
    { headers: { 'User-Agent': UA, 'Sec-Purpose': 'prefetch' } }, { headers: { 'User-Agent': UA, 'Next-Router-Prefetch': '1' } },
    { headers: { 'User-Agent': UA, RSC: '1' } }, { headers: {} }, { method: 'HEAD' }]) {
    assert.equal((await hit('/wa/522291523952', { ...o, env })).status, 302)
  }
  assert.equal(env.WA_CLICKS.m.size, 0)
})

test('KV missing or failing still redirects', async () => {
  assert.equal((await hit('/wa/522291523952', { env: {} })).status, 302)
  const broken = { get: async () => { throw new Error('kv down') }, put: async () => {} }
  assert.equal((await hit('/wa/522291523952', { env: { WA_CLICKS: broken } })).status, 302)
})

test('anything but /wa/<8-15 digits> is a 404', async () => {
  for (const p of ['/wa/', '/wa/123', '/wa/abc', '/wa/5212283538827/x', '/wa//evil.com']) {
    assert.equal((await hit(p, { env: {} })).status, 404, p)
  }
})

test('month is Mexico City time', () => {
  assert.equal(month(new Date('2026-12-01T03:00:00Z')), '2026-11')  // 21:00 Nov 30 in CDMX
})

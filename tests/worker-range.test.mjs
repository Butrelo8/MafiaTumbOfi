// worker.js answers Range for /video/*: a 206 cut from the stream, not from a buffered copy of the whole file.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import worker from '../worker.js'

const CHUNK = 1000, CHUNKS = 50, SIZE = CHUNK * CHUNKS
const file = Uint8Array.from({ length: SIZE }, (_, i) => i % 251)

// ASSETS stub: the file in 1000-byte chunks, one per pull, so `pulled` shows how much of it was read.
const assets = ({ length = true } = {}) => {
  const o = { pulled: 0, seen: [] }
  o.env = { ASSETS: { fetch: async (req) => {
    o.seen.push(req.headers.get('Range'))
    let i = 0
    const body = new ReadableStream({ pull(c) { if (i >= CHUNKS) return c.close(); o.pulled++; c.enqueue(file.slice(i * CHUNK, ++i * CHUNK)) } }, { highWaterMark: 0 })
    const headers = { 'Content-Type': 'video/webm' }
    if (length) headers['Content-Length'] = String(SIZE)
    return new Response(body, { status: 200, headers })
  } } }
  return o
}
const get = (o, range, method = 'GET') => worker.fetch(new Request('https://x.test/video/a.webm', { method, headers: range ? { Range: range } : {} }), o.env)
const bytes = async (r) => new Uint8Array(await r.arrayBuffer())

test('bytes=0-1 is a 206 with two bytes and reads only the first chunk of the file', async () => {
  const o = assets(), r = await get(o, 'bytes=0-1')
  assert.equal(r.status, 206)
  assert.equal(r.headers.get('Content-Range'), `bytes 0-1/${SIZE}`)
  assert.equal(r.headers.get('Content-Length'), '2')
  assert.equal(r.headers.get('Accept-Ranges'), 'bytes')
  assert.deepEqual([...await bytes(r)], [0, 1])
  assert.ok(o.pulled <= 3, `pulled ${o.pulled} of ${CHUNKS} chunks`)
  assert.deepEqual(o.seen, [null], 'Range is not passed to ASSETS')
})

test('a range in the middle, an open end, a suffix and an end past the file return the right bytes', async () => {
  for (const [range, from, to] of [['bytes=12345-23456', 12345, 23456], [`bytes=${SIZE - 10}-`, SIZE - 10, SIZE - 1], ['bytes=-100', SIZE - 100, SIZE - 1], [`bytes=10-${SIZE + 500}`, 10, SIZE - 1]]) {
    const r = await get(assets(), range)
    assert.equal(r.status, 206, range)
    assert.equal(r.headers.get('Content-Range'), `bytes ${from}-${to}/${SIZE}`, range)
    assert.equal(r.headers.get('Content-Length'), String(to - from + 1), range)
    assert.deepEqual(await bytes(r), file.slice(from, to + 1), range)
  }
})

test('a middle slice stops reading the file after its last byte', async () => {
  const o = assets(), r = await get(o, 'bytes=5000-5999')
  assert.deepEqual(await bytes(r), file.slice(5000, 6000))
  assert.ok(o.pulled <= 8, `pulled ${o.pulled} of ${CHUNKS} chunks`)
})

test('no Range: 200 with the whole file and Accept-Ranges', async () => {
  const r = await get(assets())
  assert.equal(r.status, 200)
  assert.equal(r.headers.get('Accept-Ranges'), 'bytes')
  assert.deepEqual(await bytes(r), file)
})

test('an unsatisfiable range is a 416 with Content-Range bytes */size', async () => {
  for (const range of [`bytes=${SIZE}-`, `bytes=${SIZE + 5}-${SIZE + 9}`, 'bytes=30-10', 'bytes=-0']) {
    const r = await get(assets(), range)
    assert.equal(r.status, 416, range)
    assert.equal(r.headers.get('Content-Range'), `bytes */${SIZE}`, range)
  }
})

test('HEAD with and without Range keeps the headers of the GET', async () => {
  const r = await get(assets(), 'bytes=0-99', 'HEAD')
  assert.equal(r.status, 206)
  assert.equal(r.headers.get('Content-Range'), `bytes 0-99/${SIZE}`)
  assert.equal(r.headers.get('Content-Length'), '100')
  const h = await get(assets(), null, 'HEAD')
  assert.equal(h.status, 200)
  assert.equal(h.headers.get('Accept-Ranges'), 'bytes')
})

test('without a Content-Length upstream it falls back to buffering and answers the same', async () => {
  const r = await get(assets({ length: false }), 'bytes=12345-23456')
  assert.equal(r.status, 206)
  assert.equal(r.headers.get('Content-Range'), `bytes 12345-23456/${SIZE}`)
  assert.deepEqual(await bytes(r), file.slice(12345, 23457))
  const e = await get(assets({ length: false }), `bytes=${SIZE}-`)
  assert.equal(e.status, 416)
})

test('a non-200 from ASSETS passes through', async () => {
  const env = { ASSETS: { fetch: async () => new Response('nope', { status: 404 }) } }
  const r = await worker.fetch(new Request('https://x.test/video/missing.mp4', { headers: { Range: 'bytes=0-1' } }), env)
  assert.equal(r.status, 404)
})

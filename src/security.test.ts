import { describe, expect, test } from 'bun:test'
import { app } from './index'

describe('Security middleware', () => {
  test('body limit: returns 413 when Content-Length exceeds 100KB', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': String(101 * 1024),
      },
      body: JSON.stringify({ name: 'x', email: 'a@b.com' }),
    })
    expect(res.status).toBe(413)
    const data = await res.json()
    expect(data.error?.code).toBe('PAYLOAD_TOO_LARGE')
  })

  test('body limit: returns 413 when Content-Length is missing', async () => {
    const big = new Uint8Array(101 * 1024 + 10)
    const body = new ReadableStream({
      start(controller) {
        controller.enqueue(big)
        controller.close()
      },
    })

    const req = new Request('http://localhost/api/booking', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    })

    const res = await app.fetch(req)
    expect(res.status).toBe(413)
    const data = await res.json()
    expect(data.error?.code).toBe('PAYLOAD_TOO_LARGE')
  })

  test('CORS: allows configured origin', async () => {
    const res = await app.request('/health', {
      headers: { Origin: 'http://localhost:4321' },
    })
    expect(res.status).toBe(200)
    expect(res.headers.get('access-control-allow-origin')).toBe('http://localhost:4321')
  })

  test('CORS: does not set Access-Control-Allow-Origin for unknown origins', async () => {
    const res = await app.request('/health', {
      headers: { Origin: 'https://malicious.example' },
    })
    expect(res.status).toBe(200)
    expect(res.headers.get('access-control-allow-origin')).toBeNull()
  })

  test('CORS preflight: unknown origin does not get Access-Control-Allow-Origin', async () => {
    const res = await app.request('/health', {
      method: 'OPTIONS',
      headers: {
        Origin: 'https://malicious.example',
        'Access-Control-Request-Method': 'GET',
      },
    })
    expect(res.status).toBe(204)
    expect(res.headers.get('access-control-allow-origin')).toBeNull()
  })

  test('HTTPS: does not redirect when not in production', async () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'

    try {
      const res = await app.request('/health', {
        headers: { 'x-forwarded-proto': 'http' },
      })
      expect(res.status).toBe(200)
      expect(res.headers.get('location')).toBeNull()
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('HTTPS: in production, does not redirect when x-forwarded-proto is missing', async () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    try {
      const res = await app.request('/health')
      expect(res.status).toBe(200)
      expect(res.headers.get('location')).toBeNull()
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('HTTPS: in production, treats Forwarded: proto=https like secure when x-forwarded-proto absent', async () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    try {
      const res = await app.request('/health', {
        headers: { Forwarded: 'for=1.2.3.4;proto=https' },
      })
      expect(res.status).toBe(200)
      expect(res.headers.get('location')).toBeNull()
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('health: returns 429 after rate limit per IP (120/min)', async () => {
    const ip = '192.168.77.88'
    for (let i = 0; i < 120; i++) {
      const res = await app.request('/health', {
        headers: { 'x-forwarded-for': ip },
      })
      expect(res.status).toBe(200)
    }
    const limited = await app.request('/health', {
      headers: { 'x-forwarded-for': ip },
    })
    expect(limited.status).toBe(429)
    const data = await limited.json()
    expect(data.error?.code).toBe('RATE_LIMITED')
  })

  test('HTTPS: in production, redirects when x-forwarded-proto is http', async () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    try {
      const res = await app.request('/health', {
        headers: { 'x-forwarded-proto': 'http', host: 'example.com' },
      })

      expect(res.status).toBe(301)
      expect(res.headers.get('location')).toBe('https://example.com/health')
    } finally {
      process.env.NODE_ENV = prev
    }
  })
})

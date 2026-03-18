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

  test('auth rate limit: returns 429 after 10 requests per IP', async () => {
    const ip = '192.168.100.50'
    for (let i = 0; i < 10; i++) {
      const res = await app.request('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-forwarded-for': ip },
        body: JSON.stringify({}),
      })
      expect(res.status).toBe(501)
    }
    const res = await app.request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': ip },
      body: JSON.stringify({}),
    })
    expect(res.status).toBe(429)
    const data = await res.json()
    expect(data.error?.code).toBe('RATE_LIMITED')
  })

  test('CORS: allows configured origin', async () => {
    const res = await app.request('/health', {
      headers: { Origin: 'http://localhost:4321' },
    })
    expect(res.status).toBe(200)
    expect(res.headers.get('access-control-allow-origin')).toBe('http://localhost:4321')
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

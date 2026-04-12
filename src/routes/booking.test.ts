import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { Hono } from 'hono'
import type { Resend } from 'resend'
import { setResendForTesting } from '../lib/resend'

const mockDb = {
  insert: () => ({
    values: () => ({
      returning: async () => [{ id: 1 }],
    }),
  }),
  update: () => ({
    set: () => ({
      where: async () => undefined,
    }),
  }),
}

function defaultResendMock(): Resend {
  return {
    emails: {
      send: async () => ({ data: { id: 'mock-id' }, error: null }),
    },
  } as Resend
}

mock.module('../db', () => ({ db: mockDb }))

const { bookingRoutes } = await import('./booking')
const app = new Hono().route('/api', bookingRoutes)

beforeEach(() => {
  setResendForTesting(defaultResendMock())
})

afterEach(() => {
  setResendForTesting(null)
})

describe('POST /api/booking', () => {
  test('returns 400 for invalid JSON', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: 'not json',
      headers: { 'Content-Type': 'application/json' },
    })
    expect(res.status).toBe(400)
    const data = await res.json()
    expect(data.error?.code).toBe('INVALID_JSON')
  })

  test('returns 400 for validation error (missing name)', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ email: 'a@b.com' }),
      headers: { 'Content-Type': 'application/json' },
    })
    expect(res.status).toBe(400)
    const data = await res.json()
    expect(data.error?.code).toBe('VALIDATION_ERROR')
  })

  test('returns 400 for invalid email', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'invalid' }),
      headers: { 'Content-Type': 'application/json' },
    })
    expect(res.status).toBe(400)
    const data = await res.json()
    expect(data.error?.code).toBe('VALIDATION_ERROR')
  })

  test('returns 400 SPAM_DETECTED when honeypot (website) is filled', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Test',
        email: 'test@example.com',
        website: 'http://spam.com',
      }),
      headers: { 'Content-Type': 'application/json' },
    })
    expect(res.status).toBe(400)
    const data = await res.json()
    expect(data.error?.code).toBe('SPAM_DETECTED')
  })

  test('returns 500 when BOOKING_NOTIFICATION_EMAIL is not set', async () => {
    const prev = process.env.BOOKING_NOTIFICATION_EMAIL
    delete process.env.BOOKING_NOTIFICATION_EMAIL
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'test@example.com' }),
      headers: { 'Content-Type': 'application/json' },
    })
    if (prev !== undefined) process.env.BOOKING_NOTIFICATION_EMAIL = prev
    expect(res.status).toBe(500)
    const data = await res.json()
    expect(data.error?.code).toBe('CONFIG_ERROR')
  })

  test('returns 201 when valid and env set', async () => {
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Promoter',
        email: 'promoter@example.com',
        message: 'Hello',
      }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '192.168.1.1' },
    })
    expect(res.status).toBe(201)
    const data = await res.json()
    expect(data.data?.ok).toBe(true)
    expect(data.data?.confirmation).toBe('sent')
    expect(data.data?.bookingId).toBe(1)
  })

  test('calls Resend twice on success (band notification + confirmation)', async () => {
    let sendCalls = 0
    setResendForTesting({
      emails: {
        send: async () => {
          sendCalls += 1
          return { data: { id: 'mock-id' }, error: null }
        },
      },
    } as Resend)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'A', email: 'a@b.com' }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '10.0.0.1' },
    })
    expect(res.status).toBe(201)
    expect(sendCalls).toBe(2)
  })

  test('plain text bodies keep blank-line paragraph breaks', async () => {
    const texts: string[] = []
    setResendForTesting({
      emails: {
        send: async (opts: { text?: string }) => {
          if (typeof opts.text === 'string') texts.push(opts.text)
          return { data: { id: 'mock-id' }, error: null }
        },
      },
    } as Resend)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Pat', email: 'pat@example.com', phone: '555' }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '10.0.0.2' },
    })
    expect(res.status).toBe(201)
    expect(texts).toHaveLength(2)
    expect(texts[0]).toMatch(/sitio web\.\n\nNombre:/)
    expect(texts[1]).toMatch(/^Hola Pat,\n\nGracias/)
  })

  test('returns 500 and EMAIL_FAILED when Resend send fails', async () => {
    setResendForTesting({
      emails: {
        send: async () => ({ data: null, error: { message: 'Resend API error' } }),
      },
    } as Resend)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'test@example.com' }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '192.168.1.99',
      },
    })
    expect(res.status).toBe(500)
    const data = await res.json()
    expect(data.error?.code).toBe('EMAIL_FAILED')
  })

  test('sets status to pending when band email succeeds but confirmation fails', async () => {
    let callCount = 0
    let lastStatus: string | undefined
    let lastConfirmationLastError: string | null | undefined
    let lastConfirmationAttempts: number | undefined
    const captureDb = {
      insert: () => ({
        values: () => ({
          returning: async () => [{ id: 1 }],
        }),
      }),
      update: () => ({
        set: (obj: {
          status?: string
          confirmationLastError?: string | null
          confirmationAttempts?: number
        }) => {
          callCount += 1
          lastStatus = obj.status
          lastConfirmationLastError = obj.confirmationLastError
          lastConfirmationAttempts = obj.confirmationAttempts
          return { where: async () => undefined }
        },
      }),
    }
    mock.module('../db', () => ({ db: captureDb }))
    setResendForTesting({
      emails: {
        send: async () => {
          callCount += 1
          if (callCount === 1) return { data: { id: 'ok' }, error: null }
          return { data: null, error: { message: 'Confirmation rejected' } }
        },
      },
    } as Resend)
    const { bookingRoutes: routes } = await import('./booking')
    const testApp = new Hono().route('/api', routes)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await testApp.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'X', email: 'x@y.com' }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '127.0.0.1' },
    })
    expect(res.status).toBe(201)
    expect(lastStatus).toBe('pending')
    expect(lastConfirmationLastError).toBe('Confirmation rejected')
    expect(lastConfirmationAttempts).toBe(1)
    const data = await res.json()
    expect(data.data?.confirmation).toBe('pending')
  })

  test('sets status to pending when confirmation send throws', async () => {
    let callCount = 0
    let lastStatus: string | undefined
    let lastConfirmationLastError: string | null | undefined
    let lastConfirmationAttempts: number | undefined
    const captureDb = {
      insert: () => ({
        values: () => ({
          returning: async () => [{ id: 1 }],
        }),
      }),
      update: () => ({
        set: (obj: {
          status?: string
          confirmationLastError?: string | null
          confirmationAttempts?: number
        }) => {
          lastStatus = obj.status
          lastConfirmationLastError = obj.confirmationLastError
          lastConfirmationAttempts = obj.confirmationAttempts
          return { where: async () => undefined }
        },
      }),
    }

    mock.module('../db', () => ({ db: captureDb }))
    setResendForTesting({
      emails: {
        send: async () => {
          callCount += 1
          if (callCount === 1) return { data: { id: 'ok' }, error: null }
          throw new Error('Resend failure during confirmation')
        },
      },
    } as Resend)

    const { bookingRoutes: routes } = await import('./booking')
    const testApp = new Hono().route('/api', routes)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'

    const res = await testApp.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Y', email: 'y@y.com' }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '127.0.0.2' },
    })

    expect(res.status).toBe(201)
    expect(lastStatus).toBe('pending')
    expect(lastConfirmationLastError).toBe('Resend failure during confirmation')
    expect(lastConfirmationAttempts).toBe(1)
    const data = await res.json()
    expect(data.data?.confirmation).toBe('pending')
  })

  test('returns 500 BOOKING_PERSIST_FAILED when insert returns no row', async () => {
    mock.module('../db', () => ({
      db: {
        insert: () => ({
          values: () => ({
            returning: async () => [] as { id: number }[],
          }),
        }),
      },
    }))
    const { bookingRoutes: routesEmpty } = await import('./booking')
    const appEmpty = new Hono().route('/api', routesEmpty)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appEmpty.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'X', email: 'x@y.com' }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '10.99.0.1',
      },
    })
    expect(res.status).toBe(500)
    const data = await res.json()
    expect(data.error?.code).toBe('BOOKING_PERSIST_FAILED')
  })

  test('returns 500 BOOKING_PERSIST_FAILED when insert throws', async () => {
    mock.module('../db', () => ({
      db: {
        insert: () => ({
          values: () => ({
            returning: async () => {
              throw new Error('SQLITE_FULL')
            },
          }),
        }),
      },
    }))
    const { bookingRoutes: routesThrow } = await import('./booking')
    const appThrow = new Hono().route('/api', routesThrow)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appThrow.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Z', email: 'z@z.com' }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '10.99.0.2',
      },
    })
    expect(res.status).toBe(500)
    const data = await res.json()
    expect(data.error?.code).toBe('BOOKING_PERSIST_FAILED')
  })

  test('returns 201 and persists extended booking fields when provided', async () => {
    let insertRow: Record<string, unknown> | undefined
    const captureDb = {
      insert: () => ({
        values: (row: Record<string, unknown>) => {
          insertRow = row
          return {
            returning: async () => [{ id: 1 }],
          }
        },
      }),
      update: () => ({
        set: () => ({
          where: async () => undefined,
        }),
      }),
    }
    mock.module('../db', () => ({ db: captureDb }))
    const { bookingRoutes: routesExtended } = await import('./booking')
    const appExtended = new Hono().route('/api', routesExtended)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appExtended.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Organizer',
        email: 'org@example.com',
        phone: '555-0100',
        eventDate: '2026-06-15',
        city: 'Xalapa, Veracruz',
        eventType: 'boda',
        duration: '2h',
        showType: 'mix',
        attendees: '100_300',
        venueSound: 'si',
        budget: '30k_50k',
        message: 'Boda al aire libre',
      }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '10.1.1.1' },
    })
    expect(res.status).toBe(201)
    const data = await res.json()
    expect(data.data?.confirmation).toBe('sent')
    expect(insertRow?.city).toBe('Xalapa, Veracruz')
    expect(insertRow?.eventType).toBe('boda')
    expect(insertRow?.duration).toBe('2h')
    expect(insertRow?.showType).toBe('mix')
    expect(insertRow?.attendees).toBe('100_300')
    expect(insertRow?.venueSound).toBe('si')
    expect(insertRow?.budget).toBe('30k_50k')
    expect(insertRow?.pipelineStatus).toBe('new')
  })

  test('returns 201 when budget is omitted', async () => {
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'test@example.com' }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '10.88.1.1',
      },
    })
    expect(res.status).toBe(201)
    const data = await res.json()
    expect(data.data?.ok).toBe(true)
  })

  test('persists null budget when omitted', async () => {
    let insertRow: Record<string, unknown> | undefined
    const captureDb = {
      insert: () => ({
        values: (row: Record<string, unknown>) => {
          insertRow = row
          return {
            returning: async () => [{ id: 1 }],
          }
        },
      }),
      update: () => ({
        set: () => ({
          where: async () => undefined,
        }),
      }),
    }
    mock.module('../db', () => ({ db: captureDb }))
    const { bookingRoutes: routesNoBudget } = await import('./booking')
    const appNoBudget = new Hono().route('/api', routesNoBudget)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appNoBudget.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'nobudget@example.com' }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '10.88.1.4',
      },
    })
    expect(res.status).toBe(201)
    expect(insertRow?.budget).toBeNull()
    expect(insertRow?.pipelineStatus).toBe('new')
  })

  test('returns 400 VALIDATION_ERROR when budget has invalid value', async () => {
    const res = await app.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Test',
        email: 'test@example.com',
        budget: 'free',
      }),
      headers: {
        'Content-Type': 'application/json',
        'x-forwarded-for': '10.88.1.2',
      },
    })
    expect(res.status).toBe(400)
    const data = await res.json()
    expect(data.error?.code).toBe('VALIDATION_ERROR')
  })

  test('rate limit: returns 429 after 5 requests per IP', async () => {
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const ip = '198.51.100.77'
    const headers = {
      'Content-Type': 'application/json',
      'x-forwarded-for': ip,
    }
    const body = JSON.stringify({ name: 'Rate limit', email: 'limit@example.com' })
    for (let i = 0; i < 5; i++) {
      const res = await app.request('/api/booking', {
        method: 'POST',
        headers,
        body,
      })
      expect(res.status).not.toBe(429)
    }
    const res = await app.request('/api/booking', {
      method: 'POST',
      headers,
      body,
    })
    expect(res.status).toBe(429)
    const data = await res.json()
    expect(data.error?.code).toBe('RATE_LIMITED')
  })
})

import { describe, expect, mock, test } from 'bun:test'
import { Hono } from 'hono'

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

mock.module('../db', () => ({ db: mockDb }))
mock.module('../lib/resend', () => ({
  getResend: () => ({
    emails: {
      send: async () => ({ data: { id: 'mock-id' }, error: null }),
    },
  }),
}))

const { bookingRoutes } = await import('./booking')
const app = new Hono().route('/api', bookingRoutes)

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
    mock.module('../lib/resend', () => ({
      getResend: () => ({
        emails: {
          send: async () => {
            sendCalls += 1
            return { data: { id: 'mock-id' }, error: null }
          },
        },
      }),
    }))
    const { bookingRoutes: bookingRoutesConfirm } = await import('./booking')
    const appConfirm = new Hono().route('/api', bookingRoutesConfirm)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appConfirm.request('/api/booking', {
      method: 'POST',
      body: JSON.stringify({ name: 'A', email: 'a@b.com' }),
      headers: { 'Content-Type': 'application/json', 'x-forwarded-for': '10.0.0.1' },
    })
    expect(res.status).toBe(201)
    expect(sendCalls).toBe(2)
  })

  test('returns 500 and EMAIL_FAILED when Resend send fails', async () => {
    mock.module('../lib/resend', () => ({
      getResend: () => ({
        emails: {
          send: async () => ({ data: null, error: { message: 'Resend API error' } }),
        },
      }),
    }))
    const { bookingRoutes: bookingRoutesFail } = await import('./booking')
    const appFail = new Hono().route('/api', bookingRoutesFail)
    process.env.BOOKING_NOTIFICATION_EMAIL = 'band@example.com'
    const res = await appFail.request('/api/booking', {
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
    mock.module('../lib/resend', () => ({
      getResend: () => ({
        emails: {
          send: async () => {
            callCount += 1
            if (callCount === 1) return { data: { id: 'ok' }, error: null }
            return { data: null, error: { message: 'Confirmation rejected' } }
          },
        },
      }),
    }))
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
    mock.module('../lib/resend', () => ({
      getResend: () => ({
        emails: {
          send: async () => {
            callCount += 1
            if (callCount === 1) return { data: { id: 'ok' }, error: null }
            throw new Error('Resend failure during confirmation')
          },
        },
      }),
    }))

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

  test('returns 500 INTERNAL_ERROR when insert returns no row', async () => {
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
    expect(data.error?.code).toBe('INTERNAL_ERROR')
  })
})

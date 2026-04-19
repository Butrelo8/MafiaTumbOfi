import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import type { Resend } from 'resend'
import { setResendForTesting } from '../lib/resend'

const mockAdminUser = {
  id: 1,
  clerkId: 'user_123',
  email: 'admin@test.com',
  name: 'Test Admin',
  isAdmin: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

const mockNonAdminUser = {
  id: 2,
  clerkId: 'user_456',
  email: 'user@test.com',
  name: 'Non Admin',
  isAdmin: false,
  createdAt: new Date(),
  updatedAt: new Date(),
}

let bookingToReturn: unknown = null
let getOrCreateUserReturn: typeof mockAdminUser | typeof mockNonAdminUser = mockAdminUser
let lastUpdate: {
  status?: 'pending' | 'sent' | 'failed'
  confirmationLastError?: string | null
  confirmationAttempts?: number
} | null = null
let resendBehavior: 'success' | 'error' | 'throw' = 'success'

mock.module('../db', () => ({
  db: {
    select: () => ({
      from: () => ({
        where: () => ({
          get: async () => bookingToReturn,
        }),
      }),
    }),
    update: () => ({
      set: (values: unknown) => {
        lastUpdate = values as {
          status?: 'pending' | 'sent' | 'failed'
          confirmationLastError?: string | null
          confirmationAttempts?: number
        }
        return {
          where: async () => undefined,
        }
      },
    }),
  },
}))

mock.module('../lib/users', () => ({
  getOrCreateUser: async () => getOrCreateUserReturn,
}))

const resendApiMock = {
  emails: {
    send: async () => {
      if (resendBehavior === 'throw') {
        throw new Error('Resend throw during confirmation')
      }

      if (resendBehavior === 'error') {
        return {
          data: null,
          error: { message: 'Resend API error', name: 'Test' },
        }
      }

      return { data: { id: 'mock-id' }, error: null }
    },
  },
} as Resend

const { app } = await import('../index')
const { setClerkClientForTesting } = await import('../middleware/auth')

const mockClerkClient = {
  authenticateRequest: async (req: Request) => {
    const token = req.headers.get('Authorization')
    const isAuthenticated = token === 'Bearer valid_token'
    return {
      isAuthenticated,
      toAuth: () => ({ userId: 'user_123', sessionId: 'sess_456' }),
    }
  },
}

setClerkClientForTesting(mockClerkClient as never)

describe('POST /api/admin/bookings/:id/resend-confirmation', () => {
  beforeEach(() => {
    setResendForTesting(resendApiMock)
    resendBehavior = 'success'
  })

  afterEach(() => {
    setResendForTesting(null)
  })

  test('returns 401 when unauthenticated', async () => {
    getOrCreateUserReturn = mockAdminUser
    bookingToReturn = null
    lastUpdate = null

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
    })

    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error.code).toBe('UNAUTHORIZED')
  })

  test('returns 403 for authenticated non-admin users', async () => {
    getOrCreateUserReturn = mockNonAdminUser
    bookingToReturn = null
    lastUpdate = null

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })

    expect(res.status).toBe(403)
    const body = await res.json()
    expect(body.error.code).toBe('FORBIDDEN')
  })

  test('returns 404 when booking does not exist', async () => {
    getOrCreateUserReturn = mockAdminUser
    bookingToReturn = null
    lastUpdate = null

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })

    expect(res.status).toBe(404)
    const body = await res.json()
    expect(body.error.code).toBe('NOT_FOUND')
  })

  test('rejects resend when booking status is failed', async () => {
    getOrCreateUserReturn = mockAdminUser
    bookingToReturn = {
      id: 1,
      name: 'X',
      email: 'x@test.com',
      phone: null,
      eventDate: null,
      message: null,
      status: 'failed',
      confirmationLastError: null,
      confirmationAttempts: 0,
      createdAt: new Date(),
    }
    lastUpdate = null
    resendBehavior = 'success'

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })

    expect(res.status).toBe(400)
    const body = await res.json()
    expect(body.error.code).toBe('INVALID_STATUS')
  })

  test('success: sets status sent, clears last error, increments attempt count', async () => {
    getOrCreateUserReturn = mockAdminUser
    bookingToReturn = {
      id: 1,
      name: 'X',
      email: 'x@test.com',
      phone: null,
      eventDate: null,
      message: null,
      status: 'pending',
      confirmationLastError: 'previous failure',
      confirmationAttempts: 1,
      createdAt: new Date(),
    }
    lastUpdate = null
    resendBehavior = 'success'

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })

    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.status).toBe('sent')
    expect(body.data.confirmationLastError).toBe(null)
    expect(body.data.confirmationAttempts).toBe(2)

    expect(lastUpdate.status).toBe('sent')
    expect(lastUpdate.confirmationLastError).toBe(null)
    expect(lastUpdate.confirmationAttempts).toBe(2)
  })

  test('failure: keeps status pending, sets last error, increments attempt count', async () => {
    getOrCreateUserReturn = mockAdminUser
    bookingToReturn = {
      id: 1,
      name: 'X',
      email: 'x@test.com',
      phone: null,
      eventDate: null,
      message: null,
      status: 'pending',
      confirmationLastError: 'previous failure',
      confirmationAttempts: 1,
      createdAt: new Date(),
    }
    lastUpdate = null
    resendBehavior = 'error'

    const res = await app.request('/api/admin/bookings/1/resend-confirmation', {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })

    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.status).toBe('pending')
    expect(body.data.confirmationLastError).toBe('Resend API error')
    expect(body.data.confirmationAttempts).toBe(2)

    expect(lastUpdate.status).toBe('pending')
    expect(lastUpdate.confirmationLastError).toBe('Resend API error')
    expect(lastUpdate.confirmationAttempts).toBe(2)
  })
})

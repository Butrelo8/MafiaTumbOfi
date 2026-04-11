/**
 * Auth-protected route tests. Uses setClerkClientForTesting to inject a mock
 * so tests don't require real Clerk keys.
 */
import { describe, expect, mock, test } from 'bun:test'

const mockBookings = [
  {
    id: 1,
    name: 'Test Band',
    email: 'band@test.com',
    phone: '555-1234',
    eventDate: '2025-06-01',
    message: 'Hello',
    status: 'pending',
    createdAt: new Date('2020-01-15'),
  },
]

const mockAdminUser = {
  id: 1,
  clerkId: 'user_123',
  email: 'admin@test.com',
  name: 'Test Admin',
  isAdmin: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

mock.module('../db', () => ({
  db: {
    select: (fields?: unknown) => {
      const isCount =
        fields != null &&
        typeof fields === 'object' &&
        !Array.isArray(fields) &&
        'total' in (fields as Record<string, unknown>)
      if (isCount) {
        const fromResult = Object.assign(Promise.resolve([{ total: mockBookings.length }]), {
          where: () => Promise.resolve([{ total: 0 }]),
        })
        return {
          from: () => fromResult,
        }
      }
      return {
        from: () => ({
          orderBy: () => ({
            limit: (lim: number) => {
              const sorted = [...mockBookings].sort(
                (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
              )
              const page = Promise.resolve(sorted.slice(0, lim))
              return Object.assign(page, {
                offset: (off: number) => Promise.resolve(sorted.slice(off, off + lim)),
              })
            },
          }),
          where: () => ({
            get: () => Promise.resolve(mockAdminUser),
          }),
        }),
      }
    },
  },
}))

mock.module('../lib/users', () => ({
  getOrCreateUser: async () => mockAdminUser,
}))

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

describe('Admin Routes', () => {
  test('GET /api/admin/bookings - unauthorized without token', async () => {
    const res = await app.request('/api/admin/bookings')
    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error.code).toBe('UNAUTHORIZED')
  })

  test('GET /api/admin/bookings - success with valid token', async () => {
    const res = await app.request('/api/admin/bookings', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body).toHaveProperty('data')
    expect(body.data).toHaveProperty('bookings')
    expect(body.data).toHaveProperty('total', 1)
    expect(body.data).toHaveProperty('limit', 50)
    expect(body.data).toHaveProperty('offset', 0)
    expect(body.data).toHaveProperty('hasMore', false)
    expect(Array.isArray(body.data.bookings)).toBe(true)
    expect(body.data.bookings).toHaveLength(1)
    expect(body.data.bookings[0].name).toBe('Test Band')
  })

  test('GET /api/admin/export/bookings - returns export shape when authenticated', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'development'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      const res = await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
      expect(res.status).toBe(200)
      const body = await res.json()
      expect(body).toHaveProperty('data')
      expect(body.data).toHaveProperty('exportedAt')
      expect(body.data).toHaveProperty('total', 1)
      expect(body.data).toHaveProperty('last24hCount')
      expect(typeof body.data.last24hCount).toBe('number')
      expect(body.data).toHaveProperty('returnedCount', 1)
      expect(body.data).toHaveProperty('truncated', false)
      expect(body.data).toHaveProperty('bookings')
      expect(Array.isArray(body.data.bookings)).toBe(true)
      expect(body.data.bookings).toHaveLength(1)
      expect(body.data.bookings[0].name).toBe('Test Band')
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('GET /api/admin/export/bookings - 403 in production when export flag unset', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'production'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      const res = await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
      expect(res.status).toBe(403)
      const body = await res.json()
      expect(body.error.code).toBe('ADMIN_BOOKING_EXPORT_DISABLED')
      expect(body.error.status).toBe(403)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('GET /api/admin/export/bookings - 200 in production when ALLOW_ADMIN_BOOKING_EXPORT=true', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'production'
      process.env.ALLOW_ADMIN_BOOKING_EXPORT = 'true'
      const res = await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
      expect(res.status).toBe(200)
      const body = await res.json()
      expect(body.data.bookings).toHaveLength(1)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('GET /api/admin/export/bookings - writes audit log line on success', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    const lines: string[] = []
    const origLog = console.log
    console.log = (...args: unknown[]) => {
      lines.push(args.map((a) => (typeof a === 'string' ? a : JSON.stringify(a))).join(' '))
    }
    try {
      process.env.NODE_ENV = 'development'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
    } finally {
      console.log = origLog
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
    const auditLine = lines.find((l) => l.includes('admin_booking_export'))
    expect(auditLine).toBeDefined()
    const parsed = JSON.parse(auditLine!) as {
      type: string
      action: string
      userId: string
      sessionId: string | null
    }
    expect(parsed.type).toBe('audit')
    expect(parsed.action).toBe('admin_booking_export')
    expect(parsed.userId).toBe('user_123')
    expect(parsed.sessionId).toBe('sess_456')
  })

  test('GET /api/admin/export/bookings - no audit log when gated off', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    const lines: string[] = []
    const origLog = console.log
    console.log = (...args: unknown[]) => {
      lines.push(args.map((a) => (typeof a === 'string' ? a : JSON.stringify(a))).join(' '))
    }
    try {
      process.env.NODE_ENV = 'production'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
    } finally {
      console.log = origLog
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
    expect(lines.some((l) => l.includes('admin_booking_export'))).toBe(false)
  })
})

describe('User Routes', () => {
  test('GET /api/users/me - unauthorized without token', async () => {
    const res = await app.request('/api/users/me')
    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error.code).toBe('UNAUTHORIZED')
  })

  test('GET /api/users/me - returns 200 with user when authenticated', async () => {
    const res = await app.request('/api/users/me', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data).toBeDefined()
    expect(body.data.clerkId).toBe('user_123')
    expect(body.data.isAdmin).toBe(true)
  })
})

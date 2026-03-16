/**
 * Admin authorization tests: non-admin users get 403 on admin routes.
 */
import { describe, expect, mock, test } from 'bun:test'

const mockBookings: Array<{
  id: number
  name: string
  email: string
  phone: string | null
  eventDate: string | null
  message: string | null
  status: string
  createdAt: Date
}> = []

const mockNonAdminUser = {
  id: 2,
  clerkId: 'user_123',
  email: 'fan@test.com',
  name: 'Test Fan',
  isAdmin: false,
  createdAt: new Date(),
  updatedAt: new Date(),
}

mock.module('../db', () => ({
  db: {
    select: () => ({
      from: () => ({
        orderBy: () => Promise.resolve(mockBookings),
        where: () => ({
          get: () => Promise.resolve(mockNonAdminUser),
        }),
      }),
    }),
  },
}))

mock.module('../lib/users', () => ({
  getOrCreateUser: async () => mockNonAdminUser,
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

describe('Admin authorization', () => {
  test('GET /api/admin/bookings returns 403 when user is not admin', async () => {
    const res = await app.request('/api/admin/bookings', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(403)
    const body = await res.json()
    expect(body.error.code).toBe('FORBIDDEN')
    expect(body.error.message).toContain('Admin')
  })
})

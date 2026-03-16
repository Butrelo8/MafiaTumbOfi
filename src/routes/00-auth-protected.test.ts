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
    createdAt: new Date('2025-03-15'),
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
    select: () => ({
      from: () => ({
        orderBy: () => Promise.resolve(mockBookings),
        where: () => ({
          get: () => Promise.resolve(mockAdminUser),
        }),
      }),
    }),
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
    expect(body).toHaveProperty('total')
    expect(Array.isArray(body.data)).toBe(true)
    expect(body.data).toHaveLength(1)
    expect(body.data[0].name).toBe('Test Band')
    expect(body.total).toBe(1)
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

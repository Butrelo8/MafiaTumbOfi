/**
 * Soft-delete bookings: DELETE /api/admin/bookings/:id + list/resend/PATCH visibility (real SQLite).
 */

import { Database } from 'bun:sqlite'
import { afterAll, beforeAll, beforeEach, describe, expect, mock, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { eq } from 'drizzle-orm'
import { drizzle } from 'drizzle-orm/bun-sqlite'
import * as schema from '../db/schema'
import { bookings } from '../db/schema'
import { setClerkClientForTesting } from '../middleware/auth'

function applyDrizzleMigrations(sqlite: Database): void {
  const drizzleDir = join(import.meta.dir, '..', '..', 'drizzle')
  const files = readdirSync(drizzleDir)
    .filter((f) => f.endsWith('.sql'))
    .sort()
  for (const file of files) {
    const fileSql = readFileSync(join(drizzleDir, file), 'utf8')
    const statements = fileSql
      .split('--> statement-breakpoint')
      .map((s) => s.trim())
      .filter(Boolean)
    for (const st of statements) {
      try {
        sqlite.run(st)
      } catch (e: unknown) {
        const msg = (e as Error).message ?? ''
        const isIdempotent = msg.includes('already exists') || msg.includes('duplicate column name')
        if (!isIdempotent) throw e
      }
    }
  }
}

const mockAdminUser = {
  id: 1,
  clerkId: 'user_123',
  email: 'admin@test.com',
  name: 'Test Admin',
  isAdmin: true,
  createdAt: new Date(),
  updatedAt: new Date(),
}

mock.module('../lib/users', () => ({
  getOrCreateUser: async () => mockAdminUser,
}))

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

describe('DELETE /api/admin/bookings/:id (soft delete)', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>
  let app: typeof import('../index').app
  let bookingId = 1

  beforeAll(async () => {
    sqlite = new Database(':memory:')
    applyDrizzleMigrations(sqlite)
    testDb = drizzle(sqlite, { schema })
    mock.module('../db', () => ({ db: testDb }))
    setClerkClientForTesting(mockClerkClient as never)
    ;({ app } = await import('../index'))
  })

  beforeEach(async () => {
    await testDb.delete(bookings)
    const [row] = await testDb
      .insert(bookings)
      .values({
        name: 'Lead',
        email: 'lead@example.com',
        status: 'pending',
        pipelineStatus: 'new',
      })
      .returning({ id: bookings.id })
    bookingId = row?.id ?? 1
  })

  afterAll(() => {
    setClerkClientForTesting(null)
    sqlite.close()
  })

  test('returns 401 without token', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, { method: 'DELETE' })
    expect(res.status).toBe(401)
  })

  test('returns 400 for invalid id', async () => {
    const res = await app.request('/api/admin/bookings/0', {
      method: 'DELETE',
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(400)
  })

  test('returns 404 when booking missing', async () => {
    const res = await app.request('/api/admin/bookings/99999', {
      method: 'DELETE',
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(404)
  })

  test('sets deletedAt and second DELETE returns 404', async () => {
    const res1 = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'DELETE',
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res1.status).toBe(200)
    const j1 = await res1.json()
    expect(j1.data.id).toBe(bookingId)
    expect(typeof j1.data.deletedAt).toBe('string')

    const row = await testDb.select().from(bookings).where(eq(bookings.id, bookingId)).get()
    expect(row?.deletedAt).toBeInstanceOf(Date)

    const res2 = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'DELETE',
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res2.status).toBe(404)
  })

  test('GET list excludes soft-deleted from total and rows', async () => {
    await testDb.insert(bookings).values({
      name: 'Gone',
      email: 'gone@example.com',
      status: 'pending',
      deletedAt: new Date(),
    })

    const res = await app.request('/api/admin/bookings?limit=50&offset=0', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.total).toBe(1)
    expect(body.data.bookings).toHaveLength(1)
    expect(body.data.bookings[0].name).toBe('Lead')
  })

  test('PATCH returns 404 for soft-deleted booking', async () => {
    await testDb.update(bookings).set({ deletedAt: new Date() }).where(eq(bookings.id, bookingId))

    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'contacted' }),
    })
    expect(res.status).toBe(404)
    const body = await res.json()
    expect(body.error.code).toBe('NOT_FOUND')
  })

  test('POST resend-confirmation returns 404 for soft-deleted booking', async () => {
    await testDb.update(bookings).set({ deletedAt: new Date() }).where(eq(bookings.id, bookingId))

    const res = await app.request(`/api/admin/bookings/${bookingId}/resend-confirmation`, {
      method: 'POST',
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(404)
  })

  test('GET export counts exclude soft-deleted', async () => {
    await testDb.insert(bookings).values({
      name: 'Hidden',
      email: 'h@h.com',
      status: 'sent',
      deletedAt: new Date(),
    })

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
      expect(body.data.total).toBe(1)
      expect(body.data.bookings).toHaveLength(1)
      expect(body.data.bookings[0].name).toBe('Lead')
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })
})

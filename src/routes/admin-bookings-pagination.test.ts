/**
 * Admin bookings list + export pagination (real SQLite).
 */

import { Database } from 'bun:sqlite'
import { afterAll, beforeAll, beforeEach, describe, expect, mock, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { sql } from 'drizzle-orm'
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

describe('admin bookings list + export pagination', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>
  let app: typeof import('../index').app

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
    const base = new Date('2025-06-01T12:00:00Z').getTime()
    for (let i = 0; i < 5; i++) {
      await testDb.insert(bookings).values({
        name: `Band ${i}`,
        email: `b${i}@t.com`,
        status: 'pending',
        createdAt: new Date(base - i * 3_600_000),
      })
    }
  })

  afterAll(() => {
    setClerkClientForTesting(null)
    sqlite.close()
  })

  test('GET /api/admin/bookings returns page with total and hasMore', async () => {
    const res = await app.request('/api/admin/bookings?limit=2&offset=0', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.total).toBe(5)
    expect(body.data.bookings).toHaveLength(2)
    expect(body.data.bookings[0].name).toBe('Band 0')
    expect(body.data.limit).toBe(2)
    expect(body.data.offset).toBe(0)
    expect(body.data.hasMore).toBe(true)
  })

  test('GET /api/admin/bookings offset returns correct slice', async () => {
    const res = await app.request('/api/admin/bookings?limit=2&offset=4', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.bookings).toHaveLength(1)
    expect(body.data.bookings[0].name).toBe('Band 4')
    expect(body.data.hasMore).toBe(false)
  })

  test('GET /api/admin/bookings orders by lead priority (high first) then createdAt desc', async () => {
    await testDb.delete(bookings)
    const tOld = new Date('2024-01-01T12:00:00Z')
    const tNew = new Date('2025-06-15T12:00:00Z')
    await testDb.insert(bookings).values({
      name: 'LowRow',
      email: 'low@t.com',
      status: 'pending',
      leadPriority: 'low',
      createdAt: tNew,
    })
    await testDb.insert(bookings).values({
      name: 'HighOld',
      email: 'ho@t.com',
      status: 'pending',
      leadPriority: 'high',
      createdAt: tOld,
    })
    await testDb.insert(bookings).values({
      name: 'HighNew',
      email: 'hn@t.com',
      status: 'pending',
      leadPriority: 'high',
      createdAt: tNew,
    })
    await testDb.insert(bookings).values({
      name: 'MedRow',
      email: 'med@t.com',
      status: 'pending',
      leadPriority: 'medium',
      createdAt: tNew,
    })
    const res = await app.request('/api/admin/bookings?limit=10&offset=0', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.bookings.map((b: { name: string }) => b.name)).toEqual([
      'HighNew',
      'HighOld',
      'MedRow',
      'LowRow',
    ])
  })

  test('GET /api/admin/bookings 400 for negative offset', async () => {
    const res = await app.request('/api/admin/bookings?offset=-1', {
      headers: { Authorization: 'Bearer valid_token' },
    })
    expect(res.status).toBe(400)
    const body = await res.json()
    expect(body.error.code).toBe('VALIDATION_ERROR')
  })

  test('GET /api/admin/export/bookings truncates when rows exceed ADMIN_EXPORT_MAX_ROWS', async () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    const prevCap = process.env.ADMIN_EXPORT_MAX_ROWS
    try {
      process.env.NODE_ENV = 'development'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      process.env.ADMIN_EXPORT_MAX_ROWS = '3'
      const res = await app.request('/api/admin/export/bookings', {
        headers: { Authorization: 'Bearer valid_token' },
      })
      expect(res.status).toBe(200)
      const body = await res.json()
      expect(body.data.total).toBe(5)
      expect(body.data.bookings).toHaveLength(3)
      expect(body.data.returnedCount).toBe(3)
      expect(body.data.truncated).toBe(true)
      expect(body.data.totalInDb).toBe(5)
      expect(typeof body.data.warning).toBe('string')
      expect(body.data.last24hCount).toBe(0)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
      if (prevCap === undefined) delete process.env.ADMIN_EXPORT_MAX_ROWS
      else process.env.ADMIN_EXPORT_MAX_ROWS = prevCap
    }
  })

  test('GET /api/admin/export/bookings last24hCount from SQL', async () => {
    await testDb.delete(bookings)
    await testDb.insert(bookings).values({
      name: 'Old',
      email: 'old@t.com',
      status: 'pending',
      createdAt: sql`(unixepoch() - 90000)` as unknown as Date,
    })
    await testDb.insert(bookings).values({
      name: 'New',
      email: 'new@t.com',
      status: 'pending',
      createdAt: sql`(unixepoch() - 3600)` as unknown as Date,
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
      expect(body.data.total).toBe(2)
      expect(body.data.last24hCount).toBe(1)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })
})

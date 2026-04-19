/**
 * POST /api/admin/bookings/delete-all — hard delete all rows (real SQLite).
 */

import { Database } from 'bun:sqlite'
import { afterAll, beforeAll, beforeEach, describe, expect, mock, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { drizzle } from 'drizzle-orm/bun-sqlite'
import * as schema from '../db/schema'
import { bookings } from '../db/schema'
import { ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE } from '../lib/adminDeleteAllBookings'
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

describe('POST /api/admin/bookings/delete-all', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>
  let app: typeof import('../index').app
  const prevNode = process.env.NODE_ENV
  const prevFlag = process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS

  beforeAll(async () => {
    process.env.NODE_ENV = 'development'
    delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    sqlite = new Database(':memory:')
    applyDrizzleMigrations(sqlite)
    testDb = drizzle(sqlite, { schema })
    mock.module('../db', () => ({ db: testDb }))
    setClerkClientForTesting(mockClerkClient as never)
    ;({ app } = await import('../index'))
  })

  beforeEach(async () => {
    await testDb.delete(bookings)
  })

  afterAll(() => {
    setClerkClientForTesting(null)
    sqlite.close()
    process.env.NODE_ENV = prevNode
    if (prevFlag === undefined) delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    else process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = prevFlag
  })

  test('401 without token', async () => {
    const res = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirm: ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE }),
    })
    expect(res.status).toBe(401)
  })

  test('403 when gated off in production', async () => {
    process.env.NODE_ENV = 'production'
    delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    const res = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ confirm: ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE }),
    })
    expect(res.status).toBe(403)
    const body = await res.json()
    expect(body.error.code).toBe('ADMIN_DELETE_ALL_BOOKINGS_DISABLED')
    process.env.NODE_ENV = 'development'
  })

  test('400 when confirm missing or wrong', async () => {
    const resBad = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ confirm: 'WRONG' }),
    })
    expect(resBad.status).toBe(400)
    const resEmpty = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    })
    expect(resEmpty.status).toBe(400)
  })

  test('dryRun returns count without deleting', async () => {
    await testDb.insert(bookings).values({
      name: 'A',
      email: 'a@x.com',
      status: 'pending',
      pipelineStatus: 'new',
    })
    await testDb.insert(bookings).values({
      name: 'B',
      email: 'b@x.com',
      status: 'pending',
      pipelineStatus: 'new',
    })
    const res = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ dryRun: true }),
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data).toEqual({ dryRun: true, count: 2 })
    const rows = await testDb.select().from(bookings)
    expect(rows).toHaveLength(2)
  })

  test('happy path deletes all rows including soft-deleted', async () => {
    await testDb.insert(bookings).values({
      name: 'Live',
      email: 'l@x.com',
      status: 'pending',
      pipelineStatus: 'new',
    })
    await testDb.insert(bookings).values({
      name: 'Hidden',
      email: 'h@x.com',
      status: 'pending',
      pipelineStatus: 'new',
      deletedAt: new Date(),
    })
    const lines: string[] = []
    const origLog = console.log
    console.log = (...args: unknown[]) => {
      lines.push(args.map((a) => (typeof a === 'string' ? a : JSON.stringify(a))).join(' '))
    }
    try {
      const res = await app.request('/api/admin/bookings/delete-all', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer valid_token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ confirm: ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE }),
      })
      expect(res.status).toBe(200)
      const body = await res.json()
      expect(body.data.deletedCount).toBe(2)
      expect(body.data.dryRun).toBe(false)
    } finally {
      console.log = origLog
    }
    const rows = await testDb.select().from(bookings)
    expect(rows).toHaveLength(0)
    const auditLine = lines.find((l) => l.includes('admin_bookings_delete_all'))
    expect(auditLine).toBeDefined()
    const parsed = JSON.parse(auditLine!) as {
      type: string
      action: string
      deletedCount: number
      userId: string
    }
    expect(parsed.type).toBe('audit')
    expect(parsed.action).toBe('admin_bookings_delete_all')
    expect(parsed.deletedCount).toBe(2)
    expect(parsed.userId).toBe('user_123')
  })

  test('empty table returns deletedCount 0 and audit', async () => {
    const lines: string[] = []
    const origLog = console.log
    console.log = (...args: unknown[]) => {
      lines.push(args.map((a) => (typeof a === 'string' ? a : JSON.stringify(a))).join(' '))
    }
    try {
      const res = await app.request('/api/admin/bookings/delete-all', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer valid_token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ confirm: ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE }),
      })
      expect(res.status).toBe(200)
      const body = await res.json()
      expect(body.data.deletedCount).toBe(0)
    } finally {
      console.log = origLog
    }
    expect(lines.some((l) => l.includes('admin_bookings_delete_all'))).toBe(true)
  })

  test('production with ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true succeeds', async () => {
    process.env.NODE_ENV = 'production'
    process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = 'true'
    await testDb.insert(bookings).values({
      name: 'P',
      email: 'p@x.com',
      status: 'pending',
      pipelineStatus: 'new',
    })
    const res = await app.request('/api/admin/bookings/delete-all', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ confirm: ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE }),
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.deletedCount).toBe(1)
    process.env.NODE_ENV = 'development'
    delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
  })
})

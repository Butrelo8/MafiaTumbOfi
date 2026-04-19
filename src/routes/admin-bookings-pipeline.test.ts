/**
 * PATCH /api/admin/bookings/:id — pipeline_status (real SQLite).
 */

import { Database } from 'bun:sqlite'
import { afterAll, beforeAll, beforeEach, describe, expect, mock, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { eq, sql } from 'drizzle-orm'
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

describe('PATCH /api/admin/bookings/:id pipeline', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>
  let app: typeof import('../index').app
  /** SQLite AUTOINCREMENT does not reset after DELETE; never assume id === 1. */
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
        status: 'sent',
        pipelineStatus: 'new',
        createdAt: sql`(unixepoch())` as unknown as Date,
      })
      .returning({ id: bookings.id })
    bookingId = row?.id ?? 1
  })

  afterAll(() => {
    setClerkClientForTesting(null)
    sqlite.close()
  })

  test('returns 401 without token', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pipelineStatus: 'contacted' }),
    })
    expect(res.status).toBe(401)
  })

  test('returns 400 for invalid JSON', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: 'not-json',
    })
    expect(res.status).toBe(400)
    const body = await res.json()
    expect(body.error.code).toBe('INVALID_JSON')
  })

  test('returns 400 for invalid pipelineStatus', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'won' }),
    })
    expect(res.status).toBe(400)
    const body = await res.json()
    expect(body.error.code).toBe('VALIDATION_ERROR')
  })

  test('returns 404 when booking missing', async () => {
    await testDb.delete(bookings)
    const res = await app.request('/api/admin/bookings/99', {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'contacted' }),
    })
    expect(res.status).toBe(404)
  })

  test('returns 200 and persists pipelineStatus', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'contacted' }),
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.id).toBe(bookingId)
    expect(body.data.pipelineStatus).toBe('contacted')
    const row = await testDb.select().from(bookings).where(eq(bookings.id, bookingId)).get()
    expect(row?.pipelineStatus).toBe('contacted')
  })

  test('can set back to new', async () => {
    await testDb
      .update(bookings)
      .set({ pipelineStatus: 'closed' })
      .where(eq(bookings.id, bookingId))
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'new' }),
    })
    expect(res.status).toBe(200)
    const row = await testDb.select().from(bookings).where(eq(bookings.id, bookingId)).get()
    expect(row?.pipelineStatus).toBe('new')
  })

  test('returns 400 for invalid booking id on PATCH', async () => {
    const res = await app.request('/api/admin/bookings/0', {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pipelineStatus: 'contacted' }),
    })
    expect(res.status).toBe(400)
  })

  test('returns 400 when body omits both pipelineStatus and internalNotes', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    })
    expect(res.status).toBe(400)
  })

  test('returns 200 and persists internalNotes', async () => {
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ internalNotes: 'Nota interna' }),
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.data.internalNotes).toBe('Nota interna')
    const row = await testDb.select().from(bookings).where(eq(bookings.id, bookingId)).get()
    expect(row?.internalNotes).toBe('Nota interna')
  })

  test('clears internalNotes with null', async () => {
    await testDb
      .update(bookings)
      .set({ internalNotes: 'temp' })
      .where(eq(bookings.id, bookingId))
    const res = await app.request(`/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        Authorization: 'Bearer valid_token',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ internalNotes: null }),
    })
    expect(res.status).toBe(200)
    const row = await testDb.select().from(bookings).where(eq(bookings.id, bookingId)).get()
    expect(row?.internalNotes).toBeNull()
  })
})

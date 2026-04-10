/**
 * Integration tests for getOrCreateUser (real SQLite + Clerk mock).
 */
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'
import { Database } from 'bun:sqlite'
import { drizzle } from 'drizzle-orm/bun-sqlite'
import { eq } from 'drizzle-orm'
import * as schema from '../db/schema'
import { users } from '../db/schema'
import { setClerkClientForTesting } from '../middleware/auth'
import { getOrCreateUser } from './users'

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
        const isIdempotent =
          msg.includes('already exists') || msg.includes('duplicate column name')
        if (!isIdempotent) throw e
      }
    }
  }
}

function mockClerkForUserIds() {
  return {
    users: {
      getUser: async (userId: string) => ({
        id: userId,
        primaryEmailAddress: {
          emailAddress: `person-${userId.replace(/[^a-zA-Z0-9_-]/g, '_')}@test.invalid`,
        },
        emailAddresses: [] as [],
        firstName: 'Test',
        lastName: userId,
      }),
    },
  }
}

describe('getOrCreateUser', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>

  beforeEach(() => {
    sqlite = new Database(':memory:')
    applyDrizzleMigrations(sqlite)
    testDb = drizzle(sqlite, { schema })
    setClerkClientForTesting(mockClerkForUserIds() as never)
  })

  afterEach(() => {
    setClerkClientForTesting(null)
    sqlite.close()
  })

  test('first new user becomes admin on empty database', async () => {
    const row = await getOrCreateUser('clerk_first', { db: testDb })
    expect(row.clerkId).toBe('clerk_first')
    expect(row.isAdmin).toBe(true)
  })

  test('second new user is not admin when an admin already exists', async () => {
    await getOrCreateUser('clerk_admin', { db: testDb })
    const row = await getOrCreateUser('clerk_member', { db: testDb })
    expect(row.isAdmin).toBe(false)
  })

  test('updatedAt advances on update when column is omitted from set()', async () => {
    const row = await getOrCreateUser('clerk_update_ts', { db: testDb })
    const createdMs = row.createdAt?.getTime() ?? 0
    const updatedBeforeMs = row.updatedAt?.getTime() ?? 0
    expect(updatedBeforeMs).toBeGreaterThanOrEqual(createdMs)

    // SQLite `integer` + `mode: 'timestamp'` stores epoch seconds; same wall-clock second => same value.
    await new Promise((r) => setTimeout(r, 1100))

    await testDb
      .update(users)
      .set({ name: 'Renamed' })
      .where(eq(users.clerkId, 'clerk_update_ts'))

    const [after] = await testDb
      .select()
      .from(users)
      .where(eq(users.clerkId, 'clerk_update_ts'))

    expect(after?.name).toBe('Renamed')
    expect(after?.updatedAt?.getTime() ?? 0).toBeGreaterThan(updatedBeforeMs)
    expect(after?.createdAt?.getTime()).toBe(createdMs)
  })

  test('concurrent first signups leave exactly one admin', async () => {
    const [a, b] = await Promise.all([
      getOrCreateUser('clerk_parallel_a', { db: testDb }),
      getOrCreateUser('clerk_parallel_b', { db: testDb }),
    ])
    expect(a.clerkId).not.toBe(b.clerkId)

    const admins = await testDb
      .select({ id: users.id })
      .from(users)
      .where(eq(users.isAdmin, true))
    expect(admins).toHaveLength(1)

    const adminIds = new Set(admins.map((r) => r.id))
    const winnerIsAdmin =
      (a.isAdmin && adminIds.has(a.id)) || (b.isAdmin && adminIds.has(b.id))
    expect(winnerIsAdmin).toBe(true)
    expect(a.isAdmin !== b.isAdmin).toBe(true)
  })
})

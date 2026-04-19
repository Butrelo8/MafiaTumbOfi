/**
 * Integration tests for getOrCreateUser (real SQLite + Clerk mock).
 */

import { Database } from 'bun:sqlite'
import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { eq } from 'drizzle-orm'
import { drizzle } from 'drizzle-orm/bun-sqlite'
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
        const isIdempotent = msg.includes('already exists') || msg.includes('duplicate column name')
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
  let prevAdmin: string | undefined

  beforeEach(() => {
    prevAdmin = process.env.ADMIN_CLERK_ID
    process.env.ADMIN_CLERK_ID = 'clerk_authoritative'
    sqlite = new Database(':memory:')
    applyDrizzleMigrations(sqlite)
    testDb = drizzle(sqlite, { schema })
    setClerkClientForTesting(mockClerkForUserIds() as never)
  })

  afterEach(() => {
    if (prevAdmin === undefined) delete process.env.ADMIN_CLERK_ID
    else process.env.ADMIN_CLERK_ID = prevAdmin
    setClerkClientForTesting(null)
    sqlite.close()
  })

  test('user whose clerk id matches ADMIN_CLERK_ID becomes admin on insert', async () => {
    const row = await getOrCreateUser('clerk_authoritative', { db: testDb })
    expect(row.clerkId).toBe('clerk_authoritative')
    expect(row.isAdmin).toBe(true)
  })

  test('user whose clerk id does not match ADMIN_CLERK_ID is not admin on insert', async () => {
    await getOrCreateUser('clerk_authoritative', { db: testDb })
    const row = await getOrCreateUser('clerk_member', { db: testDb })
    expect(row.isAdmin).toBe(false)
  })

  test('when ADMIN_CLERK_ID unset, new user is never admin', async () => {
    delete process.env.ADMIN_CLERK_ID
    const row = await getOrCreateUser('clerk_noenv', { db: testDb })
    expect(row.isAdmin).toBe(false)
  })

  test('reconciles existing row to admin when ADMIN_CLERK_ID matches', async () => {
    await testDb.insert(users).values({
      clerkId: 'clerk_rec',
      email: 'rec@test.invalid',
      name: 'X',
      isAdmin: false,
    })
    process.env.ADMIN_CLERK_ID = 'clerk_rec'
    const row = await getOrCreateUser('clerk_rec', { db: testDb })
    expect(row.isAdmin).toBe(true)
  })

  test('reconciles existing admin row to non-admin when ADMIN_CLERK_ID does not match', async () => {
    await testDb.insert(users).values({
      clerkId: 'clerk_old_admin',
      email: 'old@test.invalid',
      name: 'Old',
      isAdmin: true,
    })
    process.env.ADMIN_CLERK_ID = 'clerk_authoritative'
    const row = await getOrCreateUser('clerk_old_admin', { db: testDb })
    expect(row.isAdmin).toBe(false)
  })

  test('updatedAt advances on update when column is omitted from set()', async () => {
    const row = await getOrCreateUser('clerk_update_ts', { db: testDb })
    const createdMs = row.createdAt?.getTime() ?? 0
    const updatedBeforeMs = row.updatedAt?.getTime() ?? 0
    expect(updatedBeforeMs).toBeGreaterThanOrEqual(createdMs)

    // SQLite `integer` + `mode: 'timestamp'` stores epoch seconds; same wall-clock second => same value.
    await new Promise((r) => setTimeout(r, 1100))

    await testDb.update(users).set({ name: 'Renamed' }).where(eq(users.clerkId, 'clerk_update_ts'))

    const [after] = await testDb.select().from(users).where(eq(users.clerkId, 'clerk_update_ts'))

    expect(after?.name).toBe('Renamed')
    expect(after?.updatedAt?.getTime() ?? 0).toBeGreaterThan(updatedBeforeMs)
    expect(after?.createdAt?.getTime()).toBe(createdMs)
  })

  test('concurrent signups: only clerk id matching ADMIN_CLERK_ID ends admin', async () => {
    process.env.ADMIN_CLERK_ID = 'clerk_parallel_a'
    const [a, b] = await Promise.all([
      getOrCreateUser('clerk_parallel_a', { db: testDb }),
      getOrCreateUser('clerk_parallel_b', { db: testDb }),
    ])
    expect(a.clerkId).not.toBe(b.clerkId)
    expect(a.isAdmin).toBe(true)
    expect(b.isAdmin).toBe(false)
    const admins = await testDb.select({ id: users.id }).from(users).where(eq(users.isAdmin, true))
    expect(admins).toHaveLength(1)
  })
})

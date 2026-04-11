/**
 * Drip processor — real SQLite (in-memory) + mocked Resend.
 */

import { Database } from 'bun:sqlite'
import { afterAll, beforeAll, beforeEach, describe, expect, mock, test } from 'bun:test'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { eq } from 'drizzle-orm'
import { drizzle } from 'drizzle-orm/bun-sqlite'
import type { Resend } from 'resend'
import * as schema from '../db/schema'
import { bookings } from '../db/schema'
import { setResendForTesting } from './resend'

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

describe('processDripEmails', () => {
  let sqlite: Database
  let testDb: ReturnType<typeof drizzle<typeof schema>>
  let processDripEmails: typeof import('./dripProcessor').processDripEmails

  beforeAll(async () => {
    sqlite = new Database(':memory:')
    applyDrizzleMigrations(sqlite)
    testDb = drizzle(sqlite, { schema })
    mock.module('../db', () => ({ db: testDb }))
    ;({ processDripEmails } = await import('./dripProcessor'))
  })

  beforeEach(async () => {
    setResendForTesting(null)
    await testDb.delete(bookings)
  })

  afterAll(() => {
    setResendForTesting(null)
    sqlite.close()
  })

  test('empty table returns zeros', async () => {
    setResendForTesting({
      emails: { send: async () => ({ data: { id: 'x' }, error: null }) },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2099-01-01') })
    expect(r).toEqual({ email2Sent: 0, email3Sent: 0, errors: 0 })
  })

  test('skips bookings when status is not sent', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'A',
      email: 'a@b.com',
      status: 'pending',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: new Date('2020-01-03'),
    })
    let sends = 0
    setResendForTesting({
      emails: {
        send: async () => {
          sends += 1
          return { data: { id: 'x' }, error: null }
        },
      },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.email2Sent).toBe(0)
    expect(sends).toBe(0)
  })

  test('sends Email 2 and sets drip2SentAt', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'B',
      email: 'b@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: new Date('2099-01-01'),
    })
    const [row] = await testDb.select({ id: bookings.id }).from(bookings)
    setResendForTesting({
      emails: { send: async () => ({ data: { id: 'ok' }, error: null }) },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.email2Sent).toBe(1)
    expect(r.errors).toBe(0)
    const updated = await testDb.select().from(bookings).where(eq(bookings.id, row!.id)).get()
    expect(updated?.drip2SentAt).toBeInstanceOf(Date)
  })

  test('idempotent: second run does not resend Email 2', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'C',
      email: 'c@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: new Date('2099-01-01'),
    })
    let sends = 0
    setResendForTesting({
      emails: {
        send: async () => {
          sends += 1
          return { data: { id: 'ok' }, error: null }
        },
      },
    } as Resend)
    const now = new Date('2025-01-01')
    await processDripEmails({ now })
    const firstSends = sends
    const r2 = await processDripEmails({ now })
    expect(firstSends).toBe(1)
    expect(r2.email2Sent).toBe(0)
    expect(sends).toBe(1)
  })

  test('when both stages due, same run sends Email 2 then Email 3', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'D',
      email: 'd@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: past,
    })
    let sends = 0
    setResendForTesting({
      emails: {
        send: async () => {
          sends += 1
          return { data: { id: 'ok' }, error: null }
        },
      },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.email2Sent).toBe(1)
    expect(r.email3Sent).toBe(1)
    expect(sends).toBe(2)
    const row = await testDb.select().from(bookings).get()
    expect(row?.drip2SentAt).toBeInstanceOf(Date)
    expect(row?.drip3SentAt).toBeInstanceOf(Date)
  })

  test('Email 3 not sent when Email 2 never sent (drip2SentAt null)', async () => {
    const past = new Date('2020-01-01')
    const future = new Date('2099-01-01')
    await testDb.insert(bookings).values({
      name: 'G',
      email: 'g@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: future,
      drip3DueAt: past,
    })
    let sends = 0
    setResendForTesting({
      emails: {
        send: async () => {
          sends += 1
          return { data: { id: 'ok' }, error: null }
        },
      },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.email2Sent).toBe(0)
    expect(r.email3Sent).toBe(0)
    expect(sends).toBe(0)
  })

  test('Resend error does not set drip2SentAt and counts errors', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'E',
      email: 'e@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: new Date('2099-01-01'),
    })
    setResendForTesting({
      emails: {
        send: async () => ({ data: null, error: { message: 'fail', name: 'ApiError' } }),
      },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.email2Sent).toBe(0)
    expect(r.errors).toBe(1)
    const row = await testDb.select().from(bookings).get()
    expect(row?.drip2SentAt).toBeNull()
  })

  test('Resend throw does not set drip2SentAt', async () => {
    const past = new Date('2020-01-01')
    await testDb.insert(bookings).values({
      name: 'F',
      email: 'f@b.com',
      status: 'sent',
      pipelineStatus: 'new',
      drip2DueAt: past,
      drip3DueAt: new Date('2099-01-01'),
    })
    setResendForTesting({
      emails: {
        send: async () => {
          throw new Error('network down')
        },
      },
    } as Resend)
    const r = await processDripEmails({ now: new Date('2025-01-01') })
    expect(r.errors).toBe(1)
    const row = await testDb.select().from(bookings).get()
    expect(row?.drip2SentAt).toBeNull()
  })
})

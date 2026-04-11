import { eq } from 'drizzle-orm'
import { db } from '../db'
import { users } from '../db/schema'
import { getClerkClient } from '../middleware/auth'
import { clerkIdIsConfiguredAdmin, getConfiguredAdminClerkId } from './adminClerkConfig'

export type UserRow = typeof users.$inferSelect

async function reconcileAdminWithEnv(database: typeof db, row: UserRow): Promise<UserRow> {
  if (getConfiguredAdminClerkId() === null) return row
  const expected = clerkIdIsConfiguredAdmin(row.clerkId)
  if (row.isAdmin === expected) return row
  await database.update(users).set({ isAdmin: expected }).where(eq(users.clerkId, row.clerkId))
  const updated = await database.select().from(users).where(eq(users.clerkId, row.clerkId)).get()
  if (!updated) throw new Error('User row missing after admin flag sync')
  return updated
}

export type GetOrCreateUserOptions = {
  /**
   * Tests: pass an isolated DB (e.g. :memory:) so integration tests do not use the app file DB.
   */
  db?: typeof db
}

/**
 * Get user by Clerk ID from DB, or create. Admin flag: `ADMIN_CLERK_ID` env (trimmed) must match
 * `clerkId` for `is_admin` true on insert; when env is set, existing rows are reconciled on read.
 * Used by admin routes and /me.
 */
export async function getOrCreateUser(
  clerkId: string,
  options?: GetOrCreateUserOptions,
): Promise<UserRow> {
  const database = options?.db ?? db
  const existing = await database.select().from(users).where(eq(users.clerkId, clerkId)).get()

  if (existing) return reconcileAdminWithEnv(database, existing)

  const clerkClient = getClerkClient()
  const clerkUser = await clerkClient.users.getUser(clerkId)
  const primaryEmail = clerkUser.primaryEmailAddress ?? clerkUser.emailAddresses?.[0]
  const email = primaryEmail?.emailAddress ?? `${clerkId}@clerk.placeholder`
  const name = [clerkUser.firstName, clerkUser.lastName].filter(Boolean).join(' ') || null

  const [inserted] = await database
    .insert(users)
    .values({
      clerkId,
      email,
      name,
      isAdmin: clerkIdIsConfiguredAdmin(clerkId),
    })
    .returning()

  if (!inserted) throw new Error('Failed to create user')
  return inserted
}

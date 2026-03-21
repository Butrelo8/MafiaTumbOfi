import { eq, sql } from 'drizzle-orm'
import { db } from '../db'
import { users } from '../db/schema'
import { getClerkClient } from '../middleware/auth'

export type UserRow = typeof users.$inferSelect

/** First bootstrap admin: single-statement check + insert avoids count-then-insert races. */
const firstBootstrapAdminIsAdmin = sql`(SELECT CASE WHEN EXISTS (SELECT 1 FROM ${users} WHERE ${users.isAdmin} = 1) THEN 0 ELSE 1 END)`

export type GetOrCreateUserOptions = {
  /**
   * Tests: pass an isolated DB (e.g. :memory:) so integration tests do not use the app file DB.
   */
  db?: typeof db
}

/**
 * Get user by Clerk ID from DB, or create with first-user-is-admin logic.
 * Fetches email/name from Clerk when creating. Used by admin routes and /me.
 */
export async function getOrCreateUser(
  clerkId: string,
  options?: GetOrCreateUserOptions,
): Promise<UserRow> {
  const database = options?.db ?? db
  const existing = await database
    .select()
    .from(users)
    .where(eq(users.clerkId, clerkId))
    .get()

  if (existing) return existing

  const clerkClient = getClerkClient()
  const clerkUser = await clerkClient.users.getUser(clerkId)
  const primaryEmail = clerkUser.primaryEmailAddress ?? clerkUser.emailAddresses?.[0]
  const email = primaryEmail?.emailAddress ?? `${clerkId}@clerk.placeholder`
  const name =
    [clerkUser.firstName, clerkUser.lastName].filter(Boolean).join(' ') || null

  const [inserted] = await database
    .insert(users)
    .values({
      clerkId,
      email,
      name,
      isAdmin: firstBootstrapAdminIsAdmin,
    })
    .returning()

  if (!inserted) throw new Error('Failed to create user')
  return inserted
}

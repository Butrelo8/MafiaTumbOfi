import { eq } from 'drizzle-orm'
import { db } from '../db'
import { users } from '../db/schema'
import { getClerkClient } from '../middleware/auth'

export type UserRow = typeof users.$inferSelect

/**
 * Get user by Clerk ID from DB, or create with first-user-is-admin logic.
 * Fetches email/name from Clerk when creating. Used by admin routes and /me.
 */
export async function getOrCreateUser(clerkId: string): Promise<UserRow> {
  const existing = await db
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

  const adminUsers = await db
    .select({ id: users.id })
    .from(users)
    .where(eq(users.isAdmin, true))
  const isFirstUser = adminUsers.length === 0

  const [inserted] = await db
    .insert(users)
    .values({
      clerkId,
      email,
      name,
      isAdmin: isFirstUser,
    })
    .returning()

  if (!inserted) throw new Error('Failed to create user')
  return inserted
}

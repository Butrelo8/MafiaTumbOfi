/**
 * Single Clerk user id (`sub` in session JWT) that may have admin in this deployment.
 * Set `ADMIN_CLERK_ID` on the API; unset/empty disables env-based admin (inserts never auto-admin).
 */
export function getConfiguredAdminClerkId(): string | null {
  const raw = process.env.ADMIN_CLERK_ID
  if (raw === undefined || raw === null) return null
  const v = raw.trim()
  return v.length > 0 ? v : null
}

export function clerkIdIsConfiguredAdmin(clerkId: string): boolean {
  const admin = getConfiguredAdminClerkId()
  return admin !== null && admin === clerkId
}

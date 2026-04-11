import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'
import { logServerError } from '../lib/safeLog'
import { getOrCreateUser } from '../lib/users'

/**
 * Requires authMiddleware to have run first (userId set).
 * Ensures user exists in DB (first user becomes admin), then requires isAdmin for access.
 */
export async function adminAuth(c: Context, next: Next) {
  const userId = c.get('userId')
  if (!userId) {
    return errorResponse(c, 401, 'UNAUTHORIZED', 'Authentication required')
  }

  try {
    const user = await getOrCreateUser(userId)
    if (!user.isAdmin) {
      return errorResponse(c, 403, 'FORBIDDEN', 'Admin access required')
    }
    c.set('user', user)
    return await next()
  } catch (err) {
    logServerError('adminAuth', 'GET_OR_CREATE_FAILED', err)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to verify admin access')
  }
}

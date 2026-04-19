import { Hono } from 'hono'
import { errorResponse, successResponse } from '../lib/errors'
import { logServerError } from '../lib/safeLog'
import { getOrCreateUser } from '../lib/users'
import { authMiddleware } from '../middleware/auth'

export const usersRoutes = new Hono()

usersRoutes.use('*', authMiddleware)

usersRoutes.get('/me', async (c) => {
  const userId = c.get('userId')

  try {
    const user = await getOrCreateUser(userId)
    return successResponse(c, user)
  } catch (error) {
    logServerError('users', 'FETCH_ME_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to fetch user')
  }
})

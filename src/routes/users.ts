import { Hono } from 'hono'
import { authMiddleware } from '../middleware/auth'
import { errorResponse } from '../lib/errors'
import { getOrCreateUser } from '../lib/users'
import { logServerError } from '../lib/safeLog'

export const usersRoutes = new Hono()

usersRoutes.use('*', authMiddleware)

usersRoutes.get('/me', async (c) => {
  const userId = c.get('userId')

  try {
    const user = await getOrCreateUser(userId)
    return c.json({ data: user })
  } catch (error) {
    logServerError('users', 'FETCH_ME_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to fetch user')
  }
})

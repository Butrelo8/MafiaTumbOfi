import { Hono } from 'hono'
import { errorResponse } from '../lib/errors'
import { rateLimitAuth } from '../middleware/rateLimitAuth'

export const authRoutes = new Hono()

authRoutes.use('*', rateLimitAuth)
authRoutes.post('/login', async (c) => {
  // TODO: implement login
  return errorResponse(c, 501, 'NOT_IMPLEMENTED', 'Login not implemented yet')
})

authRoutes.post('/logout', async (c) => {
  // TODO: implement logout
  return errorResponse(c, 501, 'NOT_IMPLEMENTED', 'Logout not implemented yet')
})

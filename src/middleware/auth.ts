import { createClerkClient } from '@clerk/backend'
import type { Context, Next } from 'hono'
import { allowedOrigins } from '../lib/allowedOrigins'
import { errorResponse } from '../lib/errors'

let clerkClientOverride: Awaited<ReturnType<typeof createClerkClient>> | null = null

/** Only for tests: inject a mock Clerk client so tests don't need real keys. */
export function setClerkClientForTesting(
  client: Awaited<ReturnType<typeof createClerkClient>> | null,
) {
  clerkClientOverride = client
}

export function getClerkClient() {
  if (clerkClientOverride) return clerkClientOverride
  return createClerkClient({
    secretKey: process.env.CLERK_SECRET_KEY,
    publishableKey: process.env.CLERK_PUBLISHABLE_KEY ?? process.env.PUBLIC_CLERK_PUBLISHABLE_KEY,
  })
}

export const authMiddleware = async (c: Context, next: Next) => {
  const { isAuthenticated, toAuth } = await getClerkClient().authenticateRequest(c.req.raw, {
    authorizedParties: allowedOrigins,
  })

  if (!isAuthenticated) {
    return errorResponse(c, 401, 'UNAUTHORIZED', 'Authentication required')
  }

  const auth = toAuth()
  c.set('userId', auth.userId)
  c.set('sessionId', auth.sessionId)

  return await next()
}

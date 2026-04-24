import { createClerkClient } from '@clerk/backend'
import type { Context, Next } from 'hono'
import { clerkAuthorizedParties } from '../lib/allowedOrigins'
import { errorResponse } from '../lib/errors'

let clerkClientOverride: Awaited<ReturnType<typeof createClerkClient>> | null = null

/** Only for tests: inject a mock Clerk client so tests don't need real keys. */
export function setClerkClientForTesting(
  client: Awaited<ReturnType<typeof createClerkClient>> | null,
) {
  clerkClientOverride = client
}

function clerkPublishableKeyFromEnv(): string | undefined {
  const fromPk = process.env.CLERK_PUBLISHABLE_KEY?.trim()
  if (fromPk) return fromPk
  return process.env.PUBLIC_CLERK_PUBLISHABLE_KEY?.trim() || undefined
}

export function getClerkClient() {
  if (clerkClientOverride) return clerkClientOverride
  const secretKey = process.env.CLERK_SECRET_KEY?.trim()
  const publishableKey = clerkPublishableKeyFromEnv()
  if (secretKey && !publishableKey) {
    throw new Error(
      'Clerk publishable key is missing on the API. Set CLERK_PUBLISHABLE_KEY (or PUBLIC_CLERK_PUBLISHABLE_KEY) in the root .env — use the same publishable key as web/.env PUBLIC_CLERK_PUBLISHABLE_KEY. See .env.example.',
    )
  }
  return createClerkClient({
    secretKey,
    publishableKey,
  })
}

export const authMiddleware = async (c: Context, next: Next) => {
  const { isAuthenticated, toAuth } = await getClerkClient().authenticateRequest(c.req.raw, {
    authorizedParties: clerkAuthorizedParties,
  })

  if (!isAuthenticated) {
    return errorResponse(c, 401, 'UNAUTHORIZED', 'Authentication required')
  }

  const auth = toAuth()
  c.set('userId', auth.userId)
  c.set('sessionId', auth.sessionId)

  return await next()
}

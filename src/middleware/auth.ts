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
    // #region agent log
    try {
      const path = new URL(c.req.url).pathname
      if (path.startsWith('/api/admin')) {
        const partyHosts = allowedOrigins.map((o) => {
          try {
            return new URL(o).hostname
          } catch {
            return 'invalid'
          }
        })
        const __body = JSON.stringify({
          sessionId: '0436d5',
          location: 'auth.ts:authenticateRequest',
          message: 'API rejected session',
          data: { path, partyHosts, hypothesisId: 'H3' },
          timestamp: Date.now(),
          runId: 'pre-fix',
        })
        console.warn('[agent-debug]', __body)
        fetch('http://127.0.0.1:7813/ingest/b731065b-0a2c-4578-8e8d-91a4a7063b54',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'0436d5'},body:__body}).catch(()=>{})
      }
    } catch {
      /* ignore */
    }
    // #endregion
    return errorResponse(c, 401, 'UNAUTHORIZED', 'Authentication required')
  }

  const auth = toAuth()
  c.set('userId', auth.userId)
  c.set('sessionId', auth.sessionId)

  return await next()
}

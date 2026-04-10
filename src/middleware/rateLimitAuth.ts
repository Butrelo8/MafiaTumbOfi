import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'
import { getClientId } from './getClientId'
import { createRateLimiter } from './rateLimitFactory'

const WINDOW_MS = 5 * 60 * 1000 // 5 minutes
const MAX_REQUESTS = 10

const limiter = createRateLimiter(WINDOW_MS, MAX_REQUESTS)

/**
 * Rate limiter for auth endpoints: max MAX_REQUESTS per WINDOW_MS per client ID.
 */
export async function rateLimitAuth(c: Context, next: Next) {
  const { allowed } = limiter.check(getClientId(c))

  if (!allowed) {
    return errorResponse(
      c,
      429,
      'RATE_LIMITED',
      'Demasiadas solicitudes. Espera un momento antes de intentar de nuevo.',
    )
  }

  await next()
}

import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'
import { getClientId } from './getClientId'
import { createRateLimiter } from './rateLimitFactory'

/** Light protection for synthetic monitoring / trivial abuse of GET /health */
const WINDOW_MS = 60 * 1000
const MAX_REQUESTS = 120

const limiter = createRateLimiter(WINDOW_MS, MAX_REQUESTS)

export async function rateLimitHealth(c: Context, next: Next) {
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

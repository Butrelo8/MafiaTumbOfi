import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'
import { getClientId } from './getClientId'
import { createRateLimiter } from './rateLimitFactory'

const WINDOW_MS = 60 * 1000 // 1 minute
const MAX_REQUESTS = 5

const limiter = createRateLimiter(WINDOW_MS, MAX_REQUESTS)

/**
 * In-memory rate limiter: max MAX_REQUESTS per WINDOW_MS per client ID.
 * Use only on the booking route; not applied globally.
 */
export async function rateLimitBooking(c: Context, next: Next) {
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

export { getClientId } from './getClientId'

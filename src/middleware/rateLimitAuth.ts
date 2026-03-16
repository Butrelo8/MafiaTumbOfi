import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'

const WINDOW_MS = 5 * 60 * 1000 // 5 minutes
const MAX_REQUESTS = 10

interface WindowState {
  count: number
  resetAt: number
}

const store = new Map<string, WindowState>()

const CLEANUP_INTERVAL = 5 * 60 * 1000 // 5 min

setInterval(() => {
  const now = Date.now()
  for (const [key, state] of store.entries()) {
    if (now >= state.resetAt) store.delete(key)
  }
}, CLEANUP_INTERVAL).unref()

function getClientId(c: Context): string {
  const forwarded = c.req.header('x-forwarded-for')
  if (forwarded) {
    return forwarded.split(',')[0]?.trim() ?? 'unknown'
  }
  const realIp = c.req.header('x-real-ip')
  if (realIp) return realIp
  return 'unknown'
}

/**
 * Rate limiter for auth endpoints: max MAX_REQUESTS per WINDOW_MS per client ID.
 */
export async function rateLimitAuth(c: Context, next: Next) {
  const id = getClientId(c)
  const now = Date.now()
  let state = store.get(id)

  if (!state || now >= state.resetAt) {
    state = { count: 0, resetAt: now + WINDOW_MS }
    store.set(id, state)
  }

  state.count += 1

  if (state.count > MAX_REQUESTS) {
    return errorResponse(
      c,
      429,
      'RATE_LIMITED',
      'Demasiadas solicitudes. Espera un momento antes de intentar de nuevo.',
    )
  }

  await next()
}

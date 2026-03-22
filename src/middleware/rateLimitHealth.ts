import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'
import { getClientId } from './rateLimit'

/** Light protection for synthetic monitoring / trivial abuse of GET /health */
const WINDOW_MS = 60 * 1000
const MAX_REQUESTS = 120

interface WindowState {
  count: number
  resetAt: number
}

const store = new Map<string, WindowState>()

const CLEANUP_INTERVAL = 5 * 60 * 1000

setInterval(() => {
  const now = Date.now()
  for (const [key, state] of store.entries()) {
    if (now >= state.resetAt) store.delete(key)
  }
}, CLEANUP_INTERVAL).unref()

export async function rateLimitHealth(c: Context, next: Next) {
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

/**
 * In-memory fixed-window rate limiter (per client id).
 * Same semantics as the pre-refactor Map + resetAt logic: count resets when now >= resetAt.
 */

export interface RateLimitStore {
  check(clientId: string): { allowed: boolean; remaining: number }
  /** Clears state and the cleanup timer (for tests / shutdown). */
  destroy(): void
}

interface WindowState {
  count: number
  resetAt: number
}

const CLEANUP_INTERVAL_MS = 5 * 60 * 1000

export function createRateLimiter(windowMs: number, max: number): RateLimitStore {
  const store = new Map<string, WindowState>()

  const interval = setInterval(() => {
    const now = Date.now()
    for (const [key, state] of store.entries()) {
      if (now >= state.resetAt) store.delete(key)
    }
  }, CLEANUP_INTERVAL_MS)

  if (typeof interval.unref === 'function') {
    interval.unref()
  }

  return {
    check(clientId: string) {
      const now = Date.now()
      let state = store.get(clientId)

      if (!state || now >= state.resetAt) {
        state = { count: 0, resetAt: now + windowMs }
        store.set(clientId, state)
      }

      state.count += 1

      const allowed = state.count <= max
      const remaining = Math.max(0, max - state.count)
      return { allowed, remaining }
    },
    destroy() {
      clearInterval(interval)
      store.clear()
    },
  }
}

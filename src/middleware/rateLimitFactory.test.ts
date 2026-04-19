import { describe, expect, test } from 'bun:test'
import { createRateLimiter } from './rateLimitFactory'

describe('createRateLimiter', () => {
  test('allows up to max requests per client then rejects', () => {
    const limiter = createRateLimiter(60_000, 3)
    try {
      const r1 = limiter.check('a')
      expect(r1.allowed).toBe(true)
      expect(r1.remaining).toBe(2)
      expect(limiter.check('a').allowed).toBe(true)
      expect(limiter.check('a').allowed).toBe(true)
      const r4 = limiter.check('a')
      expect(r4.allowed).toBe(false)
      expect(r4.remaining).toBe(0)
    } finally {
      limiter.destroy()
    }
  })

  test('isolates buckets per client id', () => {
    const limiter = createRateLimiter(60_000, 1)
    try {
      expect(limiter.check('x').allowed).toBe(true)
      expect(limiter.check('x').allowed).toBe(false)
      expect(limiter.check('y').allowed).toBe(true)
    } finally {
      limiter.destroy()
    }
  })
})

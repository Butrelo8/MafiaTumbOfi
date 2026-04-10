import type { Context } from 'hono'

/**
 * Client key for in-memory rate limits: first hop in `x-forwarded-for`, else `x-real-ip`, else `unknown`.
 *
 * **Production (e.g. Render):** Reverse proxy sets `x-forwarded-for`; only trust this behind a proxy that does not honor client-forged XFF.
 *
 * **Local dev (direct Bun):** Headers are often absent → every client maps to `unknown` and shares one bucket. That is intentional for a single dev machine; do not be surprised if local load tests hit the limit quickly.
 */
export function getClientId(c: Context): string {
  const forwarded = c.req.header('x-forwarded-for')
  if (forwarded) {
    return forwarded.split(',')[0]?.trim() ?? 'unknown'
  }
  const realIp = c.req.header('x-real-ip')
  if (realIp) {
    return realIp
  }
  return 'unknown'
}

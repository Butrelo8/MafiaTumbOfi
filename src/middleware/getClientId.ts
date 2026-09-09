import type { Context } from 'hono'

/**
 * Client key for in-memory rate limits: rightmost hop in `x-forwarded-for`, else `x-real-ip`, else `unknown`.
 *
 * **Production (e.g. Render):** Render's reverse proxy appends the real client IP as the rightmost entry.
 * Using the rightmost value prevents clients from spoofing a forged IP via the leftmost XFF position.
 *
 * **Local dev (direct Bun):** Headers are often absent → every client maps to `unknown` and shares one bucket. That is intentional for a single dev machine; do not be surprised if local load tests hit the limit quickly.
 */
export function getClientId(c: Context): string {
  const forwarded = c.req.header('x-forwarded-for')
  if (forwarded) {
    const parts = forwarded.split(',')
    return parts[parts.length - 1]?.trim() ?? 'unknown'
  }
  const realIp = c.req.header('x-real-ip')
  if (realIp) {
    return realIp
  }
  return 'unknown'
}

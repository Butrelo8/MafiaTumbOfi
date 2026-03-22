import type { Context, Next } from 'hono'
import { getForwardedProtoFromRequest } from '../lib/forwardedProto'

export async function enforceHttps(c: Context, next: Next) {
  if (process.env.NODE_ENV === 'production') {
    const proto = getForwardedProtoFromRequest((name) => c.req.header(name))
    if (proto) {
      if (proto !== 'https') {
        const host = c.req.header('host')
        if (host) {
          return c.redirect(`https://${host}${c.req.path}`, 301)
        }
      }
    }
  }
  await next()
}

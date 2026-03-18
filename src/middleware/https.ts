import type { Context, Next } from 'hono'

export async function enforceHttps(c: Context, next: Next) {
  if (process.env.NODE_ENV === 'production') {
    const forwardedProto = c.req.header('x-forwarded-proto')
    if (forwardedProto) {
      const proto = forwardedProto.toLowerCase().trim()
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

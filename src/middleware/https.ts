import type { Context, Next } from 'hono'

export async function enforceHttps(c: Context, next: Next) {
  if (process.env.NODE_ENV === 'production') {
    const proto = c.req.header('x-forwarded-proto')
    if (proto !== 'https') {
      const host = c.req.header('host')
      return c.redirect(`https://${host}${c.req.path}`, 301)
    }
  }
  await next()
}

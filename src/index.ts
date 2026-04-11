import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { allowedOrigins as rawAllowedOrigins } from './lib/allowedOrigins'
import { getAppVersion } from './lib/appVersion'
import { expandCorsAllowedOrigins, normalizeRequestOrigin } from './lib/corsOrigins'
import { bodyLimit } from './middleware/bodyLimit'
import { errorHandler } from './middleware/error'
import { enforceHttps } from './middleware/https'
import { rateLimitHealth } from './middleware/rateLimitHealth'
import { securityHeaders } from './middleware/security'
import { routes } from './routes'

const app = new Hono()

const allowedOrigins = expandCorsAllowedOrigins(rawAllowedOrigins)

// ─── Global Middleware ────────────────────────────────
app.use('*', enforceHttps)
app.use('*', logger())
app.use('*', securityHeaders)
app.use('*', bodyLimit)
app.use(
  '*',
  cors({
    origin: (origin) => {
      if (!origin) return origin
      const key = normalizeRequestOrigin(origin)
      if (allowedOrigins.includes(key)) return origin
      return undefined
    },
    credentials: true,
  }),
)

// ─── Routes ───────────────────────────────────────────
app.route('/api', routes)

// ─── Health Check ─────────────────────────────────────
const START_TIME = Date.now()

app.use('/health', rateLimitHealth)
app.get('/health', (c) =>
  c.json(
    {
      status: 'ok',
      version: getAppVersion(),
      uptime: Math.floor((Date.now() - START_TIME) / 1000),
    },
    200,
  ),
)

// ─── Error Handler ────────────────────────────────────
app.onError(errorHandler)

export { app }
export default {
  port: process.env.PORT ?? 3001,
  fetch: app.fetch,
}

import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { bodyLimit } from './middleware/bodyLimit'
import { enforceHttps } from './middleware/https'
import { rateLimitHealth } from './middleware/rateLimitHealth'
import { securityHeaders } from './middleware/security'
import { errorHandler } from './middleware/error'
import { getAppVersion } from './lib/appVersion'
import { routes } from './routes'

const app = new Hono()

const allowedOrigins = [
  'http://localhost:4321',
  'http://localhost:4322',
  process.env.FRONTEND_URL,
  process.env.STAGING_URL,
  process.env.PRODUCTION_URL,
].filter(Boolean) as string[]

// ─── Global Middleware ────────────────────────────────
app.use('*', enforceHttps)
app.use('*', logger())
app.use('*', securityHeaders)
app.use('*', bodyLimit)
app.use('*', cors({
  origin: (origin) => {
    if (!origin || allowedOrigins.includes(origin)) return origin
    return undefined
  },
  credentials: true,
}))

// ─── Routes ───────────────────────────────────────────
app.route('/api', routes)

// ─── Health Check ─────────────────────────────────────
const APP_VERSION = getAppVersion()
const START_TIME = Date.now()

app.use('/health', rateLimitHealth)
app.get('/health', (c) =>
  c.json({
    status: 'ok',
    version: APP_VERSION,
    uptime: Math.floor((Date.now() - START_TIME) / 1000),
  }, 200),
)

// ─── Error Handler ────────────────────────────────────
app.onError(errorHandler)

export { app }
export default {
  port: process.env.PORT ?? 3001,
  fetch: app.fetch,
}

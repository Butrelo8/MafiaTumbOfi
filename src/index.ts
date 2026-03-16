import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { bodyLimit } from './middleware/bodyLimit'
import { enforceHttps } from './middleware/https'
import { securityHeaders } from './middleware/security'
import { errorHandler } from './middleware/error'
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
    return allowedOrigins[0]
  },
  credentials: true,
}))

// ─── Routes ───────────────────────────────────────────
app.route('/api', routes)

// ─── Health Check ─────────────────────────────────────
app.get('/health', (c) => c.json({ status: 'ok', version: '0.4.0' }))

// ─── Error Handler ────────────────────────────────────
app.onError(errorHandler)

export { app }
export default {
  port: process.env.PORT ?? 3001,
  fetch: app.fetch,
}

import type { APIRoute } from 'astro'
import { getWebAppVersion } from '../lib/webAppVersion'

/**
 * Health check for the frontend (Vercel). Used by N8N or monitors to confirm the site is up.
 * API health remains on the Hono service (Render) at GET /health.
 */
export const GET: APIRoute = () => {
  return new Response(
    JSON.stringify({
      status: 'ok',
      source: 'frontend',
      version: getWebAppVersion(),
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    },
  )
}

export const prerender = false

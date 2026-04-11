import type { APIRoute } from 'astro'
import { getWebAppVersion } from '../../lib/webAppVersion'

/**
 * Health check for the frontend (Vercel). Used by N8N or monitors.
 * Also available at /health; /api/health often works more reliably on Vercel serverless.
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

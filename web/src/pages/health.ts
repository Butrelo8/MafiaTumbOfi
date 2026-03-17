import type { APIRoute } from 'astro';

/**
 * Health check for the frontend (Vercel). Used by N8N or monitors to confirm the site is up.
 * API health remains on the Hono service (Render) at GET /health.
 */
export const GET: APIRoute = () => {
  return new Response(
    JSON.stringify({ status: 'ok', source: 'frontend', version: '0.4.0' }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
};

export const prerender = false;

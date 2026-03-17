import type { APIRoute } from 'astro';

/**
 * Health check for the frontend (Vercel). Used by N8N or monitors.
 * Also available at /health; /api/health often works more reliably on Vercel serverless.
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

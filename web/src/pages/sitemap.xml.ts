import type { APIRoute } from 'astro'
import { buildPublicSitemapXml } from '../lib/publicSitemap'
import { resolvePublicBaseUrl } from '../lib/publicSiteUrl'

export const prerender = false

export const GET: APIRoute = ({ request }) => {
  const origin = new URL(request.url).origin
  const base = resolvePublicBaseUrl(import.meta.env.PUBLIC_SITE_URL, origin)
  const body = buildPublicSitemapXml(base)
  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  })
}

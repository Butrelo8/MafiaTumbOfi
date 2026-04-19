/**
 * Build `sitemap.xml` body for indexable marketing routes only (no `/admin`).
 */

/** Escape text for XML element bodies (e.g. `<loc>`). */
export function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

/** Path segments after the public origin; `''` = homepage (same URL as `base`, no trailing slash). */
const INDEXABLE_PATHS = ['', '/booking'] as const

/**
 * @param baseUrl Public site base, e.g. `https://example.com` (trailing slash optional; stripped).
 */
export function buildPublicSitemapXml(baseUrl: string): string {
  const base = baseUrl.trim().replace(/\/$/, '')
  const lines = INDEXABLE_PATHS.map((path) => {
    const loc = path === '' ? base : `${base}${path}`
    return `  <url><loc>${escapeXml(loc)}</loc></url>`
  }).join('\n')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${lines}
</urlset>
`
}

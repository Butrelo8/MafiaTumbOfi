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

interface SitemapEntry {
  /** Path segment after the public origin. `''` = homepage. */
  path: string
  changefreq: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never'
  priority: string
}

const INDEXABLE_ENTRIES: SitemapEntry[] = [
  { path: '', changefreq: 'weekly', priority: '1.0' },
  { path: '/contratacion', changefreq: 'monthly', priority: '0.8' },
]

/**
 * @param baseUrl Public site base, e.g. `https://example.com` (trailing slash optional; stripped).
 */
export function buildPublicSitemapXml(baseUrl: string): string {
  const base = baseUrl.trim().replace(/\/$/, '')
  const lines = INDEXABLE_ENTRIES.map(({ path, changefreq, priority }) => {
    const loc = path === '' ? base : `${base}${path}`
    return [
      '  <url>',
      `    <loc>${escapeXml(loc)}</loc>`,
      `    <changefreq>${changefreq}</changefreq>`,
      `    <priority>${priority}</priority>`,
      '  </url>',
    ].join('\n')
  }).join('\n')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${lines}
</urlset>
`
}

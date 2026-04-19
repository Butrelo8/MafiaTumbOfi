import { describe, expect, test } from 'bun:test'
import { buildPublicSitemapXml, escapeXml } from './publicSitemap'

describe('escapeXml', () => {
  test('escapes reserved characters', () => {
    expect(escapeXml(`a&b<c>"'`)).toBe('a&amp;b&lt;c&gt;&quot;&apos;')
  })
})

describe('buildPublicSitemapXml', () => {
  test('includes homepage and booking only', () => {
    const xml = buildPublicSitemapXml('https://mafiatumbada.com')
    expect(xml).toContain('<loc>https://mafiatumbada.com</loc>')
    expect(xml).toContain('<loc>https://mafiatumbada.com/booking</loc>')
    expect(xml).not.toContain('/admin')
    expect(xml).toContain('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
  })

  test('strips trailing slash on base', () => {
    const xml = buildPublicSitemapXml('https://example.com/')
    expect(xml).toContain('<loc>https://example.com</loc>')
    expect(xml).toContain('<loc>https://example.com/booking</loc>')
  })
})

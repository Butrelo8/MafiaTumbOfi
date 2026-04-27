import { describe, expect, test } from 'bun:test'
import { buildPublicSitemapXml, escapeXml } from './publicSitemap'

describe('escapeXml', () => {
  test('escapes reserved characters', () => {
    expect(escapeXml(`a&b<c>"'`)).toBe('a&amp;b&lt;c&gt;&quot;&apos;')
  })
})

describe('buildPublicSitemapXml', () => {
  test('includes homepage and contratacion only', () => {
    const xml = buildPublicSitemapXml('https://mafiatumbada.com')
    expect(xml).toContain('<loc>https://mafiatumbada.com</loc>')
    expect(xml).toContain('<loc>https://mafiatumbada.com/contratacion</loc>')
    expect(xml).not.toContain('/admin')
    expect(xml).toContain('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
  })

  test('strips trailing slash on base', () => {
    const xml = buildPublicSitemapXml('https://example.com/')
    expect(xml).toContain('<loc>https://example.com</loc>')
    expect(xml).toContain('<loc>https://example.com/contratacion</loc>')
  })

  test('includes changefreq and priority for homepage', () => {
    const xml = buildPublicSitemapXml('https://mafiatumbada.com')
    expect(xml).toContain('<changefreq>weekly</changefreq>')
    expect(xml).toContain('<priority>1.0</priority>')
  })

  test('includes changefreq and priority for contratacion', () => {
    const xml = buildPublicSitemapXml('https://mafiatumbada.com')
    expect(xml).toContain('<changefreq>monthly</changefreq>')
    expect(xml).toContain('<priority>0.8</priority>')
  })
})

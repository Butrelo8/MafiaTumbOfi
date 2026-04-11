import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const adminPath = join(__dirname, '../pages/admin.astro')

describe('admin page marketing shell', () => {
  test('uses MarketingLayout and noindex for internal panel', () => {
    const src = readFileSync(adminPath, 'utf8')
    expect(src).toContain("import MarketingLayout from '../layouts/MarketingLayout.astro'")
    expect(src).not.toContain("import Layout from '../layouts/Layout.astro'")
    expect(src).toContain('robots="noindex,nofollow"')
    expect(src).toContain('<MarketingLayout')
  })

  test('export uses site secondary button and footer matches booking pattern', () => {
    const src = readFileSync(adminPath, 'utf8')
    expect(src).toMatch(/btn-secondary[\s\S]*admin\/export-bookings|admin\/export-bookings[\s\S]*btn-secondary/)
    expect(src).toContain('class="footer-bar"')
    expect(src).toContain('class="container admin-container"')
  })
})

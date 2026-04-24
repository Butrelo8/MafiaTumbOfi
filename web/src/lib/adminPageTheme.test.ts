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

  test('danger zone bulk delete uses drawer overlay pattern', () => {
    const src = readFileSync(adminPath, 'utf8')
    expect(src).toContain('admin-danger-zone')
    expect(src).toContain('/admin/delete-all-bookings')
    expect(src).toContain('ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE')
  })

  test('bookings toolbar scopes pipeline and lead-priority filters with badges', () => {
    const src = readFileSync(adminPath, 'utf8')
    expect(src).toContain('id="admin-bookings-toolbar"')
    expect(src).toContain('data-priority-filter="high"')
    expect(src).toContain('admin-priority-badge')
    expect(src).toContain('admin-priority-high')
    expect(src).toContain('data-lead-priority=')
  })

  test('detail drawer stacks above fixed marketing header', () => {
    const adminSrc = readFileSync(adminPath, 'utf8')
    const marketingPath = join(__dirname, '../styles/marketing-press.css')
    const marketingSrc = readFileSync(marketingPath, 'utf8')
    const headerZ = marketingSrc.match(/\.site-header\s*\{[^}]*z-index:\s*(\d+)/s)
    expect(headerZ).not.toBeNull()
    const headerZNum = Number(headerZ![1])
    const drawerZ = adminSrc.match(/\.admin-drawer\s*\{[^}]*z-index:\s*(\d+)/s)
    expect(drawerZ).not.toBeNull()
    expect(Number(drawerZ![1])).toBeGreaterThan(headerZNum)
    expect(Number(drawerZ![1])).toBeLessThan(200)
  })
})

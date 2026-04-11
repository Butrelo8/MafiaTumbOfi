import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const indexPath = join(__dirname, '../pages/index.astro')
const marketingCssPath = join(__dirname, '../styles/marketing-press.css')
const packagesDataPath = join(__dirname, '../data/packages.ts')
const marketingLayoutPath = join(__dirname, '../layouts/MarketingLayout.astro')

describe('marketing homepage hero', () => {
  test('includes hero video markup and public asset path', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('class="hero-video"')
    expect(src).toContain('/video/hero.mp4')
    expect(src).toContain('hero-deco-line')
    expect(src).toContain('aria-hidden="true"')
    expect(src).toContain('playsinline')
    expect(src).toContain('muted')
  })

  test('marketing CSS defines video layer, scrim, deco line, and reduced-motion fallback', () => {
    const css = readFileSync(marketingCssPath, 'utf8')
    expect(css).toContain('.hero-video')
    expect(css).toContain('blur(2px)')
    expect(css).toContain('brightness(1.1)')
    expect(css).toContain('rgba(0, 0, 0, 0.2)')
    expect(css).toContain('rgba(0, 0, 0, 0.5)')
    expect(css).toContain('.hero-deco-line')
    expect(css).toContain('prefers-reduced-motion: reduce')
  })

  test('Apple Music social card uses a single svg (no nested svg)', () => {
    const src = readFileSync(indexPath, 'utf8')
    const start = src.indexOf('<!-- Apple Music -->')
    const end = src.indexOf('<!-- Instagram -->', start)
    expect(start).toBeGreaterThan(-1)
    expect(end).toBeGreaterThan(start)
    const block = src.slice(start, end)
    expect((block.match(/<svg/g) ?? []).length).toBe(1)
  })

  test('signed-in admin strip in index.astro uses low-emphasis styling', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('class="admin-notice"')
    expect(src).toContain('rgba(0, 0, 0, 0.75)')
    expect(src).toContain('border-bottom: 1px solid rgba(255, 255, 255, 0.1)')
    expect(src).toContain('Ver solicitudes')
    expect(src).toContain('.admin-notice a:hover')
  })
})

describe('marketing homepage conversion blocks', () => {
  test('index includes repertoire, testimonials, packages, and booking urgency markup', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('id="repertorio"')
    expect(src).toContain('class="repertoire-card"')
    expect(src).toContain('id="testimonios"')
    expect(src).toContain('class="testimonial-card"')
    expect(src).toContain('id="paquetes"')
    expect(src).toContain('package-card')
    expect(src).toContain('package-card--featured')
    expect(src).toContain('class="booking-urgency"')

    const paquetesStart = src.indexOf('id="paquetes"')
    const pressStart = src.indexOf('id="press"')
    expect(paquetesStart).toBeGreaterThan(-1)
    expect(pressStart).toBeGreaterThan(paquetesStart)
    const paquetesBlock = src.slice(paquetesStart, pressStart)
    expect(paquetesBlock).toContain('href={pkg.cta.href}')

    const pkgSrc = readFileSync(packagesDataPath, 'utf8')
    expect((pkgSrc.match(/href:\s*'\/booking'/g) ?? []).length).toBe(3)

    const layoutSrc = readFileSync(marketingLayoutPath, 'utf8')
    expect(layoutSrc).toContain('href="/#paquetes"')
  })

  test('marketing CSS defines repertoire, testimonials, packages, and booking-urgency', () => {
    const css = readFileSync(marketingCssPath, 'utf8')
    expect(css).toContain('.repertoire-grid')
    expect(css).toContain('.repertoire-card')
    expect(css).toContain('.testimonials-grid')
    expect(css).toContain('.testimonial-card')
    expect(css).toContain('.packages-grid')
    expect(css).toContain('.package-card--featured')
    expect(css).toContain('.booking-urgency')
  })
})

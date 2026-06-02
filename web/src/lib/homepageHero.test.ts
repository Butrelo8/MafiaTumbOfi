import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { shouldLoadHeroVideo } from './heroVideo'

const __dirname = dirname(fileURLToPath(import.meta.url))
const indexPath = join(__dirname, '../pages/index.astro')
const marketingCssPath = join(__dirname, '../styles/marketing-press.css')
const packagesDataPath = join(__dirname, '../data/packages.ts')
const marketingLayoutPath = join(__dirname, '../layouts/MarketingLayout.astro')
const tourTablePath = join(__dirname, '../components/TourTable.astro')

describe('marketing homepage hero', () => {
  test('includes hero video markup and public asset path', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('class="hero-video"')
    expect(src).toContain('/video/hero.mp4')
    expect(src).toContain('hero--asymmetric')
    expect(src).toContain('hero-grain')
    const heroOpen = src.indexOf('class="hero hero--asymmetric"')
    const videoClass = src.indexOf('class="hero-video"')
    expect(heroOpen).toBeGreaterThan(-1)
    expect(videoClass).toBeGreaterThan(heroOpen)
    expect(src.indexOf('hero-grain')).toBeGreaterThan(videoClass)
    expect(src).toContain('aria-hidden="true"')
    expect(src).toContain('playsinline')
    expect(src).toContain('muted')
    expect(src).toContain('poster="/video/hero-poster.webp"')
    expect(src).toContain('preload="none"')
  })

  test('marketing CSS defines video layer, scrim, deco line, poster fade-in, and reduced-motion fallback', () => {
    const css = readFileSync(marketingCssPath, 'utf8')
    expect(css).toContain('.hero-video')
    expect(css).toMatch(/\.hero-video\s*\{[^}]*pointer-events:\s*none/s)
    expect(css).toContain('opacity: 0')
    expect(css).toContain('.hero-video[data-loaded]')
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

  test('includes above-the-fold blurb, marquee, fechas, and trust strip', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('class="hero-blurb"')
    expect(src).toContain('<Marquee')
    expect(src).toContain('id="fechas"')
    expect(src).toContain('normalizePublicApiBaseUrl')
    expect(src).toContain('apiBase={apiBase}')
    expect(src).toContain('rows={[]}')
    expect(src).toContain('class="trust-strip"')
    expect(src).toContain('id="trust-heading"')
    expect(src).toContain('class="trust-grid"')
    expect(src).toContain('class="trust-item"')
    expect(src).toContain('.hero-blurb')
    expect(src).toContain('.sr-only')
    const heroMeta = src.indexOf('class="hero-meta"')
    const blurb = src.indexOf('class="hero-blurb"')
    const actions = src.indexOf('class="hero-actions"')
    expect(blurb).toBeGreaterThan(heroMeta)
    expect(actions).toBeGreaterThan(blurb)
    const trustStart = src.indexOf('<!-- ─── TRUST STRIP')
    const bioStart = src.indexOf('<!-- ─── BIO')
    expect(trustStart).toBeGreaterThan(-1)
    expect(bioStart).toBeGreaterThan(trustStart)
  })
})

describe('heroVideo capability gate', () => {
  test('returns false when prefers-reduced-motion is set', () => {
    const win = { matchMedia: () => ({ matches: true }), navigator: {} } as unknown as Window
    expect(shouldLoadHeroVideo(win)).toBe(false)
  })

  test('returns false when saveData is true', () => {
    const win = {
      matchMedia: () => ({ matches: false }),
      navigator: { connection: { saveData: true, effectiveType: '4g' } },
    } as unknown as Window
    expect(shouldLoadHeroVideo(win)).toBe(false)
  })

  test('returns false on 2g connection', () => {
    const win = {
      matchMedia: () => ({ matches: false }),
      navigator: { connection: { saveData: false, effectiveType: '2g' } },
    } as unknown as Window
    expect(shouldLoadHeroVideo(win)).toBe(false)
  })

  test('returns true on capable device', () => {
    const win = {
      matchMedia: () => ({ matches: false }),
      navigator: { connection: { saveData: false, effectiveType: '4g' } },
    } as unknown as Window
    expect(shouldLoadHeroVideo(win)).toBe(true)
  })

  test('returns true when navigator.connection is undefined', () => {
    const win = { matchMedia: () => ({ matches: false }), navigator: {} } as unknown as Window
    expect(shouldLoadHeroVideo(win)).toBe(true)
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
    expect((pkgSrc.match(/href:\s*'\/contratacion'/g) ?? []).length).toBe(3)

    const layoutSrc = readFileSync(marketingLayoutPath, 'utf8')
    expect(layoutSrc).toContain("'/#paquetes'")
    expect(layoutSrc).toContain('href="/contratacion"')
  })

  test('MarketingLayout renders admin link server-side, no Clerk client components', () => {
    const layoutSrc = readFileSync(marketingLayoutPath, 'utf8')
    expect(layoutSrc).toContain('class="menu-auth"')
    expect(layoutSrc).not.toContain('from \'@clerk/astro/components\'')
    expect(layoutSrc).not.toContain('SignInButton')
    expect(layoutSrc).not.toContain('UserButton')
    expect(layoutSrc).not.toContain('window.setTimeout(() => closeMenu(), 0)')
    expect(layoutSrc).toContain('Astro.locals.auth')
  })

  test('Plausible hook: hero CTA id, layout snippet, and ticket CTA delegation', () => {
    const indexSrc = readFileSync(indexPath, 'utf8')
    expect(indexSrc).toContain('id="hero-cta-contratacion"')
    const layoutSrc = readFileSync(marketingLayoutPath, 'utf8')
    expect(layoutSrc).toContain('normalizePlausibleDataDomain')
    expect(layoutSrc).toContain('plausible.io/js/script.js')
    expect(layoutSrc).toContain("window.plausible?.('CTA Click'")
    expect(layoutSrc).toContain("window.plausible?.('Ticket CTA'")
    const tourSrc = readFileSync(tourTablePath, 'utf8')
    expect(tourSrc).toContain('data-analytics-venue')
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
    expect(css).toContain('.marquee-wrap')
    expect(css).toContain('.signature-cta')
  })
})

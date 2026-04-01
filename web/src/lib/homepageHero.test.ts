import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const indexPath = join(__dirname, '../pages/index.astro')
const marketingCssPath = join(__dirname, '../styles/marketing-press.css')

describe('marketing homepage hero', () => {
  test('includes hero video markup and public asset path', () => {
    const src = readFileSync(indexPath, 'utf8')
    expect(src).toContain('class="hero-video"')
    expect(src).toContain('/video/hero.mov')
    expect(src).toContain('hero-deco-line')
    expect(src).toContain('aria-hidden="true"')
    expect(src).toContain('playsinline')
    expect(src).toContain('muted')
  })

  test('marketing CSS defines video layer, scrim, deco line, and reduced-motion fallback', () => {
    const css = readFileSync(marketingCssPath, 'utf8')
    expect(css).toContain('.hero-video')
    expect(css).toContain('blur(2px)')
    expect(css).toContain('brightness(0.7)')
    expect(css).toContain('rgba(0, 0, 0, 0.6)')
    expect(css).toContain('rgba(0, 0, 0, 0.8)')
    expect(css).toContain('.hero-deco-line')
    expect(css).toContain('prefers-reduced-motion: reduce')
  })
})

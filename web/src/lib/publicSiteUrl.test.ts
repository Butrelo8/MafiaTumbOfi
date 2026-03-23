import { describe, expect, test } from 'bun:test'
import { pressKitCanonical, resolvePublicBaseUrl } from './publicSiteUrl'

describe('resolvePublicBaseUrl', () => {
  test('trims and strips trailing slash from PUBLIC_SITE_URL', () => {
    expect(resolvePublicBaseUrl('https://example.com/', 'http://localhost:4321')).toBe(
      'https://example.com'
    )
  })

  test('uses fallback when env is unset', () => {
    expect(resolvePublicBaseUrl(undefined, 'http://localhost:4321/')).toBe(
      'http://localhost:4321'
    )
  })

  test('uses fallback when env is whitespace only', () => {
    expect(resolvePublicBaseUrl('   ', 'https://preview.vercel.app')).toBe(
      'https://preview.vercel.app'
    )
  })
})

describe('pressKitCanonical', () => {
  test('appends /press-kit to resolved base', () => {
    expect(pressKitCanonical('https://x.com/', 'http://local')).toBe('https://x.com/press-kit')
  })
})

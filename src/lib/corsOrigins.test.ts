import { describe, expect, test } from 'bun:test'
import { expandCorsAllowedOrigins, normalizeRequestOrigin } from './corsOrigins'

describe('expandCorsAllowedOrigins', () => {
  test('dedupes and keeps localhost without www variant', () => {
    const out = expandCorsAllowedOrigins(['http://localhost:4321', 'http://localhost:4321/'])
    expect(out).toContain('http://localhost:4321')
    expect(out.filter((o) => o.includes('www.'))).toHaveLength(0)
  })

  test('strips trailing slash via URL origin', () => {
    const out = expandCorsAllowedOrigins(['https://mafiatumbada.com/'])
    expect(out).toContain('https://mafiatumbada.com')
    expect(out).toContain('https://www.mafiatumbada.com')
  })

  test('adds apex when PRODUCTION_URL uses www', () => {
    const out = expandCorsAllowedOrigins(['https://www.example.org'])
    expect(out).toContain('https://www.example.org')
    expect(out).toContain('https://example.org')
  })

  test('skips invalid entries', () => {
    const out = expandCorsAllowedOrigins(['', '   ', 'not-a-url'])
    expect(out).toHaveLength(0)
  })

  test('does not add www for IPv4 literal', () => {
    const out = expandCorsAllowedOrigins(['http://127.0.0.1:3000'])
    expect(out).toEqual(['http://127.0.0.1:3000'])
  })
})

describe('normalizeRequestOrigin', () => {
  test('returns URL origin', () => {
    expect(normalizeRequestOrigin('https://www.foo.com')).toBe('https://www.foo.com')
  })
})

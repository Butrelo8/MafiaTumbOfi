import { describe, expect, test } from 'bun:test'
import { normalizePlausibleDataDomain, trackPlausible } from './plausibleClient'

describe('normalizePlausibleDataDomain', () => {
  test('returns null for empty', () => {
    expect(normalizePlausibleDataDomain(undefined)).toBeNull()
    expect(normalizePlausibleDataDomain('')).toBeNull()
    expect(normalizePlausibleDataDomain('   ')).toBeNull()
  })

  test('returns hostname from full URL', () => {
    expect(normalizePlausibleDataDomain('https://mafiatumbada.com/path')).toBe('mafiatumbada.com')
  })

  test('returns bare host without path', () => {
    expect(normalizePlausibleDataDomain('mafiatumbada.com')).toBe('mafiatumbada.com')
    expect(normalizePlausibleDataDomain('stats.example.com/foo')).toBe('stats.example.com')
  })
})

describe('trackPlausible', () => {
  test('no-ops when plausible is missing', () => {
    const g = globalThis as unknown as { window?: Window }
    const prev = g.window
    g.window = {} as Window
    try {
      expect(() => trackPlausible('Booking Submit')).not.toThrow()
    } finally {
      g.window = prev
    }
  })

  test('calls window.plausible when present', () => {
    const calls: unknown[][] = []
    const plausible = (name: string, opts?: object) => {
      calls.push([name, opts])
    }
    const g = globalThis as unknown as { window?: Window }
    const prev = g.window
    g.window = { plausible } as unknown as Window
    try {
      trackPlausible('CTA Click', { props: { target: 'contratacion' } })
      expect(calls).toEqual([['CTA Click', { props: { target: 'contratacion' } }]])
    } finally {
      g.window = prev
    }
  })
})

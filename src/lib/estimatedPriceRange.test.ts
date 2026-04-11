import { describe, expect, test } from 'bun:test'
import { estimatedPriceRange } from './estimatedPriceRange'

function parseKRange(range: string): { lowK: number; highK: number } | null {
  if (!range || range === '-') return null
  // Examples:
  // - "15k – 45k MXN"
  // - "20k MXN"
  const single = /^(\d+)k MXN$/.exec(range)
  if (single) return { lowK: Number(single[1]), highK: Number(single[1]) }

  const multi = /^(\d+)k – (\d+)k MXN$/.exec(range)
  if (!multi) return null
  return { lowK: Number(multi[1]), highK: Number(multi[2]) }
}

describe('estimatedPriceRange', () => {
  test('returns "-" when all inputs are missing', () => {
    expect(estimatedPriceRange({})).toBe('-')
    expect(estimatedPriceRange({ city: null, duration: null, attendees: null })).toBe('-')
    expect(estimatedPriceRange({ city: '', duration: '', attendees: '' })).toBe('-')
  })

  test('returns a base local range when only city is provided', () => {
    // Monterrey is local
    const resLocal = estimatedPriceRange({ city: 'Monterrey' })
    expect(resLocal).toBe('15k – 45k MXN')

    const parsed = parseKRange(resLocal)
    expect(parsed).not.toBeNull()
    expect(parsed?.lowK).toBeLessThanOrEqual(parsed?.highK)
  })

  test('adds travel surcharge for foraneo cities', () => {
    const resForaneo = estimatedPriceRange({ city: 'Cancún' })
    expect(resForaneo).toBe('20k – 55k MXN')

    const parsed = parseKRange(resForaneo)
    expect(parsed).not.toBeNull()
    expect(parsed?.lowK).toBeLessThanOrEqual(parsed?.highK)
  })

  test('matches local cities case-insensitively', () => {
    expect(estimatedPriceRange({ city: 'MONTERREY' })).toBe('15k – 45k MXN')
    expect(estimatedPriceRange({ city: ' San Pedro Garza García ' })).toBe('15k – 45k MXN')
  })

  test('scales with duration', () => {
    // Local, <100 attendees, 2h
    expect(estimatedPriceRange({ city: 'Monterrey', duration: '2h', attendees: 'menos_100' })).toBe(
      '27k – 45k MXN',
    )

    // Local, <100 attendees, 3h_mas
    expect(
      estimatedPriceRange({ city: 'Monterrey', duration: '3h_mas', attendees: 'menos_100' }),
    ).toBe('38k – 63k MXN')
  })

  test('scales with attendees', () => {
    // Local, 1h, 500_1000 attendees
    expect(estimatedPriceRange({ city: 'Monterrey', duration: '1h', attendees: '500_1000' })).toBe(
      '21k – 40k MXN',
    )
  })

  test('handles unknown duration and attendees gracefully (falls back)', () => {
    const res = estimatedPriceRange({
      city: 'Monterrey',
      duration: 'garbage',
      attendees: 'garbage',
    })
    // Uses defaults: duration(no_definido fallback) + attendees fallback
    expect(res).toBe('15k – 45k MXN')
  })

  test('computes even when city is missing but duration/attendees exist', () => {
    // Missing city defaults to local behavior (no travel surcharge).
    const res = estimatedPriceRange({ duration: '2h', attendees: '300_500' })
    expect(res).not.toBe('-')

    const parsed = parseKRange(res)
    expect(parsed).not.toBeNull()
    expect(parsed?.lowK).toBeLessThanOrEqual(parsed?.highK)
  })

  test('formatting is stable and produces a parseable k-range', () => {
    const inputs = [
      { city: 'Monterrey', duration: '1h', attendees: 'menos_100' },
      { city: 'Monterrey', duration: '2h', attendees: '100_300' },
      { city: 'Monterrey', duration: 'no_definido', attendees: '500_1000' },
      { city: 'Cancún', duration: '3h_mas', attendees: 'mas_1000' },
    ]

    for (const input of inputs) {
      const out = estimatedPriceRange(input)
      // Accept either the range form or the single-value form.
      expect(out === '-' || /^\d+k(?: – \d+k)? MXN$/.test(out)).toBe(true)

      const parsed = parseKRange(out)
      expect(parsed).not.toBeNull()
      if (parsed) expect(parsed.lowK).toBeLessThanOrEqual(parsed.highK)
    }
  })
})

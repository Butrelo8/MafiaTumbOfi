import { describe, expect, test } from 'bun:test'
import { eventDateSortKeyMs } from './eventDateSortKey'

describe('eventDateSortKeyMs', () => {
  test('unknown sorts last vs real date (asc intent)', () => {
    const real = eventDateSortKeyMs('2026-06-15')
    const missing = eventDateSortKeyMs(null)
    const blank = eventDateSortKeyMs('   ')
    const dash = eventDateSortKeyMs('-')
    const garbage = eventDateSortKeyMs('next summer maybe')
    expect(real).toBeLessThan(missing)
    expect(real).toBeLessThan(blank)
    expect(real).toBeLessThan(dash)
    expect(real).toBeLessThan(garbage)
  })

  test('parses ISO date strings', () => {
    expect(eventDateSortKeyMs('2026-05-01')).toBe(Date.parse('2026-05-01'))
  })
})

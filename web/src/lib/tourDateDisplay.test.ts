import { describe, expect, test } from 'bun:test'
import { formatTourDateLabel } from './tourDateDisplay'

describe('formatTourDateLabel', () => {
  test('formats ISO date in es-MX', () => {
    expect(formatTourDateLabel('2030-06-15')).toMatch(/15/)
    expect(formatTourDateLabel('2030-06-15')).toMatch(/2030/)
  })

  test('returns non-ISO strings unchanged', () => {
    expect(formatTourDateLabel('TBA')).toBe('TBA')
  })
})

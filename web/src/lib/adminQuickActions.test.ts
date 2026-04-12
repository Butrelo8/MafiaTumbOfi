import { describe, expect, test } from 'bun:test'
import { phoneToTelHref } from './adminQuickActions'

describe('phoneToTelHref', () => {
  test('returns null for empty or placeholder', () => {
    expect(phoneToTelHref(null)).toBeNull()
    expect(phoneToTelHref('')).toBeNull()
    expect(phoneToTelHref('   ')).toBeNull()
    expect(phoneToTelHref('-')).toBeNull()
  })

  test('returns null when fewer than 10 digits', () => {
    expect(phoneToTelHref('12345')).toBeNull()
    expect(phoneToTelHref('(81) 123-456')).toBeNull()
  })

  test('returns null when more than 15 digits', () => {
    expect(phoneToTelHref('1'.repeat(16))).toBeNull()
  })

  test('strips formatting and prefixes tel:', () => {
    expect(phoneToTelHref('(81) 1234-5678')).toBe('tel:8112345678')
    expect(phoneToTelHref('+52 81 1234 5678')).toBe('tel:528112345678')
  })
})

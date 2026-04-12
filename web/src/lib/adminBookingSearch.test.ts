import { describe, expect, test } from 'bun:test'
import {
  ADMIN_BOOKING_SEARCH_DEBOUNCE_MS,
  bookingMatchesAdminSearchQuery,
  normalizeAdminBookingSearchQuery,
} from './adminBookingSearch'

describe('normalizeAdminBookingSearchQuery', () => {
  test('trims and lowercases', () => {
    expect(normalizeAdminBookingSearchQuery('  Foo ')).toBe('foo')
  })
})

describe('bookingMatchesAdminSearchQuery', () => {
  test('empty normalized query matches always', () => {
    expect(
      bookingMatchesAdminSearchQuery({ name: 'x', email: 'y', phone: null }, ''),
    ).toBe(true)
  })

  test('matches name case-insensitively', () => {
    expect(
      bookingMatchesAdminSearchQuery({ name: 'María López', email: '', phone: '' }, 'maría'),
    ).toBe(true)
    expect(bookingMatchesAdminSearchQuery({ name: 'María', email: '', phone: '' }, 'xyz')).toBe(
      false,
    )
  })

  test('matches email substring', () => {
    expect(
      bookingMatchesAdminSearchQuery(
        { name: '', email: 'User@Example.com', phone: '' },
        'example',
      ),
    ).toBe(true)
  })

  test('matches phone substring', () => {
    expect(
      bookingMatchesAdminSearchQuery(
        { name: '', email: '', phone: '+52 228 123 4567' },
        '123 45',
      ),
    ).toBe(true)
  })

  test('null phone uses empty string for match', () => {
    expect(bookingMatchesAdminSearchQuery({ name: 'a', email: 'b', phone: null }, '999')).toBe(
      false,
    )
  })
})

describe('ADMIN_BOOKING_SEARCH_DEBOUNCE_MS', () => {
  test('is 200ms per product spec', () => {
    expect(ADMIN_BOOKING_SEARCH_DEBOUNCE_MS).toBe(200)
  })
})

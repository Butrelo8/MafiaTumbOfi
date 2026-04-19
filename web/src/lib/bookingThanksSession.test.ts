import { describe, expect, test } from 'bun:test'
import {
  BOOKING_THANKS_SESSION_KEY,
  normalizeBookingConfirmation,
  parseBookingThanksStored,
} from './bookingThanksSession'

describe('BOOKING_THANKS_SESSION_KEY', () => {
  test('matches contract used by booking + gracias pages', () => {
    expect(BOOKING_THANKS_SESSION_KEY).toBe('mto_booking_thanks')
  })
})

describe('normalizeBookingConfirmation', () => {
  test('maps sent and pending', () => {
    expect(normalizeBookingConfirmation('sent')).toBe('sent')
    expect(normalizeBookingConfirmation('pending')).toBe('pending')
  })

  test('maps unknown and non-strings to default', () => {
    expect(normalizeBookingConfirmation(undefined)).toBe('default')
    expect(normalizeBookingConfirmation('')).toBe('default')
    expect(normalizeBookingConfirmation('failed')).toBe('default')
    expect(normalizeBookingConfirmation(201)).toBe('default')
  })
})

describe('parseBookingThanksStored', () => {
  test('parses valid JSON', () => {
    expect(parseBookingThanksStored('{"confirmation":"sent"}')).toEqual({ confirmation: 'sent' })
    expect(parseBookingThanksStored('{"confirmation":"pending"}')).toEqual({ confirmation: 'pending' })
    expect(parseBookingThanksStored('{"confirmation":"default"}')).toEqual({ confirmation: 'default' })
  })

  test('returns null for invalid confirmation value', () => {
    expect(parseBookingThanksStored('{"confirmation":"nope"}')).toBeNull()
  })

  test('returns null for malformed JSON or wrong shape', () => {
    expect(parseBookingThanksStored(null)).toBeNull()
    expect(parseBookingThanksStored('')).toBeNull()
    expect(parseBookingThanksStored('{')).toBeNull()
    expect(parseBookingThanksStored('{}')).toBeNull()
    expect(parseBookingThanksStored('{"foo":1}')).toBeNull()
  })
})

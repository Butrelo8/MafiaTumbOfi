import { describe, expect, test } from 'bun:test'
import {
  computeBookingLeadScore,
  formatLeadPriorityLabel,
  isLeadPriority,
} from './bookingLeadScore'

describe('computeBookingLeadScore', () => {
  test('minimal payload yields low priority and bounded score', () => {
    const { leadScore, leadPriority } = computeBookingLeadScore({})
    expect(leadPriority).toBe('low')
    expect(leadScore).toBeGreaterThanOrEqual(0)
    expect(leadScore).toBeLessThan(200)
  })

  test('null budget and empty city still produce a stable score', () => {
    const a = computeBookingLeadScore({
      budget: null,
      city: '',
      attendees: null,
      duration: null,
    })
    const b = computeBookingLeadScore({
      budget: undefined,
      city: '   ',
      attendees: undefined,
      duration: undefined,
    })
    expect(a.leadScore).toBe(b.leadScore)
    expect(a.leadPriority).toBe('low')
  })

  test('high budget + large show signals high priority', () => {
    const { leadScore, leadPriority } = computeBookingLeadScore({
      budget: 'mas_100k',
      attendees: 'mas_1000',
      duration: '3h_mas',
      city: 'Ciudad de México',
      eventType: 'Festival',
      showType: 'full',
      venueSound: 'si',
    })
    expect(leadPriority).toBe('high')
    expect(leadScore).toBeGreaterThanOrEqual(400)
    expect(leadScore).toBeLessThanOrEqual(1000)
  })

  test('typical small local gig lands in medium band', () => {
    const { leadScore, leadPriority } = computeBookingLeadScore({
      budget: 'menos_15k',
      attendees: 'menos_100',
      duration: '1h',
      city: 'Monterrey',
    })
    expect(leadPriority).toBe('medium')
    expect(leadScore).toBeGreaterThanOrEqual(200)
    expect(leadScore).toBeLessThan(400)
  })

  test('local city tier uses PRICE_CONSTANTS local set', () => {
    const monterrey = computeBookingLeadScore({ city: 'Monterrey', budget: '15k_30k' })
    const foraneo = computeBookingLeadScore({ city: 'Ciudad de México', budget: '15k_30k' })
    expect(foraneo.leadScore).toBeGreaterThan(monterrey.leadScore)
  })
})

describe('formatLeadPriorityLabel', () => {
  test('maps known priorities', () => {
    expect(formatLeadPriorityLabel('high')).toBe('Alta')
    expect(formatLeadPriorityLabel('medium')).toBe('Media')
    expect(formatLeadPriorityLabel('low')).toBe('Baja')
  })

  test('null and empty', () => {
    expect(formatLeadPriorityLabel(null)).toBe('-')
    expect(formatLeadPriorityLabel('')).toBe('-')
  })

  test('legacy unknown string passes through', () => {
    expect(formatLeadPriorityLabel('unknown')).toBe('unknown')
  })
})

describe('isLeadPriority', () => {
  test('accepts only canonical values', () => {
    expect(isLeadPriority('high')).toBe(true)
    expect(isLeadPriority('invalid')).toBe(false)
  })
})

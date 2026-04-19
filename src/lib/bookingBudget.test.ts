import { describe, expect, test } from 'bun:test'
import { z } from 'zod'
import {
  BOOKING_BUDGET_HINTS_WITH_EMPTY,
  BOOKING_BUDGET_OPTIONS,
  BOOKING_BUDGET_SORT_RANK,
  BOOKING_BUDGET_VALUES,
  BUDGET_HINTS,
  BUDGET_LABELS,
  formatBudgetLabel,
  isBookingBudget,
} from './bookingBudget'

/** Parity with `src/routes/booking.ts` — `z.enum(BOOKING_BUDGET_VALUES)`. */
const bookingBudgetZod = z.enum(BOOKING_BUDGET_VALUES)

describe('bookingBudget', () => {
  test('labels and hints cover exactly BOOKING_BUDGET_VALUES', () => {
    for (const value of BOOKING_BUDGET_VALUES) {
      expect(BUDGET_LABELS[value].length).toBeGreaterThan(0)
      expect(BUDGET_HINTS[value].length).toBeGreaterThan(0)
    }
    expect(Object.keys(BUDGET_LABELS)).toHaveLength(BOOKING_BUDGET_VALUES.length)
    expect(Object.keys(BUDGET_HINTS)).toHaveLength(BOOKING_BUDGET_VALUES.length)
  })

  test('BOOKING_BUDGET_OPTIONS order matches BOOKING_BUDGET_VALUES', () => {
    expect(BOOKING_BUDGET_OPTIONS.map((o) => o.value)).toEqual([...BOOKING_BUDGET_VALUES])
    for (const opt of BOOKING_BUDGET_OPTIONS) {
      expect(opt.label).toBe(BUDGET_LABELS[opt.value])
    }
  })

  test('BOOKING_BUDGET_HINTS_WITH_EMPTY includes empty key and tier hints', () => {
    expect(BOOKING_BUDGET_HINTS_WITH_EMPTY['']).toBe('')
    for (const value of BOOKING_BUDGET_VALUES) {
      expect(BOOKING_BUDGET_HINTS_WITH_EMPTY[value]).toBe(BUDGET_HINTS[value])
    }
  })

  test('BOOKING_BUDGET_SORT_RANK matches tier order', () => {
    expect(BOOKING_BUDGET_SORT_RANK['']).toBe(0)
    BOOKING_BUDGET_VALUES.forEach((value, index) => {
      expect(BOOKING_BUDGET_SORT_RANK[value]).toBe(index + 1)
    })
  })

  test('isBookingBudget and formatBudgetLabel', () => {
    expect(isBookingBudget('menos_15k')).toBe(true)
    expect(isBookingBudget('invalid')).toBe(false)
    expect(formatBudgetLabel(null)).toBe('-')
    expect(formatBudgetLabel('')).toBe('-')
    expect(formatBudgetLabel('menos_15k')).toBe(BUDGET_LABELS.menos_15k)
    expect(formatBudgetLabel('legacy_unknown')).toBe('legacy_unknown')
  })

  test('z.enum(BOOKING_BUDGET_VALUES) accepts tiers only', () => {
    expect(bookingBudgetZod.safeParse('menos_15k').success).toBe(true)
    expect(bookingBudgetZod.safeParse('nope').success).toBe(false)
  })
})

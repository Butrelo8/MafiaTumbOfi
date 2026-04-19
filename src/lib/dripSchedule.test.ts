import { afterEach, describe, expect, test } from 'bun:test'
import {
  computeDripDueDatesFromCreatedAt,
  DRIP_EMAIL_2_DELAY_HOURS_DEFAULT,
  DRIP_EMAIL_3_DELAY_HOURS_DEFAULT,
  parseDelayHours,
} from './dripSchedule'

afterEach(() => {
  delete process.env.DRIP_EMAIL_2_DELAY_HOURS
  delete process.env.DRIP_EMAIL_3_DELAY_HOURS
})

describe('parseDelayHours', () => {
  test('empty → default', () => {
    expect(parseDelayHours(undefined, 24)).toBe(24)
    expect(parseDelayHours('', 24)).toBe(24)
    expect(parseDelayHours('   ', 24)).toBe(24)
  })

  test('valid integer', () => {
    expect(parseDelayHours('48', 24)).toBe(48)
  })

  test('floors decimal', () => {
    expect(parseDelayHours('24.9', 10)).toBe(24)
  })

  test('non-finite → default', () => {
    expect(parseDelayHours('nan', 7)).toBe(7)
    expect(parseDelayHours('-1', 7)).toBe(7)
  })
})

describe('computeDripDueDatesFromCreatedAt', () => {
  test('uses defaults when env unset', () => {
    const created = new Date('2026-01-01T12:00:00.000Z')
    const { drip2DueAt, drip3DueAt } = computeDripDueDatesFromCreatedAt(created)
    expect(drip2DueAt.getTime()).toBe(
      created.getTime() + DRIP_EMAIL_2_DELAY_HOURS_DEFAULT * 60 * 60 * 1000,
    )
    expect(drip3DueAt.getTime()).toBe(
      created.getTime() + DRIP_EMAIL_3_DELAY_HOURS_DEFAULT * 60 * 60 * 1000,
    )
  })

  test('reads env when set', () => {
    process.env.DRIP_EMAIL_2_DELAY_HOURS = '1'
    process.env.DRIP_EMAIL_3_DELAY_HOURS = '2'
    const created = new Date('2026-06-01T00:00:00.000Z')
    const { drip2DueAt, drip3DueAt } = computeDripDueDatesFromCreatedAt(created)
    expect(drip2DueAt.getTime()).toBe(created.getTime() + 3600_000)
    expect(drip3DueAt.getTime()).toBe(created.getTime() + 2 * 3600_000)
  })

  test('opts override env', () => {
    process.env.DRIP_EMAIL_2_DELAY_HOURS = '99'
    const created = new Date('2026-01-01T00:00:00.000Z')
    const { drip2DueAt } = computeDripDueDatesFromCreatedAt(created, {
      email2DelayHours: 3,
      email3DelayHours: 5,
    })
    expect(drip2DueAt.getTime()).toBe(created.getTime() + 3 * 3600_000)
  })
})

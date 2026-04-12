import { describe, expect, test } from 'bun:test'
import {
  ADMIN_STALE_NEW_DANGER_DAYS,
  ADMIN_STALE_NEW_MS_PER_DAY,
  ADMIN_STALE_NEW_WARN_DAYS,
  staleNewBadgeState,
} from './adminStaleNewBadge'

describe('staleNewBadgeState', () => {
  const t0 = Date.UTC(2026, 3, 10, 12, 0, 0)

  test('null when pipeline is not new', () => {
    expect(staleNewBadgeState('contacted', t0, t0 + 10 * ADMIN_STALE_NEW_MS_PER_DAY)).toBeNull()
    expect(staleNewBadgeState('closed', t0, t0 + 10 * ADMIN_STALE_NEW_MS_PER_DAY)).toBeNull()
  })

  test('null when created is fewer than WARN_DAYS before now', () => {
    const created = t0
    const now = t0 + (ADMIN_STALE_NEW_WARN_DAYS - 1) * ADMIN_STALE_NEW_MS_PER_DAY
    expect(staleNewBadgeState('new', created, now)).toBeNull()
  })

  test('warn at exactly WARN_DAYS whole days', () => {
    const created = t0
    const now = t0 + ADMIN_STALE_NEW_WARN_DAYS * ADMIN_STALE_NEW_MS_PER_DAY
    expect(staleNewBadgeState('new', created, now)).toEqual({
      days: ADMIN_STALE_NEW_WARN_DAYS,
      severity: 'warn',
    })
  })

  test('warn between warn and danger thresholds', () => {
    const created = t0
    const now = t0 + (ADMIN_STALE_NEW_DANGER_DAYS - 1) * ADMIN_STALE_NEW_MS_PER_DAY
    expect(staleNewBadgeState('new', created, now)).toEqual({
      days: ADMIN_STALE_NEW_DANGER_DAYS - 1,
      severity: 'warn',
    })
  })

  test('danger at exactly DANGER_DAYS whole days', () => {
    const created = t0
    const now = t0 + ADMIN_STALE_NEW_DANGER_DAYS * ADMIN_STALE_NEW_MS_PER_DAY
    expect(staleNewBadgeState('new', created, now)).toEqual({
      days: ADMIN_STALE_NEW_DANGER_DAYS,
      severity: 'danger',
    })
  })

  test('danger when many days stale', () => {
    const created = t0
    const now = t0 + 90 * ADMIN_STALE_NEW_MS_PER_DAY
    expect(staleNewBadgeState('new', created, now)).toEqual({ days: 90, severity: 'danger' })
  })

  test('null when createdAt is NaN', () => {
    expect(staleNewBadgeState('new', Number.NaN, t0)).toBeNull()
  })

  test('null when created is in the future (negative whole days)', () => {
    const created = t0 + 5 * ADMIN_STALE_NEW_MS_PER_DAY
    const now = t0
    expect(staleNewBadgeState('new', created, now)).toBeNull()
  })
})

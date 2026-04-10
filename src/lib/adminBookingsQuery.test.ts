import { describe, expect, test } from 'bun:test'
import {
  ADMIN_BOOKINGS_DEFAULT_LIMIT,
  ADMIN_BOOKINGS_MAX_LIMIT,
  getAdminExportMaxRows,
  parseAdminBookingsListParams,
} from './adminBookingsQuery'

describe('parseAdminBookingsListParams', () => {
  test('defaults when limit and offset omitted', () => {
    const r = parseAdminBookingsListParams({})
    expect(r).toEqual({
      ok: true,
      limit: ADMIN_BOOKINGS_DEFAULT_LIMIT,
      offset: 0,
    })
  })

  test('parses valid limit and offset', () => {
    expect(parseAdminBookingsListParams({ limit: '10', offset: '20' })).toEqual({
      ok: true,
      limit: 10,
      offset: 20,
    })
  })

  test('rejects negative offset', () => {
    const r = parseAdminBookingsListParams({ offset: '-1' })
    expect(r.ok).toBe(false)
    if (!r.ok) expect(r.message).toContain('offset')
  })

  test('clamps limit above max', () => {
    const r = parseAdminBookingsListParams({
      limit: String(ADMIN_BOOKINGS_MAX_LIMIT + 999),
      offset: '0',
    })
    expect(r.ok).toBe(true)
    if (r.ok) expect(r.limit).toBe(ADMIN_BOOKINGS_MAX_LIMIT)
  })

  test('invalid limit string falls back to default', () => {
    const r = parseAdminBookingsListParams({ limit: 'nope', offset: '0' })
    expect(r.ok).toBe(true)
    if (r.ok) expect(r.limit).toBe(ADMIN_BOOKINGS_DEFAULT_LIMIT)
  })

  test('limit zero falls back to default', () => {
    const r = parseAdminBookingsListParams({ limit: '0', offset: '0' })
    expect(r.ok).toBe(true)
    if (r.ok) expect(r.limit).toBe(ADMIN_BOOKINGS_DEFAULT_LIMIT)
  })
})

describe('getAdminExportMaxRows', () => {
  test('respects ADMIN_EXPORT_MAX_ROWS', () => {
    const prev = process.env.ADMIN_EXPORT_MAX_ROWS
    process.env.ADMIN_EXPORT_MAX_ROWS = '500'
    expect(getAdminExportMaxRows()).toBe(500)
    if (prev === undefined) delete process.env.ADMIN_EXPORT_MAX_ROWS
    else process.env.ADMIN_EXPORT_MAX_ROWS = prev
  })

  test('invalid env falls back to default', () => {
    const prev = process.env.ADMIN_EXPORT_MAX_ROWS
    process.env.ADMIN_EXPORT_MAX_ROWS = 'not-a-number'
    expect(getAdminExportMaxRows()).toBe(10_000)
    if (prev === undefined) delete process.env.ADMIN_EXPORT_MAX_ROWS
    else process.env.ADMIN_EXPORT_MAX_ROWS = prev
  })
})

import { describe, expect, test } from 'bun:test'
import { isAdminBookingExportAllowed } from './adminBookingExport'

describe('isAdminBookingExportAllowed', () => {
  test('allows export when NODE_ENV is not production', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'development'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      expect(isAdminBookingExportAllowed()).toBe(true)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('denies in production when ALLOW_ADMIN_BOOKING_EXPORT is unset', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'production'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      expect(isAdminBookingExportAllowed()).toBe(false)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('denies in production when ALLOW_ADMIN_BOOKING_EXPORT is not exactly true', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'production'
      process.env.ALLOW_ADMIN_BOOKING_EXPORT = '1'
      expect(isAdminBookingExportAllowed()).toBe(false)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('allows in production when ALLOW_ADMIN_BOOKING_EXPORT=true', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'production'
      process.env.ALLOW_ADMIN_BOOKING_EXPORT = 'true'
      expect(isAdminBookingExportAllowed()).toBe(true)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })
})

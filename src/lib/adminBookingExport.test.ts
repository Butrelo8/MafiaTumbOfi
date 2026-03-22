import { describe, expect, test } from 'bun:test'
import { isAdminBookingExportAllowed } from './adminBookingExport'

describe('isAdminBookingExportAllowed', () => {
  test('allows export when NODE_ENV is development', () => {
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

  test('denies when NODE_ENV is unset', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      delete process.env.NODE_ENV
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      expect(isAdminBookingExportAllowed()).toBe(false)
    } finally {
      if (prevNode === undefined) delete process.env.NODE_ENV
      else process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })

  test('denies when NODE_ENV is test (not development)', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'test'
      delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      expect(isAdminBookingExportAllowed()).toBe(false)
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

  test('allows when ALLOW_ADMIN_BOOKING_EXPORT=true even if NODE_ENV is test', () => {
    const prevNode = process.env.NODE_ENV
    const prevAllow = process.env.ALLOW_ADMIN_BOOKING_EXPORT
    try {
      process.env.NODE_ENV = 'test'
      process.env.ALLOW_ADMIN_BOOKING_EXPORT = 'true'
      expect(isAdminBookingExportAllowed()).toBe(true)
    } finally {
      process.env.NODE_ENV = prevNode
      if (prevAllow === undefined) delete process.env.ALLOW_ADMIN_BOOKING_EXPORT
      else process.env.ALLOW_ADMIN_BOOKING_EXPORT = prevAllow
    }
  })
})

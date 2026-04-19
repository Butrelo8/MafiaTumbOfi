import { describe, expect, test } from 'bun:test'
import { isAdminDeleteAllBookingsAllowed } from './adminDeleteAllBookings'

describe('isAdminDeleteAllBookingsAllowed', () => {
  test('true in development when flag unset', () => {
    const prev = process.env.NODE_ENV
    const prevFlag = process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    try {
      process.env.NODE_ENV = 'development'
      delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
      expect(isAdminDeleteAllBookingsAllowed()).toBe(true)
    } finally {
      process.env.NODE_ENV = prev
      if (prevFlag === undefined) delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
      else process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = prevFlag
    }
  })

  test('false in production when flag unset', () => {
    const prev = process.env.NODE_ENV
    const prevFlag = process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    try {
      process.env.NODE_ENV = 'production'
      delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
      expect(isAdminDeleteAllBookingsAllowed()).toBe(false)
    } finally {
      process.env.NODE_ENV = prev
      if (prevFlag === undefined) delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
      else process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = prevFlag
    }
  })

  test('true in production when flag true', () => {
    const prev = process.env.NODE_ENV
    const prevFlag = process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
    try {
      process.env.NODE_ENV = 'production'
      process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = 'true'
      expect(isAdminDeleteAllBookingsAllowed()).toBe(true)
    } finally {
      process.env.NODE_ENV = prev
      if (prevFlag === undefined) delete process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS
      else process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS = prevFlag
    }
  })
})

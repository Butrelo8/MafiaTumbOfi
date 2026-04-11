import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { clerkIdIsConfiguredAdmin, getConfiguredAdminClerkId } from './adminClerkConfig'

describe('adminClerkConfig', () => {
  let prev: string | undefined

  beforeEach(() => {
    prev = process.env.ADMIN_CLERK_ID
  })

  afterEach(() => {
    if (prev === undefined) delete process.env.ADMIN_CLERK_ID
    else process.env.ADMIN_CLERK_ID = prev
  })

  test('getConfiguredAdminClerkId returns null when unset', () => {
    delete process.env.ADMIN_CLERK_ID
    expect(getConfiguredAdminClerkId()).toBeNull()
  })

  test('getConfiguredAdminClerkId trims whitespace', () => {
    process.env.ADMIN_CLERK_ID = '  user_x  '
    expect(getConfiguredAdminClerkId()).toBe('user_x')
  })

  test('getConfiguredAdminClerkId returns null for empty string', () => {
    process.env.ADMIN_CLERK_ID = '   '
    expect(getConfiguredAdminClerkId()).toBeNull()
  })

  test('clerkIdIsConfiguredAdmin is false when env unset', () => {
    delete process.env.ADMIN_CLERK_ID
    expect(clerkIdIsConfiguredAdmin('user_x')).toBe(false)
  })

  test('clerkIdIsConfiguredAdmin matches exact id after trim', () => {
    process.env.ADMIN_CLERK_ID = '  user_x  '
    expect(clerkIdIsConfiguredAdmin('user_x')).toBe(true)
    expect(clerkIdIsConfiguredAdmin('user_y')).toBe(false)
  })
})

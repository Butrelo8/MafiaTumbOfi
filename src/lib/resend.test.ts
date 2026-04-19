import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import type { Resend } from 'resend'
import { getResend, setResendForTesting } from './resend'

beforeEach(() => {
  setResendForTesting(null)
})

afterEach(() => {
  setResendForTesting(null)
})

describe('getResend / setResendForTesting', () => {
  test('override returns same client without RESEND_API_KEY', () => {
    const prev = process.env.RESEND_API_KEY
    delete process.env.RESEND_API_KEY
    const mock = {
      emails: {
        send: async () => ({ data: { id: 'x' }, error: null }),
      },
    } as Resend
    setResendForTesting(mock)
    expect(getResend()).toBe(mock)
    if (prev !== undefined) process.env.RESEND_API_KEY = prev
  })

  test('without override and missing RESEND_API_KEY throws', () => {
    const prev = process.env.RESEND_API_KEY
    delete process.env.RESEND_API_KEY
    expect(() => getResend()).toThrow('RESEND_API_KEY')
    if (prev !== undefined) process.env.RESEND_API_KEY = prev
  })
})

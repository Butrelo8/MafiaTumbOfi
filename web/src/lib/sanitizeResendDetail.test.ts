import { describe, expect, test } from 'bun:test'
import {
  MAX_RESEND_DETAIL_LEN,
  sanitizeResendDetail,
} from './sanitizeResendDetail'

describe('sanitizeResendDetail', () => {
  test('returns null for null and empty', () => {
    expect(sanitizeResendDetail(null)).toBeNull()
    expect(sanitizeResendDetail('')).toBeNull()
  })

  test('trims whitespace', () => {
    expect(sanitizeResendDetail('  NOT_FOUND: no row  ')).toBe('NOT_FOUND: no row')
  })

  test('strips ASCII control characters', () => {
    expect(sanitizeResendDetail('a\nb\tc')).toBe('abc')
    expect(sanitizeResendDetail('x\x7Fy')).toBe('xy')
  })

  test('strips HTML-sensitive characters', () => {
    expect(sanitizeResendDetail(`BAD: <img src=x onerror=alert(1)>`)).toBe(
      'BAD: img src=x onerror=alert(1)',
    )
    expect(sanitizeResendDetail(`QUOTE: "foo" 'bar' \`baz\``)).toBe('QUOTE: foo bar baz')
  })

  test('truncates to MAX_RESEND_DETAIL_LEN', () => {
    const long = 'x'.repeat(MAX_RESEND_DETAIL_LEN + 50)
    const out = sanitizeResendDetail(long)
    expect(out).toHaveLength(MAX_RESEND_DETAIL_LEN)
    expect(out).toBe('x'.repeat(MAX_RESEND_DETAIL_LEN))
  })

  test('returns null when nothing remains after cleaning', () => {
    expect(sanitizeResendDetail('   \n\t ')).toBeNull()
    expect(sanitizeResendDetail('<>`"\'')).toBeNull()
  })

  test('preserves typical API error lines', () => {
    expect(sanitizeResendDetail('SMTP_ERROR: Connection refused')).toBe(
      'SMTP_ERROR: Connection refused',
    )
  })
})

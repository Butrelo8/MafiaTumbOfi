/** Max length for `resendDetail` shown in the admin banner (URL param is defense-in-depth). */
export const MAX_RESEND_DETAIL_LEN = 120

const CONTROL_AND_HTMLISH = /[\x00-\x1F\x7F<>"'`]/g

/**
 * Normalizes `resendDetail` from query params before embedding in UI copy.
 * Returns null if missing or nothing usable remains.
 */
export function sanitizeResendDetail(raw: string | null): string | null {
  if (raw == null || raw === '') {
    return null
  }
  const cleaned = raw.trim().replace(CONTROL_AND_HTMLISH, '').slice(0, MAX_RESEND_DETAIL_LEN)
  return cleaned.length > 0 ? cleaned : null
}

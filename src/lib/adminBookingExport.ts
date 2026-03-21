/**
 * In production only: full booking export requires explicit opt-in (reduces PII blast radius).
 * Non-production defaults to allowed for local/staging DX.
 */
export function isAdminBookingExportAllowed(): boolean {
  if (process.env.NODE_ENV !== 'production') return true
  return process.env.ALLOW_ADMIN_BOOKING_EXPORT === 'true'
}

/**
 * Full booking export is default-deny unless explicitly allowed:
 * - `ALLOW_ADMIN_BOOKING_EXPORT=true` (any NODE_ENV), or
 * - `NODE_ENV=development` for local DX.
 * Mis-set or unset NODE_ENV on a prod-like host no longer implicitly enables export.
 */
export function isAdminBookingExportAllowed(): boolean {
  if (process.env.ALLOW_ADMIN_BOOKING_EXPORT === 'true') return true
  if (process.env.NODE_ENV === 'development') return true
  return false
}

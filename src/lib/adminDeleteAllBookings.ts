/**
 * Hard-delete all rows in `bookings` is default-deny unless explicitly allowed:
 * - `ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true` (any NODE_ENV), or
 * - `NODE_ENV=development` for local DX.
 */
export const ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE = 'DELETE_ALL_BOOKINGS' as const

export function isAdminDeleteAllBookingsAllowed(): boolean {
  if (process.env.ALLOW_ADMIN_DELETE_ALL_BOOKINGS === 'true') return true
  if (process.env.NODE_ENV === 'development') return true
  return false
}

/** Debounce delay for admin booking name/email/phone search (ms). */
export const ADMIN_BOOKING_SEARCH_DEBOUNCE_MS = 200

export type AdminBookingSearchFields = {
  name?: unknown
  email?: unknown
  phone?: unknown | null
}

/**
 * Trim + lowercase for case-insensitive `includes` matching.
 */
export function normalizeAdminBookingSearchQuery(raw: string): string {
  return raw.trim().toLowerCase()
}

/**
 * When `normalizedQuery` is empty, every row matches (caller chains AND with pipeline).
 */
export function bookingMatchesAdminSearchQuery(
  booking: AdminBookingSearchFields,
  normalizedQuery: string,
): boolean {
  if (normalizedQuery === '') return true
  const hay = (v: unknown) => String(v ?? '').toLowerCase()
  return [booking.name, booking.email, booking.phone].some((v) =>
    hay(v).includes(normalizedQuery),
  )
}

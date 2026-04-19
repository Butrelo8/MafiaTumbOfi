/** `sessionStorage` key after successful `POST /api/booking` before redirect to `/booking/gracias`. */
export const BOOKING_THANKS_SESSION_KEY = 'mto_booking_thanks' as const

export type BookingThanksConfirmation = 'sent' | 'pending' | 'default'

export type BookingThanksStored = {
  confirmation: BookingThanksConfirmation
}

/** Normalize API `confirmation` for storage (only `sent` / `pending` pass through; else `default`). */
export function normalizeBookingConfirmation(
  raw: unknown,
): BookingThanksConfirmation {
  if (raw === 'sent') return 'sent'
  if (raw === 'pending') return 'pending'
  return 'default'
}

/** Parse stored JSON; returns `null` if missing or invalid. */
export function parseBookingThanksStored(raw: string | null): BookingThanksStored | null {
  if (raw == null || raw === '') return null
  try {
    const o = JSON.parse(raw) as unknown
    if (!o || typeof o !== 'object' || !('confirmation' in o)) return null
    const c = (o as { confirmation: unknown }).confirmation
    if (c === 'sent' || c === 'pending' || c === 'default') {
      return { confirmation: c }
    }
    return null
  } catch {
    return null
  }
}

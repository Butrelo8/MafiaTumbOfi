/**
 * Sales / follow-up pipeline for bookings (separate from email confirmation `status`).
 * No Zod here so `web/` can import labels safely.
 */

export const BOOKING_PIPELINE_STATUS_VALUES = ['new', 'contacted', 'closed'] as const
export type BookingPipelineStatus = (typeof BOOKING_PIPELINE_STATUS_VALUES)[number]

export const PIPELINE_STATUS_LABELS: Record<BookingPipelineStatus, string> = {
  new: 'Nuevo',
  contacted: 'Contactado',
  closed: 'Cerrado',
}

export function isBookingPipelineStatus(value: string): value is BookingPipelineStatus {
  return (BOOKING_PIPELINE_STATUS_VALUES as readonly string[]).includes(value)
}

/** Display label; unknown legacy values pass through. */
export function formatPipelineStatusLabel(value: string | null | undefined): string {
  if (value == null || value === '') return PIPELINE_STATUS_LABELS.new
  if (isBookingPipelineStatus(value)) return PIPELINE_STATUS_LABELS[value]
  return value
}

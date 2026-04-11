/**
 * Lead score + priority for `bookings` — pure helpers, no Zod (safe to import from `web/`).
 * Scores are computed once at insert and stored; tuning weights does not rewrite history.
 */

import { BOOKING_BUDGET_SORT_RANK } from './bookingBudget'
import { PRICE_CONSTANTS } from './estimatedPriceRange'

export const LEAD_PRIORITY_VALUES = ['low', 'medium', 'high'] as const
export type LeadPriority = (typeof LEAD_PRIORITY_VALUES)[number]

export const LEAD_PRIORITY_LABELS: Record<LeadPriority, string> = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
}

export interface BookingLeadScoreInput {
  budget?: string | null
  city?: string | null
  eventType?: string | null
  duration?: string | null
  showType?: string | null
  attendees?: string | null
  venueSound?: string | null
}

function normalizeCity(city?: string | null): string {
  return (city || '').trim().toLowerCase()
}

function cityPoints(city?: string | null): number {
  const n = normalizeCity(city)
  if (!n) return 25
  if (PRICE_CONSTANTS.localCities.has(n)) return 45
  return 85
}

const ATTENDEE_POINTS: Record<string, number> = {
  menos_100: 30,
  '100_300': 55,
  '300_500': 75,
  '500_1000': 90,
  mas_1000: 100,
}

const DURATION_POINTS: Record<string, number> = {
  '1h': 35,
  '2h': 55,
  '3h_mas': 75,
  no_definido: 25,
}

function budgetPoints(budget?: string | null): number {
  const rank = BOOKING_BUDGET_SORT_RANK[budget ?? ''] ?? 0
  return rank * 130
}

function attendeesPoints(attendees?: string | null): number {
  if (!attendees || attendees.trim() === '') return 20
  return ATTENDEE_POINTS[attendees] ?? 25
}

function durationPoints(duration?: string | null): number {
  if (!duration || duration.trim() === '') return 15
  return DURATION_POINTS[duration] ?? 25
}

/** Small bump for structured intent (non-PII). */
function extrasPoints(input: BookingLeadScoreInput): number {
  let p = 0
  if (input.showType && input.showType.trim().length > 0) p += 10
  if (input.venueSound && input.venueSound.trim().length > 0) p += 8
  if (input.eventType && input.eventType.trim().length > 0) p += 12
  return Math.min(p, 40)
}

function priorityFromScore(score: number): LeadPriority {
  if (score >= 400) return 'high'
  if (score >= 200) return 'medium'
  return 'low'
}

/**
 * Compute stored lead score (0–1000) and priority band from persisted booking fields.
 */
export function computeBookingLeadScore(input: BookingLeadScoreInput): {
  leadScore: number
  leadPriority: LeadPriority
} {
  let score =
    budgetPoints(input.budget) +
    attendeesPoints(input.attendees) +
    durationPoints(input.duration) +
    cityPoints(input.city) +
    extrasPoints(input)

  score = Math.min(1000, Math.max(0, Math.round(score)))
  return { leadScore: score, leadPriority: priorityFromScore(score) }
}

export function isLeadPriority(value: string): value is LeadPriority {
  return (LEAD_PRIORITY_VALUES as readonly string[]).includes(value)
}

export function formatLeadPriorityLabel(value: string | null | undefined): string {
  if (value == null || value === '') return '-'
  if (isLeadPriority(value)) return LEAD_PRIORITY_LABELS[value]
  return value
}

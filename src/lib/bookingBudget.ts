/**
 * Single source of truth for booking budget tiers (API + Astro).
 * Keep Zod schemas in `src/routes/booking.ts` only — this module has no zod dependency so `web/` can import it.
 */

export const BOOKING_BUDGET_VALUES = [
  'menos_15k',
  '15k_30k',
  '30k_50k',
  '50k_100k',
  'mas_100k',
] as const

export type BookingBudget = (typeof BOOKING_BUDGET_VALUES)[number]

export const BUDGET_LABELS: Record<BookingBudget, string> = {
  menos_15k: 'Hasta $15,000 MXN',
  '15k_30k': '$15,000 – $30,000 MXN',
  '30k_50k': '$30,000 – $50,000 MXN',
  '50k_100k': '$50,000 – $100,000 MXN',
  mas_100k: 'Más de $100,000 MXN',
}

/** Contextual copy under the budget `<select>` on the public booking page (per tier). */
export const BUDGET_HINTS: Record<BookingBudget, string> = {
  menos_15k:
    'Rango típico para eventos más íntimos o acústicos — armamos una propuesta a tu medida.',
  '15k_30k': 'Buen punto de partida para cotizar con detalle sin apuros.',
  '30k_50k': 'Aquí suele entrar show completo con logística base en la zona.',
  '50k_100k': 'Hay margen para producción, transporte y extras según tu fecha.',
  mas_100k: 'Gracias por la confianza — podemos coordinar una llamada para afinar todo.',
}

/** First `<option value="">` label on `/booking` (not a tier). */
export const BOOKING_BUDGET_EMPTY_OPTION_LABEL = 'Lo vemos después — sin problema'

/** Ordered pairs for `<option>` elements (excludes empty value). */
export const BOOKING_BUDGET_OPTIONS: readonly { value: BookingBudget; label: string }[] =
  BOOKING_BUDGET_VALUES.map((value) => ({ value, label: BUDGET_LABELS[value] }))

/**
 * Client script lookup: empty string + each tier (matches `<select>` values).
 */
export const BOOKING_BUDGET_HINTS_WITH_EMPTY: Record<string, string> = {
  '': '',
  ...BUDGET_HINTS,
}

/**
 * Admin table sort: higher rank = higher budget band. `''` = no budget / unknown.
 */
export const BOOKING_BUDGET_SORT_RANK: Record<string, number> = {
  '': 0,
  ...Object.fromEntries(BOOKING_BUDGET_VALUES.map((value, index) => [value, index + 1])),
}

export function isBookingBudget(value: string): value is BookingBudget {
  return (BOOKING_BUDGET_VALUES as readonly string[]).includes(value)
}

/** Admin / display: human label, or raw value if unknown (legacy row). */
export function formatBudgetLabel(value: string | null | undefined): string {
  if (value == null || value === '') return '-'
  if (isBookingBudget(value)) return BUDGET_LABELS[value]
  return value
}

const UNKNOWN_SORT = Number.MAX_SAFE_INTEGER

/**
 * Milliseconds since epoch for sorting admin booking rows by `event_date` text.
 * Missing or unparseable values sort last in ascending order.
 */
export function eventDateSortKeyMs(raw: string | null | undefined): number {
  if (raw == null) return UNKNOWN_SORT
  const s = raw.trim()
  if (s === '' || s === '-') return UNKNOWN_SORT
  const t = Date.parse(s)
  return Number.isFinite(t) ? t : UNKNOWN_SORT
}

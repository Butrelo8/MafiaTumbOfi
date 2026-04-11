/**
 * Query parsing and limits for admin booking list + export routes.
 */

export const ADMIN_BOOKINGS_DEFAULT_LIMIT = 50
export const ADMIN_BOOKINGS_MAX_LIMIT = 200

const DEFAULT_EXPORT_MAX_ROWS = 10_000
/** Hard ceiling so a mis-set env cannot OOM the API process. */
const ABSOLUTE_EXPORT_MAX_ROWS = 50_000

function parseLimit(raw: string | undefined): number {
  if (raw === undefined || raw === '') return ADMIN_BOOKINGS_DEFAULT_LIMIT
  const n = Number.parseInt(raw, 10)
  if (!Number.isFinite(n)) return ADMIN_BOOKINGS_DEFAULT_LIMIT
  if (n < 1) return ADMIN_BOOKINGS_DEFAULT_LIMIT
  return Math.min(n, ADMIN_BOOKINGS_MAX_LIMIT)
}

function parseOffset(raw: string | undefined): { ok: true; offset: number } | { ok: false } {
  if (raw === undefined || raw === '') return { ok: true, offset: 0 }
  const n = Number.parseInt(raw, 10)
  if (!Number.isFinite(n) || n < 0) return { ok: false }
  return { ok: true, offset: n }
}

export function parseAdminBookingsListParams(query: {
  limit?: string
  offset?: string
}): { ok: true; limit: number; offset: number } | { ok: false; message: string } {
  const off = parseOffset(query.offset)
  if (!off.ok) {
    return { ok: false, message: 'offset must be a non-negative integer' }
  }
  const limit = parseLimit(query.limit)
  return { ok: true, limit, offset: off.offset }
}

/**
 * Max rows returned in one GET /api/admin/export/bookings response.
 * Override with ADMIN_EXPORT_MAX_ROWS (clamped to ABSOLUTE_EXPORT_MAX_ROWS).
 */
export function getAdminExportMaxRows(): number {
  const raw = process.env.ADMIN_EXPORT_MAX_ROWS
  if (raw === undefined || raw === '') return DEFAULT_EXPORT_MAX_ROWS
  const n = Number.parseInt(raw, 10)
  if (!Number.isFinite(n) || n < 1) return DEFAULT_EXPORT_MAX_ROWS
  return Math.min(n, ABSOLUTE_EXPORT_MAX_ROWS)
}

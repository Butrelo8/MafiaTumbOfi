import { formatBudgetLabel } from '../../../src/lib/bookingBudget'
import { formatLeadPriorityLabel } from '../../../src/lib/bookingLeadScore'
import { formatPipelineStatusLabel } from '../../../src/lib/bookingPipeline'

/** Spanish headers aligned with admin table + drawer fields (fixed column order). */
export const ADMIN_BOOKING_CSV_HEADERS = [
  'ID',
  'Nombre',
  'Correo',
  'Teléfono',
  'Fecha evento',
  'Ciudad',
  'Tipo evento',
  'Duración',
  'Tipo show',
  'Asistentes',
  'Lugar sonido',
  'Presupuesto',
  'Prioridad',
  'Lead score',
  'Rango estimado',
  'Mensaje',
  'Status correo',
  'Seguimiento',
  'Intentos confirmación',
  'Último error confirmación',
  'Notas internas',
  'Drip2 programado',
  'Drip2 enviado',
  'Drip3 programado',
  'Drip3 enviado',
  'Creado',
] as const

function str(value: unknown): string {
  if (value == null || value === '') return ''
  return String(value)
}

function toIsoUtc(value: unknown): string {
  if (value == null || value === '') return ''
  if (value instanceof Date) {
    const t = value.getTime()
    return Number.isNaN(t) ? '' : new Date(t).toISOString()
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    const d = new Date(value)
    return Number.isNaN(d.getTime()) ? '' : d.toISOString()
  }
  if (typeof value === 'string') {
    const d = new Date(value)
    return Number.isNaN(d.getTime()) ? value : d.toISOString()
  }
  return str(value)
}

/**
 * RFC 4180-style field escaping for CSV (comma, quote, CR/LF → quoted + doubled quotes).
 */
export function escapeCsvField(raw: unknown): string {
  if (raw === null || raw === undefined) return ''
  const s = String(raw)
  if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

/** One data row as plain strings (before per-field escaping). */
export function bookingToCsvCells(booking: Record<string, unknown>): string[] {
  const budgetLabel = formatBudgetLabel(
    typeof booking.budget === 'string' || booking.budget == null
      ? (booking.budget as string | null)
      : str(booking.budget) || null,
  )
  const priorityLabel = formatLeadPriorityLabel(
    typeof booking.leadPriority === 'string' || booking.leadPriority == null
      ? (booking.leadPriority as string | null)
      : str(booking.leadPriority) || null,
  )
  const pipelineLabel = formatPipelineStatusLabel(
    typeof booking.pipelineStatus === 'string' ? booking.pipelineStatus : undefined,
  )

  const attempts =
    booking.status === 'failed' ? '' : str(booking.confirmationAttempts)

  return [
    str(booking.id),
    str(booking.name),
    str(booking.email),
    str(booking.phone),
    str(booking.eventDate),
    str(booking.city),
    str(booking.eventType),
    str(booking.duration),
    str(booking.showType),
    str(booking.attendees),
    str(booking.venueSound),
    budgetLabel,
    priorityLabel,
    booking.leadScore == null ? '' : str(booking.leadScore),
    str(booking.estimatedPriceRange),
    str(booking.message),
    str(booking.status),
    pipelineLabel,
    attempts,
    str(booking.confirmationLastError),
    str(booking.internalNotes),
    toIsoUtc(booking.drip2DueAt),
    toIsoUtc(booking.drip2SentAt),
    toIsoUtc(booking.drip3DueAt),
    toIsoUtc(booking.drip3SentAt),
    toIsoUtc(booking.createdAt),
  ]
}

/**
 * Full CSV document (UTF-8 BOM + CRLF) for the given booking rows **in caller order**
 * (e.g. DOM order after sort/filter).
 */
export function buildAdminBookingsCsv(
  bookingsOrdered: ReadonlyArray<Record<string, unknown>>,
): string {
  const headerLine = ADMIN_BOOKING_CSV_HEADERS.map((h) => escapeCsvField(h)).join(',')
  const bodyLines = bookingsOrdered.map((b) =>
    bookingToCsvCells(b).map((c) => escapeCsvField(c)).join(','),
  )
  return `\uFEFF${[headerLine, ...bodyLines].join('\r\n')}\r\n`
}

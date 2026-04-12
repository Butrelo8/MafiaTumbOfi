import { formatBudgetLabel } from '../../../src/lib/bookingBudget'
import { formatLeadPriorityLabel } from '../../../src/lib/bookingLeadScore'
import { formatPipelineStatusLabel } from '../../../src/lib/bookingPipeline'

const EMPTY = '—'

function asString(value: unknown, fallback = EMPTY): string {
  if (value == null || value === '') return fallback
  return String(value)
}

/** Format API/JSON date-ish values for admin drawer (es-MX). */
export function formatAdminDrawerDate(value: unknown): string {
  if (value == null || value === '') return EMPTY
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? EMPTY : value.toLocaleString('es-MX')
  }
  if (typeof value === 'number') {
    const d = new Date(value)
    return Number.isNaN(d.getTime()) ? EMPTY : d.toLocaleString('es-MX')
  }
  const d = new Date(String(value))
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('es-MX')
}

export type DrawerFieldRow = { label: string; value: string }

/**
 * Ordered label/value pairs for the admin booking detail drawer.
 * Accepts a plain object (SSR `bookings` row from API JSON).
 */
export function buildAdminBookingDrawerRows(
  booking: Record<string, unknown>,
): DrawerFieldRow[] {
  const pipelineLabel = formatPipelineStatusLabel(
    typeof booking.pipelineStatus === 'string' ? booking.pipelineStatus : undefined,
  )

  const budgetLabel =
    typeof booking.budget === 'string' || booking.budget == null
      ? formatBudgetLabel(booking.budget ?? null)
      : asString(booking.budget)

  const priorityLabel =
    typeof booking.leadPriority === 'string' || booking.leadPriority == null
      ? formatLeadPriorityLabel(booking.leadPriority ?? null)
      : asString(booking.leadPriority)

  return [
    { label: 'ID', value: asString(booking.id, '') },
    { label: 'Nombre', value: asString(booking.name) },
    { label: 'Correo', value: asString(booking.email) },
    { label: 'Teléfono', value: asString(booking.phone) },
    { label: 'Fecha del evento', value: asString(booking.eventDate) },
    { label: 'Ciudad', value: asString(booking.city) },
    { label: 'Tipo de evento', value: asString(booking.eventType) },
    { label: 'Duración', value: asString(booking.duration) },
    { label: 'Tipo de show', value: asString(booking.showType) },
    { label: 'Asistentes', value: asString(booking.attendees) },
    { label: 'Lugar / sonido', value: asString(booking.venueSound) },
    { label: 'Presupuesto', value: budgetLabel },
    { label: 'Lead score', value: asString(booking.leadScore) },
    { label: 'Prioridad', value: priorityLabel },
    { label: 'Rango estimado', value: asString(booking.estimatedPriceRange) },
    { label: 'Mensaje', value: asString(booking.message) },
    { label: 'Estado (correo)', value: asString(booking.status) },
    { label: 'Seguimiento', value: pipelineLabel },
    {
      label: 'Intentos de confirmación',
      value: asString(booking.confirmationAttempts),
    },
    {
      label: 'Último error de confirmación',
      value: asString(booking.confirmationLastError),
    },
    { label: 'Notas internas', value: asString(booking.internalNotes) },
    { label: 'Drip 2 programado', value: formatAdminDrawerDate(booking.drip2DueAt) },
    { label: 'Drip 2 enviado', value: formatAdminDrawerDate(booking.drip2SentAt) },
    { label: 'Drip 3 programado', value: formatAdminDrawerDate(booking.drip3DueAt) },
    { label: 'Drip 3 enviado', value: formatAdminDrawerDate(booking.drip3SentAt) },
    { label: 'Creado', value: formatAdminDrawerDate(booking.createdAt) },
  ]
}

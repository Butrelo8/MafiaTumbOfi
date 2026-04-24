import { and, asc, count, desc, eq, gte, sql } from 'drizzle-orm'
import { Hono } from 'hono'
import { z } from 'zod'
import type { AdminTourRow } from '../data/tourDates'
import { db } from '../db'
import { bookings, tourDates } from '../db/schema'
import { isAdminBookingExportAllowed } from '../lib/adminBookingExport'
import { getAdminExportMaxRows, parseAdminBookingsListParams } from '../lib/adminBookingsQuery'
import {
  ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE,
  isAdminDeleteAllBookingsAllowed,
} from '../lib/adminDeleteAllBookings'
import { BOOKING_PIPELINE_STATUS_VALUES } from '../lib/bookingPipeline'
import { bookingNotSoftDeleted } from '../lib/bookingSoftDeleteFilter'
import { errorResponse, successResponse } from '../lib/errors'
import { estimatedPriceRange } from '../lib/estimatedPriceRange'
import { getResend } from '../lib/resend'
import { parseJsonRequestBody } from '../lib/parseJsonRequestBody'
import { logServerError, logServerErrorDetails } from '../lib/safeLog'
import { spanishErrorMap } from '../lib/zod-es'
import { adminAuth } from '../middleware/adminAuth'
import { authMiddleware } from '../middleware/auth'

const MAX_INTERNAL_NOTES_LEN = 10_000

const deleteAllBookingsBodySchema = z
  .object({
    dryRun: z.boolean().optional(),
    confirm: z.string().optional(),
  })
  .superRefine((val, ctx) => {
    if (val.dryRun === true) return
    if (val.confirm !== ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Se requiere confirm: "${ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE}"`,
        path: ['confirm'],
      })
    }
  })

const patchBookingBodySchema = z
  .object({
    pipelineStatus: z.enum(BOOKING_PIPELINE_STATUS_VALUES).optional(),
    internalNotes: z.union([z.string().max(MAX_INTERNAL_NOTES_LEN), z.null()]).optional(),
  })
  .superRefine((val, ctx) => {
    if (val.pipelineStatus === undefined && val.internalNotes === undefined) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Se requiere pipelineStatus y/o internalNotes',
        path: [],
      })
    }
  })

function parseRequiredBookingId(raw: string | undefined): number | null {
  if (raw === undefined || raw === '') return null
  const id = Number(raw)
  if (!Number.isInteger(id) || id <= 0) return null
  return id
}

export const adminRoutes = new Hono()

adminRoutes.use('*', authMiddleware)
adminRoutes.use('*', adminAuth)

adminRoutes.get('/bookings', async (c) => {
  const parsed = parseAdminBookingsListParams({
    limit: c.req.query('limit'),
    offset: c.req.query('offset'),
  })
  if (!parsed.ok) {
    return errorResponse(c, 400, 'VALIDATION_ERROR', parsed.message)
  }
  const { limit, offset } = parsed

  try {
    const [countRow] = await db
      .select({ total: count() })
      .from(bookings)
      .where(bookingNotSoftDeleted)
    const total = countRow?.total ?? 0

    const leadPriorityRank = sql`(CASE ${bookings.leadPriority} WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END)`

    const pageRows = await db
      .select()
      .from(bookings)
      .where(bookingNotSoftDeleted)
      .orderBy(asc(leadPriorityRank), desc(bookings.createdAt))
      .limit(limit)
      .offset(offset)

    const enriched = pageRows.map((b) => ({
      ...b,
      estimatedPriceRange: estimatedPriceRange({
        city: b.city,
        duration: b.duration,
        attendees: b.attendees,
      }),
    }))

    return successResponse(c, {
      bookings: enriched,
      total,
      limit,
      offset,
      hasMore: offset + enriched.length < total,
    })
  } catch (error) {
    logServerError('admin', 'FETCH_BOOKINGS_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to fetch bookings')
  }
})

function mapTourRowToAdmin(row: typeof tourDates.$inferSelect): AdminTourRow {
  const s = row.status
  const status: AdminTourRow['status'] = s === 'tentative' || s === 'cancelled' ? s : 'confirmed'
  return {
    id: row.id,
    date: row.date,
    time: row.time ?? null,
    city: row.city,
    venue: row.venue,
    status,
    ticketUrl: row.ticketUrl ?? null,
    soldOut: row.soldOut,
    notes: row.internalNotes ?? null,
  }
}

adminRoutes.get('/tours', async (c) => {
  try {
    const rows = await db.select().from(tourDates).orderBy(asc(tourDates.date))
    const payload: AdminTourRow[] = rows.map(mapTourRowToAdmin)
    return successResponse(c, payload)
  } catch (error) {
    logServerError('admin', 'FETCH_TOURS_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to fetch tour dates')
  }
})

const createTourBodySchema = z
  .object({
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    time: z.union([z.string().max(32), z.literal(''), z.null()]).optional(),
    city: z.string().trim().min(1).max(200),
    venue: z.string().trim().min(1).max(300),
    status: z.enum(['confirmed', 'tentative', 'cancelled']).default('confirmed'),
    ticketUrl: z.union([z.string().url(), z.literal(''), z.null()]).optional(),
    soldOut: z.boolean().optional(),
    notes: z.union([z.string().max(10000), z.null()]).optional(),
  })
  .strict()

adminRoutes.post('/tours', async (c) => {
  let body: unknown
  try {
    body = parseJsonRequestBody(await c.req.text())
  } catch {
    return errorResponse(c, 400, 'INVALID_JSON', 'Invalid JSON body')
  }

  const parsed = createTourBodySchema.safeParse(body, { errorMap: spanishErrorMap })
  if (!parsed.success) {
    const flat = parsed.error.flatten()
    const formMsg = flat.formErrors[0]
    const fieldMsg = Object.entries(flat.fieldErrors)
      .map(([k, v]) => (Array.isArray(v) ? `${k}: ${v[0]}` : `${k}: ${v}`))
      .filter(Boolean)[0]
    return errorResponse(
      c,
      400,
      'VALIDATION_ERROR',
      fieldMsg ?? formMsg ?? 'Datos inválidos',
    )
  }

  const v = parsed.data
  const time = v.time === '' || v.time === undefined || v.time === null ? null : v.time
  const ticketUrl =
    v.ticketUrl === '' || v.ticketUrl === undefined || v.ticketUrl === null ? null : v.ticketUrl
  const notes = v.notes === '' || v.notes === undefined || v.notes === null ? null : v.notes

  try {
    const insertedRows = await db
      .insert(tourDates)
      .values({
        date: v.date,
        time,
        city: v.city,
        venue: v.venue,
        status: v.status,
        ticketUrl,
        soldOut: v.soldOut ?? false,
        internalNotes: notes,
      })
      .returning()

    const row = insertedRows[0]
    if (!row) {
      logServerError('admin', 'INSERT_TOUR_EMPTY', new Error('insert returned no row'))
      return errorResponse(c, 500, 'INTERNAL_ERROR', 'No se pudo crear la fecha')
    }
    return successResponse(c, mapTourRowToAdmin(row))
  } catch (error) {
    logServerError('admin', 'CREATE_TOUR_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'No se pudo crear la fecha')
  }
})

adminRoutes.patch('/bookings/:id', async (c) => {
  const id = parseRequiredBookingId(c.req.param('id'))
  if (id === null) {
    return errorResponse(c, 400, 'VALIDATION_ERROR', 'Invalid booking id')
  }

  let body: unknown
  try {
    body = parseJsonRequestBody(await c.req.text())
  } catch {
    return errorResponse(c, 400, 'INVALID_JSON', 'Invalid JSON body')
  }

  const parsed = patchBookingBodySchema.safeParse(body, { errorMap: spanishErrorMap })
  if (!parsed.success) {
    const flat = parsed.error.flatten()
    const formMsg = flat.formErrors[0]
    const fieldMsg = Object.entries(flat.fieldErrors)
      .map(([, v]) => (Array.isArray(v) ? v[0] : v))
      .filter(Boolean)
      .join('; ')
    const message = formMsg || fieldMsg || 'Error de validación'
    return errorResponse(c, 400, 'VALIDATION_ERROR', message)
  }

  const { pipelineStatus, internalNotes } = parsed.data

  try {
    const existing = await db
      .select()
      .from(bookings)
      .where(and(eq(bookings.id, id), bookingNotSoftDeleted))
      .get()
    if (!existing) {
      return errorResponse(c, 404, 'NOT_FOUND', 'Booking not found')
    }

    const setPayload: Partial<typeof bookings.$inferInsert> = {}
    if (pipelineStatus !== undefined) {
      setPayload.pipelineStatus = pipelineStatus
    }
    if (internalNotes !== undefined) {
      setPayload.internalNotes = internalNotes === '' ? null : internalNotes
    }

    await db.update(bookings).set(setPayload).where(eq(bookings.id, id))

    const responseData: {
      id: number
      pipelineStatus?: string
      internalNotes?: string | null
    } = { id }
    if (pipelineStatus !== undefined) {
      responseData.pipelineStatus = pipelineStatus
    }
    if (internalNotes !== undefined) {
      responseData.internalNotes = internalNotes === '' ? null : internalNotes
    }

    return successResponse(c, responseData, 200)
  } catch (error) {
    logServerError('admin', 'PATCH_BOOKING_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to update booking')
  }
})

adminRoutes.delete('/bookings/:id', async (c) => {
  const id = parseRequiredBookingId(c.req.param('id'))
  if (id === null) {
    return errorResponse(c, 400, 'VALIDATION_ERROR', 'Invalid booking id')
  }

  try {
    const existing = await db
      .select()
      .from(bookings)
      .where(and(eq(bookings.id, id), bookingNotSoftDeleted))
      .get()
    if (!existing) {
      return errorResponse(c, 404, 'NOT_FOUND', 'Booking not found')
    }

    const deletedAt = new Date()
    await db.update(bookings).set({ deletedAt }).where(eq(bookings.id, id))

    return successResponse(c, { id, deletedAt: deletedAt.toISOString() }, 200)
  } catch (error) {
    logServerError('admin', 'SOFT_DELETE_BOOKING_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to delete booking')
  }
})

/** Hard-delete every row in `bookings` (incl. soft-deleted). Admin-only; gated by env like export. */
adminRoutes.post('/bookings/delete-all', async (c) => {
  if (!isAdminDeleteAllBookingsAllowed()) {
    return errorResponse(
      c,
      403,
      'ADMIN_DELETE_ALL_BOOKINGS_DISABLED',
      'Bulk delete-all is disabled. Set ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true on the API, or NODE_ENV=development for local use.',
    )
  }

  let body: unknown
  try {
    body = parseJsonRequestBody(await c.req.text())
  } catch {
    return errorResponse(c, 400, 'INVALID_JSON', 'Invalid JSON body')
  }

  const parsed = deleteAllBookingsBodySchema.safeParse(body, { errorMap: spanishErrorMap })
  if (!parsed.success) {
    const flat = parsed.error.flatten()
    const formMsg = flat.formErrors[0]
    const fieldMsg = Object.entries(flat.fieldErrors)
      .map(([, v]) => (Array.isArray(v) ? v[0] : v))
      .filter(Boolean)
      .join('; ')
    const message = formMsg || fieldMsg || 'Error de validación'
    return errorResponse(c, 400, 'VALIDATION_ERROR', message)
  }

  if (parsed.data.dryRun === true) {
    try {
      const [countRow] = await db.select({ total: count() }).from(bookings)
      const countVal = countRow?.total ?? 0
      return successResponse(c, { dryRun: true, count: countVal })
    } catch (error) {
      logServerError('admin', 'DELETE_ALL_BOOKINGS_DRY_RUN_FAILED', error)
      return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to count bookings')
    }
  }

  try {
    const deletedCount = await db.transaction(async (tx) => {
      const [countRow] = await tx.select({ total: count() }).from(bookings)
      const n = countRow?.total ?? 0
      await tx.delete(bookings)
      return n
    })

    console.log(
      JSON.stringify({
        type: 'audit',
        action: 'admin_bookings_delete_all',
        timestamp: new Date().toISOString(),
        userId: c.get('userId'),
        sessionId: c.get('sessionId') ?? null,
        deletedCount,
      }),
    )

    return successResponse(c, { deletedCount, dryRun: false })
  } catch (error) {
    logServerError('admin', 'DELETE_ALL_BOOKINGS_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to delete all bookings')
  }
})

adminRoutes.post('/bookings/:id/resend-confirmation', async (c) => {
  const id = parseRequiredBookingId(c.req.param('id'))
  if (id === null) {
    return errorResponse(c, 400, 'VALIDATION_ERROR', 'Invalid booking id')
  }

  try {
    const booking = await db
      .select()
      .from(bookings)
      .where(and(eq(bookings.id, id), bookingNotSoftDeleted))
      .get()

    if (!booking) {
      return errorResponse(c, 404, 'NOT_FOUND', 'Booking not found')
    }

    if (booking.status !== 'pending') {
      return errorResponse(
        c,
        400,
        'INVALID_STATUS',
        `Cannot resend confirmation when status is ${booking.status}`,
      )
    }

    const from = process.env.RESEND_FROM_EMAIL ?? 'onboarding@resend.dev'
    const subject = 'Recibimos tu solicitud — Mafia Tumbada'
    const text = `Hola ${booking.name},\n\nRecibimos tu solicitud de contratación. Te contactaremos pronto.\n\n— Mafia Tumbada`
    const confirmationAttempts = booking.confirmationAttempts + 1

    let status: 'pending' | 'sent' = 'pending'
    let confirmationLastError: string | null = null

    try {
      const { error } = await getResend().emails.send({
        from,
        to: [booking.email],
        subject,
        text,
      })

      if (error) {
        logServerErrorDetails('admin', 'RESEND_CONFIRMATION_API', {
          message: error.message,
          name: error.name,
        })
        confirmationLastError = error.message ?? null
        status = 'pending'
      } else {
        status = 'sent'
        confirmationLastError = null
      }
    } catch (err) {
      logServerError('admin', 'RESEND_CONFIRMATION_THROW', err)
      status = 'pending'
      confirmationLastError = err instanceof Error ? err.message : String(err)
    }

    await db
      .update(bookings)
      .set({
        status,
        confirmationLastError,
        confirmationAttempts,
      })
      .where(eq(bookings.id, id))

    return successResponse(
      c,
      {
        id: booking.id,
        status,
        confirmationLastError,
        confirmationAttempts,
      },
      200,
    )
  } catch (error) {
    logServerError('admin', 'RESEND_CONFIRMATION_OUTER', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to resend confirmation')
  }
})

/** Admin-only export for debugging: full booking list + counts. Use to verify production data (e.g. missing submissions). */
adminRoutes.get('/export/bookings', async (c) => {
  if (!isAdminBookingExportAllowed()) {
    return errorResponse(
      c,
      403,
      'ADMIN_BOOKING_EXPORT_DISABLED',
      'Admin booking export is disabled. Set ALLOW_ADMIN_BOOKING_EXPORT=true on the API, or NODE_ENV=development for local use.',
    )
  }

  try {
    const exportCap = getAdminExportMaxRows()
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

    const [totalRow] = await db
      .select({ total: count() })
      .from(bookings)
      .where(bookingNotSoftDeleted)
    const totalInDb = totalRow?.total ?? 0

    const [last24Row] = await db
      .select({ total: count() })
      .from(bookings)
      .where(and(bookingNotSoftDeleted, gte(bookings.createdAt, oneDayAgo)))
    const last24hCount = last24Row?.total ?? 0

    const leadPriorityRankExport = sql`(CASE ${bookings.leadPriority} WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END)`

    const pageRows = await db
      .select()
      .from(bookings)
      .where(bookingNotSoftDeleted)
      .orderBy(asc(leadPriorityRankExport), desc(bookings.createdAt))
      .limit(exportCap)

    const enriched = pageRows.map((b) => ({
      ...b,
      estimatedPriceRange: estimatedPriceRange({
        city: b.city,
        duration: b.duration,
        attendees: b.attendees,
      }),
    }))

    const truncated = totalInDb > exportCap
    const returnedCount = enriched.length

    console.log(
      JSON.stringify({
        type: 'audit',
        action: 'admin_booking_export',
        timestamp: new Date().toISOString(),
        userId: c.get('userId'),
        sessionId: c.get('sessionId') ?? null,
      }),
    )

    return successResponse(c, {
      exportedAt: new Date().toISOString(),
      total: totalInDb,
      last24hCount,
      bookings: enriched,
      returnedCount,
      truncated,
      ...(truncated
        ? {
            totalInDb,
            warning: `Export includes at most ${exportCap} rows (${totalInDb} in database). Set ADMIN_EXPORT_MAX_ROWS to raise the cap (see .env.example).`,
          }
        : {}),
    })
  } catch (error) {
    logServerError('admin', 'EXPORT_BOOKINGS_FAILED', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to export bookings')
  }
})

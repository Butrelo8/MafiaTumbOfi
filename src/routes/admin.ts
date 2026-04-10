import { Hono } from 'hono'
import { count, desc, eq, gte } from 'drizzle-orm'
import { authMiddleware } from '../middleware/auth'
import { adminAuth } from '../middleware/adminAuth'
import { errorResponse, successResponse } from '../lib/errors'
import { db } from '../db'
import { bookings } from '../db/schema'
import { getResend } from '../lib/resend'
import { isAdminBookingExportAllowed } from '../lib/adminBookingExport'
import { logServerError, logServerErrorDetails } from '../lib/safeLog'
import { estimatedPriceRange } from '../lib/estimatedPriceRange'
import {
  getAdminExportMaxRows,
  parseAdminBookingsListParams,
} from '../lib/adminBookingsQuery'

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
    const [countRow] = await db.select({ total: count() }).from(bookings)
    const total = countRow?.total ?? 0

    const pageRows = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))
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

adminRoutes.post('/bookings/:id/resend-confirmation', async (c) => {
  const idParam = c.req.param('id')
  const id = Number(idParam)
  if (!idParam || Number.isNaN(id) || !Number.isInteger(id) || id <= 0) {
    return errorResponse(c, 400, 'VALIDATION_ERROR', 'Invalid booking id')
  }

  try {
    const booking = await db
      .select()
      .from(bookings)
      .where(eq(bookings.id, id))
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

    const [totalRow] = await db.select({ total: count() }).from(bookings)
    const totalInDb = totalRow?.total ?? 0

    const [last24Row] = await db
      .select({ total: count() })
      .from(bookings)
      .where(gte(bookings.createdAt, oneDayAgo))
    const last24hCount = last24Row?.total ?? 0

    const pageRows = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))
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

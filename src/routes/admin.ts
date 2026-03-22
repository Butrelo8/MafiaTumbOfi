import { Hono } from 'hono'
import { desc, eq } from 'drizzle-orm'
import { authMiddleware } from '../middleware/auth'
import { adminAuth } from '../middleware/adminAuth'
import { errorResponse, successResponse } from '../lib/errors'
import { db } from '../db'
import { bookings } from '../db/schema'
import { getResend } from '../lib/resend'
import { isAdminBookingExportAllowed } from '../lib/adminBookingExport'

export const adminRoutes = new Hono()

adminRoutes.use('*', authMiddleware)
adminRoutes.use('*', adminAuth)

adminRoutes.get('/bookings', async (c) => {
  try {
    const allBookings = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))

    return successResponse(c, {
      bookings: allBookings,
      total: allBookings.length,
    })
  } catch (error) {
    console.error('Failed to fetch bookings:', error)
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
        console.error('[admin] Resend confirmation error:', {
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
      console.error('[admin] Resend confirmation threw:', err)
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
    console.error('[admin] Resend confirmation failed:', error)
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
      'Admin booking export is disabled in production unless ALLOW_ADMIN_BOOKING_EXPORT=true is set on the API.',
    )
  }

  try {
    const allBookings = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))

    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
    const last24h = allBookings.filter((b) => b.createdAt && b.createdAt >= oneDayAgo)

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
      total: allBookings.length,
      last24hCount: last24h.length,
      bookings: allBookings,
    })
  } catch (error) {
    console.error('Failed to export bookings:', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to export bookings')
  }
})

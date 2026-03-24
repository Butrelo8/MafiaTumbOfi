import { eq } from 'drizzle-orm'
import { Hono } from 'hono'
import { z } from 'zod'
import { db } from '../db'
import { bookings } from '../db/schema'
import { errorResponse, successResponse } from '../lib/errors'
import { getResend } from '../lib/resend'
import { spanishErrorMap } from '../lib/zod-es'
import { getClientId, rateLimitBooking } from '../middleware/rateLimit'
import {
  logServerError,
  logServerErrorDetails,
  logServerInfo,
  logServerWarning,
} from '../lib/safeLog'

async function markBandEmailFailed(bookingId: number) {
  await db
    .update(bookings)
    .set({ status: 'failed', confirmationLastError: null, confirmationAttempts: 0 })
    .where(eq(bookings.id, bookingId))
}

const bookingSchema = z.object({
  name: z.string().min(1).max(200),
  email: z.string().email(),
  phone: z.string().max(50).optional(),
  eventDate: z.string().max(100).optional(),
  city: z.string().max(200).optional(),
  eventType: z.string().max(50).optional(),
  duration: z.string().max(30).optional(),
  showType: z.string().max(50).optional(),
  attendees: z.string().max(30).optional(),
  venueSound: z.string().max(10).optional(),
  message: z.string().max(2000).optional(),
  website: z.string().max(100).optional(),
})

export type BookingBody = z.infer<typeof bookingSchema>

export const bookingRoutes = new Hono()

bookingRoutes.use('/booking', rateLimitBooking)
bookingRoutes.post('/booking', async (c) => {
  let body: unknown
  try {
    body = await c.req.json()
  } catch {
    return errorResponse(c, 400, 'INVALID_JSON', 'Invalid JSON body')
  }

  const parsed = bookingSchema.safeParse(body, { errorMap: spanishErrorMap })
  if (!parsed.success) {
    const first = parsed.error.flatten().fieldErrors
    const message = Object.entries(first)
      .map(([, v]) => (Array.isArray(v) ? v[0] : v))
      .join('; ') || 'Error de validación'
    return errorResponse(c, 400, 'VALIDATION_ERROR', message)
  }

  const {
    name,
    email,
    phone,
    eventDate,
    city,
    eventType,
    duration,
    showType,
    attendees,
    venueSound,
    message,
    website,
  } = parsed.data
  if (website) {
    return errorResponse(c, 400, 'SPAM_DETECTED', 'Solicitud rechazada')
  }

  const to = process.env.BOOKING_NOTIFICATION_EMAIL
  if (!to) {
    logServerWarning('booking', 'CONFIG', 'BOOKING_NOTIFICATION_EMAIL not set')
    return errorResponse(c, 500, 'CONFIG_ERROR', 'Booking is not configured')
  }

  try {
    getResend()
  } catch (err) {
    logServerError('booking', 'RESEND_INIT', err)
    return errorResponse(c, 500, 'CONFIG_ERROR', 'Booking email is not configured')
  }

  const insertedRows = await db
    .insert(bookings)
    .values({
      name,
      email,
      phone: phone ?? null,
      eventDate: eventDate ?? null,
      city: city ?? null,
      eventType: eventType ?? null,
      duration: duration ?? null,
      showType: showType ?? null,
      attendees: attendees ?? null,
      venueSound: venueSound ?? null,
      message: message ?? null,
      status: 'pending',
      confirmationLastError: null,
      confirmationAttempts: 0,
    })
    .returning({ id: bookings.id })

  const inserted = insertedRows[0]
  if (!inserted) {
    logServerError('booking', 'INSERT_RETURN_EMPTY', new Error('insert returned no row'))
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Could not create booking')
  }

  logServerInfo('booking', 'REQUEST_RECEIVED', {
    bookingId: inserted.id,
    ip: getClientId(c),
    timestamp: new Date().toISOString(),
    hasMessage: !!message,
  })

  const from = process.env.RESEND_FROM_EMAIL ?? 'onboarding@resend.dev'
  const text = [
    `New booking request from ${name}`,
    `Email: ${email}`,
    phone ? `Phone: ${phone}` : null,
    eventDate ? `Event date: ${eventDate}` : null,
    city ? `City: ${city}` : null,
    eventType ? `Event type: ${eventType}` : null,
    duration ? `Duration: ${duration}` : null,
    showType ? `Show type: ${showType}` : null,
    attendees ? `Attendees: ${attendees}` : null,
    venueSound ? `Venue sound: ${venueSound}` : null,
    message ? `Message:\n${message}` : null,
  ]
    .filter(Boolean)
    .join('\n')

  // Two independent email sends:
  // 1) notify band (failure => booking becomes `failed` and endpoint returns 500)
  // 2) notify customer confirmation (failure/throw => booking becomes `pending` but endpoint remains 201)
  let confirmation: 'sent' | 'pending' = 'pending'
  let confirmationLastError: string | null = null
  let confirmationAttempts = 0

  try {
    const { error } = await getResend().emails.send({
      from,
      to: [to],
      subject: `[Mafia Tumbada] Booking request from ${name}`,
      text,
    })

    if (error) {
      logServerErrorDetails('booking', 'RESEND_BAND_API', {
        message: error.message,
        name: error.name,
      })
      await markBandEmailFailed(inserted.id)
      return errorResponse(
        c,
        500,
        'EMAIL_FAILED',
        'Could not send booking request',
      )
    }
  } catch (err) {
    logServerError('booking', 'RESEND_BAND_THROW', err)
    await markBandEmailFailed(inserted.id)
    return errorResponse(c, 500, 'EMAIL_FAILED', 'Could not send booking request')
  }

  confirmationAttempts = 1
  try {
    const confirmResult = await getResend().emails.send({
      from,
      to: [email],
      subject: 'Recibimos tu solicitud — Mafia Tumbada',
      text: `Hola ${name},\n\nRecibimos tu solicitud de contratación. Te contactaremos pronto.\n\n— Mafia Tumbada`,
    })

    confirmation = confirmResult.error ? 'pending' : 'sent'
    if (confirmResult.error) {
      logServerErrorDetails('booking', 'RESEND_CONFIRM_CUSTOMER', {
        message: confirmResult.error?.message,
        name: confirmResult.error?.name,
      })
      confirmationLastError = confirmResult.error.message ?? null
    } else {
      confirmationLastError = null
    }
  } catch (err) {
    logServerError('booking', 'RESEND_CONFIRM_THROW', err)
    confirmation = 'pending'
    confirmationLastError = err instanceof Error ? err.message : String(err)
  }

  // Status semantics: pending = band OK but customer confirmation failed; sent = both succeeded; failed = band email failed.
  await db
    .update(bookings)
    .set({
      status: confirmation === 'sent' ? 'sent' : 'pending',
      confirmationLastError: confirmation === 'sent' ? null : confirmationLastError,
      confirmationAttempts,
    })
    .where(eq(bookings.id, inserted.id))

  return successResponse(c, { ok: true, bookingId: inserted.id, confirmation }, 201)
})

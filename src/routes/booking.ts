import { eq } from 'drizzle-orm'
import { Hono } from 'hono'
import { z } from 'zod'
import { db } from '../db'
import { bookings } from '../db/schema'
import { errorResponse, successResponse } from '../lib/errors'
import { getResend } from '../lib/resend'
import { spanishErrorMap } from '../lib/zod-es'
import { getClientId, rateLimitBooking } from '../middleware/rateLimit'

const bookingSchema = z.object({
  name: z.string().min(1).max(200),
  email: z.string().email(),
  phone: z.string().max(50).optional(),
  eventDate: z.string().max(100).optional(),
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

  const { name, email, phone, eventDate, message, website } = parsed.data
  if (website) {
    return errorResponse(c, 400, 'SPAM_DETECTED', 'Solicitud rechazada')
  }

  const to = process.env.BOOKING_NOTIFICATION_EMAIL
  if (!to) {
    console.error('[booking] BOOKING_NOTIFICATION_EMAIL not set')
    return errorResponse(c, 500, 'CONFIG_ERROR', 'Booking is not configured')
  }

  try {
    getResend()
  } catch (err) {
    console.error('[booking] Resend not configured:', err instanceof Error ? err.message : err)
    return errorResponse(c, 500, 'CONFIG_ERROR', 'Booking email is not configured')
  }

  const [inserted] = await db
    .insert(bookings)
    .values({
      name,
      email,
      phone: phone ?? null,
      eventDate: eventDate ?? null,
      message: message ?? null,
      status: 'pending',
    })
    .returning({ id: bookings.id })

  console.log('[booking] Request received', {
    id: inserted.id,
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
    message ? `Message:\n${message}` : null,
  ]
    .filter(Boolean)
    .join('\n')

  const { error } = await getResend().emails.send({
    from,
    to: [to],
    subject: `[Mafia Tumbada] Booking request from ${name}`,
    text,
  })

  if (error) {
    console.error('[booking] Resend error:', {
      message: error.message,
      name: error.name,
    })
    await db
      .update(bookings)
      .set({ status: 'failed' })
      .where(eq(bookings.id, inserted.id))
    return errorResponse(c, 500, 'EMAIL_FAILED', 'Could not send booking request')
  }

  const confirmResult = await getResend().emails.send({
    from,
    to: [email],
    subject: 'Recibimos tu solicitud — Mafia Tumbada',
    text: `Hola ${name},\n\nRecibimos tu solicitud de contratación. Te contactaremos pronto.\n\n— Mafia Tumbada`,
  })
  const confirmationSent = !confirmResult.error
  if (!confirmationSent) {
    console.error('[booking] Confirmation email failed:', {
      message: confirmResult.error?.message,
      name: confirmResult.error?.name,
    })
  }

  // Status semantics: pending = initial or band OK but customer confirmation failed;
  // sent = both band notification and customer confirmation succeeded; failed = band email failed (set earlier).
  await db
    .update(bookings)
    .set({ status: confirmationSent ? 'sent' : 'pending' })
    .where(eq(bookings.id, inserted.id))

  return successResponse(c, { ok: true }, 201)
})

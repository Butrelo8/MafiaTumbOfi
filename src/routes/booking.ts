import { eq } from 'drizzle-orm'
import { Hono } from 'hono'
import { z } from 'zod'
import { db } from '../db'
import { bookings } from '../db/schema'
import { BOOKING_BUDGET_VALUES, BUDGET_LABELS } from '../lib/bookingBudget'
import { computeBookingLeadScore } from '../lib/bookingLeadScore'
import { computeDripDueDatesFromCreatedAt } from '../lib/dripSchedule'
import { errorResponse, successResponse } from '../lib/errors'
import { getResend } from '../lib/resend'
import {
  logServerError,
  logServerErrorDetails,
  logServerInfo,
  logServerWarning,
} from '../lib/safeLog'
import { spanishErrorMap } from '../lib/zod-es'
import { getClientId, rateLimitBooking } from '../middleware/rateLimit'

async function markBandEmailFailed(bookingId: number) {
  await db
    .update(bookings)
    .set({ status: 'failed', confirmationLastError: null, confirmationAttempts: 0 })
    .where(eq(bookings.id, bookingId))
}

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function multilineToHtml(value: string): string {
  return escapeHtml(value).replace(/\r?\n/g, '<br />')
}

function publicSiteBase(): string {
  const raw =
    process.env.PUBLIC_SITE_URL ?? process.env.PRODUCTION_URL ?? process.env.FRONTEND_URL ?? ''
  return raw.trim().replace(/\/$/, '')
}

function bookingPageUrl(): string {
  const base = publicSiteBase()
  return base ? `${base}/booking` : 'https://mafiatumbada.com/booking'
}

type CustomerCta = {
  label: string
  url: string
  bookingUrl: string
}

function resolveCustomerCta(): CustomerCta {
  const bookingUrl = bookingPageUrl()
  const wa = process.env.PUBLIC_WHATSAPP_URL?.trim()
  if (wa) {
    return {
      label: 'Hablar por WhatsApp',
      url: wa,
      bookingUrl,
    }
  }
  return {
    label: 'Ver formulario de contratacion',
    url: bookingUrl,
    bookingUrl,
  }
}

function buildBookingBandEmailHtml(input: {
  name: string
  email: string
  /** `string | undefined` (not only optional) so callers can pass Zod fields under `exactOptionalPropertyTypes`. */
  phone?: string | undefined
  eventDate?: string | undefined
  city?: string | undefined
  eventType?: string | undefined
  duration?: string | undefined
  showType?: string | undefined
  attendees?: string | undefined
  venueSound?: string | undefined
  budgetLabel?: string | undefined
  message?: string | undefined
}): string {
  const rows = [
    ['Nombre', input.name],
    ['Correo', input.email],
    ['Telefono', input.phone],
    ['Fecha del evento', input.eventDate],
    ['Ciudad', input.city],
    ['Tipo de evento', input.eventType],
    ['Duracion', input.duration],
    ['Formato solicitado', input.showType],
    ['Asistentes estimados', input.attendees],
    ['Audio del venue', input.venueSound],
    ['Presupuesto estimado', input.budgetLabel],
  ]
    .filter(([, value]) => value)
    .map(([label, value]) => {
      const safeLabel = escapeHtml(String(label))
      const safeValue = escapeHtml(String(value))
      return `<tr><td style="padding:10px 12px;font-weight:700;border-bottom:1px solid #ececec;vertical-align:top;color:#111827;width:220px;">${safeLabel}</td><td style="padding:10px 12px;border-bottom:1px solid #ececec;color:#1f2937;">${safeValue}</td></tr>`
    })
    .join('')

  const messageBlock = input.message
    ? `<div style="margin-top:18px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;"><p style="margin:0 0 8px;font-size:13px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:#334155;">Mensaje del cliente</p><p style="margin:0;line-height:1.6;color:#0f172a;">${multilineToHtml(input.message)}</p></div>`
    : ''

  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;background:#f2f2f2;">
<tr>
<td align="center" style="padding:22px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;border-collapse:separate;border-spacing:0;background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;">
<tr>
<td style="padding:20px 22px;background:linear-gradient(135deg, #0b0b0b 0%, #1c1c1c 100%);">
<p style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:#f3c965;">Mafia Tumbada</p>
<h2 style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:24px;line-height:1.2;color:#ffffff;">Nueva solicitud de contratacion</h2>
<p style="margin:0;font-family:Arial,sans-serif;font-size:14px;line-height:1.55;color:#d1d5db;">Se recibio una nueva solicitud desde el sitio web.</p>
</td>
</tr>
<tr>
<td style="padding:20px 22px;font-family:Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;border:1px solid #ececec;border-radius:10px;overflow:hidden;background:#ffffff;">${rows}</table>
${messageBlock}
<div style="margin-top:18px;padding:12px 14px;background:#fff8e1;border:1px solid #f0d98b;border-radius:10px;font-family:Arial,sans-serif;font-size:14px;line-height:1.55;color:#5f4a12;">
Responder a este correo para continuar la cotizacion.
</div>
</td>
</tr>
</table>
</td>
</tr>
</table>`
}

function buildBookingCustomerConfirmationHtml(name: string, cta: CustomerCta): string {
  const safeName = escapeHtml(name)
  const safeCtaLabel = escapeHtml(cta.label)
  const safeCtaUrl = escapeHtml(cta.url)
  const safeBookingUrl = escapeHtml(cta.bookingUrl)
  const bookingFallback =
    cta.url === cta.bookingUrl
      ? ''
      : `<p style="margin:14px 0 0;font-size:14px;color:#334155;">Tambien puedes revisar el formulario aqui: <a href="${safeBookingUrl}" style="color:#7a5a0a;text-decoration:underline;">Formulario de contratacion</a></p>`
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;background:#f2f2f2;">
<tr>
<td align="center" style="padding:22px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;border-collapse:separate;border-spacing:0;background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;">
<tr>
<td style="padding:20px 22px;background:linear-gradient(135deg, #0b0b0b 0%, #1c1c1c 100%);">
<p style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:#f3c965;">Mafia Tumbada</p>
<h2 style="margin:0;font-family:Arial,sans-serif;font-size:24px;line-height:1.2;color:#ffffff;">Solicitud recibida</h2>
</td>
</tr>
<tr>
<td style="padding:20px 22px;font-family:Arial,sans-serif;color:#1f2937;line-height:1.65;">
<p style="margin:0 0 12px;">Hola ${safeName},</p>
<p style="margin:0 0 12px;">Gracias por escribirnos.</p>
<p style="margin:0 0 12px;">Recibimos tu solicitud de contratacion y ya la estamos revisando.</p>
<p style="margin:0 0 16px;">En breve te contactaremos para confirmar disponibilidad y afinar detalles.</p>
<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:separate;margin:0 0 14px;">
  <tr>
    <td align="center" style="background:#f3c965;border-radius:999px;">
      <a href="${safeCtaUrl}" style="display:inline-block;padding:12px 20px;font-size:14px;font-weight:700;color:#111827;text-decoration:none;">${safeCtaLabel}</a>
    </td>
  </tr>
</table>
${bookingFallback}
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;">
<p style="margin:0 0 8px;font-size:13px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:#334155;">Para avanzar mas rapido, puedes responder con:</p>
<ul style="margin:0 0 0 18px;padding:0;color:#0f172a;">
  <li style="margin:0 0 6px;">Fecha y ciudad del evento</li>
  <li style="margin:0 0 6px;">Tipo de evento</li>
  <li style="margin:0;">Presupuesto aproximado</li>
</ul>
</div>
<p style="margin:16px 0 0;">Equipo Mafia Tumbada</p>
</td>
</tr>
</table>
</td>
</tr>
</table>`
}

const bookingBudgetSchema = z.enum(BOOKING_BUDGET_VALUES)

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
  budget: z.preprocess(
    (val) => (val === '' || val === null || val === undefined ? undefined : val),
    bookingBudgetSchema.optional(),
  ),
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
    const message =
      Object.entries(first)
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
    budget,
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

  const { leadScore, leadPriority } = computeBookingLeadScore({
    budget: budget ?? null,
    city: city ?? null,
    eventType: eventType ?? null,
    duration: duration ?? null,
    showType: showType ?? null,
    attendees: attendees ?? null,
    venueSound: venueSound ?? null,
  })

  const createdAt = new Date()
  const { drip2DueAt, drip3DueAt } = computeDripDueDatesFromCreatedAt(createdAt)

  let inserted: { id: number }
  try {
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
        budget: budget ?? null,
        leadScore,
        leadPriority,
        message: message ?? null,
        pipelineStatus: 'new',
        status: 'pending',
        confirmationLastError: null,
        confirmationAttempts: 0,
        createdAt,
        drip2DueAt,
        drip3DueAt,
      })
      // `db` is bun-sqlite | libsql union — overload resolution leaves only `.returning()` (no field pick).
      .returning()

    const row = insertedRows[0]
    if (!row) {
      logServerError('booking', 'INSERT_RETURN_EMPTY', new Error('insert returned no row'))
      return errorResponse(c, 500, 'BOOKING_PERSIST_FAILED', 'No se pudo guardar la solicitud.')
    }
    inserted = { id: row.id }
  } catch (err) {
    logServerError('booking', 'BOOKING_INSERT_FAILED', err)
    return errorResponse(c, 500, 'BOOKING_PERSIST_FAILED', 'No se pudo guardar la solicitud.')
  }

  logServerInfo('booking', 'REQUEST_RECEIVED', {
    bookingId: inserted.id,
    ip: getClientId(c),
    timestamp: new Date().toISOString(),
    hasMessage: !!message,
  })

  const from = process.env.RESEND_FROM_EMAIL ?? 'onboarding@resend.dev'
  const bandText = [
    'Nueva solicitud de contratacion desde el sitio web.',
    '',
    `Nombre: ${name}`,
    `Correo: ${email}`,
    phone ? `Telefono: ${phone}` : null,
    eventDate ? `Fecha del evento: ${eventDate}` : null,
    city ? `Ciudad: ${city}` : null,
    eventType ? `Tipo de evento: ${eventType}` : null,
    duration ? `Duracion: ${duration}` : null,
    showType ? `Formato solicitado: ${showType}` : null,
    attendees ? `Asistentes estimados: ${attendees}` : null,
    venueSound ? `Audio del venue: ${venueSound}` : null,
    budget ? `Presupuesto estimado: ${BUDGET_LABELS[budget]}` : null,
    message ? `Mensaje del cliente:\n${message}` : null,
    '',
    'Responder a este correo para continuar la cotizacion.',
  ]
    .filter(Boolean)
    .join('\n')
  const bandHtml = buildBookingBandEmailHtml({
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
    budgetLabel: budget ? BUDGET_LABELS[budget] : undefined,
    message,
  })

  // Two independent email sends:
  // 1) notify band (failure => booking becomes `failed` and endpoint returns 500)
  // 2) notify customer confirmation (failure/throw => booking becomes `pending` but endpoint remains 201)
  let confirmation: 'sent' | 'pending' = 'pending'
  let confirmationLastError: string | null = null
  let confirmationAttempts = 0

  const returnBandEmailFailure = async (kind: 'api' | 'throw', err: unknown) => {
    if (kind === 'api') {
      const resendError = err as { message?: string; name?: string }
      logServerErrorDetails('booking', 'RESEND_BAND_API', {
        message: resendError.message,
        name: resendError.name,
      })
    } else {
      logServerError('booking', 'RESEND_BAND_THROW', err)
    }

    await markBandEmailFailed(inserted.id)
    return errorResponse(c, 500, 'EMAIL_FAILED', 'Could not send booking request')
  }

  let bandEmailError: unknown = null
  try {
    const result = await getResend().emails.send({
      from,
      to: [to],
      subject: `[Mafia Tumbada] Nueva solicitud de contratacion - ${name}`,
      text: bandText,
      html: bandHtml,
    })
    bandEmailError = result.error
  } catch (err) {
    return returnBandEmailFailure('throw', err)
  }

  if (bandEmailError) {
    return returnBandEmailFailure('api', bandEmailError)
  }

  const customerCta = resolveCustomerCta()
  const customerConfirmationText = [
    `Hola ${name},`,
    '',
    'Gracias por escribirnos.',
    'Recibimos tu solicitud de contratacion y ya la estamos revisando.',
    'En breve te contactaremos para confirmar disponibilidad y afinar detalles.',
    '',
    `${customerCta.label}: ${customerCta.url}`,
    customerCta.url === customerCta.bookingUrl
      ? null
      : `Formulario de contratacion: ${customerCta.bookingUrl}`,
    '',
    'Si quieres adelantar informacion, responde este correo con:',
    '- Fecha y ciudad del evento',
    '- Tipo de evento',
    '- Presupuesto aproximado',
    '',
    'Equipo Mafia Tumbada',
  ]
    .filter(Boolean)
    .join('\n')
  const customerConfirmationHtml = buildBookingCustomerConfirmationHtml(name, customerCta)

  confirmationAttempts = 1
  try {
    const confirmResult = await getResend().emails.send({
      from,
      to: [email],
      subject: 'Recibimos tu solicitud - Mafia Tumbada',
      text: customerConfirmationText,
      html: customerConfirmationHtml,
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

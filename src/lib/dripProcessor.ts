import { and, eq, isNotNull, isNull, lte } from 'drizzle-orm'
import { db } from '../db'
import { bookings } from '../db/schema'
import { bookingNotSoftDeleted } from './bookingSoftDeleteFilter'
import { buildDripEmail2, buildDripEmail3 } from './dripEmails'
import { getResend } from './resend'
import { logServerError, logServerErrorDetails } from './safeLog'

export type DripProcessResult = {
  email2Sent: number
  email3Sent: number
  errors: number
}

function parseBatchSize(): number {
  const raw = process.env.DRIP_BATCH_SIZE
  if (raw === undefined || raw.trim() === '') return 20
  const n = Number(raw)
  if (!Number.isFinite(n) || n < 1) return 20
  return Math.min(500, Math.floor(n))
}

/**
 * Sends due nurture emails (Email 2 then Email 3) for bookings with confirmation `status === 'sent'`.
 * Updates `drip*_sent_at` only after Resend reports success — safe under repeated cron runs.
 */
export async function processDripEmails(opts?: {
  batchSize?: number
  now?: Date
}): Promise<DripProcessResult> {
  const now = opts?.now ?? new Date()
  const batchSize = opts?.batchSize ?? parseBatchSize()
  const from = process.env.RESEND_FROM_EMAIL ?? 'onboarding@resend.dev'

  let email2Sent = 0
  let email3Sent = 0
  let errors = 0

  const due2 = await db
    .select()
    .from(bookings)
    .where(
      and(
        bookingNotSoftDeleted,
        eq(bookings.status, 'sent'),
        isNotNull(bookings.drip2DueAt),
        lte(bookings.drip2DueAt, now),
        isNull(bookings.drip2SentAt),
      ),
    )
    .limit(batchSize)

  for (const row of due2) {
    const payload = buildDripEmail2(row.name)
    try {
      const { error } = await getResend().emails.send({
        from,
        to: [row.email],
        subject: payload.subject,
        html: payload.html,
        text: payload.text,
      })
      if (error) {
        errors += 1
        logServerErrorDetails('drip', 'RESEND_DRIP2_API', {
          bookingId: row.id,
          message: error.message,
          name: error.name,
        })
        continue
      }
      await db.update(bookings).set({ drip2SentAt: new Date() }).where(eq(bookings.id, row.id))
      email2Sent += 1
    } catch (err) {
      errors += 1
      logServerError('drip', 'RESEND_DRIP2_THROW', err, { bookingId: row.id })
    }
  }

  const due3 = await db
    .select()
    .from(bookings)
    .where(
      and(
        bookingNotSoftDeleted,
        eq(bookings.status, 'sent'),
        isNotNull(bookings.drip2SentAt),
        isNotNull(bookings.drip3DueAt),
        lte(bookings.drip3DueAt, now),
        isNull(bookings.drip3SentAt),
      ),
    )
    .limit(batchSize)

  for (const row of due3) {
    const payload = buildDripEmail3(row.name)
    try {
      const { error } = await getResend().emails.send({
        from,
        to: [row.email],
        subject: payload.subject,
        html: payload.html,
        text: payload.text,
      })
      if (error) {
        errors += 1
        logServerErrorDetails('drip', 'RESEND_DRIP3_API', {
          bookingId: row.id,
          message: error.message,
          name: error.name,
        })
        continue
      }
      await db.update(bookings).set({ drip3SentAt: new Date() }).where(eq(bookings.id, row.id))
      email3Sent += 1
    } catch (err) {
      errors += 1
      logServerError('drip', 'RESEND_DRIP3_THROW', err, { bookingId: row.id })
    }
  }

  return { email2Sent, email3Sent, errors }
}

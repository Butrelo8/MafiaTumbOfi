/** Default +24h from booking for first nurture email. */
export const DRIP_EMAIL_2_DELAY_HOURS_DEFAULT = 24
/** Default +72h from booking for second nurture email. */
export const DRIP_EMAIL_3_DELAY_HOURS_DEFAULT = 72

/**
 * Parses `DRIP_EMAIL_*_DELAY_HOURS`-style env. Non-finite or negative → default.
 */
export function parseDelayHours(raw: string | undefined, defaultHours: number): number {
  if (raw === undefined || raw.trim() === '') return defaultHours
  const n = Number(raw)
  if (!Number.isFinite(n) || n < 0) return defaultHours
  return Math.floor(n)
}

export function computeDripDueDatesFromCreatedAt(
  createdAt: Date,
  opts?: { email2DelayHours?: number; email3DelayHours?: number },
): { drip2DueAt: Date; drip3DueAt: Date } {
  const h2 =
    opts?.email2DelayHours ??
    parseDelayHours(process.env.DRIP_EMAIL_2_DELAY_HOURS, DRIP_EMAIL_2_DELAY_HOURS_DEFAULT)
  const h3 =
    opts?.email3DelayHours ??
    parseDelayHours(process.env.DRIP_EMAIL_3_DELAY_HOURS, DRIP_EMAIL_3_DELAY_HOURS_DEFAULT)
  const ms2 = h2 * 60 * 60 * 1000
  const ms3 = h3 * 60 * 60 * 1000
  return {
    drip2DueAt: new Date(createdAt.getTime() + ms2),
    drip3DueAt: new Date(createdAt.getTime() + ms3),
  }
}

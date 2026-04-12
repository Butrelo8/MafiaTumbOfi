/** Whole calendar days since `createdAt` (floor), for “stale Nuevo” badge. */
export const ADMIN_STALE_NEW_MS_PER_DAY = 86_400_000

/** Inclusive: show warn badge when pipeline is `new` and age ≥ this many days. */
export const ADMIN_STALE_NEW_WARN_DAYS = 3

/** Inclusive: escalate to danger when age ≥ this many days. */
export const ADMIN_STALE_NEW_DANGER_DAYS = 7

export type StaleNewBadgeSeverity = 'warn' | 'danger'

export type StaleNewBadgeState = {
  days: number
  severity: StaleNewBadgeSeverity
}

/**
 * Badge for admin table: only **`pipelineStatus === 'new'`**, and age ≥ warn threshold.
 * Uses the same “days since” floor as the TODOS spec: `floor((now - created) / 86400000)`.
 */
export function staleNewBadgeState(
  pipelineStatus: string,
  createdAtMs: number,
  nowMs: number,
): StaleNewBadgeState | null {
  if (pipelineStatus !== 'new') return null
  if (!Number.isFinite(createdAtMs) || !Number.isFinite(nowMs)) return null
  const days = Math.floor((nowMs - createdAtMs) / ADMIN_STALE_NEW_MS_PER_DAY)
  if (days < ADMIN_STALE_NEW_WARN_DAYS) return null
  if (days >= ADMIN_STALE_NEW_DANGER_DAYS) {
    return { days, severity: 'danger' }
  }
  return { days, severity: 'warn' }
}

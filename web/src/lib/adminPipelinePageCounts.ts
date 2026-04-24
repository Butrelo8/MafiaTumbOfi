import { isLeadPriority } from '../../../src/lib/bookingLeadScore'
import {
  isBookingPipelineStatus,
  type BookingPipelineStatus,
} from '../../../src/lib/bookingPipeline'/** Same default as admin row `data-pipeline-status` when value missing or unknown. */
function rowPipelineKey(value: string | null | undefined): BookingPipelineStatus {
  return value != null && isBookingPipelineStatus(value) ? value : 'new'
}

/**
 * Count bookings on the current admin list page by `pipeline_status`
 * (normalized like the admin table rows).
 */
export function pipelineCountsForAdminRows(
  rows: ReadonlyArray<{ pipelineStatus?: string | null }>,
): Record<BookingPipelineStatus, number> {
  const acc: Record<BookingPipelineStatus, number> = {
    new: 0,
    contacted: 0,
    closed: 0,
  }
  for (const b of rows) {
    acc[rowPipelineKey(b.pipelineStatus)] += 1
  }
  return acc
}

/** Count rows on the current admin page by stored `lead_priority` (`high` / `medium` / `low` only). */
export function leadPriorityCountsForAdminRows(
  rows: ReadonlyArray<{ leadPriority?: string | null }>,
): { high: number; medium: number; low: number } {
  const acc = { high: 0, medium: 0, low: 0 }
  for (const b of rows) {
    const v = b.leadPriority
    if (isLeadPriority(v)) acc[v] += 1
  }
  return acc
}

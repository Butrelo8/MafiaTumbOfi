import {
  isBookingPipelineStatus,
  type BookingPipelineStatus,
} from '../../../src/lib/bookingPipeline'
/** Same default as admin row `data-pipeline-status` when value missing or unknown. */
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

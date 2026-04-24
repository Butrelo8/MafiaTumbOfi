import type { TourDateRow } from '../data/tourDates'
import { normalizePublicApiBaseUrl } from './publicApiUrl'

export type { TourDateRow }

export type LoadTourDatesOptions = {
  /** Override for tests */
  fetchFn?: typeof fetch
  timeoutMs?: number
}

/**
 * SSR: load tour rows from Hono `GET /api/tours/upcoming` (DB-backed). Empty array if none or on fetch failure.
 */
export async function loadTourDates(
  publicApiUrl: string | undefined,
  options?: LoadTourDatesOptions,
): Promise<TourDateRow[]> {
  const apiUrl = normalizePublicApiBaseUrl(publicApiUrl)
  const fetchFn = options?.fetchFn ?? globalThis.fetch
  const timeoutMs = options?.timeoutMs ?? 5000
  try {
    const res = await fetchFn(`${apiUrl}/api/tours/upcoming`, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(timeoutMs),
    })
    if (!res.ok) return []
    const json = (await res.json()) as { data?: TourDateRow[] }
    return Array.isArray(json.data) ? json.data : []
  } catch {
    return []
  }
}

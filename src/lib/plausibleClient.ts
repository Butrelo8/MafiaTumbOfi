/**
 * Browser-only Plausible custom events. No-op when script is absent or `plausible` is not loaded.
 * See `PUBLIC_PLAUSIBLE_DOMAIN` in `web/.env.example`.
 */

export type PlausibleEventOptions = {
  props?: Record<string, string | number | boolean>
}

declare global {
  interface Window {
    plausible?: (eventName: string, options?: PlausibleEventOptions) => void
  }
}

/** Normalize env to `data-domain` (hostname only, no path). */
export function normalizePlausibleDataDomain(raw: string | undefined): string | null {
  if (raw == null || typeof raw !== 'string') return null
  const t = raw.trim()
  if (!t) return null
  if (t.includes('://')) {
    try {
      const host = new URL(t).hostname.trim()
      return host || null
    } catch {
      return null
    }
  }
  const host = t.split('/')[0]?.trim()
  return host || null
}

export function trackPlausible(eventName: string, options?: PlausibleEventOptions): void {
  if (typeof window === 'undefined') return
  const fn = window.plausible
  if (typeof fn !== 'function') return
  fn(eventName, options ?? {})
}

const DEFAULT_DEV_API_BASE = 'http://localhost:3001'

/**
 * Public API origin for fetch() / new URL (no trailing slash).
 * When `PUBLIC_API_URL` ends with `/`, appending `/api/...` would otherwise produce `//api/...` and 404.
 */
export function normalizePublicApiBaseUrl(
  raw: string | undefined | null,
  devDefault: string = DEFAULT_DEV_API_BASE,
): string {
  const trimmed = String(raw ?? '').trim()
  const base = trimmed || devDefault
  return base.replace(/\/+$/, '')
}

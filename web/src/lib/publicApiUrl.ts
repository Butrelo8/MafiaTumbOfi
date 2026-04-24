const DEFAULT_DEV_API_BASE = 'http://localhost:3001'

/**
 * Public API origin for fetch() / new URL (no trailing slash).
 * When `PUBLIC_API_URL` ends with `/`, appending `/api/...` would otherwise produce `//api/...` and 404.
 * When it ends with `/api`, callers would build `/api/api/...` and get 404 — strip that suffix.
 */
export function normalizePublicApiBaseUrl(
  raw: string | undefined | null,
  devDefault: string = DEFAULT_DEV_API_BASE,
): string {
  const trimmed = String(raw ?? '').trim()
  const base = trimmed || devDefault
  let out = base.replace(/\/+$/, '')
  if (out.endsWith('/api')) {
    out = out.slice(0, -4)
  }
  return out
}

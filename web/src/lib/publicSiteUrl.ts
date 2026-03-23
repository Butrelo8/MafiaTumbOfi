/**
 * Resolve the public site base URL for canonical / OG links.
 * Prefer PUBLIC_SITE_URL in production; fall back to the request origin in dev/preview.
 */
export function resolvePublicBaseUrl(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string
): string {
  const fromEnv = publicSiteUrl?.trim()
  if (fromEnv) return fromEnv.replace(/\/$/, '')
  return fallbackOrigin.trim().replace(/\/$/, '')
}

/** Canonical URL for the press kit page (no trailing slash on base). */
export function pressKitCanonical(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string
): string {
  return `${resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)}/press-kit`
}

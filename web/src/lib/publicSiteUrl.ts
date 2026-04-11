/**
 * Resolve the public site base URL for canonical / OG links.
 * Prefer PUBLIC_SITE_URL in production; fall back to the request origin in dev/preview.
 */
export function resolvePublicBaseUrl(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string,
): string {
  const fromEnv = publicSiteUrl?.trim()
  if (fromEnv) return fromEnv.replace(/\/$/, '')
  return fallbackOrigin.trim().replace(/\/$/, '')
}

/** Canonical URL for the homepage (no trailing slash on base). */
export function homeCanonical(publicSiteUrl: string | undefined, fallbackOrigin: string): string {
  return resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)
}

/** Canonical URL for the press kit page (no trailing slash on base). */
export function pressKitCanonical(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string,
): string {
  return `${resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)}/press-kit`
}

/** Canonical URL for the booking (contrataciones) page. */
export function bookingCanonical(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string,
): string {
  return `${resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)}/booking`
}

/** Canonical URL for the post-submit thank-you page (`noindex` in layout). */
export function bookingThanksCanonical(
  publicSiteUrl: string | undefined,
  fallbackOrigin: string,
): string {
  return `${resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)}/booking/gracias`
}

/** Canonical URL for the admin panel (no trailing slash on base). */
export function adminCanonical(publicSiteUrl: string | undefined, fallbackOrigin: string): string {
  return `${resolvePublicBaseUrl(publicSiteUrl, fallbackOrigin)}/admin`
}

/**
 * Absolute URL for a same-origin asset, resolved against any absolute page URL
 * from the site (e.g. `bookingCanonical(...)`). Root-relative paths should start with `/`.
 */
export function absoluteAssetUrl(pageCanonicalUrl: string, rootRelativePath: string): string {
  const path = rootRelativePath.startsWith('/') ? rootRelativePath : `/${rootRelativePath}`
  try {
    return new URL(path, pageCanonicalUrl).href
  } catch {
    return path
  }
}

import { expandCorsAllowedOrigins } from './corsOrigins'

/**
 * Single source of truth for allowed frontend origins (raw URLs).
 * CORS uses `expandCorsAllowedOrigins` on this list in `index.ts`.
 * Clerk `authorizedParties` must include the browser origin (often `www` vs apex); use `clerkAuthorizedParties`.
 */
export const allowedOrigins = [
  'http://localhost:4321',
  'http://localhost:4322',
  process.env.FRONTEND_URL,
  process.env.STAGING_URL,
  process.env.PRODUCTION_URL,
  process.env.PUBLIC_SITE_URL,
].filter((x): x is string => Boolean(x))

/** Clerk session JWT `azp` must match one of these origins (includes www ↔ apex pairs). */
export const clerkAuthorizedParties = expandCorsAllowedOrigins(allowedOrigins)

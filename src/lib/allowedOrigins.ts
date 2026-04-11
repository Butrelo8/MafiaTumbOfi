/**
 * Single source of truth for allowed frontend origins (raw URLs).
 * CORS uses `expandCorsAllowedOrigins` on this list; Clerk `authorizedParties` uses it as-is.
 */
export const allowedOrigins = [
  'http://localhost:4321',
  'http://localhost:4322',
  process.env.FRONTEND_URL,
  process.env.STAGING_URL,
  process.env.PRODUCTION_URL,
].filter((x): x is string => Boolean(x))

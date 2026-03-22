/**
 * Server-side logging: avoid dumping full Error stacks/objects into production log sinks.
 * In development, includes stack when the value is an Error.
 */

function isDevelopment(): boolean {
  return process.env.NODE_ENV === 'development'
}

function errorMessage(err: unknown): string {
  if (err instanceof Error) return err.message
  if (typeof err === 'string') return err
  try {
    return JSON.stringify(err)
  } catch {
    return 'unserializable_error'
  }
}

/**
 * Log a server error path. Production: scope, code, message, optional meta (JSON line).
 * Development: same plus stack when `err` is an Error.
 */
export function logServerError(
  scope: string,
  code: string,
  err: unknown,
  meta?: Record<string, unknown>,
): void {
  const payload: Record<string, unknown> = {
    level: 'error',
    scope,
    code,
    message: errorMessage(err),
    ...meta,
  }
  if (isDevelopment() && err instanceof Error && err.stack) {
    payload.stack = err.stack
  }
  console.error(JSON.stringify(payload))
}

/**
 * Non-throw paths where there is no Error instance (e.g. Resend API returned { error }).
 */
export function logServerErrorDetails(
  scope: string,
  code: string,
  details: Record<string, unknown>,
): void {
  const payload: Record<string, unknown> = {
    level: 'error',
    scope,
    code,
    ...details,
  }
  console.error(JSON.stringify(payload))
}

/**
 * Configuration or operational warnings (no stack).
 */
export function logServerWarning(
  scope: string,
  code: string,
  message: string,
  meta?: Record<string, unknown>,
): void {
  console.error(
    JSON.stringify({
      level: 'warn',
      scope,
      code,
      message,
      ...meta,
    }),
  )
}

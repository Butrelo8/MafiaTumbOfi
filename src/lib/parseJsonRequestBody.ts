/**
 * Parse a JSON HTTP body string. Empty or whitespace-only input becomes `{}`.
 * `c.req.json()` rejects empty bodies on some runtimes; this matches typical REST behavior.
 *
 * @throws {SyntaxError} If the string is non-empty but not valid JSON.
 */
export function parseJsonRequestBody(raw: string): unknown {
  const t = raw.trim()
  if (t === '') return {}
  return JSON.parse(t)
}

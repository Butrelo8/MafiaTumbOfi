/**
 * Safely stringify JSON for embedding in a <script type="application/json"> tag.
 * It escapes <, >, and & to prevent XSS via </script> injection.
 */
export function safeJsonForScript(data: any): string {
  return JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026')
}

/**
 * Build `tel:` href for admin quick-call links from stored phone text.
 * Returns `null` when there are too few digits to treat as a dialable number.
 */
export function phoneToTelHref(raw: string | null | undefined): string | null {
  if (raw == null) return null
  const t = raw.trim()
  if (t === '' || t === '-') return null
  const digits = t.replace(/\D/g, '')
  if (digits.length < 10 || digits.length > 15) return null
  return `tel:${digits}`
}

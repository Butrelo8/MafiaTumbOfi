/**
 * Parse `proto` from the first segment of an RFC 7239 `Forwarded` header value.
 * Example: `for=192.0.2.1;proto=https` → `https`
 */
export function parseForwardedHeaderProto(
  forwarded: string | undefined,
): string | undefined {
  if (!forwarded) return undefined
  const segment = forwarded.split(',')[0]?.trim()
  if (!segment) return undefined
  for (const part of segment.split(';')) {
    const eq = part.indexOf('=')
    if (eq < 0) continue
    const key = part.slice(0, eq).trim().toLowerCase()
    if (key !== 'proto') continue
    let raw = part.slice(eq + 1).trim()
    raw = raw.replace(/^"+|"+$/g, '')
    if (raw) return raw.toLowerCase()
  }
  return undefined
}

export function getForwardedProtoFromRequest(
  getHeader: (name: string) => string | undefined,
): string | undefined {
  const xfp = getHeader('x-forwarded-proto')
  if (xfp) {
    const p = xfp.split(',')[0]?.trim().toLowerCase()
    if (p) return p
  }
  const fwd = getHeader('Forwarded') ?? getHeader('forwarded')
  return parseForwardedHeaderProto(fwd)
}

/**
 * Builds the CORS allowlist from env URLs: normalizes trailing slashes and adds
 * the paired www ↔ apex origin so https://example.com and https://www.example.com
 * both match (browser Origin must be listed exactly; they differ).
 */
export function expandCorsAllowedOrigins(rawOrigins: string[]): string[] {
  const set = new Set<string>()

  for (const raw of rawOrigins) {
    const trimmed = raw.trim()
    if (!trimmed) continue

    let base: string
    try {
      base = new URL(trimmed).origin
    } catch {
      continue
    }

    set.add(base)
    addWwwApexPair(base, set)
  }

  return [...set]
}

function addWwwApexPair(origin: string, set: Set<string>): void {
  let url: URL
  try {
    url = new URL(origin)
  } catch {
    return
  }

  const host = url.hostname
  if (host === 'localhost' || host.endsWith('.localhost') || /^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
    return
  }

  try {
    if (host.startsWith('www.')) {
      const apexHost = host.slice(4)
      if (apexHost) {
        set.add(`${url.protocol}//${apexHost}${url.port ? `:${url.port}` : ''}`)
      }
    } else {
      set.add(`${url.protocol}//www.${host}${url.port ? `:${url.port}` : ''}`)
    }
  } catch {
    /* ignore */
  }
}

/** Normalize request Origin header for lookup (handles odd trailing slashes). */
export function normalizeRequestOrigin(origin: string): string {
  try {
    return new URL(origin).origin
  } catch {
    return origin.replace(/\/$/, '')
  }
}

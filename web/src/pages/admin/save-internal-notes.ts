import type { APIRoute } from 'astro'
import { normalizePublicApiBaseUrl } from '../../lib/publicApiUrl'

const MAX_NOTES_LEN = 10_000

/**
 * Admin relay: PATCH booking `internal_notes` with Clerk Bearer (server-side token).
 * JSON body: `{ bookingId: number, internalNotes: string | null }`.
 */
export const prerender = false

export const POST: APIRoute = async ({ request, locals }) => {
  const { isAuthenticated, getToken } = locals.auth()
  if (!isAuthenticated) {
    return new Response(JSON.stringify({ ok: false, code: 'UNAUTHORIZED' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  let body: unknown
  try {
    body = await request.json()
  } catch {
    return new Response(JSON.stringify({ ok: false, code: 'INVALID_JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const rec = body as { bookingId?: unknown; internalNotes?: unknown }
  const bookingId = Number(rec.bookingId)
  if (!Number.isInteger(bookingId) || bookingId <= 0) {
    return new Response(
      JSON.stringify({ ok: false, code: 'VALIDATION_ERROR', message: 'ID inválido' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } },
    )
  }

  let internalNotes: string | null
  if (rec.internalNotes === null || rec.internalNotes === undefined) {
    internalNotes = null
  } else if (typeof rec.internalNotes === 'string') {
    if (rec.internalNotes.length > MAX_NOTES_LEN) {
      return new Response(
        JSON.stringify({ ok: false, code: 'VALIDATION_ERROR', message: 'Texto demasiado largo' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } },
      )
    }
    internalNotes = rec.internalNotes === '' ? null : rec.internalNotes
  } else {
    return new Response(
      JSON.stringify({ ok: false, code: 'VALIDATION_ERROR', message: 'Notas inválidas' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } },
    )
  }

  const apiUrl = normalizePublicApiBaseUrl(import.meta.env.PUBLIC_API_URL)
  const token = await getToken()

  try {
    const response = await fetch(`${apiUrl}/api/admin/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ internalNotes }),
    })

    const text = await response.text()
    let parsed: unknown
    try {
      parsed = text ? JSON.parse(text) : null
    } catch {
      parsed = null
    }

    if (!response.ok) {
      const err = (parsed as { error?: { message?: string; code?: string } })?.error
      return new Response(
        JSON.stringify({
          ok: false,
          code: err?.code ?? 'API_ERROR',
          message: err?.message ?? `HTTP ${response.status}`,
        }),
        {
          status: response.status >= 500 ? 502 : 400,
          headers: { 'Content-Type': 'application/json' },
        },
      )
    }

    const data = (parsed as { data?: { internalNotes?: string | null } })?.data
    return new Response(JSON.stringify({ ok: true, data: data ?? { internalNotes } }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('[admin-ui] save-internal-notes relay failed:', error)
    return new Response(
      JSON.stringify({ ok: false, code: 'RELAY_FAILED', message: 'Error de red' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } },
    )
  }
}

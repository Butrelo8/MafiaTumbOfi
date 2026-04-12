import type { APIRoute } from 'astro'
import { ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE } from '../../../../src/lib/adminDeleteAllBookings'
import { normalizePublicApiBaseUrl } from '../../lib/publicApiUrl'

/**
 * Admin relay: hard-delete all booking rows via API POST (Clerk Bearer server-side).
 * JSON body: `{ confirm: 'DELETE_ALL_BOOKINGS' }` or `{ dryRun: true }` for count only.
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

  const rec = body as { confirm?: unknown; dryRun?: unknown }
  if (rec.dryRun === true) {
    // ok
  } else if (rec.confirm !== ADMIN_DELETE_ALL_BOOKINGS_CONFIRM_PHRASE) {
    return new Response(
      JSON.stringify({ ok: false, code: 'VALIDATION_ERROR', message: 'Confirmación inválida' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } },
    )
  }

  const apiUrl = normalizePublicApiBaseUrl(import.meta.env.PUBLIC_API_URL)
  const token = await getToken()

  try {
    const response = await fetch(`${apiUrl}/api/admin/bookings/delete-all`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body as Record<string, unknown>),
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
          status: response.status >= 500 ? 502 : response.status === 403 ? 403 : 400,
          headers: { 'Content-Type': 'application/json' },
        },
      )
    }

    return new Response(JSON.stringify({ ok: true, data: (parsed as { data?: unknown })?.data }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('[admin-ui] delete-all-bookings relay failed:', error)
    return new Response(
      JSON.stringify({ ok: false, code: 'RELAY_FAILED', message: 'Error de red' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } },
    )
  }
}

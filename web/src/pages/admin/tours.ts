import type { APIRoute } from 'astro'
import { normalizePublicApiBaseUrl } from '../../lib/publicApiUrl'

/**
 * Admin relay for tour dates (Clerk Bearer):
 * - `GET /admin/tours` → `GET /api/admin/tours`
 * - `POST /admin/tours` → `POST /api/admin/tours` (JSON body forwarded)
 */
export const prerender = false

export const GET: APIRoute = async ({ locals }) => {
  const { isAuthenticated, getToken } = locals.auth()
  if (!isAuthenticated) {
    return new Response(
      JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'Authentication required' } }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      },
    )
  }

  const apiUrl = normalizePublicApiBaseUrl(import.meta.env.PUBLIC_API_URL)
  const token = await getToken()

  try {
    const response = await fetch(`${apiUrl}/api/admin/tours`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })

    const text = await response.text()
    return new Response(text || 'null', {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('[admin-ui] admin/tours relay failed:', error)
    return new Response(
      JSON.stringify({ error: { code: 'RELAY_FAILED', message: 'Error de red' } }),
      {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      },
    )
  }
}

export const POST: APIRoute = async ({ request, locals }) => {
  const { isAuthenticated, getToken } = locals.auth()
  if (!isAuthenticated) {
    return new Response(
      JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'Authentication required' } }),
      {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      },
    )
  }

  let bodyText: string
  try {
    bodyText = await request.text()
  } catch {
    return new Response(
      JSON.stringify({ error: { code: 'INVALID_BODY', message: 'Cuerpo inválido' } }),
      { status: 400, headers: { 'Content-Type': 'application/json' } },
    )
  }

  const forwardBody = bodyText.trim().length > 0 ? bodyText.trim() : '{}'

  const apiUrl = normalizePublicApiBaseUrl(import.meta.env.PUBLIC_API_URL)
  const token = await getToken()

  try {
    const response = await fetch(`${apiUrl}/api/admin/tours`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: forwardBody,
    })

    const text = await response.text()
    return new Response(text || 'null', {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (error) {
    console.error('[admin-ui] admin/tours POST relay failed:', error)
    return new Response(
      JSON.stringify({ error: { code: 'RELAY_FAILED', message: 'Error de red' } }),
      {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      },
    )
  }
}

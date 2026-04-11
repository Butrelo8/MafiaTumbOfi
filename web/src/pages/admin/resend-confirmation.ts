import type { APIRoute } from 'astro'
import { normalizePublicApiBaseUrl } from '../../lib/publicApiUrl'

/**
 * Admin operator action relay:
 * - Reads Clerk token server-side (via locals.auth())
 * - Calls backend POST /api/admin/bookings/:id/resend-confirmation
 * - Redirects back to /admin for simple operator workflow
 */
export const POST: APIRoute = async ({ request, locals }) => {
  const { isAuthenticated, redirectToSignIn, getToken } = locals.auth()
  if (!isAuthenticated) {
    return redirectToSignIn({ returnBackUrl: '/admin' })
  }

  const formData = await request.formData()
  const bookingIdRaw = formData.get('bookingId')
  const bookingId = Number(bookingIdRaw)

  if (!bookingIdRaw || Number.isNaN(bookingId) || !Number.isInteger(bookingId) || bookingId <= 0) {
    return new Response('', {
      status: 303,
      headers: { Location: '/admin?resend=invalid' },
    })
  }

  const apiUrl = normalizePublicApiBaseUrl(import.meta.env.PUBLIC_API_URL)
  const token = await getToken()

  try {
    const response = await fetch(`${apiUrl}/api/admin/bookings/${bookingId}/resend-confirmation`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })

    if (response.ok) {
      return new Response('', {
        status: 303,
        headers: {
          Location: `/admin?resend=ok&bookingId=${bookingId}`,
        },
      })
    }

    let resendDetail = 'Error al reenviar la confirmación'
    try {
      const body: unknown = await response.json()
      const error = (body as { error?: { code?: string; message?: string } }).error
      const code = error?.code
      const message = error?.message
      resendDetail = `${code ?? 'ERROR'}: ${message ?? 'Sin mensaje detallado'}`
    } catch {
      // Ignore parse errors and keep generic detail.
    }

    // Avoid very long URLs; keep the first chunk.
    resendDetail = resendDetail.slice(0, 200)

    return new Response('', {
      status: 303,
      headers: {
        Location: `/admin?resend=error&bookingId=${bookingId}&resendDetail=${encodeURIComponent(
          resendDetail,
        )}`,
      },
    })
  } catch (error) {
    console.error('[admin-ui] Resend relay failed:', error)
    return new Response('', {
      status: 303,
      headers: { Location: '/admin?resend=error' },
    })
  }
}

export const prerender = false

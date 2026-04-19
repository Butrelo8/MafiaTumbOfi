import type { APIRoute } from 'astro'
import { BOOKING_PIPELINE_STATUS_VALUES } from '../../../../src/lib/bookingPipeline'
import { normalizePublicApiBaseUrl } from '../../lib/publicApiUrl'

function isPipelineValue(v: string): boolean {
  return (BOOKING_PIPELINE_STATUS_VALUES as readonly string[]).includes(v)
}

/**
 * Admin operator relay: updates `pipeline_status` via API PATCH (Clerk token server-side).
 */
export const POST: APIRoute = async ({ request, locals }) => {
  const { isAuthenticated, redirectToSignIn, getToken } = locals.auth()
  if (!isAuthenticated) {
    return redirectToSignIn({ returnBackUrl: '/admin' })
  }

  const formData = await request.formData()
  const bookingIdRaw = formData.get('bookingId')
  const pipelineRaw = formData.get('pipelineStatus')
  const bookingId = Number(bookingIdRaw)
  const pipelineStatus = typeof pipelineRaw === 'string' ? pipelineRaw : ''

  if (!bookingIdRaw || Number.isNaN(bookingId) || !Number.isInteger(bookingId) || bookingId <= 0) {
    return new Response('', {
      status: 303,
      headers: { Location: '/admin?pipeline=invalid' },
    })
  }

  if (!isPipelineValue(pipelineStatus)) {
    return new Response('', {
      status: 303,
      headers: { Location: '/admin?pipeline=invalid' },
    })
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
      body: JSON.stringify({ pipelineStatus }),
    })

    if (response.ok) {
      return new Response('', {
        status: 303,
        headers: { Location: '/admin?pipeline=ok' },
      })
    }

    return new Response('', {
      status: 303,
      headers: { Location: '/admin?pipeline=error' },
    })
  } catch (error) {
    console.error('[admin-ui] Pipeline update relay failed:', error)
    return new Response('', {
      status: 303,
      headers: { Location: '/admin?pipeline=error' },
    })
  }
}

export const prerender = false

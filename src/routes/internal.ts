import { Hono } from 'hono'
import { processDripEmails } from '../lib/dripProcessor'
import { errorResponse, successResponse } from '../lib/errors'
import { logServerError } from '../lib/safeLog'

export const internalRoutes = new Hono()

internalRoutes.post('/process-drip', async (c) => {
  const secret = process.env.DRIP_CRON_SECRET
  const auth = c.req.header('Authorization') ?? ''
  const expected = secret ? `Bearer ${secret}` : ''
  if (!secret || auth !== expected) {
    return errorResponse(c, 401, 'UNAUTHORIZED', 'Invalid or missing secret')
  }

  try {
    const result = await processDripEmails()
    return successResponse(c, result)
  } catch (err) {
    logServerError('internal', 'DRIP_PROCESS_FAILED', err)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to process drip emails')
  }
})

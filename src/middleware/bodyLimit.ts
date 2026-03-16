import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'

const MAX_SIZE = 100 * 1024 // 100KB

export async function bodyLimit(c: Context, next: Next) {
  const contentLength = c.req.header('content-length')
  if (contentLength && parseInt(contentLength, 10) > MAX_SIZE) {
    return errorResponse(c, 413, 'PAYLOAD_TOO_LARGE', 'Request body exceeds 100KB')
  }
  await next()
}

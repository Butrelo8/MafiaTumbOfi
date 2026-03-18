import type { Context, Next } from 'hono'
import { errorResponse } from '../lib/errors'

const MAX_SIZE = 100 * 1024 // 100KB

export async function bodyLimit(c: Context, next: Next) {
  const contentLengthHeader = c.req.header('content-length')
  if (contentLengthHeader) {
    const contentLength = Number.parseInt(contentLengthHeader, 10)
    if (!Number.isNaN(contentLength) && contentLength > MAX_SIZE) {
      return errorResponse(
        c,
        413,
        'PAYLOAD_TOO_LARGE',
        'Request body exceeds 100KB',
      )
    }
  }

  // If we don't have a usable Content-Length, enforce the limit by streaming the body.
  // We read only from a cloned request and stop once we exceed MAX_SIZE, then cancel.
  // This keeps the protection robust across proxies/clients that omit Content-Length.
  const rawReq = c.req.raw
  if (!rawReq.body) {
    await next()
    return
  }

  const clonedReq = rawReq.clone()
  const stream = clonedReq.body
  if (!stream) {
    await next()
    return
  }

  const reader = stream.getReader()
  let totalBytes = 0

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      if (!value) continue

      totalBytes += value.byteLength
      if (totalBytes > MAX_SIZE) {
        await reader.cancel().catch(() => undefined)
        return errorResponse(
          c,
          413,
          'PAYLOAD_TOO_LARGE',
          'Request body exceeds 100KB',
        )
      }
    }
  } catch {
    // Best-effort: if streaming enforcement fails, don't break legitimate requests.
    // (The Content-Length branch above still covers the common case.)
  }

  await next()
}

import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { Hono } from 'hono'

mock.module('../lib/dripProcessor', () => ({
  processDripEmails: async () => ({ email2Sent: 3, email3Sent: 1, errors: 0 }),
}))

const { internalRoutes } = await import('./internal')
const app = new Hono().route('/api/internal', internalRoutes)

describe('POST /api/internal/process-drip', () => {
  beforeEach(() => {
    process.env.DRIP_CRON_SECRET = 'cron-test-secret'
  })

  afterEach(() => {
    delete process.env.DRIP_CRON_SECRET
  })

  test('401 without Authorization', async () => {
    const res = await app.request('/api/internal/process-drip', { method: 'POST' })
    expect(res.status).toBe(401)
  })

  test('401 when DRIP_CRON_SECRET unset', async () => {
    delete process.env.DRIP_CRON_SECRET
    const res = await app.request('/api/internal/process-drip', {
      method: 'POST',
      headers: { Authorization: 'Bearer cron-test-secret' },
    })
    expect(res.status).toBe(401)
  })

  test('401 wrong secret', async () => {
    const res = await app.request('/api/internal/process-drip', {
      method: 'POST',
      headers: { Authorization: 'Bearer wrong' },
    })
    expect(res.status).toBe(401)
  })

  test('200 with correct Bearer secret', async () => {
    const res = await app.request('/api/internal/process-drip', {
      method: 'POST',
      headers: { Authorization: 'Bearer cron-test-secret' },
    })
    expect(res.status).toBe(200)
    const body = (await res.json()) as { data: { email2Sent: number; email3Sent: number } }
    expect(body.data.email2Sent).toBe(3)
    expect(body.data.email3Sent).toBe(1)
  })
})

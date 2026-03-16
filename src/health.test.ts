import { expect, test } from 'bun:test'
import { app } from './index'

test('GET /health returns 200 and status ok', async () => {
  const res = await app.request('/health')
  expect(res.status).toBe(200)
  const data = await res.json()
  expect(data).toEqual(expect.objectContaining({ status: 'ok' }))
  expect(data.version).toBeDefined()
})

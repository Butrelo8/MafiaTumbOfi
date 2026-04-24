import { describe, expect, test } from 'bun:test'
import { app } from '../index'

describe('GET /api/tours/upcoming', () => {
  test('returns { data } array with Cache-Control', async () => {
    const res = await app.request('/api/tours/upcoming')
    expect(res.status).toBe(200)
    expect(res.headers.get('Cache-Control')).toContain('max-age=60')
    const body = (await res.json()) as { data: unknown }
    expect(Array.isArray(body.data)).toBe(true)
    expect((body.data as unknown[]).length).toBeGreaterThanOrEqual(0)
  })
})

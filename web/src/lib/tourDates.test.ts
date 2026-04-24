import { describe, expect, mock, test } from 'bun:test'
import { loadTourDates } from './tourDates'

describe('loadTourDates', () => {
  test('uses API payload on 200 with non-empty data', async () => {
    const apiRow = {
      date: '2030-01-01',
      city: 'API City',
      venue: 'Venue',
      cta: { label: 'x', href: '#' },
    }
    const fetchFn = mock(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({ data: [apiRow] }),
      } as Response),
    )
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([apiRow])
    expect(fetchFn).toHaveBeenCalledWith('http://localhost:3001/api/tours/upcoming', {
      headers: { Accept: 'application/json' },
      signal: expect.any(AbortSignal),
    })
  })

  test('returns empty on HTTP error', async () => {
    const fetchFn = mock(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: async () => ({}),
      } as Response),
    )
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([])
  })

  test('returns empty when API returns empty data array', async () => {
    const fetchFn = mock(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({ data: [] }),
      } as Response),
    )
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([])
  })

  test('returns empty when json.data missing', async () => {
    const fetchFn = mock(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({}),
      } as Response),
    )
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([])
  })

  test('returns empty on fetch throw', async () => {
    const fetchFn = mock(() => Promise.reject(new Error('network')))
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([])
  })

  test('returns empty on JSON parse error', async () => {
    const fetchFn = mock(() =>
      Promise.resolve({
        ok: true,
        json: async () => {
          throw new SyntaxError('bad json')
        },
      } as Response),
    )
    const rows = await loadTourDates('http://localhost:3001', { fetchFn })
    expect(rows).toEqual([])
  })
})

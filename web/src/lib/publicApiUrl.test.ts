import { describe, expect, test } from 'bun:test'
import { normalizePublicApiBaseUrl } from './publicApiUrl'

describe('normalizePublicApiBaseUrl', () => {
  test('strips trailing slashes', () => {
    expect(normalizePublicApiBaseUrl('https://api.example.com/')).toBe('https://api.example.com')
    expect(normalizePublicApiBaseUrl('https://api.example.com///')).toBe('https://api.example.com')
  })

  test('uses dev default when unset or blank', () => {
    expect(normalizePublicApiBaseUrl(undefined)).toBe('http://localhost:3001')
    expect(normalizePublicApiBaseUrl('')).toBe('http://localhost:3001')
    expect(normalizePublicApiBaseUrl('   ')).toBe('http://localhost:3001')
  })

  test('leaves host without slash unchanged', () => {
    expect(normalizePublicApiBaseUrl('https://api.example.com')).toBe('https://api.example.com')
  })

  test('strips trailing /api so callers do not produce /api/api/...', () => {
    expect(normalizePublicApiBaseUrl('http://localhost:3001/api')).toBe('http://localhost:3001')
    expect(normalizePublicApiBaseUrl('http://localhost:3001/api/')).toBe('http://localhost:3001')
    expect(normalizePublicApiBaseUrl('https://render.example.com/api')).toBe('https://render.example.com')
  })
})

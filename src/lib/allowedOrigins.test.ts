import { describe, expect, test } from 'bun:test'
import { allowedOrigins, clerkAuthorizedParties } from './allowedOrigins'
import { expandCorsAllowedOrigins } from './corsOrigins'

describe('clerkAuthorizedParties', () => {
  test('matches CORS expansion of configured origins (www ↔ apex)', () => {
    expect(clerkAuthorizedParties).toEqual(expandCorsAllowedOrigins(allowedOrigins))
  })

  test('includes paired www host when list contains apex https origin', () => {
    const expanded = expandCorsAllowedOrigins(['https://mafiatumbada.com'])
    expect(expanded).toContain('https://www.mafiatumbada.com')
    expect(expanded).toContain('https://mafiatumbada.com')
  })
})

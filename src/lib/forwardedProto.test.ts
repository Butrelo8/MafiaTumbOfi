import { describe, expect, test } from 'bun:test'
import {
  getForwardedProtoFromRequest,
  parseForwardedHeaderProto,
} from './forwardedProto'

describe('parseForwardedHeaderProto', () => {
  test('extracts proto from first segment', () => {
    expect(parseForwardedHeaderProto('for=1.2.3.4;proto=https')).toBe('https')
  })

  test('handles quoted proto token', () => {
    expect(parseForwardedHeaderProto('proto="http"')).toBe('http')
  })

  test('uses first comma-separated forwarded pair', () => {
    expect(
      parseForwardedHeaderProto(
        'proto=https;host=a.com, for=9.9.9.9;proto=http',
      ),
    ).toBe('https')
  })

  test('returns undefined when missing', () => {
    expect(parseForwardedHeaderProto(undefined)).toBeUndefined()
    expect(parseForwardedHeaderProto('for=1.1.1.1')).toBeUndefined()
  })
})

describe('getForwardedProtoFromRequest', () => {
  test('prefers x-forwarded-proto over Forwarded', () => {
    const proto = getForwardedProtoFromRequest((name) => {
      if (name === 'x-forwarded-proto') return 'https, http'
      if (name === 'Forwarded') return 'proto=http'
      return undefined
    })
    expect(proto).toBe('https')
  })

  test('falls back to Forwarded when x-forwarded-proto absent', () => {
    const proto = getForwardedProtoFromRequest((name) => {
      if (name === 'Forwarded') return 'for=1.2.3.4;proto=https'
      return undefined
    })
    expect(proto).toBe('https')
  })
})

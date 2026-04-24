import { describe, expect, test } from 'bun:test'
import { parseJsonRequestBody } from './parseJsonRequestBody'

describe('parseJsonRequestBody', () => {
  test('empty and whitespace become empty object', () => {
    expect(parseJsonRequestBody('')).toEqual({})
    expect(parseJsonRequestBody('   ')).toEqual({})
    expect(parseJsonRequestBody('\n\t')).toEqual({})
  })

  test('parses valid JSON', () => {
    expect(parseJsonRequestBody('{"a":1}')).toEqual({ a: 1 })
    expect(parseJsonRequestBody('[]')).toEqual([])
  })

  test('throws on invalid JSON', () => {
    expect(() => parseJsonRequestBody('not json')).toThrow()
  })
})

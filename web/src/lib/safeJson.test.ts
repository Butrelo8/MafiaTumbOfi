import { describe, it, expect } from 'bun:test'
import { safeJsonForScript } from './safeJson'

describe('safeJsonForScript', () => {
  it('should stringify JSON', () => {
    const data = { foo: 'bar' }
    expect(safeJsonForScript(data)).toBe('{"foo":"bar"}')
  })

  it('should escape < characters', () => {
    const data = { html: '</script><script>alert(1)</script>' }
    const result = safeJsonForScript(data)
    expect(result).not.toContain('</script>')
    expect(result).toContain('\\u003c/script\\u003e')
  })

  it('should escape > characters', () => {
    const data = { html: '>' }
    const result = safeJsonForScript(data)
    expect(result).toContain('\\u003e')
    expect(result).not.toContain('>')
  })

  it('should escape & characters', () => {
    const data = { text: 'foo & bar' }
    const result = safeJsonForScript(data)
    expect(result).toContain('\\u0026')
    expect(result).not.toContain('&')
  })

  it('should handle complex objects', () => {
    const data = {
      id: 1,
      nested: {
        meta: '<script>',
        other: '&'
      }
    }
    const result = safeJsonForScript(data)
    expect(result).toContain('\\u003cscript\\u003e')
    expect(result).toContain('\\u0026')
  })
})

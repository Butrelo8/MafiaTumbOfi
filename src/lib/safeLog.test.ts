import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { logServerError, logServerErrorDetails, logServerInfo, logServerWarning } from './safeLog'

describe('safeLog', () => {
  const lines: string[] = []
  let origError: typeof console.error

  beforeEach(() => {
    lines.length = 0
    origError = console.error
    console.error = mock((msg: string) => {
      lines.push(msg)
    })
  })

  afterEach(() => {
    console.error = origError
  })

  test('logServerError in production omits stack', () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'
    try {
      const err = new Error('boom')
      err.stack = 'STACK_LINE'
      logServerError('test', 'E_CODE', err, { path: '/x' })
      expect(lines).toHaveLength(1)
      const parsed = JSON.parse(lines[0]!) as Record<string, unknown>
      expect(parsed.scope).toBe('test')
      expect(parsed.code).toBe('E_CODE')
      expect(parsed.message).toBe('boom')
      expect(parsed.path).toBe('/x')
      expect(parsed.stack).toBeUndefined()
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('logServerError in development includes stack for Error', () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'
    try {
      const err = new Error('boom')
      err.stack = 'STACK_LINE'
      logServerError('test', 'E_CODE', err)
      const parsed = JSON.parse(lines[0]!) as Record<string, unknown>
      expect(parsed.stack).toBe('STACK_LINE')
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('logServerErrorDetails emits JSON without throwing', () => {
    const prev = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'
    try {
      logServerErrorDetails('booking', 'RESEND', { name: 'ApiError', detail: 'x' })
      const parsed = JSON.parse(lines[0]!) as Record<string, unknown>
      expect(parsed.scope).toBe('booking')
      expect(parsed.code).toBe('RESEND')
      expect(parsed.name).toBe('ApiError')
    } finally {
      process.env.NODE_ENV = prev
    }
  })

  test('logServerWarning emits warn level', () => {
    logServerWarning('booking', 'CONFIG', 'missing env')
    const parsed = JSON.parse(lines[0]!) as Record<string, unknown>
    expect(parsed.level).toBe('warn')
    expect(parsed.message).toBe('missing env')
  })
})

describe('logServerInfo', () => {
  const lines: string[] = []
  let origLog: typeof console.log

  beforeEach(() => {
    lines.length = 0
    origLog = console.log
    console.log = mock((msg: string) => {
      lines.push(msg)
    })
  })

  afterEach(() => {
    console.log = origLog
  })

  test('emits single JSON line with info level on stdout', () => {
    logServerInfo('booking', 'REQUEST_RECEIVED', {
      bookingId: 1,
      ip: '10.0.0.1',
      hasMessage: false,
    })
    expect(lines).toHaveLength(1)
    const parsed = JSON.parse(lines[0]!) as Record<string, unknown>
    expect(parsed.level).toBe('info')
    expect(parsed.scope).toBe('booking')
    expect(parsed.code).toBe('REQUEST_RECEIVED')
    expect(parsed.bookingId).toBe(1)
    expect(parsed.ip).toBe('10.0.0.1')
  })
})

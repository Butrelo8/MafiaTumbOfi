import { describe, expect, test } from 'bun:test'
import {
  ADMIN_BOOKING_CSV_HEADERS,
  bookingToCsvCells,
  buildAdminBookingsCsv,
  escapeCsvField,
} from './adminExportCsv'

describe('escapeCsvField', () => {
  test('empty nullish', () => {
    expect(escapeCsvField(null)).toBe('')
    expect(escapeCsvField(undefined)).toBe('')
  })

  test('plain token unchanged', () => {
    expect(escapeCsvField('hello')).toBe('hello')
    expect(escapeCsvField(42)).toBe('42')
  })

  test('wraps comma quote cr lf', () => {
    expect(escapeCsvField('a,b')).toBe('"a,b"')
    expect(escapeCsvField('say "hi"')).toBe('"say ""hi"""')
    expect(escapeCsvField('line1\nline2')).toBe('"line1\nline2"')
    expect(escapeCsvField('a\rb')).toBe('"a\rb"')
  })
})

describe('buildAdminBookingsCsv', () => {
  test('header and data row column counts match', () => {
    const booking = {
      id: 7,
      name: 'Test',
      email: 't@example.com',
      phone: null,
      eventDate: '2026-06-01',
      city: 'Monterrey',
      eventType: null,
      duration: '2h',
      showType: null,
      attendees: 'menos_100',
      venueSound: null,
      budget: '15k_30k',
      leadPriority: 'medium',
      leadScore: 400,
      estimatedPriceRange: '15k – 45k MXN',
      message: 'Hello, world',
      status: 'sent',
      pipelineStatus: 'contacted',
      confirmationAttempts: 1,
      confirmationLastError: null,
      internalNotes: null,
      drip2DueAt: null,
      drip2SentAt: null,
      drip3DueAt: null,
      drip3SentAt: null,
      createdAt: 1_700_000_000_000,
    }
    expect(bookingToCsvCells(booking).length).toBe(ADMIN_BOOKING_CSV_HEADERS.length)
  })

  test('BOM prefix and CRLF line endings', () => {
    const csv = buildAdminBookingsCsv([
      {
        id: 1,
        name: 'A',
        email: 'a@b.co',
        phone: null,
        eventDate: null,
        city: null,
        eventType: null,
        duration: null,
        showType: null,
        attendees: null,
        venueSound: null,
        budget: null,
        leadPriority: null,
        leadScore: null,
        estimatedPriceRange: '-',
        message: null,
        status: 'pending',
        pipelineStatus: 'new',
        confirmationAttempts: 0,
        confirmationLastError: null,
        internalNotes: null,
        drip2DueAt: null,
        drip2SentAt: null,
        drip3DueAt: null,
        drip3SentAt: null,
        createdAt: 1_700_000_000_000,
      },
    ])
    expect(csv.startsWith('\uFEFF')).toBe(true)
    expect(csv.includes('\r\n')).toBe(true)
    expect(csv.split('\r\n').length).toBeGreaterThanOrEqual(3)
  })

  test('pending row includes confirmation attempts', () => {
    const cells = bookingToCsvCells({
      id: 2,
      name: 'B',
      email: 'b@b.co',
      phone: null,
      eventDate: null,
      city: null,
      eventType: null,
      duration: null,
      showType: null,
      attendees: null,
      venueSound: null,
      budget: null,
      leadPriority: null,
      leadScore: null,
      estimatedPriceRange: '-',
      message: null,
      status: 'pending',
      pipelineStatus: 'new',
      confirmationAttempts: 2,
      confirmationLastError: 'oops',
      internalNotes: null,
      drip2DueAt: null,
      drip2SentAt: null,
      drip3DueAt: null,
      drip3SentAt: null,
      createdAt: 1,
    })
    const attemptsIdx = ADMIN_BOOKING_CSV_HEADERS.indexOf('Intentos confirmación')
    expect(cells[attemptsIdx]).toBe('2')
  })

  test('failed status leaves attempts column empty', () => {
    const cells = bookingToCsvCells({
      id: 3,
      name: 'C',
      email: 'c@b.co',
      phone: null,
      eventDate: null,
      city: null,
      eventType: null,
      duration: null,
      showType: null,
      attendees: null,
      venueSound: null,
      budget: null,
      leadPriority: null,
      leadScore: null,
      estimatedPriceRange: '-',
      message: null,
      status: 'failed',
      pipelineStatus: 'new',
      confirmationAttempts: 9,
      confirmationLastError: null,
      internalNotes: null,
      drip2DueAt: null,
      drip2SentAt: null,
      drip3DueAt: null,
      drip3SentAt: null,
      createdAt: 1,
    })
    const attemptsIdx = ADMIN_BOOKING_CSV_HEADERS.indexOf('Intentos confirmación')
    expect(cells[attemptsIdx]).toBe('')
  })
})

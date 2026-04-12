import { describe, expect, test } from 'bun:test'
import {
  buildAdminBookingDrawerRows,
  formatAdminDrawerDate,
} from './adminBookingDrawer'

describe('formatAdminDrawerDate', () => {
  test('returns em dash for nullish', () => {
    expect(formatAdminDrawerDate(null)).toBe('—')
    expect(formatAdminDrawerDate(undefined)).toBe('—')
    expect(formatAdminDrawerDate('')).toBe('—')
  })

  test('formats ISO string', () => {
    const s = formatAdminDrawerDate('2026-04-11T12:00:00.000Z')
    expect(s).not.toBe('—')
    expect(s).toContain('2026')
  })

  test('formats unix ms number', () => {
    const s = formatAdminDrawerDate(1_714_300_800_000)
    expect(s).not.toBe('—')
  })
})

describe('buildAdminBookingDrawerRows', () => {
  test('includes core fields and drip labels', () => {
    const rows = buildAdminBookingDrawerRows({
      id: 7,
      name: 'Test Band',
      email: 'a@b.co',
      phone: '555',
      eventDate: '2026-05-01',
      city: 'Xalapa',
      eventType: 'Private',
      duration: '2h',
      showType: 'DJ',
      attendees: '100',
      venueSound: 'PA provided',
      budget: 'tier_2',
      leadScore: 400,
      leadPriority: 'medium',
      estimatedPriceRange: '15k–25k',
      message: 'Hello\nLine2',
      status: 'sent',
      pipelineStatus: 'contacted',
      confirmationLastError: null,
      confirmationAttempts: 1,
      drip2DueAt: null,
      drip2SentAt: null,
      drip3DueAt: null,
      drip3SentAt: null,
      createdAt: '2026-04-10T10:00:00.000Z',
    })
    const labels = rows.map((r) => r.label)
    expect(labels).toContain('ID')
    expect(labels).toContain('Mensaje')
    expect(labels).toContain('Drip 2 programado')
    expect(rows.find((r) => r.label === 'ID')?.value).toBe('7')
    expect(rows.find((r) => r.label === 'Nombre')?.value).toBe('Test Band')
    expect(rows.find((r) => r.label === 'Seguimiento')?.value).toBe('Contactado')
    expect(rows.find((r) => r.label === 'Mensaje')?.value).toContain('Hello')
  })
})

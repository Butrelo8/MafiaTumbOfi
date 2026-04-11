import { describe, expect, test } from 'bun:test'
import {
  BOOKING_PIPELINE_STATUS_VALUES,
  formatPipelineStatusLabel,
  isBookingPipelineStatus,
} from './bookingPipeline'

describe('BOOKING_PIPELINE_STATUS_VALUES', () => {
  test('has expected order', () => {
    expect(BOOKING_PIPELINE_STATUS_VALUES).toEqual(['new', 'contacted', 'closed'])
  })
})

describe('formatPipelineStatusLabel', () => {
  test('maps known values', () => {
    expect(formatPipelineStatusLabel('new')).toBe('Nuevo')
    expect(formatPipelineStatusLabel('contacted')).toBe('Contactado')
    expect(formatPipelineStatusLabel('closed')).toBe('Cerrado')
  })

  test('null and empty default to Nuevo', () => {
    expect(formatPipelineStatusLabel(null)).toBe('Nuevo')
    expect(formatPipelineStatusLabel('')).toBe('Nuevo')
  })

  test('unknown legacy passes through', () => {
    expect(formatPipelineStatusLabel('legacy')).toBe('legacy')
  })
})

describe('isBookingPipelineStatus', () => {
  test('guards enum', () => {
    expect(isBookingPipelineStatus('new')).toBe(true)
    expect(isBookingPipelineStatus('open')).toBe(false)
  })
})

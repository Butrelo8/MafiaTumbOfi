import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const bookingPath = join(__dirname, '../pages/booking.astro')

describe('booking page copy / structure', () => {
  test('includes intro, form section headings, and FAQ without changing fetch endpoint', () => {
    const src = readFileSync(bookingPath, 'utf8')
    expect(src).toContain('class="booking-intro"')
    expect(src).toContain('class="form-section-heading"')
    expect(src).toContain('Datos de contacto')
    expect(src).toContain('Detalles del evento')
    expect(src).toContain('section faq-section')
    expect(src).toContain('id="faq-heading"')
    expect(src).toContain('Preguntas frecuentes')
    expect(src).toContain('class="faq-item"')
    expect(src.match(/<details class="faq-item">/g)?.length).toBe(5)
    expect(src).toContain('/api/booking')
  })
})

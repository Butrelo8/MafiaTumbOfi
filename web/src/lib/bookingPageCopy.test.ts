import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const bookingRedirectPath = join(__dirname, '../pages/booking.astro')
const contratacionPath = join(__dirname, '../pages/contratacion.astro')
const bookingFormPath = join(__dirname, '../components/BookingForm.astro')

describe('booking / contratación pages', () => {
  test('legacy /booking route redirects to canonical press-kit URL', () => {
    const src = readFileSync(bookingRedirectPath, 'utf8')
    expect(src).toContain("Astro.redirect('/contratacion', 301)")
  })

  test('contratacion page includes intro, BookingForm, and FAQ', () => {
    const src = readFileSync(contratacionPath, 'utf8')
    expect(src).toContain("import Eyebrow from '../components/Eyebrow.astro'")
    expect(src).toContain('Para promotores y organizadores de eventos')
    expect(src).toContain('class="contratacion-home-ghost"')
    expect(src).toContain('>← Volver al sitio</a>')
    expect(src).toContain('class="booking-intro"')
    expect(src).toContain('<BookingForm')
    expect(src).toContain('section faq-section')
    expect(src).toContain('id="faq-heading"')
    expect(src).toContain('Preguntas frecuentes')
    expect(src).toContain('class="faq-item"')
    expect(src.match(/<details class="faq-item">/g)?.length).toBe(5)
  })

  test('BookingForm still posts to /api/booking', () => {
    const formSrc = readFileSync(bookingFormPath, 'utf8')
    expect(formSrc).toContain('/api/booking')
    expect(formSrc).toContain("trackPlausible('Booking Submit')")
    expect(formSrc).toContain("../lib/plausibleClient")
  })
})

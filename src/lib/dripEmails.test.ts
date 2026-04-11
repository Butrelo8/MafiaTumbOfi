import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { buildDripEmail2, buildDripEmail3, DRIP_EMAIL_2_VIDEO_URL } from './dripEmails'

afterEach(() => {
  delete process.env.PUBLIC_SITE_URL
  delete process.env.PRODUCTION_URL
  delete process.env.FRONTEND_URL
  delete process.env.PUBLIC_WHATSAPP_URL
})

beforeEach(() => {
  delete process.env.PUBLIC_SITE_URL
  delete process.env.PRODUCTION_URL
  delete process.env.FRONTEND_URL
})

describe('buildDripEmail2', () => {
  test('includes video URL and returns subject, html, text', () => {
    process.env.PUBLIC_SITE_URL = 'https://example.com'
    const e = buildDripEmail2('Ana')
    expect(e.subject).toContain('Mafia Tumbada')
    expect(e.html).toContain(DRIP_EMAIL_2_VIDEO_URL)
    expect(e.text).toContain(DRIP_EMAIL_2_VIDEO_URL)
    expect(e.html).toContain('Ana')
    expect(e.text).toContain('https://example.com/booking')
  })
})

describe('buildDripEmail3', () => {
  test('includes urgency + booking CTA', () => {
    process.env.FRONTEND_URL = 'https://band.test'
    const e = buildDripEmail3('Luis')
    expect(e.subject.toLowerCase()).toMatch(/asegura|fecha/)
    expect(e.html).toContain('https://band.test/booking')
    expect(e.text).toContain('https://band.test/booking')
    expect(e.html).toContain('Luis')
  })

  test('includes WhatsApp when PUBLIC_WHATSAPP_URL set', () => {
    process.env.FRONTEND_URL = 'https://x.com'
    process.env.PUBLIC_WHATSAPP_URL = 'https://wa.me/5215512345678'
    const e = buildDripEmail3('X')
    expect(e.text).toContain('wa.me')
    expect(e.html).toContain('wa.me')
  })
})

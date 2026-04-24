import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { buildDripEmail2, buildDripEmail3 } from './dripEmails'

const DEFAULT_DRIP_VIDEO_URL = 'https://www.youtube.com/watch?v=7Sx0yDjGoq0'

afterEach(() => {
  delete process.env.PUBLIC_SITE_URL
  delete process.env.PRODUCTION_URL
  delete process.env.FRONTEND_URL
  delete process.env.PUBLIC_WHATSAPP_URL
  delete process.env.DRIP_VIDEO_URL
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
    expect(e.html).toContain(DEFAULT_DRIP_VIDEO_URL)
    expect(e.text).toContain(DEFAULT_DRIP_VIDEO_URL)
    expect(e.html).toContain('Ana')
    expect(e.text).toContain('https://example.com/booking')
  })

  test('uses DRIP_VIDEO_URL when set', () => {
    process.env.PUBLIC_SITE_URL = 'https://example.com'
    process.env.DRIP_VIDEO_URL = 'https://www.youtube.com/watch?v=customid'
    const e = buildDripEmail2('Ana')
    expect(e.html).toContain('https://www.youtube.com/watch?v=customid')
    expect(e.text).toContain('https://www.youtube.com/watch?v=customid')
    expect(e.html).not.toContain(DEFAULT_DRIP_VIDEO_URL)
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

  test('plain text keeps blank-line paragraph breaks (only null lines dropped)', () => {
    process.env.FRONTEND_URL = 'https://band.test'
    const e = buildDripEmail3('Luis')
    expect(e.text).toMatch(/^Hola Luis,\n\n/)
    expect(e.text).toContain('\n\nLas fechas')
    expect(e.text).toMatch(/\n\nEquipo Mafia Tumbada$/)
  })

  test('includes WhatsApp when PUBLIC_WHATSAPP_URL set', () => {
    process.env.FRONTEND_URL = 'https://x.com'
    process.env.PUBLIC_WHATSAPP_URL = 'https://wa.me/5215512345678'
    const e = buildDripEmail3('X')
    expect(e.text).toContain('wa.me')
    expect(e.html).toContain('wa.me')
  })
})

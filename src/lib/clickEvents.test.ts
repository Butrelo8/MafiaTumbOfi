import { describe, expect, test } from 'bun:test'
import { bandSocialUrls } from '../../research/contenido/socials'
import { classifyLink } from './clickEvents'

const host = 'mafiatumbada.com'

describe('classifyLink', () => {
  test('WhatsApp redirect and phone', () => {
    expect(classifyLink(bandSocialUrls.whatsapp, host)).toEqual({ event: 'wa_click', net: '' })
    expect(classifyLink('tel:+522283538827', host)?.event).toBe('contact_click')
    expect(classifyLink('mailto:a@b.mx', host)?.event).toBe('contact_click')
  })
  test('every band social maps to its net', () => {
    const nets = { spotify: 'spotify', instagram: 'instagram', youtube: 'youtube', tiktok: 'tiktok', facebook: 'facebook', appleMusic: 'apple_music' } as const
    for (const [key, net] of Object.entries(nets)) {
      expect(classifyLink(bandSocialUrls[key as keyof typeof nets], host)).toEqual({ event: 'follow_click', net })
    }
  })
  test('nav anchors, other pages and foreign hosts are not counted', () => {
    expect(classifyLink('/#contratacion', host)).toBeNull()
    expect(classifyLink('https://example.com/', host)).toBeNull()
    expect(classifyLink('https://notinstagram.com/x', host)).toBeNull()
  })
})

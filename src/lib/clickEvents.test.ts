import { describe, expect, test } from 'bun:test'
import { bandSocialUrls } from '../../research/contenido/socials'
import { classifyLink, clickId, nologCookie, visitFlags } from './clickEvents'

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

describe('click id and nolog cookie', () => {
  test('the click id joins event, net and placement and fits what /e accepts', () => {
    expect(clickId({ event: 'follow_click', net: 'spotify' }, 'hero')).toBe('follow_click:spotify:hero')
    expect(clickId({ event: 'wa_click', net: '' }, '')).toBe('wa_click')
    expect(clickId({ event: 'follow_click', net: 'apple_music' }, 'footer')).toMatch(/^[a-z0-9_:-]{1,60}$/)
  })
  test('?nolog=1 sets a one-year cookie, ?nolog=0 clears it, anything else does nothing', () => {
    expect(nologCookie('?nolog=1')).toBe('nolog=1; Max-Age=31536000; Path=/; SameSite=Lax')
    expect(nologCookie('?a=b&nolog=0')).toContain('Max-Age=0')
    expect(nologCookie('')).toBeNull()
    expect(nologCookie('?nolog=2')).toBeNull()
  })
})

describe('visitFlags', () => {
  const mem = (init: Record<string, string> = {}) => {
    const m = { ...init }
    return { m, getItem: (k: string) => m[k] ?? null, setItem: (k: string, v: string) => { m[k] = v } }
  }
  test('first visit sets both flags and stores the local day and month', () => {
    const s = mem()
    expect(visitFlags(s, new Date(2026, 10, 23, 12))).toEqual({ nd: 1, nm: 1 })
    expect(s.m).toEqual({ ev_d: '2026-11-23', ev_m: '2026-11' })
  })
  test('same day sends nothing, next day only nd, next month both', () => {
    const s = mem()
    visitFlags(s, new Date(2026, 10, 23, 9))
    expect(visitFlags(s, new Date(2026, 10, 23, 22))).toEqual({})
    expect(visitFlags(s, new Date(2026, 10, 24))).toEqual({ nd: 1 })
    expect(visitFlags(s, new Date(2026, 11, 1))).toEqual({ nd: 1, nm: 1 })
  })
  test('a storage that throws sends nothing extra', () => {
    const boom = { getItem: () => { throw new Error('denied') }, setItem: () => { throw new Error('denied') } }
    expect(visitFlags(boom)).toEqual({})
  })
})

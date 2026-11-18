// POST /signup: fan-list sign-up (form field `contacto` = email or WhatsApp number, optional `ciudad`) into D1 (binding DB, table mto_fans).
// Stored: contact, kind, city, consent version, UTC time. Not stored: IP, user agent, headers. Spam: a hidden field (`web`) that people leave
// empty, a per-IP limit with the Rate Limiting binding SIGNUP_LIMIT (it keeps nothing), same-origin only. Duplicates answer ok and do not insert.
// Answers JSON { ok } or { ok:false, error } with error in contacto | consentimiento | limite | servidor.
import { record } from './e.js'

export const CONSENT_VERSION = 'aviso-2026-11-18'
const EMAIL = /^[^\s@]{1,64}@[^\s@.]+(\.[^\s@.]+)+$/
const json = (body, status = 200) => Response.json(body, { status })

export function parseContact(raw) {
  const text = String(raw ?? '').trim()
  if (text.length > 254) return null
  if (text.includes('@')) return EMAIL.test(text) ? { kind: 'email', contact: text.toLowerCase() } : null
  const digits = text.replace(/[\s().+-]/g, '')
  if (!/^\d{10,15}$/.test(digits)) return null
  return { kind: 'whatsapp', contact: digits.length === 10 ? `52${digits}` : digits }
}

export async function signup(request, env) {
  if (request.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } })
  const origin = request.headers.get('Origin')
  if (origin && origin !== new URL(request.url).origin) return json({ ok: false, error: 'servidor' }, 403)
  if (Number(request.headers.get('Content-Length') || 0) > 2000) return json({ ok: false, error: 'contacto' }, 413)
  let form
  try {
    form = await request.formData()
  } catch {
    return json({ ok: false, error: 'contacto' }, 400)
  }
  if (form.get('web')) return json({ ok: true }) // honeypot: looks like success, stores nothing
  if (env.SIGNUP_LIMIT) {
    const { success } = await env.SIGNUP_LIMIT.limit({ key: request.headers.get('CF-Connecting-IP') || 'none' })
    if (!success) return json({ ok: false, error: 'limite' }, 429)
  }
  const parsed = parseContact(form.get('contacto'))
  if (!parsed) return json({ ok: false, error: 'contacto' }, 400)
  if (form.get('consent') !== 'on') return json({ ok: false, error: 'consentimiento' }, 400)
  const city = String(form.get('ciudad') ?? '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, 60) || null
  try {
    await env.DB.prepare('INSERT OR IGNORE INTO mto_fans (contact, kind, city, consent_version) VALUES (?, ?, ?, ?)')
      .bind(parsed.contact, parsed.kind, city, CONSENT_VERSION).run()
  } catch {
    return json({ ok: false, error: 'servidor' }, 500)
  }
  record(env, 'signup', { page: '/', placement: 'lista' })
  return json({ ok: true })
}

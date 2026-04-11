/** Primary “how we sound” video for nurture Email 2. */
export const DRIP_EMAIL_2_VIDEO_URL = 'https://www.youtube.com/watch?v=7Sx0yDjGoq0'

export type DripEmailPayload = {
  subject: string
  html: string
  text: string
}

function publicSiteBase(): string {
  const raw =
    process.env.PUBLIC_SITE_URL ?? process.env.PRODUCTION_URL ?? process.env.FRONTEND_URL ?? ''
  return raw.replace(/\/$/, '')
}

function bookingPageUrl(): string {
  const base = publicSiteBase()
  return base ? `${base}/booking` : 'https://mafiatumbada.com/booking'
}

/**
 * Email 2 — “how we sound” + video link (Spanish, band voice).
 */
export function buildDripEmail2(name: string): DripEmailPayload {
  const bookingUrl = bookingPageUrl()
  const subject = 'Así sonamos — Mafia Tumbada'
  const text = [
    `Hola ${name},`,
    '',
    'Gracias por tu interés. Aquí puedes escuchar cómo suena Mafia Tumbada en vivo:',
    DRIP_EMAIL_2_VIDEO_URL,
    '',
    `Si quieres avanzar con tu evento, entra aquí: ${bookingUrl}`,
    '',
    '— Mafia Tumbada',
  ].join('\n')
  const html = `<p>Hola ${escapeHtml(name)},</p>
<p>Gracias por tu interés. Aquí puedes escuchar cómo suena Mafia Tumbada en vivo:</p>
<p><a href="${escapeHtml(DRIP_EMAIL_2_VIDEO_URL)}">${escapeHtml(DRIP_EMAIL_2_VIDEO_URL)}</a></p>
<p><a href="${escapeHtml(bookingUrl)}">Seguir con mi solicitud / contratación</a></p>
<p>— Mafia Tumbada</p>`
  return { subject, html, text }
}

/**
 * Email 3 — urgency + CTA (Spanish).
 */
export function buildDripEmail3(name: string): DripEmailPayload {
  const bookingUrl = bookingPageUrl()
  const wa = process.env.PUBLIC_WHATSAPP_URL?.trim()
  const subject = 'Asegura tu fecha — Mafia Tumbada'
  const lines = [
    `Hola ${name},`,
    '',
    'Las fechas para eventos se llenan rápido. Si quieres que revisemos tu evento con prioridad, responde pronto o vuelve al formulario.',
    '',
    `Formulario de contratación: ${bookingUrl}`,
  ]
  if (wa) lines.push('', `WhatsApp directo: ${wa}`)
  lines.push('', '— Mafia Tumbada')
  const text = lines.join('\n')
  const waHtml = wa ? `<p><a href="${escapeHtml(wa)}">WhatsApp directo</a></p>` : ''
  const html = `<p>Hola ${escapeHtml(name)},</p>
<p>Las fechas para eventos se llenan rápido. Si quieres que revisemos tu evento con prioridad, responde pronto o vuelve al formulario.</p>
<p><a href="${escapeHtml(bookingUrl)}">Ir al formulario de contratación</a></p>
${waHtml}
<p>— Mafia Tumbada</p>`
  return { subject, html, text }
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

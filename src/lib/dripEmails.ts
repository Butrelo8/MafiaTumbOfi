/** Primary "how we sound" video for nurture Email 2. */
export const DRIP_EMAIL_2_VIDEO_URL = 'https://www.youtube.com/watch?v=7Sx0yDjGoq0'

export type DripEmailPayload = {
  subject: string
  html: string
  text: string
}

type DripCta = {
  label: string
  url: string
  bookingUrl: string
}

function publicSiteBase(): string {
  const raw =
    process.env.PUBLIC_SITE_URL ?? process.env.PRODUCTION_URL ?? process.env.FRONTEND_URL ?? ''
  return raw.trim().replace(/\/$/, '')
}

function bookingPageUrl(): string {
  const base = publicSiteBase()
  return base ? `${base}/booking` : 'https://mafiatumbada.com/booking'
}

function resolveDripPrimaryCta(bookingUrl: string): DripCta {
  const wa = process.env.PUBLIC_WHATSAPP_URL?.trim()
  if (wa) {
    return {
      label: 'Hablar por WhatsApp',
      url: wa,
      bookingUrl,
    }
  }

  return {
    label: 'Ir al formulario de contratacion',
    url: bookingUrl,
    bookingUrl,
  }
}

function renderEmailShell(title: string, subtitle: string, bodyHtml: string): string {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;background:#f2f2f2;">
<tr>
<td align="center" style="padding:22px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;width:100%;border-collapse:separate;border-spacing:0;background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;">
<tr>
<td style="padding:20px 22px;background:linear-gradient(135deg, #0b0b0b 0%, #1c1c1c 100%);">
<p style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:#f3c965;">Mafia Tumbada</p>
<h2 style="margin:0 0 8px;font-family:Arial,sans-serif;font-size:24px;line-height:1.2;color:#ffffff;">${escapeHtml(title)}</h2>
<p style="margin:0;font-family:Arial,sans-serif;font-size:14px;line-height:1.55;color:#d1d5db;">${escapeHtml(subtitle)}</p>
</td>
</tr>
<tr>
<td style="padding:20px 22px;font-family:Arial,sans-serif;color:#1f2937;line-height:1.65;">
${bodyHtml}
</td>
</tr>
</table>
</td>
</tr>
</table>`
}

function renderPrimaryButton(label: string, url: string): string {
  const safeLabel = escapeHtml(label)
  const safeUrl = escapeHtml(url)
  return `<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:separate;margin:0;">
<tr>
<td align="center" style="background:#f3c965;border-radius:999px;">
<a href="${safeUrl}" style="display:inline-block;padding:12px 20px;font-size:14px;font-weight:700;color:#111827;text-decoration:none;">${safeLabel}</a>
</td>
</tr>
</table>`
}

/**
 * Email 2 - "how we sound" + video link (Spanish, band voice).
 */
export function buildDripEmail2(name: string): DripEmailPayload {
  const bookingUrl = bookingPageUrl()
  const subject = 'Asi sonamos - Mafia Tumbada'
  const text = [
    `Hola ${name},`,
    '',
    'Gracias por tu interes.',
    'Aqui puedes escuchar como suena Mafia Tumbada en vivo:',
    DRIP_EMAIL_2_VIDEO_URL,
    '',
    `Seguir con mi solicitud: ${bookingUrl}`,
    '',
    'Equipo Mafia Tumbada',
  ].join('\n')

  const safeName = escapeHtml(name)
  const html = renderEmailShell(
    'Asi sonamos',
    'Una muestra rapida para ayudarte a decidir.',
    `<p style="margin:0 0 12px;">Hola ${safeName},</p>
<p style="margin:0 0 16px;">Gracias por tu interes. Te compartimos un video para que escuches como suena Mafia Tumbada en vivo.</p>
${renderPrimaryButton('Ver video en YouTube', DRIP_EMAIL_2_VIDEO_URL)}
<p style="margin:14px 0 10px;">Si ya tienes fecha en mente, puedes continuar aqui:</p>
${renderPrimaryButton('Seguir con mi solicitud', bookingUrl)}
<p style="margin:16px 0 0;">Equipo Mafia Tumbada</p>`,
  )

  return { subject, html, text }
}

/**
 * Email 3 - urgency + CTA (Spanish).
 */
export function buildDripEmail3(name: string): DripEmailPayload {
  const bookingUrl = bookingPageUrl()
  const cta = resolveDripPrimaryCta(bookingUrl)
  const subject = 'Asegura tu fecha - Mafia Tumbada'

  const lines = [
    `Hola ${name},`,
    '',
    'Las fechas para eventos se llenan rapido.',
    'Si quieres que revisemos tu evento con prioridad, escribenos hoy.',
    '',
    `${cta.label}: ${cta.url}`,
    cta.url === bookingUrl ? null : `Formulario de contratacion: ${bookingUrl}`,
    '',
    'Equipo Mafia Tumbada',
  ]
  const text = lines.filter((line): line is string => line !== null).join('\n')

  const safeName = escapeHtml(name)
  const safeBookingUrl = escapeHtml(bookingUrl)
  const bookingFallback =
    cta.url === bookingUrl
      ? ''
      : `<p style="margin:14px 0 0;font-size:14px;color:#334155;">Tambien puedes revisar el formulario aqui: <a href="${safeBookingUrl}" style="color:#7a5a0a;text-decoration:underline;">Formulario de contratacion</a></p>`
  const html = renderEmailShell(
    'Asegura tu fecha',
    'Te ayudamos a cerrar disponibilidad cuanto antes.',
    `<p style="margin:0 0 12px;">Hola ${safeName},</p>
<p style="margin:0 0 16px;">Las fechas para eventos se llenan rapido. Si quieres que revisemos tu evento con prioridad, escribenos hoy.</p>
${renderPrimaryButton(cta.label, cta.url)}
${bookingFallback}
<div style="margin-top:16px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;">
<p style="margin:0 0 8px;font-size:13px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:#334155;">Para avanzar mas rapido, comparte:</p>
<ul style="margin:0 0 0 18px;padding:0;color:#0f172a;">
<li style="margin:0 0 6px;">Fecha y ciudad del evento</li>
<li style="margin:0 0 6px;">Tipo de evento</li>
<li style="margin:0;">Presupuesto aproximado</li>
</ul>
</div>
<p style="margin:16px 0 0;">Equipo Mafia Tumbada</p>`,
  )

  return { subject, html, text }
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
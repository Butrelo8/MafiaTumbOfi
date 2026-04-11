import { Resend } from 'resend'

let _resend: Resend | null = null

/** Only for tests: inject a mock client; `null` clears override and the lazy singleton. */
let resendOverride: Resend | null = null

export function setResendForTesting(client: Resend | null) {
  resendOverride = client
  if (client === null) {
    _resend = null
  }
}

export function getResend(): Resend {
  if (resendOverride) {
    return resendOverride
  }
  if (!_resend) {
    if (!process.env.RESEND_API_KEY) {
      throw new Error('RESEND_API_KEY is required for booking notifications')
    }
    _resend = new Resend(process.env.RESEND_API_KEY)
  }
  return _resend
}

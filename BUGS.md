# BUGS

Known bugs and workarounds. Updated automatically by the AI agent.

---

<!-- Add bugs below as they are found -->
<!-- Format:
## [BUG] Title
**Description:** What happens and when
**Workaround:** How to work around it in the meantime
**Status:** pending / in progress / blocked
**Reported:** YYYY-MM-DD
-->

## Resend: no email delivered to customer / “only send to your own email”
**Description:** In development, Resend only delivers to the Resend account owner’s email. Sending to other addresses (e.g. the booking customer) is rejected with a validation error; the app may still mark the booking as sent.
**Workaround:** Verify a domain at [resend.com/domains](https://resend.com/domains), set `RESEND_FROM_EMAIL` to an address on that domain (e.g. `noreply@tudominio.com`), and use that in production. For testing, use your Resend account email as the booking email so the confirmation is delivered.
**Status:** pending (Resend platform limitation)
**Reported:** 2026-03-16

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

## [BUG] API HTTPS redirect skipped when `x-forwarded-proto` is missing
**Description:** In production, `enforceHttps` (`src/middleware/https.ts`) only redirects to HTTPS when the `x-forwarded-proto` header is present and equals `http`. If the reverse proxy does not set `x-forwarded-proto` at all, the middleware does nothing and traffic may reach the app over plain HTTP (depending on how the host is exposed).
**Workaround:** Configure the edge proxy (Render, nginx, Caddy, etc.) to always set `x-forwarded-proto: https` for TLS-terminated requests; prefer TLS termination at the proxy so the app never receives raw HTTP from the internet.
**Status:** pending
**Reported:** 2026-03-22

## [BUG] Verbose `console.error` with full `Error` objects in API routes (production logs)
**Description:** Several handlers log the entire caught value (`console.error(..., error)` or `err`), e.g. `src/routes/admin.ts` (fetch/export failures), `src/routes/users.ts`, `src/middleware/adminAuth.ts`, and some `src/routes/booking.ts` catch paths. Log aggregators may store stack traces and internal messages that aid attackers with access to logs.
**Workaround:** Restrict log access; until code changes ship, treat API stdout as sensitive. Prefer logging a stable code + request id, and map details only in dev.
**Status:** pending
**Reported:** 2026-03-22

## [BUG] Admin booking export enabled when `NODE_ENV` is not exactly `production`
**Description:** `isAdminBookingExport` (`src/lib/adminBookingExport.ts`) returns `true` whenever `NODE_ENV !== 'production'`, including **unset** `NODE_ENV`. A production-like deploy mislabeled as non-production could expose `GET /api/admin/export/bookings` without `ALLOW_ADMIN_BOOKING_EXPORT=true`.
**Workaround:** Always set `NODE_ENV=production` on real production hosts (already in `render.yaml`). Do not rely on default/unset env for “production.”
**Status:** pending
**Reported:** 2026-03-22

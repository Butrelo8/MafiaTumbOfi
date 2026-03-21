# TODOS

Track open work and completed items by version. See CHANGELOG.md for full release notes.

**Roadmap (Hold Scope):** No first-paying-customer goal; no merch yet. **Primary milestone: deploy to VPS** (your domain + HTTPS). Resend, Monitoring, and Content/SEO are done as part of or right after that deploy — one place, one domain. Stripe webhook only when there is a product to sell.

---

## Open

---

### API — CORS: allowlist-only `Access-Control-Allow-Origin`
**What:** When `Origin` is not in the allowlist, do not fall back to `allowedOrigins[0]`; omit or reject so behavior matches “only listed origins” and is easier to audit.
**Why:** Current fallback is confusing and unnecessary; browsers still block mismatched credentialed origins, but explicit deny is clearer for reviewers and future changes.
**Context:** `src/index.ts` — `cors({ origin: (origin) => { ... } })`.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P2
**Depends on:** None

---

### Infra — Distributed rate limiting for multiple API instances
**What:** Replace or back in-memory booking/auth rate limit stores with a shared limiter (e.g. Redis, Upstash) or document single-instance requirement in DEPLOY.md.
**Why:** `Map`-based limits in `rateLimit.ts` / `rateLimitAuth.ts` reset per process; multiple workers = weaker protection.
**Context:** Comments already warn about trusted `x-forwarded-for`; scaling horizontally adds a new gap.
**Solution:**  
**Done When:** 
**Effort:** M
**Priority:** P2
**Depends on:** Decision to run more than one API instance/process

---

### API — Consistent success JSON for admin list routes
**What:** Align `GET /api/admin/bookings` (and export if kept) with `successResponse` / the same `{ data: ... }` conventions as other routes.
**Why:** Clients see mixed shapes (`{ data, total }` at top level vs `{ data: T }` wrapper elsewhere).
**Context:** `src/routes/admin.ts` vs `src/lib/errors.ts` `successResponse`.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P3
**Depends on:** None

---

### Ops — Health version matches shipped release
**What:** Drive `/health` `version` from `package.json`, env, or build-time inject instead of a hardcoded string.
**Why:** Avoids drift (e.g. release branch vs `version: '0.4.0'` in code).
**Context:** `src/index.ts` — `c.json({ status: 'ok', version: '0.4.0' })`.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P3
**Depends on:** None

---

### Tests — Unit tests for Stripe webhook verification helper
**What:** Add tests for `verifyWebhookSignature` / `getStripe` error paths (mock Stripe SDK) when the webhook route exists.
**Why:** Payment boundary should be covered before production traffic; helper is currently unused until POST /api/webhooks/stripe ships.
**Context:** `src/lib/stripe.ts`; pair with open “Payments — Implement Stripe webhook handler” todo.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P3
**Depends on:** Payments — Implement Stripe webhook handler

---

### Deploy — Acquire custom domain and migrate production to a VPS
**What:** (1) Acquire a custom domain (e.g. for the band) and (2) move production to a VPS: provision server, point DNS at the VPS, reverse proxy (nginx or Caddy), SSL (e.g. Let’s Encrypt), run API (Bun + SQLite on persistent path) and optionally serve frontend (Astro build or Node); document in DEPLOY.md.
**Why:** Full control, one bill, and your own HTTPS domain — which is when Resend domain verification, monitoring (VPS logs), and a proper “official” site (content/SEO) all land in one go.
**Solution:** 
**Done When:** 
**Context:** Current prod: Render (Bun, SQLite at /data) + Vercel (Astro SSR). Steps: buy/register domain → provision VPS → DNS A/AAAA to VPS → reverse proxy + SSL → deploy app. Scope: (A) API only on VPS, frontend stays on Vercel — add VPS API URL to Clerk + CORS. (B) API + frontend on same VPS — one domain, update Clerk + CORS. Use a process manager (e.g. systemd), persistent disk for SQLite, backup strategy. **With or right after this:** Resend domain (same domain), Sentry + VPS log checks, Content/SEO.
**Effort:** L
**Priority:** P2
**Depends on:** None

---

### Resend — Verify domain so confirmation emails reach any customer
**What:** Verify a sending domain in Resend and set RESEND_FROM_EMAIL so the customer confirmation email is delivered to any address (not only the Resend account owner).
**Why:** In test mode Resend only delivers to the account owner’s email; customers never receive the “Recibimos tu solicitud” email until a domain is verified.
**Context:** Verify at resend.com/domains; use a From address on that domain (e.g. noreply@tudominio.com). See BUGS.md “Resend: no email delivered to customer”. **Do when you have your domain on the VPS (HTTPS)** — same deploy cycle.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P2
**Depends on:** VPS (or any environment where you already use your custom domain with HTTPS)

---

### Payments — Implement Stripe webhook handler
**What:** Create POST /api/webhooks/stripe endpoint
**Why:** Required to handle subscription lifecycle events when ticket sales or merch are added
**Context:** Stripe client in src/lib/stripe.ts (lazy init). Verify signature before processing. Use idempotency keys.
**Solution:** 
**Done When:** 
**Effort:** M
**Priority:** P3
**Depends on:** STRIPE_WEBHOOK_SECRET in .env

---

### Content / SEO — Homepage, press kit, meta
**What:** Copy and structure for homepage, press kit, booking page; meta tags, Open Graph, optional sitemap so the site reads as the band’s official presence.
**Why:** Makes the site feel like a real official site for promoters and SEO.
**Context:** Astro pages in web/src/pages; add/expand content and meta in layouts or per-page. **Natural to do with or right after VPS** (one real domain, one “official” launch).
**Solution:** 
**Done When:** 
**Effort:** M
**Priority:** P3
**Depends on:** None

---

### Monitoring — Sentry or similar; check logs after deploys
**What:** Add Sentry (or similar) for error tracking; ensure logs are checked after each deploy.
**Why:** Catch production errors and failed deploys early; avoid blind debugging.
**Context:** .env.example has optional SENTRY_DSN. Wire Sentry in API (Hono) and/or frontend (Astro). **On VPS:** check VPS logs (e.g. systemd/journald or your reverse proxy logs) after deploy. If still on Render/Vercel, check their logs. Same habit either way.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P3
**Depends on:** None

---

### N8N — Run local instance on VPS for scheduled tasks and integrations
**What:** Run N8N as a local instance on the VPS (Docker or systemd); use it for scheduled tasks, optional notifications, and external API workflows; keep booking and Stripe in the app.
**Why:** One place for cron-like and integration workflows without adding cron or a queue to the app; webhooks, emails/notifications, and external API glue live in N8N.
**Context:** Boundary: app = DB, auth, booking, Stripe, critical path; N8N = schedules, inbound webhooks from external systems, optional emails/notifications, API glue. Secure N8N (auth, no public exposure or admin-only). Document in DEPLOY.md.
**Solution:** 
**Done When:** 
**Effort:** M
**Priority:** P3
**Depends on:** VPS deploy

---

### Postgres (VPS) — Add migration support (separate folders)
**What:** Add PostgreSQL support for the API by:
- introducing a runtime DB switch (e.g. `DB_DIALECT=sqlite|postgres`)
- reading Postgres connection from `PG_HOST/PG_PORT/PG_USER/PG_PASSWORD/PG_DATABASE`
- running Postgres migrations from a separate folder (e.g. `drizzle-postgres/`) at startup (idempotent/safe to re-run)
**Why:** When the VPS is ready, production should use Postgres instead of the SQLite file to support better ops (backups/tooling/scaling).
**Context:** Current setup is SQLite-only (`drizzle.config.ts` uses `dialect: 'sqlite'`, `scripts/run-migration.ts` applies `drizzle/*.sql`, and `scripts/check-db.ts` checks SQLite system tables).
**Solution:** 
**Done When:** 
**Effort:** L
**Priority:** P2
**Depends on:** VPS is provisioned with a working Postgres instance.

---

## Completed

### Security — Harden admin booking export endpoint (2026-03-21)
- **API:** `src/lib/adminBookingExport.ts` + guard on `GET /api/admin/export/bookings`; production requires `ALLOW_ADMIN_BOOKING_EXPORT=true`; error code `ADMIN_BOOKING_EXPORT_DISABLED`; no DB query when denied; success → one JSON audit line (`admin_booking_export`, `userId`, `sessionId`, `timestamp`).
- **Docs:** `.env.example`, DEPLOY.md (Option C).
- **Frontend:** `web/src/pages/admin/export-bookings.astro` — HTML error page on 403 with API message.
- **Tests:** `src/lib/adminBookingExport.test.ts` (env matrix); `src/routes/00-auth-protected.test.ts` (403/200/audit/no-audit when gated).

### Auth — Fix first-user-admin race on parallel signups (2026-03-21)
- **Implementation:** `getOrCreateUser` sets `is_admin` via a scalar SQL subquery in the same `INSERT` (`EXISTS` check), removing the separate admin-count query.
- **Tests:** `src/lib/users.test.ts` — empty DB + concurrent two Clerk IDs leaves exactly one admin; second user stays non-admin. Optional `{ db }` passes an in-memory SQLite so tests do not touch the file DB.

### Booking — confirmation outcome contract (2026-03-18)
- **API:** `POST /api/booking` now returns `data.confirmation` (`sent` | `pending`) alongside `bookingId`, and handles Resend throws for customer confirmation by keeping booking status as `pending`.
- **Frontend:** `web/src/pages/booking.astro` now shows different messaging when confirmation is `pending` instead of always claiming the email was sent.
- **Tests:** added regression tests covering confirmation “error return” and “throw” paths (`src/routes/booking.test.ts`).

### Deploy — Ship API + frontend to production (2026-03)
- **API:** Render (Bun + SQLite on persistent disk at /data). Start: `bun run migrate && bun run check-db && bun run start`.
- **Frontend:** Vercel (Astro SSR, @astrojs/vercel, Node 20 runtime patch).
- **Auth:** Clerk (production allowed origins via Instance API for *.vercel.app).
- **Email:** Resend (band notification + customer confirmation). See open todo: verify domain so customers receive to any address.
- **Docs:** DEPLOY.md, render.yaml, env checklist.

### Auth — Implement login with Clerk (2025-03-16)
- **Backend:** @clerk/backend, auth middleware with authenticateRequest, getClerkClient + setClerkClientForTesting for tests
- **Protected routes:** GET /api/admin/bookings, GET /api/users/me
- **Frontend:** @clerk/astro, middleware, SignInButton/UserButton/Show in layout, /admin page with bookings table
- **Astro:** output server, @astrojs/node 9.0.0 pinned (Astro 4 compatible; 9.5+/10 require Astro 5+)
- **Env:** root .env and web/.env both need Clerk keys; web/.env must include CLERK_SECRET_KEY for server-side auth
- **Sign-in:** email + password (and optional social); phone for Mexico not enabled (Clerk tier limitation)
- **Tests:** 00-auth-protected.test.ts (admin and user routes with mocked Clerk)

### Docs — Fix README booking storage (2025-03-15)
- **README:** Booking flow section updated to describe SQLite persistence (pending → sent/failed), confirmation email, and `bookings` table.

### v0.4.0 — Security hardening (2025-03-16)
- **Auth fix:** Removed broken auth middleware from users routes; TODO to re-enable with Clerk
- **Error log sanitization:** Stack only in development; Resend errors log only message/name
- **Rate limiter cleanup:** 5-min interval + proxy warning comment in rateLimit.ts
- **Auth rate limiting:** rateLimitAuth.ts (10 req/5 min) on /api/auth/*
- **CORS:** Multiple origins (FRONTEND_URL, STAGING_URL, PRODUCTION_URL)
- **Security headers:** hono/secure-headers (CSP, X-Frame-Options, HSTS)
- **Body limit:** 100KB global → 413 PAYLOAD_TOO_LARGE
- **HTTPS enforcement:** 301 redirect in production when x-forwarded-proto !== https
- **Audit logging:** Booking requests log id, ip, timestamp
- **Tests:** security.test.ts (body limit, auth rate limit, CORS, HTTPS)

### v0.3.0 — P1 + P2 TODOs (2025-03-15)
- **Run initial migration:** scripts/run-migration.ts; users + bookings tables
- **Honeypot field:** Hidden `website` in form; 400 SPAM_DETECTED when filled
- **Confirmation email:** Requester gets "Recibimos tu solicitud" after band notification
- **Store bookings in SQLite:** Insert before email; status pending → sent/failed
- **Booking flow (initial):** Form → POST /api/booking → validate → Resend → email. Astro form at /booking.

---
<!-- New completed items: add under version block with **Item:** Short description. -->

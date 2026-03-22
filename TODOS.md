# TODOS

Track open work and completed items by version. See CHANGELOG.md for full release notes.

**Roadmap (Hold Scope):** No first-paying-customer goal; no merch yet. **Primary milestone: deploy to VPS** (your domain + HTTPS). Resend, Monitoring, and Content/SEO are done as part of or right after that deploy — one place, one domain. Stripe webhook only when there is a product to sell.

---

## Open

### Infra — Distributed rate limiting for multiple API instances
**What:** Replace or back in-memory booking/auth rate limit stores with a shared limiter (e.g. Redis, Upstash) or document single-instance requirement in DEPLOY.md.
**Why:** `Map`-based limits in `rateLimit.ts` / `rateLimitAuth.ts` reset per process; multiple workers = weaker protection.
**Context:** Comments already warn about trusted `x-forwarded-for`; scaling horizontally adds a new gap.
**Solution:** Run a single Redis service in Coolify (same host/VPC as your apps). Add REDIS_URL (or host/port/password) to the API app’s env. Refactor booking + auth rate limiting to use a shared Redis-backed fixed window (or sliding window) with distinct key prefixes (e.g. rl:booking:, rl:auth:) so limits are consistent across all API replicas. Use INCR + EXPIRE (or a small Lua script for atomic window reset) keyed by the same client id logic as today (x-forwarded-for / x-real-ip behind a trusted proxy). Keep in-memory limiter as a dev fallback when REDIS_URL is unset so local dev stays simple. Document Coolify Redis wiring, env vars, and “single-instance API + SQLite vs multi-instance + Redis” in DEPLOY.md.
**Done When:** Production/staging API uses Redis when REDIS_URL is set; dev works without it. Booking and auth routes still enforce their intended limits across processes (verified by tests with a mock Redis or testcontainer, not a live network). DEPLOY.md / .env.example describe Coolify Redis and the trust requirement for forwarded IP headers.
**Effort:** M
**Priority:** P2
**Depends on:** Decision to run more than one API instance/process, will do when migratin to more robust work.

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
**Depends on:** If we ever do a shop. STRIPE_WEBHOOK_SECRET in .env

---

### Content / SEO — Global meta & Open Graph skeleton
**What:** Extend `web/src/layouts/Layout.astro` (or a small `Seo.astro` partial) with Twitter/OG tags, default `og:image` (or per-page override), `theme-color`, and optional `robots` where needed. Per-page `title` / `description` stay props-driven.
**Why:** Link previews and crawlers get consistent, professional signals without waiting on final copy.
**Context:** Today only basic `<meta name="description">` and `<title>`. Use env like `PUBLIC_SITE_URL` only when stable; avoid wrong canonicals on preview URLs until domain todo ships.
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P2
**Depends on:** None

---

### Content / SEO — Press kit page
**What:** Add a public route (e.g. `/prensa` or `/press`) with promoter-facing structure: short/long bio, approved photos/logos (or links to Drive/Dropbox), booking/contact CTA, optional tech rider PDF link.
**Why:** One shareable URL for bookers and press; supports “official band” positioning.
**Context:** New Astro page under `web/src/pages`; nav link from `Layout.astro`. Wire page-specific `title` / `description` / OG for that URL.
**Solution:** 
**Done When:** 
**Effort:** M
**Priority:** P2
**Depends on:** None (asset hosting can be external links for v1)

---

### Content / SEO — Homepage & booking copy pass
**What:** Rewrite/structure `index.astro` and `booking.astro` for promoters and fans: clear who the band is, what “contrataciones” means, trust signals, CTA flow; optional short FAQ block for SEO.
**Why:** Current pages may be thin; this is the core conversion and clarity work separate from meta plumbing.
**Context:** Keep existing booking form behavior; focus on headings, sections, and accessibility. Align tone with press kit when both exist.
**Solution:** 
**Done When:** 
**Effort:** M
**Priority:** P2
**Depends on:** None

---

### Content / SEO — Canonical URLs & sitemap after custom domain
**What:** Set canonical `<link rel="canonical">` and `og:url` from a single source of truth (e.g. `PUBLIC_SITE_URL` or build-time); add `sitemap.xml` (Astro `@astrojs/sitemap` or static route) and ensure it lists public routes only (exclude `/admin`).
**Why:** Wrong canonicals on `*.vercel.app` / `*.onrender.com` hurt sharing and indexing; sitemap matters once the real domain is live.
**Context:** Do when production URL is stable — same window as **Deploy — Acquire custom domain and migrate production to a VPS** (or at least when frontend serves from the final hostname).
**Solution:** 
**Done When:** 
**Effort:** S
**Priority:** P2
**Depends on:** Deploy — Acquire custom domain and migrate production to a VPS (or equivalent stable production origin)

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
**Depends on:** “Postgres when we need multi-instance writes or ops wants a managed DB,” and keep SQLite as the default VPS path until then.

---

## Completed

### Security — Post-review hardening (logs, proxy, health limit, export gate) (2026-03-22)
- **Logging:** `src/lib/safeLog.ts` — JSON lines with `scope`/`code`/`message`; stacks only when `NODE_ENV=development`. Wired in `admin.ts`, `booking.ts`, `users.ts`, `middleware/error.ts`, `middleware/adminAuth.ts`.
- **HTTPS:** `src/lib/forwardedProto.ts` — `enforceHttps` uses `X-Forwarded-Proto` or RFC 7239 `Forwarded` `proto=` when the former is absent.
- **Health:** `src/middleware/rateLimitHealth.ts` — 120 GET `/health` requests/min per client id (same IP extraction as booking limiter).
- **Export:** `isAdminBookingExportAllowed` — allow only `ALLOW_ADMIN_BOOKING_EXPORT=true` or `NODE_ENV=development` (deny unset/`test`/other).
- **Docs:** DEPLOY.md — reverse-proxy header expectations; `.env.example` — admin export wording.
- **Tests:** `safeLog.test.ts`, `forwardedProto.test.ts`, `security.test.ts` (Forwarded + health limit), `adminBookingExport.test.ts`, `00-auth-protected.test.ts` (export under `development`).

### Ops — Health version matches shipped release (2026-03-22)
- **API:** `src/lib/appVersion.ts` — `getAppVersion()` reads root `package.json` once at startup; optional `APP_VERSION` or `RELEASE_VERSION` (trimmed) overrides for CI/deploy.
- **Route:** `src/index.ts` — `GET /health` uses `getAppVersion()` instead of a hardcoded semver.
- **Docs:** `.env.example` — commented `APP_VERSION` / `RELEASE_VERSION`.
- **Tests:** `src/lib/appVersion.test.ts` (override precedence + trim); `src/health.test.ts` asserts `version` equals `package.json` and honors `APP_VERSION`.

### API — Consistent success JSON for admin list routes (2026-03-21)
- **API:** `src/routes/admin.ts` — `GET /api/admin/bookings` returns `successResponse` with `data: { bookings, total }`; `GET /api/admin/export/bookings` returns `successResponse` with `data: { exportedAt, total, last24hCount, bookings }`.
- **Frontend:** `web/src/pages/admin.astro` reads `result.data.bookings`.
- **Tests:** `src/routes/00-auth-protected.test.ts` assertions updated for nested `data`.

### API — CORS allowlist-only `Access-Control-Allow-Origin` (2026-03-21)
- **Implementation:** `src/index.ts` — disallowed `Origin` returns `undefined` from the `cors` callback so Hono omits `Access-Control-Allow-Origin` (no `allowedOrigins[0]` fallback).
- **Tests:** `src/security.test.ts` — GET and OPTIONS on `/health` with unknown origin assert no `Access-Control-Allow-Origin`; existing allowlisted-origin test unchanged.

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

# TODOS

Track open work and completed items by version. See CHANGELOG.md for full release notes.

---

## Open

### Resend — Verify domain so confirmation emails reach any customer
**What:** Verify a sending domain in Resend and set RESEND_FROM_EMAIL so the customer confirmation email is delivered to any address (not only the Resend account owner).
**Why:** In test mode Resend only delivers to the account owner’s email; customers (e.g. getmula.butrensky@gmail.com) never receive the “Recibimos tu solicitud” email until a domain is verified.
**Context:** Verify at resend.com/domains; use a From address on that domain (e.g. noreply@tudominio.com). See BUGS.md entry “Resend: no email delivered to customer”.
**Effort:** S
**Priority:** P2
**Depends on:** None

---

### Payments — Implement Stripe webhook handler
**What:** Create POST /api/webhooks/stripe endpoint
**Why:** Required to handle subscription lifecycle events when ticket sales or merch are added
**Context:** Stripe client in src/lib/stripe.ts (lazy init). Verify signature before processing. Use idempotency keys.
**Effort:** M
**Priority:** P3
**Depends on:** STRIPE_WEBHOOK_SECRET in .env

---

### Content / SEO — Homepage, press kit, meta
**What:** Copy and structure for homepage, press kit, booking page; meta tags, Open Graph, optional sitemap so the site reads as the band’s official presence.
**Why:** Makes the site feel like a real official site for promoters and SEO.
**Context:** Astro pages in web/src/pages; add/expand content and meta in layouts or per-page.
**Effort:** M
**Priority:** P3
**Depends on:** None

---

### Monitoring — Sentry or similar; check Render/Vercel logs after deploys
**What:** Add Sentry (or similar) for error tracking; ensure Render and Vercel logs are checked after deploys.
**Why:** Catch production errors and failed deploys early; avoid blind debugging.
**Context:** .env.example has optional SENTRY_DSN. Wire Sentry in API (Hono) and/or frontend (Astro). Post-deploy: open Render Logs and Vercel deployment logs to confirm no errors.
**Effort:** S
**Priority:** P3
**Depends on:** None

---

## Completed

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

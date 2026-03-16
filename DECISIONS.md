# DECISIONS

Architectural decisions and their rationale.
Updated automatically by the AI agent when decisions are made.

---

## 2026-03-16 — Deploy: Render (API) + Vercel (frontend) + SQLite on disk

**Context:** Need production deploy for API (Bun + Hono), Astro frontend (SSR), and SQLite without managed Postgres.
**Decision:** API on Render as a Web Service with a persistent disk at `/data` for SQLite; migrations at startup (`bun run migrate && bun run start`). Frontend on Vercel with `@astrojs/vercel`; repo root for Vercel set to `web/`.
**Alternatives considered:** Railway, Fly.io, single Vercel full-stack (Vercel serverless + external DB), Render Postgres.
**Why not the others:** Render supports Bun and persistent disks; SQLite on disk keeps MVP simple. Vercel is a good fit for Astro SSR and is free tier friendly. Separate API and frontend allow independent scaling and clear CORS/production URL handling.

---

## YYYY-MM-DD — Initial stack selection

**Context:** Starting a new micro SaaS project as a solo developer
**Decision:** Hono + Bun + PostgreSQL + Drizzle + Clerk + Stripe
**Alternatives considered:** Express + Node, Fastify + Node
**Why not the others:**
- Express: not TypeScript-native, slower, more boilerplate
- Fastify: more config overhead, less edge-ready than Hono
- Node: Bun is faster, TypeScript-native, simpler DX

---

## 2025-03-15 — Project initialized as Mafia Tumbada Oficial

**Context:** Adapting hono-template for a regional Mexican band's official web presence (official page, press kit, booking form).
**Decision:** Clerk and Stripe deferred; Resend prioritized for booking notifications.
**Alternatives considered:** Pure static site (Astro only, no backend).
**Why not the others:** A Hono API enables the booking form, dynamic press kit, and a future admin panel.

---

## 2025-03-15 — Astro frontend, SQLite, simple booking (no DB storage)

**Context:** Align stack with Fase 2 (Astro for landing/content, SQLite for MVP) and keep booking as simple as possible.
**Decision:** Frontend = Astro (static). DB = SQLite + Drizzle. Booking = form → POST /api/booking → validate → Resend → email to band; no persistence.
**Alternatives considered:** PostgreSQL (heavier for MVP); storing requests in SQLite (deferred).
**Why not the others:** SQLite fits “MVP, cero servidor”; no DB for booking keeps scope minimal and avoids schema/migrations for this flow.

---

## 2025-03-15 — In-memory rate limiting on booking

**Context:** POST /api/booking is public and calls Resend; needed protection against abuse and quota exhaustion.
**Decision:** In-memory rate limiter (5 requests per minute per IP) applied only to /api/booking. Client ID from x-forwarded-for or x-real-ip.
**Alternatives considered:** hono-rate-limiter package (adds unstorage peer); Cloudflare/WAF (infra-level).
**Why not the others:** Minimal diff with a small middleware; no new deps. Redis-backed limiter can be added later if needed.

---

## 2025-03-16 — Security hardening (multi-origin CORS, headers, rate limits)

**Context:** Security review identified auth bypass, log leakage, and missing protections on public endpoints.
**Decision:** (1) Multi-origin CORS via FRONTEND_URL, STAGING_URL, PRODUCTION_URL. (2) Hono secure-headers (CSP, X-Frame-Options, HSTS). (3) Rate limit auth endpoints (10 req/5 min). (4) Global body limit 100KB. (5) HTTPS redirect in production via x-forwarded-proto. (6) Sanitize error logs (no stack in prod; Resend errors log only message/name). (7) Remove broken auth middleware from users until Clerk; audit logging for bookings.
**Alternatives considered:** Single-origin CORS only; no rate limit on auth; logging full error objects.
**Why not the others:** Multi-origin supports staging/prod; rate limiting prevents brute force; sanitized logs avoid leaking secrets or stack traces in production.

---

## 2025-03-16 — Clerk authentication with minimal admin

**Context:** Need to protect backend routes and provide a way for the band to view booking requests without relying solely on email.
**Decision:** Implement Clerk for authentication. Backend uses @clerk/backend with authenticateRequest for JWT verification. Frontend uses @clerk/astro with prebuilt components (SignInButton, UserButton, Show). Admin panel is a simple Astro page at /admin that fetches bookings from GET /api/admin/bookings. Auth middleware supports setClerkClientForTesting for tests. Sign-in is email + password (and optional social); phone/SMS for Mexico is not enabled (Clerk free tier requires contacting support@clerk.dev to activate that country).
**Alternatives considered:** Custom JWT auth, Auth0, Supabase Auth.
**Why not the others:** Clerk has the best DX for this stack, prebuilt UI components reduce frontend work, and it's free for the expected scale. Custom JWT is more work; Auth0/Supabase don't have Astro integrations as mature as Clerk's.

---

## 2025-03-16 — Astro 4 + @astrojs/node 9.0.0 pinned

**Context:** Clerk requires SSR (output: server + adapter). Newer @astrojs/node (9.5+, 10.x) expect Astro 5+ config (e.g. image.endpoint as object, sessionDrivers) and fail under Astro 4.
**Decision:** Stay on Astro ^4.16 and pin @astrojs/node to 9.0.0 (exact). Adapter 9.0.0 uses string image.endpoint and is compatible with Astro 4.
**Alternatives considered:** Upgrade to Astro 5/6 and @astrojs/node 10; use another SSR adapter.
**Why not the others:** Minimal change and no Astro 5 migration; 9.0.0 works. Revisit Astro 5 when ecosystem (Clerk, Tailwind adapter) is fully aligned.

---

## 2025-03-16 — Clerk keys in both root and web .env

**Context:** Hono API runs from project root (reads root .env); Astro app runs from web/ (reads only web/.env). Clerk server-side code in Astro (middleware, auth()) needs CLERK_SECRET_KEY.
**Decision:** Root .env: CLERK_SECRET_KEY, CLERK_PUBLISHABLE_KEY (for API). web/.env: same CLERK_SECRET_KEY plus PUBLIC_CLERK_PUBLISHABLE_KEY (publishable key must be PUBLIC_ in Vite to be exposed to client). Do not rely on a single .env at root for the frontend.
**Alternatives considered:** Single .env at root; symlink or env loading from root in web.
**Why not the others:** Astro/Vite only load .env from the app root (web/). Duplicating the secret in web/.env is the supported way for the Astro server to have the key.

---

## 2026-03-16 — First-user-is-admin for /admin

**Context:** GET /api/admin/bookings only checked Clerk authentication; any signed-in user could read all bookings (privacy and business data exposure).
**Decision:** Admin routes require both authentication and an `isAdmin` flag on the local `users` table. The first Clerk user to sign in (first record in `users`) is created with `isAdmin: true`; all later users get `isAdmin: false`. User records are created on first access to /me or admin (via getOrCreateUser) using Clerk’s user API for email/name. Admin routes use authMiddleware then adminAuth; adminAuth calls getOrCreateUser and returns 403 if !user.isAdmin.
**Alternatives considered:** Email allowlist, Clerk Organization/roles, explicit “promote to admin” flow.
**Why not the others:** Single-band MVP with one or few admins; first sign-up as admin is zero-config and matches “band member signs up first” without extra env or Clerk org setup.

---
<!-- Add new decisions above this line -->

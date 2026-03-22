# CHANGELOG

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Security: production opt-in for `GET /api/admin/export/bookings` via `ALLOW_ADMIN_BOOKING_EXPORT=true`; structured audit log on successful export; docs in `.env.example` and DEPLOY.md; admin Astro page shows HTML guidance on 403.
- Deploy: Render (API with Bun + SQLite on persistent disk), Vercel (Astro frontend with @astrojs/vercel)
- `render.yaml` Blueprint: web service, disk at `/data`, DB_PATH=/data/sqlite.db, migrations at startup
- `DEPLOY.md` with step-by-step and env checklist for Render and Vercel
- `web/vercel.json` and Vercel serverless adapter in `web/astro.config.mjs` (`@astrojs/vercel/serverless` for Astro 4)
- `migrate` script in root package.json (runs scripts/run-migration.ts) for Render start command
- Booking deliverability observability: persist confirmation delivery last error + attempt count and expose it in admin UI; admins can re-send customer confirmation for `pending` bookings.

### Changed
- API: `GET /health` `version` comes from root `package.json`, with optional `APP_VERSION` or `RELEASE_VERSION` override (`src/lib/appVersion.ts`); documented in `.env.example`.
- API: `GET /api/admin/bookings` and `GET /api/admin/export/bookings` success bodies use `successResponse` — payload is under `data` (e.g. `data.bookings` + `data.total` for the list; export fields under `data` as well). Admin Astro page reads `data.bookings`; JSON download from export includes the same envelope.
- TODOS: Deploy marked completed (Render + Vercel + Clerk + Resend); added Content/SEO open todo; Resend domain verification remains P2
- DEPLOY.md: Post-launch section (Resend domain, custom domain, monitoring); health-check note (use Render URL for /health)

### Fixed
- API: CORS `origin` callback no longer falls back to the first allowlisted origin when `Origin` is not allowlisted; `Access-Control-Allow-Origin` is omitted instead (allowlist-only, easier to audit). Tests in `security.test.ts`.
- Auth: first-user admin bootstrap is atomic (single `INSERT` uses `EXISTS` subquery for `is_admin`) so parallel first signups cannot both become admin; optional `{ db }` on `getOrCreateUser` for isolated integration tests (`src/lib/users.test.ts`).
- Vercel: patch serverless runtime to nodejs20.x (adapter emits nodejs18.x, which Vercel rejects for new deployments); added `web/scripts/patch-vercel-runtime.mjs` and buildCommand post-step
- Security: harden request body size limit when `Content-Length` is missing and guard production HTTPS redirects to only act when `x-forwarded-proto` is present
- Booking: expose explicit confirmation outcome (`sent` vs `pending`) and handle Resend confirmation throws consistently

---

## [0.5.0] - 2026-03-16

### Added
- Admin authorization: first user to sign in becomes admin; only admins can access GET /api/admin/bookings (403 for non-admins)
- `users.isAdmin` column and migration 0002_add_users_is_admin.sql
- adminAuth middleware and getOrCreateUser (lib/users.ts) with first-user-is-admin logic
- Early RESEND_API_KEY validation in booking route (CONFIG_ERROR before DB insert if missing)
- Tests: admin-auth.test.ts (403 when not admin), booking status transition test (pending when confirmation fails)
- DECISIONS: first-user-is-admin pattern

### Changed
- Admin routes: authMiddleware + adminAuth (replaces auth-only check)
- GET /api/users/me: auto-creates user from Clerk on first access; returns 200 with user (no longer 404 when not in DB)
- booking.astro: default PUBLIC_API_URL to http://localhost:3001 (was 3000)
- booking route: comment documenting status semantics (pending / sent / failed)
- 00-auth-protected.test.ts: mock getOrCreateUser; /me test expects 200 with user data

### Fixed
- Admin data exposure: any authenticated Clerk user could read all bookings; now restricted to users with isAdmin
- Orphaned pending bookings when RESEND_API_KEY was missing (validation now runs before insert)

---

## [0.4.0] - 2025-03-16

### Added
- Security headers middleware (CSP, X-Frame-Options, HSTS) via hono/secure-headers
- Request body size limit 100KB (413 PAYLOAD_TOO_LARGE)
- HTTPS enforcement in production (301 redirect when x-forwarded-proto !== https)
- Rate limiter on auth endpoints (10 req/5 min per IP)
- Structured audit logging for booking requests (id, ip, timestamp)
- Security tests: body limit, auth rate limit, CORS, HTTPS no-redirect in dev

### Changed
- CORS: multiple origins (FRONTEND_URL, STAGING_URL, PRODUCTION_URL)
- Error handler: stack traces only in development
- Resend/confirmation errors: log only message and name
- Rate limiter: 5-min cleanup interval; getClientId exported for audit log
- Users routes: auth middleware removed until Clerk (P3); TODO comment added
- Middleware order: HTTPS → logger → security headers → body limit → CORS

### Fixed
- Auth bypass: removed misleading middleware that always returned 501
- Log leakage: no stack in prod; sanitized third-party error objects

---

## [0.3.0] - 2025-03-15

### Added
- `bookings` table (id, name, email, phone, event_date, message, status, created_at)
- Migration script `scripts/run-migration.ts` (runs all SQL in drizzle/)
- Honeypot field `website` on booking form; 400 SPAM_DETECTED when filled
- Persist booking to SQLite before sending email; status pending → sent/failed
- Confirmation email to requester after band notification ("Recibimos tu solicitud")
- Tests: honeypot rejection, Resend called twice on success

### Changed
- POST /api/booking: insert booking, send to band, send confirmation, update status

### Fixed
- _None_

---

## [0.2.0] - 2025-03-15

### Added
- Shared Astro layout (`web/src/layouts/Layout.astro`) with header and nav
- Tailwind CSS in `web/` with brand CSS variables and form/layout styling
- Spanish Zod error map (`src/lib/zod-es.ts`) for booking validation messages
- In-memory rate limiter (5 req/min per IP) on POST /api/booking
- Test: Resend send failure returns 500 and EMAIL_FAILED
- Test: GET /health returns 200 and `{ status: 'ok' }`
- TODOS: honeypot field, confirmation email to requester, store bookings in DB

### Changed
- Resend: lazy init via `getResend()` so API can start without RESEND_API_KEY
- Drizzle scripts: `db:generate` and `db:migrate` use current CLI syntax (no `:sqlite`)
- CORS default origin: `http://localhost:4321` (matches Astro)
- Auth middleware: returns 501 NOT_IMPLEMENTED until Clerk is integrated
- Booking validation: Spanish messages and "Error de validación" fallback
- Index exports `app` for health test

### Fixed
- _None_

---

## [0.1.0] - 2025-03-15

### Added
- Initial project structure with Hono + Bun
- Clerk auth middleware scaffold
- Stripe client (lazy init) and webhook verification helper
- Consistent error response shape across all endpoints
- Astro frontend in `web/` (index, booking form)
- POST /api/booking: validate body (Zod), send email via Resend, no DB storage
- SQLite + Drizzle ORM (Bun driver), drizzle.config.ts

### Changed
- Initialized project as Mafia Tumbada Oficial — updated package.json, README, and .env.example
- Database: PostgreSQL → SQLite + Drizzle (MVP stack)
- Frontend: Astro for site and booking form; FRONTEND_URL default 4321
- .env.example: DB_PATH instead of DATABASE_URL; RESEND_FROM_EMAIL optional

---

<!-- Add new versions above this line -->
<!-- Format:
## [X.Y.Z] - YYYY-MM-DD
### Added
### Changed
### Fixed
### Removed
-->

# DECISIONS

Architectural decisions and their rationale.
Updated automatically by the AI agent when decisions are made.

---

## 2026-04-10 — CORS allowlist: normalize `PRODUCTION_URL` + www/apex pair

**Context:** The booking page calls the API cross-origin; Hono `cors` only reflects `Access-Control-Allow-Origin` when the request `Origin` is in the allowlist. `https://mafiatumbada.com` and `https://www.mafiatumbada.com` are different origins; a trailing slash in `PRODUCTION_URL` also fails string equality vs the browser `Origin` header.
**Decision:** Build the allowlist with `expandCorsAllowedOrigins()` in `src/lib/corsOrigins.ts`: each configured URL is normalized via `new URL(...).origin`, then the paired hostname is added (`www.` ↔ apex) except for `localhost` and IPv4 literals. Incoming origins are matched after `normalizeRequestOrigin()`.
**Alternatives considered:** Document-only (“set both URLs in env” or “pick one hostname only”). Separate `PRODUCTION_URL_WWW` env.
**Why not the others:** One env value should work for the common Cloudflare/Vercel setup where both hostnames redirect or serve the same app; fewer manual misconfigurations.

## 2026-04-10 — Admin bookings: offset pagination + capped export

**Context:** `GET /api/admin/bookings` and export loaded all rows; large SQLite tables risk memory and slow TTFB. Export computed **`last24hCount`** by filtering the full in-memory list.
**Decision:** List route uses **`limit`/`offset`** (defaults 50 / 0, max limit 200), separate **`count(*)`** for **`data.total`**, and **`hasMore`**. Export uses two SQL **`count`** queries (all rows + rows with **`createdAt >= now - 24h`**) and a **`select`** ordered by **`createdAt` desc** with **`limit ADMIN_EXPORT_MAX_ROWS`** (default 10000, parsed in **`getAdminExportMaxRows`**, hard cap 50000). When **`total > cap`**, response includes **`truncated`**, **`returnedCount`**, **`totalInDb`**, **`warning`**. Admin UI: fixed page size 50 with **`?page=`** SSR links.
**Alternatives considered:** Cursor-based pagination (deferred until offset proves insufficient). Streaming NDJSON export (deferred; cap + env is enough for admin debugging).
**Why not the others:** Offset matches the stated TODO and is simplest for an internal admin table at ~1k–10k rows.

## 2026-04-10 — Booking budget tiers in `src/lib/bookingBudget.ts` (API + Astro)

**Context:** Budget enum strings, human-readable labels, booking-page hint copy, and admin sort ranks lived in three places (`src/routes/booking.ts`, `web/src/pages/booking.astro`, `web/src/pages/admin.astro`), risking drift when adding or renaming a tier.
**Decision:** Centralize in `src/lib/bookingBudget.ts` with **no Zod import** so the marketing/admin app can import the module without adding `zod` to `web/package.json`. The API uses `z.enum(BOOKING_BUDGET_VALUES)` in `src/routes/booking.ts`. Astro pages import via relative path `../../../src/lib/bookingBudget`; admin client sort uses a bundled `<script>` (not `is:inline`) to read `BOOKING_BUDGET_SORT_RANK`.
**Alternatives considered:** Yarn/bun workspace `packages/shared`; duplicate constants in web with a codegen step.
**Why not the others:** A single root-level module matches the current two-folder layout and keeps deploys simple.

## 2026-04-10 — `users.updated_at` auto-refresh + `confirmation_attempts` default 0

**Context:** `users.updated_at` used only `$defaultFn`, so it never changed on `UPDATE`. `bookings.confirmation_attempts` had Drizzle `default(1)` while `POST /api/booking` always inserted `0` before the first send attempt — a future insert omitting the field would disagree with app semantics. SQLite cannot `ALTER COLUMN` default in place.
**Decision:** Add Drizzle `.$onUpdateFn(() => new Date())` on `users.updated_at` (keep `$defaultFn` for inserts). Set `confirmation_attempts` default to `0` in `src/db/schema.ts` and ship `drizzle/0006_booking_confirmation_attempts_default_zero.sql` (rebuild `bookings`, `INSERT…SELECT`, drop old table, rename). Note: SQLite `integer` + `mode: 'timestamp'` stores **epoch seconds**, so two updates in the same wall-clock second write the same `updated_at`.
**Alternatives considered:** Drop `updated_at` until user updates exist (rejected: column is useful for future admin/audit). Rely on schema-only default change without SQL migration (rejected: existing DBs would keep SQLite DEFAULT1 for raw SQL inserts).
**Why not the others:** ORM-level `onUpdate` matches how Drizzle is meant to maintain touch timestamps; rebuilding `bookings` is the portable SQLite way to change a column default.

## 2026-03-25 — `db:migrate` must apply SQL, not drizzle-kit `up:sqlite`

**Context:** `db:migrate` was wired to `drizzle-kit up:sqlite`. In drizzle-kit 0.20.x, `up` upgrades internal migration snapshots/journal metadata; it does not execute pending SQL against the database. README quickstart told developers to run `bun db:migrate` for “Run pending migrations,” while production and deploy use `bun run migrate` (`scripts/run-migration.ts`), which applies `drizzle/*.sql` in order.
**Decision:** Point `db:migrate` at the same runner as `migrate` (`scripts/run-migration.ts`). Expose `drizzle-kit up:sqlite` under `db:upgrade-kit-snapshots` for the rare case when kit metadata needs upgrading. Do not use `drizzle-kit migrate` as the primary path — deploy and idempotent SQL handling are defined by the custom script (see `STATE.md`).
**Alternatives considered:** Replace `db:migrate` with `drizzle-kit migrate` only (rejected: may diverge from the custom runner and journal/SQL source of truth).
**Why not the others:** One command name (`db:migrate`) should match README and match what Render runs in spirit (apply schema SQL).

## 2026-03-25 — Booking budget: optional MXN range enum

**Context:** Promoters need a qualification signal without free-form noise; numeric free entry invites garbage. A **required** budget felt high-pressure; some leads prefer to discuss numbers after first contact.
**Decision:** Add nullable `budget` on `bookings` (existing rows stay null). `POST /api/booking` accepts optional `budget` — one of `menos_15k`, `15k_30k`, `30k_50k`, `50k_100k`, `mas_100k` (Zod `z.enum` + preprocess so `''`/`undefined` omit); DB stores `null` when omitted. Band email includes a readable budget line only when present (labels from `src/lib/bookingBudget.ts`, shared with Astro). Public form: non-required `<select>` after date/city/event type, placeholder “Lo vemos después”, helper copy, subtle contextual hints on change. Admin: same labels + sort (`data-budget` / `data-timestamp`). Migration `drizzle/0005_booking_budget_field.sql`; apply via existing `bun run migrate`.
**Alternatives considered:** Integer MXN column; min/max two-column range; required enum (rejected for UX pressure).
**Why not the others:** Enum ranges keep validation and triage simple when provided; optional preserves conversion when the lead is not ready to share a number.

## 2026-03-25 — Admin estimated price range: computed at read time

**Context:** Admin needs a fast “expectation setting” signal for leads without adding extra DB complexity or changing the public booking POST contract. The inputs used by the marketing form (city, duration, attendees) are optional, and estimates must degrade safely when fields are missing.
**Decision:** Implement `src/lib/estimatedPriceRange.ts` as a pure helper and compute `estimatedPriceRange` at read-time inside `src/routes/admin.ts` for both `GET /api/admin/bookings` and `GET /api/admin/export/bookings`. The pricing heuristics use module-level constants (not env vars) so the algorithm stays deterministic and testable. The public booking response remains unchanged.
**Alternatives considered:** Persisting the estimate in the `bookings` table (requires migration + backfill + dealing with future model changes), computing the estimate in the client (would leak heuristics variability across environments), and wiring the constants via env vars (hurts determinism + complicates caching and tests).
**Why not the others:** This is a read-only expectation helper for admins; storing introduces long-lived data correctness concerns, and client-side computation reduces consistency across admin views. Module constants keep Bun tests deterministic and avoid configuration drift.

## 2026-03-24 — Booking form: persist structured detail fields in SQLite

**Context:** The marketing booking page collects structured fields (city, event type, duration, show type, attendees, venue sound) beyond the original free-text-centric form. The band notification email alone would lose queryable history and admin export fidelity.
**Decision:** Add six nullable columns on `bookings` (`city`, `event_type`, `duration`, `show_type`, `attendees`, `venue_sound`), extend `bookingSchema` with optional string fields (with `.max()` bounds), persist on insert, and append the same fields to the band-facing Resend plaintext body. Ship SQL migration `0004_booking_detail_fields.sql`; apply via existing `bun run migrate` / deploy pipeline.
**Alternatives considered:** Email-only (no DB columns); require `city`/`eventType` on the API (stricter than legacy clients).
**Why not the others:** Persistence keeps admin list/export and future reporting consistent; optional API fields avoid breaking older clients and tests.

## 2026-03-24 — Homepage and press kit merged into single-scroll page

**Context:** The press kit was a separate `/press-kit` route with `MarketingLayout`. To reduce friction for press/promoters (one URL, less navigation), we merged homepage and press kit into a single long-scroll page at `/`.
**Decision:** Replace minimal `index.astro` with combined page (hero, stats, bio, socials, discography, members, shows, press assets, booking CTA). Use `MarketingLayout` for consistent dark aesthetic. Canonical URL points at base domain (no `/press-kit` suffix). Old `/press-kit` URLs redirect to `/` via `web/vercel.json`. Nav links updated to homepage anchors. Add `homeCanonical` helper in `publicSiteUrl.ts` for homepage canonical; keep `pressKitCanonical` unused but safe.
**Alternatives considered:** Keep two separate pages; redirect `/press-kit` to `/` without anchor; use `Layout.astro` (light theme) instead of `MarketingLayout`.
**Why not the others:** Single scroll is simpler for press (one link to share); anchor preserves deep-link to assets; `MarketingLayout` matches existing press aesthetic and avoids theme conflict.

## 2026-03-23 — Press kit: dedicated marketing layout and `/press-kit`

**Context:** The main app layout (`Layout.astro`) is light-themed, max-width content, and tuned for booking/admin. A promoter-facing press page needs a distinct visual treatment and full-width sections without rewriting the whole site theme.
**Decision:** Add `MarketingLayout.astro` plus `marketing-press.css` for the dark “press kit” aesthetic and full-bleed sections; expose the page at `/press-kit`. Keep Clerk header affordances on that layout. Canonical and `og:url` use `PUBLIC_SITE_URL` when set, otherwise the request origin (dev/preview-safe). Optional `PUBLIC_*` env vars gate WhatsApp and downloadable asset links; missing links show a non-clickable “Próximamente” state.
**Alternatives considered:** Reuse `Layout.astro` only (rejected: would fight Tailwind/global light body styles and narrow main column); route only `/prensa` (deferred: can add redirect/alias later).
**Why not the others:** A second layout isolates marketing CSS from app pages and avoids conditional theme branching in one file.

## 2026-03-22 — Security post-review hardening (logs, `Forwarded`, `/health` limit, export matrix)

**Context:** Full-codebase security review (2026-03-22) produced BUGS entries on verbose error logging, HTTPS when `x-forwarded-proto` is absent, and admin export enabled for any non-`production` `NODE_ENV` (including unset).
**Decision:** (1) `src/lib/safeLog.ts` — structured JSON logs; no stacks unless `NODE_ENV=development`. (2) `getForwardedProtoFromRequest` — use `X-Forwarded-Proto` or RFC 7239 `Forwarded` `proto=`; if both absent, still no redirect (avoid loops; document proxy setup in DEPLOY.md). (3) `rateLimitHealth` — 120 GET `/health` per minute per client id. (4) `isAdminBookingExportAllowed` — `true` only when `ALLOW_ADMIN_BOOKING_EXPORT=true` or `NODE_ENV=development`.
**Alternatives considered:** Redirect to HTTPS when forwarded proto is missing (rejected: possible redirect loops); omit health rate limit and document only (rejected: trivial abuse / noisy monitoring); keep “any non-production allows export” (rejected: mis-set `NODE_ENV` risk).
**Why not the others:** Prefer explicit, testable gates over implicit environment semantics.

---

## 2026-03-22 — Engineering lead codebase review (findings + backlog, ship path unchanged)

**Context:** Full-pass eng lead review of architecture, data flow, code quality, tests, and performance across the Hono API (`src/`), Astro app (`web/`), SQLite + Drizzle, Clerk, and Resend. Review confirmed MVP boundaries, called out DRY and test gaps, and reiterated ops limits (single SQLite file, in-memory rate limits per process).
**Decision:** Keep **Hold Scope** execution order: prioritize VPS deploy, Resend domain verification, and Content/SEO per `TODOS.md` and `STATE.md`. Capture hygiene work as explicit open TODOs instead of blocking ship: (1) single source of truth for `allowedOrigins` shared by CORS (`src/index.ts`) and Clerk `authorizedParties` (`src/middleware/auth.ts`); (2) align `GET /api/users/me` with `successResponse` / `{ data: T }` like admin list routes; (3) optional Playwright smoke for the public booking flow when E2E maintenance cost is acceptable. Document operational risks already tracked: distributed rate limiting (`TODOS`), unpaginated admin booking list at scale, SQLite writer contention under spike load.
**Alternatives considered:** Block release until DRY origins + Playwright land; fix `/me` and shared origins in the same day as the review without filing TODOs.
**Why not the others:** Origins and response-envelope changes are small, normal feature-branch work; Playwright adds value for UI+boundary regressions but is not a prerequisite for a thin booking form if deploy QA covers it; launch-critical path stays domain, email deliverability, and hosting.

---

## 2026-03-21 — Admin booking export: env gate in production + audit log

**Context:** `GET /api/admin/export/bookings` returns full PII; admin-only but a leaked session or misconfig exposes everything at once.
**Decision:** Keep the route for free-tier DB access (DEPLOY Option C). When `NODE_ENV=production`, deny with 403 and code `ADMIN_BOOKING_EXPORT_DISABLED` unless `ALLOW_ADMIN_BOOKING_EXPORT=true`. Non-production stays allowed for DX. On successful export, emit one JSON audit line to stdout (`type: audit`, `action: admin_booking_export`, `timestamp`, `userId`, `sessionId`).
**Alternatives considered:** Remove the route; always allow with only audit logging.
**Why not the others:** Removal breaks documented export workflow; logging alone does not reduce blast radius.

---

## 2026-03-21 — First admin bootstrap: atomic `INSERT` expression

**Context:** `getOrCreateUser` used a separate “count admins” query then `insert`, so two concurrent first signups could both observe zero admins and both get `isAdmin: true`.
**Decision:** Set `is_admin` in the same SQL statement as the insert using a scalar subquery: `CASE WHEN EXISTS (SELECT 1 FROM users WHERE is_admin = 1) THEN 0 ELSE 1 END`, via Drizzle `sql` on the insert values (no separate read before write for that flag).
**Alternatives considered:** SQLite `BEGIN IMMEDIATE` transaction wrapping count+insert; dedicated bootstrap row / mutex table.
**Why not the others:** Single-statement approach matches SQLite semantics, avoids extra schema, and keeps the hot path one insert with correct serialization of the EXISTS check relative to the new row.

---

## 2026-03-17 — Roadmap: Hold Scope, no merch / first-paying-customer goal

**Context:** CEO roadmap review; need a locked execution order without scope creep or a revenue milestone.
**Decision:** Hold Scope. Priority order: Resend domain (P2) first; then Content/SEO or Monitoring (P3); Stripe webhook only when there is a product (tickets/merch) to sell. No “first paying customer” milestone — we don’t have merch yet.
**Alternatives considered:** Scope expansion (add first-revenue milestone, delight items); scope reduction (Resend + Content only, defer Stripe indefinitely).
**Why not the others:** Keeps roadmap tight and achievable; Stripe stays in backlog until there’s something to sell; Resend and content/SEO deliver trust and official presence without revenue pressure.

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
## 2026-03-18 — Security hardening: body-size cap + HTTPS guard
**Context:** Public endpoints are exposed to untrusted clients and reverse proxies may omit `Content-Length` or `x-forwarded-proto`. Header-dependent enforcement can create gaps (DoS via large/chunked bodies) or availability issues (redirect loops / broken health checks).
**Decision:** Update `bodyLimit` to enforce the 100KB cap even when `Content-Length` is missing by streaming a cloned request body and canceling once the limit is exceeded. Update `enforceHttps` to redirect only when `x-forwarded-proto` is present and not `https` (and when `host` is available).
**Alternatives considered:** Rely only on `Content-Length`; enforce limits purely at the reverse proxy/WAF; always redirect in production regardless of header presence; remove app-level HTTPS enforcement entirely.
**Why not the others:** This keeps protection robust at the app boundary (defense-in-depth) without adding dependencies, and avoids redirect behavior when the proxy contract isn’t met.
---
## 2026-03-18 — Booking confirmations: explicit contract + throw safety
**Context:** The booking form UX depends on the backend telling the truth about email delivery. If the customer confirmation email fails (or Resend throws), the API could still return a 2xx and the frontend would claim success, while DB status stays `pending`.
**Decision:** In `POST /api/booking`, keep returning `201` when the band notification succeeds, but include `data.confirmation` (`sent` | `pending`) and ensure both “error returned” and “throw” cases for the customer confirmation send result in booking status `pending`.
**Alternatives considered:** Change status codes to non-2xx on confirmation failure (forces client errors, risk of duplicates without idempotency); always return 2xx but hide confirmation outcome (reintroduces silent UX mismatch).
**Why not the others:** Explicitly returning the confirmation outcome keeps the API contract consistent and avoids duplicate inserts/idempotency work while preventing misleading user messaging.
---
## 2026-03-18 — Operator resend: auth-safe frontend relay
**Context:** Admin operators need to re-send customer confirmation, but the Clerk bearer token is server-only. A direct browser call to the backend admin endpoint would either expose credentials or require client-side token plumbing.
**Decision:** Add `web/src/pages/admin/resend-confirmation.ts` as a server-side relay that reads the Clerk token server-side, calls `POST /api/admin/bookings/:id/resend-confirmation`, and then redirects back to `/admin`.
**Alternatives considered:** Call backend admin endpoint directly from browser using a client token; make backend rely on cookies/session instead of bearer tokens.
**Why not the others:** Browser-side bearer token access is unsafe and increases auth complexity; switching to cookie/session auth would change the auth boundary more than needed for this MVP operator workflow.
---
<!-- Add new decisions above this line -->

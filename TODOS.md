# TODOS

Track open work and completed items by version. See CHANGELOG.md for full release notes.

**Roadmap (Hold Scope):** No first-paying-customer goal; no merch yet. **Primary milestone: deploy to VPS** (your domain + HTTPS). Resend, Monitoring, and Content/SEO are done as part of or right after that deploy — one place, one domain. Stripe webhook only when there is a product to sell.

---

## Open

### Code review — Stripe: remove dead code until webhook ships
**What:** If `POST /api/webhooks/stripe` is not imminent: remove `stripe` from root `package.json`, delete or stub `src/lib/stripe.ts`, and fold required helpers back in when **Payments — Implement Stripe webhook handler** is done. If webhook is next: implement minimal route instead of removal.
**Why:** Unused dependency and helpers confuse reviewers and security scanners.
**Context:** Code review 2026-04-10; aligns with existing Payments + Stripe test todos.
**Solution:** 
**Done When:** No orphaned `getStripe` / `verifyWebhookSignature` without a caller, or webhook route exists.
**Effort:** S
**Priority:** P3
**Depends on:** Coordination with **Payments — Implement Stripe webhook handler**

---

### Code review — Resend client test hook (optional)
**What:** Add `setResendForTesting` (or inject `getResend` dependency) mirroring `setClerkClientForTesting` so booking tests avoid brittle `import` mocks.
**Why:** Cleaner integration tests for email paths.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** At least one booking test uses the hook; production path unchanged.
**Effort:** S
**Priority:** P4
**Depends on:** None

---

### Code review — Web package: version, `preview`, health endpoints
**What:** (1) Align `web/package.json` version with release policy (match root semver or document why they differ). (2) Change `web/package.json` `preview` script from `astro dev` to `astro preview` after build. (3) Replace hardcoded `0.4.0` in `web/src/pages/health.ts` and `web/src/pages/api/health.ts` with read from `web/package.json` or `import.meta.env` / build-time inject.
**Why:** Ops and uptime checks show wrong version; `preview` misleads developers.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** Local `bun run build && bun run preview` serves built site; health JSON version matches package.
**Effort:** S
**Priority:** P3
**Depends on:** None

---

### Code review — Remove or document `/api/auth/*` 501 stubs
**What:** Either delete `src/routes/auth.ts` routes (and mount) if Clerk is the only auth surface, updating tests and any clients; or keep routes with a clear README/TODOS note and skip rate limiting until implemented. Prefer removal to reduce attack surface and wasted rate-limit budget.
**Why:** Endpoints return 501 but still consume `rateLimitAuth` quota.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** No unexplained 501 auth routes, or they are explicitly reserved and documented.
**Effort:** S
**Priority:** P3
**Depends on:** None

---

### Code review — CI: run tests on push/PR
**What:** Add `.github/workflows/ci.yml` (or extend repo workflows): install Bun, run `bun test` at repo root; optionally `cd web && bun test` for `*.test.ts` under `web/`.
**Why:** Only **Keep Render Alive** workflow exists today; regressions ship without a gate.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** Failing test fails CI; branch protection can require workflow (optional).
**Effort:** S
**Priority:** P2
**Depends on:** None

---

### Code review — Lint/format baseline
**What:** Add Biome (or ESLint + Prettier) with minimal rules, `bun run lint` / `bun run format` scripts; fix or grandfather existing violations in a single pass to avoid endless churn.
**Why:** No automated style gate today; drift grows with contributors.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** CI or local script runs clean on intended scope; documented in README.
**Effort:** M
**Priority:** P3
**Depends on:** None

---

### Code review — Centralize marketing social URLs
**What:** Move repeated Spotify, Instagram, TikTok, etc. URLs from `MarketingLayout.astro` and `index.astro` into e.g. `web/src/data/socials.ts`; import in both.
**Why:** One edit when a link changes.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** No duplicated long URLs across those files.
**Effort:** S
**Priority:** P4
**Depends on:** None

---

### Code review — Homepage Apple Music icon (nested `<svg>`)
**What:** In `web/src/pages/index.astro`, replace nested `<svg>` inside `<svg>` for Apple Music with a single valid SVG; align `aria-hidden` / `aria-label` with other social cards.
**Why:** Odd DOM; outer `viewBox` ineffective; a11y inconsistent.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** Markup validates; visual unchanged or improved.
**Effort:** S
**Priority:** P4
**Depends on:** None

---

### Code review — DEPLOY note: Render Node image + Bun
**What:** One short paragraph in `DEPLOY.md` (or comment in `render.yaml`): production assumes Bun is available on Render’s Node runtime — re-verify after platform upgrades before deploying.
**Why:** Base image change could break `bun run` startCommand.
**Context:** Code review 2026-04-10.
**Solution:** 
**Done When:** Operators have a checklist line for major Render upgrades.
**Effort:** S
**Priority:** P4
**Depends on:** None

---

### Product roadmap — Lead generation & booking (prioritized slice)
**What:** Execution order for turning the public site into a lead funnel + light CRM: budget capture, marketing blocks, post-submit UX, admin triage, then scoring.
**Why:** Aligns product work with fastest ROI; extends the existing `bookings` table and booking API rather than replacing them with a minimal greenfield schema.
**Context:** Booking already persists `city`, `eventType`, `duration`, `showType`, `attendees`, `venueSound`, etc. (`src/db/schema.ts`, `STATE.md`). Items below are **new** or **expand** admin/marketing.
**Solution:** 
**Done When:**
**Effort:** XL (across multiple tickets below)
**Priority:** P1
**Depends on:** None

---

### Marketing — Video hero + packages + conversion blocks
**What:** On the public marketing site (`web/`, `MarketingLayout`): **video hero** (live performance) — shipped; still to add **packages** section (e.g. Basic / Full / Premium), **repertoire** section, **testimonials** block, **urgency** copy (e.g. limited weekend availability). Match existing marketing CSS and a11y patterns.
**Why:** Increases conversion without new backend surface area.
**Context:** Can ship as one vertical slice or split into sub-tasks; no dependency on budget DB work except for coherent CTA toward `/booking`. Source footage can stay in repo root `herovid/HEROVIDLV.mov`; the site serves **`web/public/video/hero.mov`** (copy or symlink for deploy).
**Solution:** **Video hero (done):** Markup in [`web/src/pages/index.astro`](web/src/pages/index.astro) — `<video class="hero-video">` (`/video/hero.mov`, muted autoplay, `playsinline`, `loop`, `aria-hidden`), `.hero-deco-line` for the gold accent. Styles in [`web/src/styles/marketing-press.css`](web/src/styles/marketing-press.css) — full-bleed video + `blur(2px) brightness(0.7)`, `.hero::after` linear scrim, z-index stack, `prefers-reduced-motion: reduce` hides video + `var(--bg)` fallback. Regression checks in [`web/src/lib/homepageHero.test.ts`](web/src/lib/homepageHero.test.ts). See [CHANGELOG.md](CHANGELOG.md) [Unreleased] for summary.
**Done When:** Packages, repertoire, testimonials, and urgency blocks are on `/` with CTAs to `/booking` or `#booking`; a11y and marketing CSS consistency pass. (Video hero slice already meets its own bar: build + tests green.)
**Effort:** M
**Priority:** P1
**Depends on:** None

---

### Booking UX — Thank-you page + WhatsApp follow-up CTA
**What:** After successful submit, redirect (or in-page flow) to a dedicated thank-you route with embedded/linked performance video and a prominent **WhatsApp** CTA (`PUBLIC_WHATSAPP_URL` or equivalent). Keep confirmation messaging consistent with `data.confirmation` (`sent` | `pending`).
**Why:** Closes the loop on leads immediately; roadmap Phase 2 UX upgrade.
**Context:** May require Astro page + `bookingCanonical`/`publicSiteUrl` patterns; avoid breaking existing booking tests.
**Solution:** 
**Done When:**
**Effort:** S
**Priority:** P2
**Depends on:** None (coordinate copy with Marketing slice if shipped together)

---

### Booking — Lead score + priority field
**What:** Add `priority` (`low` | `medium` | `high`) and/or numeric `score` on `bookings` (or compute priority in API on insert/update). Implement scoring rules in a small module (e.g. budget thresholds, event type, attendees, city vs local) so rules can change without scattered conditionals. Expose in admin + optional API for future automation.
**Why:** Filters noise and ranks follow-up order (roadmap Phase 2).
**Context:** Requires parseable budget and stable enums for event type; document rule versions in `DECISIONS.md` when tuned.
**Solution:** 
**Done When:**
**Effort:** M
**Priority:** P2
**Depends on:** None (prerequisite: budget enum shipped 2026-03-25)

---

### Booking — Workflow statuses (new / contacted / closed)
**What:** Replace or map `status` beyond `pending`/`sent`/`failed` (confirmation) to **sales** states: e.g. `new`, `contacted`, `closed` — clarify separation between “email delivery” and “pipeline” (may be a second column `pipelineStatus` if confirmation status must stay). Admin UI to update state; API patch if missing; tests.
**Why:** Light CRM without external tooling (roadmap Phase 2).
**Context:** Current `bookings.status` is confirmation-oriented; avoid breaking existing flows — see `DECISIONS.md` before migrating semantics.
**Solution:** 
**Done When:**
**Effort:** M
**Priority:** P3
**Depends on:** None (admin budget column + sort shipped 2026-03-25)

---

---

### Email — Follow-up sequence (drip after booking)
**What:** Beyond single confirmation: schedule or trigger Email 2 (e.g. “how we sound” / video) and Email 3 (e.g. urgency). Options: Resend batch + `scheduledAt`, N8N on VPS, or external drip — pick one and document in `DECISIONS.md`. Must be idempotent and mock-friendly in tests; no flaky network in CI.
**Why:** Roadmap Phase 3 nurture; separate from transactional confirmation.
**Context:** Open **Resend — Verify domain** todo still applies for 
deliverability to arbitrary addresses.
**Solution:** 
**Done When:**
**Effort:** L
**Priority:** P3
**Depends on:** Resend — Verify domain so confirmation emails reach any customer; optional: N8N — Run local instance on VPS

---

### API — DRY origins + `/users/me` success envelope (bundle)
**What:** Ship both consistency fixes together: (1) move duplicated `allowedOrigins` into a shared module consumed by `src/index.ts` (CORS) and `src/middleware/auth.ts` (Clerk `authorizedParties`), and (2) change `GET /api/users/me` in `src/routes/users.ts` to use `successResponse(c, user)` instead of hand-rolled `c.json({ data: user })`.
**Why:** Keeps CORS + Clerk origin policy in lockstep and standardizes success responses through one helper path.
**Context:** Both tasks are small P2 API consistency follow-ups from engineering review; bundling avoids two tiny PRs and reduces review overhead.
**Solution:** Implement exactly as defined in this saved plan: [dry_origins_+_me_successresponse_e3c11ce0.plan.md](c:/Users/black/.cursor/plans/dry_origins_+_me_successresponse_e3c11ce0.plan.md).
**Done When:** `allowedOrigins` is shared by both call sites, `/api/users/me` returns through `successResponse`, and `bun test` remains green with no behavior regressions.
**Effort:** S
**Priority:** P2
**Depends on:** None

---

### Tests — Playwright smoke: public booking flow
**What:** Add Playwright under `web/` (or repo root) with a minimal smoke: open booking page, fill required fields, submit, assert expected success or error UI (mock API or point at test/staging per convention).
**Why:** Crosses UI + API boundary; catches form and confirmation-message regressions.
**Context:** No Playwright in `web/package.json` today; workspace standards prefer Playwright for boundary-crossing flows. Keep deterministic: no live Resend/network in CI.
**Solution:** Add `@playwright/test`, one spec (e.g. `web/e2e/booking.spec.ts`), document browser install in README or DEPLOY.md.
**Done When:** One smoke passes locally; CI runs it when feasible; tests do not depend on third-party APIs without mocks.
**Effort:** M
**Priority:** P3
**Depends on:** None (optional: stable staging URL for real API)

---

### Infra — Distributed rate limiting for multiple API instances
**What:** Replace or back in-memory booking/auth rate limit stores with a shared limiter (e.g. Redis, Upstash) or document single-instance requirement in DEPLOY.md.
**Why:** `Map`-based limits in `rateLimit.ts` / `rateLimitAuth.ts` reset per process; multiple workers = weaker protection.
**Context:** Comments already warn about trusted `x-forwarded-for`; scaling horizontally adds a new gap.
**Solution:** Run a single Redis service in Coolify (same host/VPC as your apps). Add REDIS_URL (or host/port/password) to the API app’s env. Refactor booking + auth rate limiting to use a shared Redis-backed fixed window (or sliding window) with distinct key prefixes (e.g. rl:booking:, rl:auth:) so limits are consistent across all API replicas. Use INCR + EXPIRE (or a small Lua script for atomic window reset) keyed by the same client id logic as today (x-forwarded-for / x-real-ip behind a trusted proxy). Keep in-memory limiter as a dev fallback when REDIS_URL is unset so local dev stays simple. Document Coolify Redis wiring, env vars, and “single-instance API + SQLite vs multi-instance + Redis” in DEPLOY.md.
**Done When:** Production/staging API uses Redis when REDIS_URL is set; dev works without it. Booking and auth routes still enforce their intended limits across processes (verified by tests with a mock Redis or testcontainer, not a live network). DEPLOY.md / .env.example describe Coolify Redis and the trust requirement for forwarded IP headers.
**Effort:** M
**Priority:** P2
**Depends on:** Decision to run more than one API instance/process; do when migrating to more robust hosting.

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
**Priority:** P1
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

### Code review — Admin bookings: pagination or caps (2026-04-10)
- **API:** `GET /api/admin/bookings` — query `limit` (default 50, max 200) + `offset` (default 0); `400` on negative offset; `data.total` = full row count; `data.limit`, `data.offset`, `data.hasMore`; same enrichment as before (`src/routes/admin.ts`). `GET /api/admin/export/bookings` — `data.total` = full DB count; `last24hCount` via SQL `count` + `gte(createdAt, …)`; rows capped by `ADMIN_EXPORT_MAX_ROWS` (default 10000, max 50000); when capped: `truncated`, `returnedCount`, `totalInDb`, `warning`.
- **Lib:** `src/lib/adminBookingsQuery.ts` — `parseAdminBookingsListParams`, `getAdminExportMaxRows`; tests `src/lib/adminBookingsQuery.test.ts`.
- **Web:** `web/src/pages/admin.astro` — page size 50, `?page=` SSR pagination + redirect if page out of range.
- **Tests:** `src/routes/admin-bookings-pagination.test.ts` (SQLite :memory:); `src/routes/00-auth-protected.test.ts` mock updated for count + `limit`/`offset` chains.
- **Docs:** `.env.example`, `DEPLOY.md` (Option C); `CHANGELOG.md` [Unreleased]; `DECISIONS.md`.

### Code review — Booking insert: structured error handling (2026-04-10)
- **API:** `src/routes/booking.ts` — `try/catch` around insert + `returning`; throw → `logServerError('booking', 'BOOKING_INSERT_FAILED', err)` + `500` / `BOOKING_PERSIST_FAILED` / Spanish user message; empty `returning` → `INSERT_RETURN_EMPTY` log + same public code.
- **Tests:** `src/routes/booking.test.ts` — empty row + `returning` throw cases.
- **Docs:** `CHANGELOG.md` [Unreleased].

### Code review — Rate limiters: DRY factory + `getClientId` consistency (2026-04-10)
- **Factory:** `src/middleware/rateLimitFactory.ts` — `createRateLimiter` (fixed-window `count` + `resetAt`, 5 min cleanup interval, `destroy()` for tests).
- **Client id:** `src/middleware/getClientId.ts` — documented `unknown` single-bucket behavior for local dev; `rateLimit.ts` re-exports for `booking.ts` imports.
- **Middleware:** `rateLimit.ts` (5/min booking), `rateLimitHealth.ts` (120/min), `rateLimitAuth.ts` (10 / 5 min); unchanged `errorResponse` / `RATE_LIMITED` shape.
- **Tests:** `src/middleware/rateLimitFactory.test.ts`; `src/security.test.ts` rate limit cases pass.
- **Docs:** `DEPLOY.md` local dev note; `CHANGELOG.md` [Unreleased].

### Code review — Admin resend banner: harden `resendDetail` query param (2026-04-10)
- **Lib:** `web/src/lib/sanitizeResendDetail.ts` — `sanitizeResendDetail` + `MAX_RESEND_DETAIL_LEN` (120); strips ASCII controls and `<>\"'\``; read-side only (`/admin` can be hit with arbitrary query strings).
- **Page:** `web/src/pages/admin.astro` — uses sanitizer before building `resendMessage`; banner still plain `{resendMessage}` (Astro escaping unchanged). **No change** to `web/src/pages/admin/resend-confirmation.ts`.
- **Tests:** `web/src/lib/sanitizeResendDetail.test.ts`.
- **Docs:** `CHANGELOG.md` [Unreleased].

### Code review — `check-db` must verify `bookings` table (2026-04-10)
- **Script:** `scripts/check-db.ts` — `REQUIRED_TABLES` `users` + `bookings`; default `DB_PATH` still `join(import.meta.dir, '..', 'data', 'sqlite.db')`; aggregated error lists all missing tables; success log for deploy visibility.
- **Lib:** `src/lib/findMissingSqliteTables.ts` — parameterized `sqlite_master` lookup.
- **Tests:** `src/lib/findMissingSqliteTables.test.ts` (`:memory:` SQLite).
- **Docs:** `DEPLOY.md` — `check-db` fails fast if `users` or `bookings` missing; `CHANGELOG.md` [Unreleased].

### Code review — Single source for budget tiers (API + web) (2026-04-10)
- **Module:** `src/lib/bookingBudget.ts` — `BOOKING_BUDGET_VALUES`, `BUDGET_LABELS`, `BUDGET_HINTS`, `BOOKING_BUDGET_OPTIONS`, `BOOKING_BUDGET_HINTS_WITH_EMPTY`, `BOOKING_BUDGET_SORT_RANK`, `formatBudgetLabel`, `isBookingBudget` (no Zod so `web/` can import).
- **API:** `src/routes/booking.ts` — `z.enum(BOOKING_BUDGET_VALUES)` + shared `BUDGET_LABELS`.
- **Web:** `web/src/pages/booking.astro` — options + `define:vars` hints from module; `web/src/pages/admin.astro` — `formatBudgetLabel` + bundled script imports `BOOKING_BUDGET_SORT_RANK`.
- **Tests:** `src/lib/bookingBudget.test.ts`; `bun test` + `web` build green.

### Code review — Schema & startup correctness (2026-04-10)
- **DB:** `src/db/schema.ts` — `users.updated_at` uses `.$onUpdateFn(() => new Date())` with existing `.$defaultFn`; `bookings.confirmation_attempts` default **0** (was `1` in Drizzle + migration0003).
- **Migration:** `drizzle/0006_booking_confirmation_attempts_default_zero.sql` — rebuild `bookings` so SQLite column default is `0` (copy all rows, drop, rename).
- **Tests:** `src/lib/users.test.ts` — `updatedAt` advances after `update()` when wall clock crosses a new second (SQLite timestamp = epoch seconds).
- **Docs:** `CHANGELOG.md` [Unreleased]. **Still open:** **API — DRY origins + `/users/me` success envelope** (unchanged by this slice).

### Booking — Budget field (optional enum) + admin budget/date sort (2026-03-25)
- **DB:** `drizzle/0005_booking_budget_field.sql`; `bookings.budget` nullable text enum in `src/db/schema.ts` (`menos_15k` … `mas_100k`).
- **API:** `POST /api/booking` requires `budget` (`src/routes/booking.ts`); band email includes readable label via `BUDGET_LABELS`; admin/export JSON includes `budget` automatically.
- **Web:** `web/src/pages/booking.astro` — optional presupuesto `<select>` (MXN ranges); `web/src/pages/admin.astro` — Budget column, `formatBudget`, client-side sort on Budget + Created (`data-budget`, `data-timestamp`).
- **Tests:** `src/routes/booking.test.ts` — missing/invalid budget, payloads updated; `bun test` green.
- **Docs:** `DECISIONS.md` (2026-03-25), `CHANGELOG.md` [Unreleased].

### Quotes — Server-side estimated price range (quote helper) (2026-03-25)
- **API:** `src/routes/admin.ts` enriches `GET /api/admin/bookings` and `GET /api/admin/export/bookings` with `estimatedPriceRange` (computed from `city`/`duration`/`attendees` via `src/lib/estimatedPriceRange.ts`).
- **Web:** `web/src/pages/admin.astro` shows new `Est. Price` column in the bookings table.
- **Tests:** `src/lib/estimatedPriceRange.test.ts` covers missing/unknown inputs, local vs foraneo behavior, and formatting/invariants.
- **Docs:** `DECISIONS.md` + `CHANGELOG.md` [Unreleased].

### Content / SEO — Homepage + press kit (merged 2026-03-24; replaces standalone `/press-kit` 2026-03-23)
- **Route:** `GET /` — `web/src/pages/index.astro` (public; no auth); press assets section `id="press"` for `/#press` deep links.
- **Legacy:** `GET /press-kit` → 301 to `/` via `web/vercel.json` (removed `web/src/pages/press-kit.astro`).
- **Layout:** `web/src/layouts/MarketingLayout.astro` + `web/src/styles/marketing-press.css` — full-bleed dark theme; Clerk nav/auth preserved.
- **URLs:** `homeCanonical()` in `web/src/lib/publicSiteUrl.ts` for homepage canonical; `pressKitCanonical()` retained for tests. Tests in `web/src/lib/publicSiteUrl.test.ts`.
- **Env (documented in `web/.env.example`):** optional `PUBLIC_WHATSAPP_URL`, `PUBLIC_PRESS_PHOTOS_URL`, `PUBLIC_PRESS_LOGO_URL`, `PUBLIC_PRESS_BIO_URL`.
- **Nav:** `Layout.astro` / `MarketingLayout.astro` “Press kit” → `/#press`.

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

# Project State

## Current Position
- Phase: **Booking + optional budget qualification shipped in tree** — marketing `/booking` (`MarketingLayout`, expanded fields + optional **presupuesto** dropdown); API persists `budget` enum when provided + prior detail fields; migrations through `drizzle/0005_booking_budget_field.sql`; `bookingCanonical()` in `web/src/lib/publicSiteUrl.ts`; Render runs `bun run migrate` at startup (see `render.yaml` / `DEPLOY.md`).
- **Eng lead / backlog:** API hygiene follow-ups were bundled into one P2 todo (`DRY origins + /users/me success envelope`) with a saved execution plan link in `TODOS.md`; other ship priorities unchanged (VPS, Resend domain, Content/SEO when ready).
- Branch: **`feat/budget-fixes-admin-range-deployment-cors-admin-api`** — currently clean except docs todo update; run `git status` before committing.
- Last completed (this workstream): **Optional budget UX + API** — `src/routes/booking.ts` (optional `budget` + email line when set), `web/src/pages/booking.astro` (placement, helper, contextual hints), `booking.test.ts`, docs updated.
- Last completed (this workstream): **Admin estimated price range helper + UI** — `src/lib/estimatedPriceRange.ts` (+ tests), enriched `src/routes/admin.ts` (`GET /api/admin/bookings` + `GET /api/admin/export/bookings`), and added `Est. Price` column in `web/src/pages/admin.astro` (computed at read-time). `bun test` green.
- Last completed (this session): **Verification + planning bundle** — confirmed git history/reflog is healthy, reran targeted admin/estimator tests (green), and consolidated two P2 API cleanup todos into one bundled item with a saved plan reference.
- Next up: **Pick next execution slice** — either ship PR/deploy verification for current branch work, or execute the bundled P2 API consistency plan in a fresh feature commit.

## Accumulated Decisions
- 2026-03-25: **Budget as optional MXN range enum** — five values on `bookings.budget`; optional on `POST /api/booking`; label map for email + admin UI; see `DECISIONS.md`.
- 2026-03-25: **Admin estimated price range: computed at read-time** — implemented as a pure helper (`src/lib/estimatedPriceRange.ts`) and computed inside admin list/export routes (`src/routes/admin.ts`). Module-level constants for deterministic behavior and testability; public booking POST contract unchanged (see `DECISIONS.md` same date).
- 2026-03-24: **Booking detail fields** — persist six nullable columns on `bookings` + optional API fields + band email lines; idempotent `migrate` script applies SQL in `drizzle/` (see `DECISIONS.md` same date).
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup (`bun run migrate && bun run check-db && bun run start`).
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.
- 2026-03-22: Post-review hardening — `safeLog` (no stacks in prod), `Forwarded` + `X-Forwarded-Proto` for HTTPS, `/health` rate limit, admin export only via `ALLOW_*` or `NODE_ENV=development` (see `DECISIONS.md`).
- 2026-03-22: Booking `REQUEST_RECEIVED` — JSON info line via `logServerInfo` (stdout); band-email failure uses `markBandEmailFailed`; empty `.returning()` → 500 `INTERNAL_ERROR`.
- 2026-03-22: Eng lead review — document follow-ups in `TODOS.md` (DRY origins, `/me` `successResponse`, Playwright smoke); do not reorder launch priorities.
- 2026-03-23: Press kit merged into homepage — single-scroll `/`; `pressKitCanonical` retained for tests; nav `/#press` (`DECISIONS.md`).

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance); see **TODOS — Infra — Distributed rate limiting**.
- **Drizzle journal** (`drizzle/meta/_journal.json`) may be out of sync with historical SQL files; **source of truth for deploy** is `scripts/run-migration.ts` applying all `drizzle/*.sql` in sorted order. If you regenerate migrations, verify output before committing.

## Session Notes
Last session: **Review + QA + backlog cleanup** (git sanity check, targeted tests, todo bundling).
Stopped at: Bundled P2 API cleanup task created in `TODOS.md` with plan link `c:/Users/black/.cursor/plans/dry_origins_+_me_successresponse_e3c11ce0.plan.md`; no implementation started.
Resume with: **Choose path** — (A) continue PR/deploy verification for current branch changes, or (B) switch to a fresh branch and execute the bundled API plan (`allowedOrigins` shared module + `/users/me` `successResponse`) with full `bun test`.

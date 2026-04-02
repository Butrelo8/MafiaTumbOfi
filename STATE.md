# Project State

## Current Position
- Phase: **Marketing homepage hero video shipped** (slice of P1 “Marketing — Video hero + packages + conversion blocks” in `TODOS.md`); **booking + budget** work remains in tree as before (`/booking`, admin, migrations through `drizzle/0005_*`).
- **Eng lead / backlog:** P2 bundled API cleanup (`DRY origins + /users/me success envelope`) still in `TODOS.md` with plan link; VPS / Resend / Content unchanged as roadmap.
- Branch: run `git status` before committing (prior note named `feat/budget-fixes-admin-range-deployment-cors-admin-api`; confirm current branch locally).
- Last completed: **Hero video + scrim + cinematic blur** — `web/src/pages/index.astro` (`<video class="hero-video">` → `/video/hero.mov`, `.hero-deco-line`), `web/src/styles/marketing-press.css` (z-index stack, linear scrim on `.hero::after`, `prefers-reduced-motion` fallback), asset at `web/public/video/hero.mov` (copy from `herovid/HEROVIDLV.mov`), smoke tests `web/src/lib/homepageHero.test.ts`; `CHANGELOG.md` [Unreleased] + `TODOS.md` marketing item updated with file pointers.
- Next up: **Remaining marketing slice** — packages, repertoire, testimonials, urgency on `/` with CTAs to `/booking` / `#booking`; optional: add H.264 `hero.mp4` `<source>` for non-Safari browsers. **Or** resume API bundle / deploy verification per prior priorities.

## Accumulated Decisions
- 2026-04-01: **Marketing hero video layering** — Full-bleed `<video>` under radial `.hero::before`, dark linear scrim on `.hero::after` (replaced prior gold-line pseudo; gold accent moved to `.hero-deco-line` in markup). Video gets `filter: blur(2px) brightness(0.7)` only on `.hero-video`. `prefers-reduced-motion: reduce` hides video and sets `.hero` to `var(--bg)`. Public URL `/video/hero.mov` from `web/public/video/`; source master can live in `herovid/`. Rationale: readable text, policy-safe muted autoplay, deterministic z-index, tests co-located in `src/lib` (not `pages/`) so Astro build does not bundle `bun:test`.
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
Last session: **Hero video implementation** (plan: gradient scrim + blur, deco line migration), **TODOS.md** marketing entry refreshed with file paths, **save state**.
Stopped at: Marketing P1 todo still open for packages / repertoire / testimonials / urgency; hero video sub-slice done (`bun test` + `astro build` were green when last run).
Resume with: **Pick slice** — (1) Build remaining marketing blocks on `web/src/pages/index.astro` + `marketing-press.css`, or (2) execute bundled P2 API plan from `TODOS.md`, or (3) deploy/PR verification — run `git status` and `bun test` (root + `web/`) first.

# Project State

## Current Position
- Phase: **Marketing site** — hero video + **header / logo redesign** shipped (`MarketingLayout.astro`, `index.astro`, `marketing-press.css`); **booking + budget** unchanged in tree. **Vercel:** production aligned with **`main`** — user confirmed all good.
- **Eng lead / backlog:** P2 bundled API cleanup still in `TODOS.md`; VPS / Resend / Content unchanged as roadmap.
- Branch: run `git status` before committing (merge/header work may be on a feature branch until merged to `main`).
- Last completed: **Vercel** — dashboard + Git production branch fixed (`main`). **Header redesign** — see **Accumulated Decisions** (logo image in header + hero `h1`, overlay menu, gold `#B8973A`, Cormorant Garamond typographic treatment where applicable, social icons + hamburger, no visible Sign in/up in bar). **Prior:** hero video + scrim + tests.
- Next up: Remaining marketing slice (packages, repertoire, testimonials, urgency on `/`); **or** P2 API bundle / deploy verification — `bun test` + `git status` first.

## Accumulated Decisions
- 2026-04-01: **Vercel production branch** — Deploys now track **`main`**; prior URL/duplicate-project confusion resolved in dashboard (user confirmed).
- 2026-04-01: **Marketing header redesign + logo assets (file-level)** — `MarketingLayout.astro`: header logo is `<img src="/icon/mafiatumbada.png">` inside the home link with `aria-label` for a11y. `index.astro`: hero `<h1>` wraps the same image (not text); `h1` kept for SEO, `alt` carries the name. `marketing-press.css`: `.header-logo-img` — 36px tall mobile, 42px at ≥640px, max-width 180px; `.hero-logo-img` — fluid `min(480px, 80vw)` (≈80% viewport on phones, caps 480px desktop); `.hero-title` — spacing wrapper only (old font sizing removed).
- 2026-04-01: **Marketing header UX / layout (`MarketingLayout` + `marketing-press.css`)** — **Layout:** “Mafia Tumbada” typographic logo left (Cormorant Garamond serif, gold `#B8973A`); social icons right (Instagram, TikTok, Facebook, X) in gold; hamburger far right; **no** visible Sign in / Sign up in bar — auth lives in fullscreen overlay menu. **Overlay:** opens on hamburger; links Inicio, Redes, Música, Integrantes, Press kit, Contrataciones; Admin when signed in; closes on X, link click, or Escape. **Styling:** header bar semi-transparent black + `backdrop-blur` (reads over hero video, solid when scrolling); `position: fixed` top; gold `#B8973A` for logo, icons, hamburger, close; hovers — icons scale, close rotates 90°, nav links go gold; smooth fade on overlay.
- 2026-04-01: **Vercel URLs and custom domains** — Two different `*.vercel.app` hosts almost always means **two Vercel projects** (or CLI linked to one while Git deploys the other). **Production Branch** must match the branch you actually push (dead branch → fix in Project → Settings → Git). **Root Directory** for this repo should be `web/` for the Astro app. Multiple custom domains on **one** project are aliases to the same production deployment; a domain can only attach to one project at a time. Deleting a **duplicate** project is reasonable **after** moving domains and Git to the canonical project and copying env vars — do not delete the project that holds the live primary domain and secrets until migrated.
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
Last session: **STATE refresh** — Vercel confirmed fixed on **`main`**; documented **header / logo redesign** (three files + layout/styling spec) in Accumulated Decisions.
Stopped at: Marketing P1 still open for packages / repertoire / testimonials / urgency; Vercel blocker cleared.
Resume with: **Marketing slice** on `web/src/pages/index.astro` + `marketing-press.css`, **or** P2 API bundle from `TODOS.md` — run `git status` + `bun test` (root + `web/`) first.

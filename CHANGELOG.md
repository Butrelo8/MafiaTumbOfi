# CHANGELOG

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **Homepage + booking copy (SEO):** **`web/src/pages/index.astro`** — **`hero-blurb`** (2–3 sentences above CTAs), **`trust-strip`** (sr-only **`h2`** + **`.trust-grid`** / **`.trust-item`** + SVG icons) after stats bar, scoped CSS (`.hero-blurb`, `.sr-only`, trust grid). **`web/src/pages/booking.astro`** — **`booking-intro`**, form **`h2.form-section-heading`** (“Datos de contacto” / “Detalles del evento”), **`faq-section`** with five **`<details>`** Q&amp;As + styles. Tests: **`homepageHero.test.ts`**, **`bookingPageCopy.test.ts`**.
- **Booking email drip (nurture):** After confirmation **`status === 'sent'`**, scheduled **Email 2** (+24h default) and **Email 3** (+72h default) via Resend. Columns **`drip2_due_at`**, **`drip2_sent_at`**, **`drip3_due_at`**, **`drip3_sent_at`** on **`bookings`**; migration **`drizzle/0009_booking_drip.sql`**. **`POST /api/booking`** sets due dates from **`computeDripDueDatesFromCreatedAt`** (**`src/lib/dripSchedule.ts`**). **`processDripEmails`** (**`src/lib/dripProcessor.ts`**) + **`buildDripEmail2` / `buildDripEmail3`** (**`src/lib/dripEmails.ts`** — video **`https://www.youtube.com/watch?v=7Sx0yDjGoq0`**). **`POST /api/internal/process-drip`** (**`src/routes/internal.ts`**, Bearer **`DRIP_CRON_SECRET`**). Render Blueprint: **`mto-drip-cron`** curls **`DRIP_PROCESS_URL`** every 15 min. Tests: **`dripSchedule.test.ts`**, **`dripEmails.test.ts`**, **`dripProcessor.test.ts`**, **`internal.test.ts`**. **`DECISIONS.md`** — why HTTP cron vs SQLite on disk.
- **Booking thank-you (`/booking/gracias`):** On **`POST /api/booking`** success, **`web/src/pages/booking.astro`** stores normalized **`confirmation`** in **`sessionStorage`** (**`mto_booking_thanks`**) via **`web/src/lib/bookingThanksSession.ts`**, then redirects to **`/booking/gracias`**. **`web/src/pages/booking/gracias.astro`** — **`MarketingLayout`** + **`bookingThanksCanonical()`** (**`publicSiteUrl.ts`**), **`robots="noindex,nofollow"`** (optional **`Seo`** **`robots`** on layout), same three success copy branches as before, hero **`/video/hero.mp4`** + link, WhatsApp **`btn-primary`** when **`PUBLIC_WHATSAPP_URL`** else fallback copy; missing/invalid session → **`/booking`**. Session key **removed after successful read** (refresh / direct hit → form). Form script uses **`data-api-url`** / **`data-budget-hints`** (no **`define:vars`**) so client imports work. Tests: **`bookingThanksSession.test.ts`**, **`publicSiteUrl.test.ts`** (`bookingThanksCanonical`); **`web/e2e/booking.e2e.ts`** — gracias URL + **`sent`/`pending`** copy, redirect without session.
- **Marketing homepage — conversion blocks:** **`web/src/pages/index.astro`** — sections **Repertorio** (`#repertorio`), **Testimonios** (`#testimonios`, placeholder quotes), **Paquetes** (`#paquetes`, three tiers + featured **Completo**), urgency line (`.booking-urgency`) in **`#booking`**. Data: **`web/src/data/repertoire.ts`**, **`testimonials.ts`**, **`packages.ts`**. Styles in **`web/src/styles/marketing-press.css`**. **`MarketingLayout.astro`** mobile nav — **Paquetes** → `/#paquetes`. Tests: **`web/src/lib/homepageHero.test.ts`** (`marketing homepage conversion blocks`).
- **SEO / Open Graph:** **`web/src/components/Seo.astro`** — shared **`<title>`**, description, **canonical**, **OG** (`og:image` absolute via **`absoluteAssetUrl`**, `og:locale` **`es_MX`**, `og:site_name`), **Twitter Card** (`summary_large_image` + image alt), **`theme-color`**. Optional **`PUBLIC_ALLOW_INDEXING=false`** → **`noindex,nofollow`**. **`MarketingLayout.astro`** and **`Layout.astro`** use **`Seo`**; **`admin.astro`** uses **`MarketingLayout`** + **`adminCanonical()`** and explicit **`robots="noindex,nofollow"`**. **`web/src/lib/publicSiteUrl.ts`** — **`adminCanonical`**, **`absoluteAssetUrl`**; tests in **`publicSiteUrl.test.ts`**. **`web/.env.example`** — **`PUBLIC_ALLOW_INDEXING`** comment.
- **Playwright (booking smoke):** **`@playwright/test`** in **`web/`**; **`web/playwright.config.ts`** starts **`astro dev`** on **127.0.0.1:4329** (avoids port 4321); **`web/e2e/booking.e2e.ts`** mocks **`POST …/api/booking`** — success navigates to **`/booking/gracias`** + copy; error path asserts **`#form-status`**; bare **`/booking/gracias`** redirects to **`/booking`**. Root **`bun run test:e2e`**; **`bunx playwright install chromium`** once per machine. **`README.md`** + **`DEPLOY.md`**; **`.gitignore`** Playwright output dirs under **`web/`**. Specs named **`*.e2e.ts`** so **`bun test`** does not execute them as Bun specs.
- **Booking pipeline (CRM):** **`bookings.pipeline_status`** (`new` \| `contacted` \| `closed`), default **`new`** on **`POST /api/booking`**; admin **`PATCH /api/admin/bookings/:id`** with **`{ pipelineStatus }`** (Zod + Spanish errors). Migration **`drizzle/0008_booking_pipeline_status.sql`**; **`src/lib/bookingPipeline.ts`** + tests. Admin table: **Seguimiento** column + **`/admin/update-pipeline`** relay; legend splits **Correo** vs **Seguimiento**. Tests: **`src/routes/admin-bookings-pipeline.test.ts`** (real SQLite; insert id from **`.returning()`** — SQLite AUTOINCREMENT does not reset after DELETE). **`DECISIONS.md`** — two-axis model.
- **Booking lead score + priority:** Nullable **`bookings.lead_score`** / **`bookings.lead_priority`**; computed once on **`POST /api/booking`** via **`src/lib/bookingLeadScore.ts`** (budget, attendees, duration, city/foraneo, extras). Migration **`drizzle/0007_booking_lead_score.sql`**. Admin table shows **Prioridad** + sortable **Lead score** (`web/src/pages/admin.astro`). Tests: **`src/lib/bookingLeadScore.test.ts`**. **`DECISIONS.md`** — frozen-at-insert policy.
- **Marketing sitemap:** `web/src/pages/sitemap.xml.ts` — dynamic **`GET /sitemap.xml`** with homepage + **`/booking`** only (excludes `/admin`); uses **`PUBLIC_SITE_URL`** via **`resolvePublicBaseUrl`** (same as canonicals). **`web/src/lib/publicSitemap.ts`** + **`publicSitemap.test.ts`**.
- **Deploy docs:** `DEPLOY.md` §1 — **“Bun on Render (Node runtime)”** — documents reliance on Bun in Render’s Node image, operator checklist after Node/env/platform upgrades, and fallbacks if Bun is removed. **`render.yaml`** comments link to that section.

### Changed
- **Marketing homepage — trust strip:** **`web/src/pages/index.astro`** — cuatro columnas iguales (**`grid-template-columns: repeat(4, 1fr)`**), 2×2 en **≤640px**, fondo y bordes alineados con **`.stats-bar`** (**`--surface`**, **`--border`**); iconos **SVG** (micrófono, bocina, rayo, mapa) sustituyen emoji. **`homepageHero.test.ts`** — aserciones **`trust-grid`** / **`trust-item`**.

### Fixed
- **Clerk sign-in/up from mobile menu:** **`MarketingLayout.astro`** — after a click on **`.menu-auth`** (Sign in / Crear cuenta / `UserButton`), **`closeMenu()`** runs on the next tick so the fullscreen **`.mobile-menu`** overlay (z-index **200**) does not sit above Clerk’s modal. **`marketing-press.css`** — **`pointer-events: none`** on **`.hero-video`** so the background video never captures clicks meant for hero content or overlays.
- **Admin bootstrap:** Removed “first SQLite user is admin” insert logic. **`ADMIN_CLERK_ID`** (API env, trimmed) is the only Clerk id that gets **`is_admin`** on create; when set, **`getOrCreateUser`** reconciles **`is_admin`** on read so prod can correct rows without Shell. Migration **`drizzle/0010_admin_explicit_clerk_ids.sql`** aligns known **`users.clerk_id`** rows. **`src/lib/adminClerkConfig.ts`** + tests; **`render.yaml`** documents **`ADMIN_CLERK_ID`**.
- **Admin redirect loop (`/admin`):** API **`authenticateRequest`** used raw **`allowedOrigins`** for Clerk **`authorizedParties`** while CORS already expanded **www ↔ apex**. Sessions minted for **`https://www.…`** failed on the API when Render had only the apex **`PRODUCTION_URL`**, so **`GET /api/admin/bookings`** returned **401** and Astro kept calling **`redirectToSignIn`**. **`clerkAuthorizedParties`** now uses **`expandCorsAllowedOrigins`**, and **`PUBLIC_SITE_URL`** is merged into the raw list when set on the API.
- **`web/src/pages/admin/update-pipeline.ts`:** import path to **`bookingPipeline`** — one **`../`** short (`../../../…` → **`../../../../src/lib/…`**) so **`astro build`** could resolve from **`web/src/pages/admin/`**.
- **Resend / booking confirmation:** Production uses a **verified domain** and **`RESEND_FROM_EMAIL`** (`noreply@mafiatumbada.com` on Render) so the customer “Recibimos tu solicitud” email can reach **any recipient address**, not only the Resend account owner. **`BUGS.md`** entry updated (dev without domain still limited).

### Removed
- **GitHub Actions:** Deleted `.github/workflows/keep-alive.yml` (scheduled Render HTTP ping). No replacement CI workflow — tests are run locally (`bun test`) before ship.
- **`/api/auth/*` stubs:** Deleted `src/routes/auth.ts` (`POST /api/auth/login` and `POST /api/auth/logout` returned 501) and `src/middleware/rateLimitAuth.ts`; dropped mount from `src/routes/index.ts`. Clerk remains the auth surface (`src/middleware/auth.ts`, `/api/users`, `/api/admin`). **Rate-limit coverage:** `POST /api/booking` 5/min per client id asserted in **`src/routes/booking.test.ts`** (mocked `db` + Resend — no real inserts or API calls).
- **Stripe (unused):** Dropped `stripe` from root `package.json` and removed `src/lib/stripe.ts` until `POST /api/webhooks/stripe` or checkout is implemented; `.cursor/rules/hono-template.mdc` and `TODOS.md` (**Payments** / Stripe test todo) describe re-adding the SDK and verification pattern.

### Added
- **Lint / format (Biome):** Root **`@biomejs/biome`** + **`biome.json`** — scope `src/**/*.ts`, `scripts/**/*.ts`, `web/src/**/*.ts` (`.astro` out of scope). Scripts **`bun run lint`**, **`bun run format`**, **`bun run lint:fix`**. Baseline: formatter + recommended lint with small overrides; **`node:`** import protocol via unsafe fixes. **`README.md`** — “Lint and format” section.
- **Resend test hook:** `setResendForTesting` in `src/lib/resend.ts` (mirrors Clerk override pattern); `src/lib/resend.test.ts`. Booking and admin resend tests use the hook instead of `mock.module('../lib/resend')`.

### Changed
- **Admin (`/admin`):** Switched from light **`Layout.astro`** to **`MarketingLayout.astro`** — same header/nav/fonts/dark tokens as the marketing site; **`robots="noindex,nofollow"`**; **`footer-bar`** like booking; table, banners, legend, pagination, and status pills use **`marketing-press.css`** variables (**`--bg`**, **`--surface`**, **`--gold`**, **`--muted`**, **`--border`**). Export link uses **`btn-secondary`**. Tests: **`web/src/lib/adminPageTheme.test.ts`** (markup regression).
- **Booking thank-you (`/booking/gracias`):** Replaced local **`hero.mp4`** `<video>` with lazy-loaded **YouTube** embed **`HTA31yUX41A`** (~600px max width, 16:9, same border treatment). **`prefers-reduced-motion: reduce`** hides the iframe and shows **“Ver presentación en YouTube”** (watch URL). Constants + unit tests: **`web/src/lib/bookingThanksPresentation.ts`**, **`bookingThanksPresentation.test.ts`**. Playwright **`web/e2e/booking.e2e.ts`** asserts embed **`src`**. **`web/public/video/hero.mp4`** unchanged — still used on the marketing homepage.
- **Marketing homepage — Repertorio:** **`web/src/pages/index.astro`** — single **`repertoire-cta`** (removed broken nested wrappers); streaming row **`repertoire-stream`** with compact **`.repertoire-stream-link`** buttons (Apple Music / Spotify / YouTube icons + labels). **`marketing-press.css`** — cards use centered flex wrap (balances the 5-card last row), light surface gradient + radius, gold titles; CTA column centered with full-width capped booking button.
- **API:** Shared **`src/lib/allowedOrigins.ts`** — single raw origin list for CORS (`expandCorsAllowedOrigins` in **`src/index.ts`**); Clerk **`authorizedParties`** uses **`clerkAuthorizedParties`** (same expansion + optional **`PUBLIC_SITE_URL`**). **`GET /api/users/me`** uses **`successResponse`** from **`src/lib/errors.ts`** instead of ad-hoc **`c.json({ data })`**.
- **Homepage (`web/src/pages/index.astro`):** Apple Music social card — removed **nested `<svg>`** (invalid HTML); single icon `<svg>` + `<path>` like other cards; **`homepageHero.test.ts`** asserts one `<svg` in that block.
- **Marketing social URLs:** Single source **`web/src/data/socials.ts`** (`bandSocialUrls`); **`MarketingLayout.astro`** and **`index.astro`** import it instead of duplicating Spotify / TikTok / YouTube / Instagram / Facebook / Apple Music links.
- **Biome / git:** **`.code-review-graph/`** in root **`.gitignore`**; **`biome.json`** VCS integration **`useIgnoreFile`** enabled again (Biome no longer reads the ignored tool tree).

### Fixed
- **API `GET /health`:** `version` now comes from **`getAppVersion()`** on each request (honors `APP_VERSION` / `RELEASE_VERSION` at runtime). It previously used a value captured once at module load, so overrides did not apply and **`src/health.test.ts`** could fail.

### Changed
- **Web package:** `web/package.json` — `version` `0.5.0` (aligned with root); `preview` script runs `astro preview` after build. **`web/src/lib/webAppVersion.ts`** — `getWebAppVersion()` from `web/package.json` with `APP_VERSION` / `RELEASE_VERSION` overrides (same semantics as API). **`web/src/pages/health.ts`** and **`web/src/pages/api/health.ts`** use it instead of hardcoded `0.4.0`. Tests: **`web/src/lib/webAppVersion.test.ts`**. **`README.md`** — versioning note; **`web/.env.example`** — optional override comments.
- **Marketing homepage (`web/src/pages/index.astro`):** Signed-in admin strip (`.admin-notice`) — dark translucent bar, subtle border, small muted label text; link uses gold + hover for affordance instead of full-width brand fill. **`web/src/lib/homepageHero.test.ts`:** expectations match current hero asset (`/video/hero.mp4`) and `marketing-press.css` scrim/video filter; new test for admin strip styling.
- **README:** New “Email (Resend)” section — `BOOKING_NOTIFICATION_EMAIL` vs `RESEND_FROM_EMAIL`, customer confirmation, Render vs Resend UI, link to `DEPLOY.md`.

### Added
- **Admin bookings — pagination + export cap:** `GET /api/admin/bookings` accepts **`limit`** (default 50, max 200) and **`offset`**; returns **`data.total`** (full count), **`data.hasMore`**, plus existing **`bookings`**. `GET /api/admin/export/bookings` uses SQL counts for **`total`** and **`last24hCount`**, caps **`bookings`** per **`ADMIN_EXPORT_MAX_ROWS`** (default 10000, ceiling 50000; see `.env.example`), and when capped adds **`truncated`**, **`returnedCount`**, **`totalInDb`**, **`warning`**. **`web/src/pages/admin.astro`** uses **`?page=`** (50 rows per page) with prev/next. Helpers + tests: `src/lib/adminBookingsQuery.ts`, `src/routes/admin-bookings-pagination.test.ts`.

### Changed
- **Booking API:** `POST /api/booking` — `db.insert(bookings)` wrapped in `try/catch`; DB throw logs `BOOKING_INSERT_FAILED`, returns `500` + `BOOKING_PERSIST_FAILED` (same user message as empty `returning`). Empty `returning` still logs `INSERT_RETURN_EMPTY`, now uses `BOOKING_PERSIST_FAILED` for consistent client shape. Tests: `src/routes/booking.test.ts`.
- **Rate limiting:** Shared `createRateLimiter` fixed-window store (`src/middleware/rateLimitFactory.ts`) + single `getClientId` (`src/middleware/getClientId.ts`); `rateLimit.ts`, `rateLimitHealth.ts`, and `rateLimitAuth.ts` delegate to them (same limits: booking 5/min, health 120/min, auth 10/5min). `getClientId` still re-exported from `rateLimit.ts` for existing imports. Tests: `src/middleware/rateLimitFactory.test.ts`. **Docs:** `DEPLOY.md` — local dev `unknown` shared bucket.
- **Admin (`web/src/pages/admin.astro`):** `resendDetail` query param is sanitized (`web/src/lib/sanitizeResendDetail.ts`) — max length 120, ASCII control and HTML-string-risk characters stripped; empty-after-clean falls back to generic resend error copy. Tests: `web/src/lib/sanitizeResendDetail.test.ts`.
- **check-db:** `scripts/check-db.ts` requires both `users` and `bookings` (parameterized `sqlite_master` checks via `findMissingSqliteTables` in `src/lib/findMissingSqliteTables.ts`); logs `[check-db] OK` on success. Tests: `src/lib/findMissingSqliteTables.test.ts`.
- **Booking budget:** Tier values, display labels, booking-page hints, admin sort ranks, and empty-option copy live in `src/lib/bookingBudget.ts` (no Zod dependency). Consumed by `src/routes/booking.ts` (`z.enum(BOOKING_BUDGET_VALUES)`), `web/src/pages/booking.astro`, and `web/src/pages/admin.astro`. Tests: `src/lib/bookingBudget.test.ts`.
- **DB / schema:** `users.updated_at` now uses Drizzle `.$onUpdateFn(() => new Date())` alongside `.$defaultFn` so ORM `update()` refreshes the column when it is omitted from `.set()` (SQLite `timestamp` mode stores **second** precision).
- **DB / schema:** `bookings.confirmation_attempts` default is **0** in `src/db/schema.ts`, aligned with `POST /api/booking`. Existing SQLite files pick up the new table default via migration `drizzle/0006_booking_confirmation_attempts_default_zero.sql` (rebuild `bookings`, copy rows, rename).

### Added
- **Tests:** `src/lib/users.test.ts` — regression that `updatedAt` increases after `update()` when the clock advances past the previous second (required because SQLite stores epoch seconds for `mode: 'timestamp'`).
- Marketing homepage hero (`web/src/pages/index.astro`): full-bleed background video from `web/public/video/hero.mov` with blur/brightness filter, linear gradient scrim (`.hero::after`), gold accent line moved to `.hero-deco-line`; `prefers-reduced-motion: reduce` hides video and uses solid `--bg` fallback (`web/src/styles/marketing-press.css`). Smoke test `web/src/lib/homepageHero.test.ts`.
- Booking: **presupuesto** (optional) on `/booking` (`web/src/pages/booking.astro`) — MXN range dropdown + helper/context hints; `budget` text enum on `bookings`; validated in `POST /api/booking` (`src/routes/booking.ts`); band email includes budget line when provided; migration `drizzle/0005_booking_budget_field.sql`.
- Admin (`web/src/pages/admin.astro`): Budget column with readable labels; sortable Budget and Created columns (client-side).
- Admin (`web/src/pages/admin.astro`): Added `Est. Price` column; API computes `estimatedPriceRange` at read-time from `city`/`duration`/`attendees` (`src/lib/estimatedPriceRange.ts` + `src/routes/admin.ts`).

### Changed
- Marketing header redesign (`web/src/layouts/MarketingLayout.astro`, `web/src/styles/marketing-press.css`): header logo is `<img src="/icon/mafiatumbada.png">` inside the home link with `aria-label`; typographic “Mafia Tumbada” treatment (Cormorant Garamond, gold `#B8973A`); social icons (Instagram, TikTok, Facebook, X) and hamburger in gold; no visible Sign in/Sign up in the bar — auth and nav live in a fullscreen overlay (Inicio, Redes, Música, Integrantes, Press kit, Contrataciones; Admin when signed in); overlay closes on X, link click, or Escape. Fixed header bar uses semi-transparent black with backdrop blur; hover states (icon scale, close rotation, link gold) and smooth overlay fade.
- Marketing homepage hero (`web/src/pages/index.astro`, `web/src/styles/marketing-press.css`): hero `<h1>` wraps the same logo image (SEO + `alt` for the name). CSS: `.header-logo-img` — 36px tall mobile, 42px at ≥640px, max-width 180px; `.hero-logo-img` — `min(480px, 80vw)`; `.hero-title` — spacing wrapper only (prior standalone title font sizing removed).

### Fixed
- **Booking / admin API calls:** `PUBLIC_API_URL` with a **trailing slash** produced URLs like `https://api…com//api/booking` (404). `normalizePublicApiBaseUrl()` in `web/src/lib/publicApiUrl.ts` strips trailing slashes; used from `booking.astro`, `admin.astro`, `admin/export-bookings.astro`, `admin/resend-confirmation.ts`. Tests: `web/src/lib/publicApiUrl.test.ts`.
- **CORS (booking form):** `PRODUCTION_URL` is normalized (trailing slash) and expanded with the paired **www ↔ apex** origin so browsers on `https://www.example.com` still match when env only lists `https://example.com` (avoids `fetch` failing with a generic “connection” error). Helpers: `src/lib/corsOrigins.ts`, tests `src/lib/corsOrigins.test.ts`.
- Vercel: Git **production branch** set to **`main`** so production deploys and custom domains track the intended default branch (resolves wrong-URL / stale-branch confusion when production pointed at a deleted or unused branch).
- Root `package.json`: `db:migrate` now runs `migrate` / `scripts/run-migration.ts` so it applies SQL migrations to SQLite (same as Render). It previously ran `drizzle-kit up:sqlite`, which only upgrades Drizzle kit journal metadata — developers following README saw success but got no tables. Rare kit upgrades use `db:upgrade-kit-snapshots`.
- Booking page (`web/src/pages/booking.astro`): form labels and radio labels use marketing theme `--text` instead of a light-theme fallback (`#1c1917`), so copy stays readable on the dark `MarketingLayout` background; input borders use `--border`.

### Added
- Booking: expanded public form at `/booking` (`web/src/pages/booking.astro`) with `MarketingLayout`, city/event type/duration/show type/attendees/venue sound fields; `bookingCanonical()` in `web/src/lib/publicSiteUrl.ts` for canonical URL.
- API + DB: optional booking payload fields `city`, `eventType`, `duration`, `showType`, `attendees`, `venueSound` validated in `src/routes/booking.ts`, persisted on `bookings`, included in band notification email; migration `drizzle/0004_booking_detail_fields.sql`.
- Web: combined homepage and press kit into single-scroll page at `/` (`web/src/pages/index.astro`) using `MarketingLayout.astro` and `web/src/styles/marketing-press.css`; includes hero, stats, bio, social links, discography, members, shows, press assets, and booking CTA with anchor navigation. Old `/press-kit` route redirects to `/` via `web/vercel.json`. `homeCanonical` helper in `web/src/lib/publicSiteUrl.ts` for base-domain canonical URL; `pressKitCanonical` retained for tests/back-compat. Optional env vars in `web/.env.example` (`PUBLIC_SITE_URL`, `PUBLIC_WHATSAPP_URL`, asset URLs). Tests in `web/src/lib/publicSiteUrl.test.ts`.

### Changed
- Root `package.json`: `db:generate` still uses `drizzle-kit generate:sqlite`; `db:migrate` applies SQL via `scripts/run-migration.ts`; `db:upgrade-kit-snapshots` runs `drizzle-kit up:sqlite` when kit metadata needs upgrading.
- Web: removed standalone `web/src/pages/press-kit.astro`; nav “Press kit” links point to `/#press` on `Layout.astro` and `MarketingLayout.astro`.

### Documentation
- Engineering lead codebase review (2026-03-22): recorded decision and follow-ups in `DECISIONS.md`; added **Open** items in `TODOS.md` (shared `allowedOrigins` for CORS + Clerk, `GET /api/users/me` via `successResponse`, optional Playwright booking smoke); updated `STATE.md` to point at those docs.

### Added
- `logServerInfo` in `src/lib/safeLog.ts` for structured JSON lines on stdout (`level: info`); test in `safeLog.test.ts`.
- Security: `src/lib/safeLog.ts` for JSON error/warn logs (stacks only in `NODE_ENV=development`); `src/lib/forwardedProto.ts` for `X-Forwarded-Proto` + RFC 7239 `Forwarded` `proto=`; `rateLimitHealth` (120 GET `/health` per minute per client id); tests in `safeLog.test.ts`, `forwardedProto.test.ts`, extended `security.test.ts`.
- Security: production opt-in for `GET /api/admin/export/bookings` via `ALLOW_ADMIN_BOOKING_EXPORT=true`; structured audit log on successful export; docs in `.env.example` and DEPLOY.md; admin Astro page shows HTML guidance on 403.
- Deploy: Render (API with Bun + SQLite on persistent disk), Vercel (Astro frontend with @astrojs/vercel)
- `render.yaml` Blueprint: web service, disk at `/data`, DB_PATH=/data/sqlite.db, migrations at startup
- `DEPLOY.md` with step-by-step and env checklist for Render and Vercel
- `web/vercel.json` and Vercel serverless adapter in `web/astro.config.mjs` (`@astrojs/vercel/serverless` for Astro 4)
- `migrate` script in root package.json (runs scripts/run-migration.ts) for Render start command
- Booking deliverability observability: persist confirmation delivery last error + attempt count and expose it in admin UI; admins can re-send customer confirmation for `pending` bookings.

### Changed
- API: booking route logs `REQUEST_RECEIVED` via `logServerInfo` (JSON line) instead of unstructured `console.log`; band-email failure path uses shared `markBandEmailFailed` helper; empty insert `.returning()` yields 500 `INTERNAL_ERROR`.
- Admin booking export: default-deny unless `ALLOW_ADMIN_BOOKING_EXPORT=true` or `NODE_ENV=development` (unset/`test`/staging no longer implicitly allow export); user-facing 403 message and DEPLOY Option C text updated.
- Docs: `DEPLOY.md` — reverse-proxy header table (`X-Forwarded-Proto`, `Forwarded`, `X-Forwarded-For`) and `/health` rate limit note.
- Docs: full codebase security review (2026-03-22) — `BUGS.md` items addressed by post-review hardening; **TODOS — Security — Post-review hardening** completed.
- API: `GET /health` `version` comes from root `package.json`, with optional `APP_VERSION` or `RELEASE_VERSION` override (`src/lib/appVersion.ts`); documented in `.env.example`.
- API: `GET /api/admin/bookings` and `GET /api/admin/export/bookings` success bodies use `successResponse` — payload is under `data` (e.g. `data.bookings` + `data.total` for the list; export fields under `data` as well). Admin Astro page reads `data.bookings`; JSON download from export includes the same envelope.
- TODOS: Deploy marked completed (Render + Vercel + Clerk + Resend); added Content/SEO open todo; Resend domain verification remains P2
- DEPLOY.md: Post-launch section (Resend domain, custom domain, monitoring); health-check note (use Render URL for /health)

### Fixed
- Security (2026-03-22 review): verbose `console.error` with full errors replaced by `safeLog`; `enforceHttps` honors RFC 7239 `Forwarded` when `X-Forwarded-Proto` is missing; admin export no longer enabled for unset/non-`development` `NODE_ENV` without `ALLOW_ADMIN_BOOKING_EXPORT=true`.
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

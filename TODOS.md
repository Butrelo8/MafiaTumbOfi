# TODOS

Track open work and completed items by version. See CHANGELOG.md for full release notes.

**Roadmap (Hold Scope):** No first-paying-customer goal; no merch yet. **P1 lead-funnel roadmap (slices 1–4)** — closed **2026-04-11**; see **## Completed** → **Product roadmap — Lead generation & booking (P1 closed)**. **Custom domain + HTTPS** already live (Vercel + Render). **Optional later:** migrate stack to a **VPS** (P3 todo — cost/ops preference). **Resend** verified domain + prod `**RESEND_FROM_EMAIL`** shipped (see Completed). Monitoring and Content/SEO can stay on current hosts or move with a VPS. Stripe webhook only when there is a product to sell.

---

## Open

### Perf — Defer tour dates API call (SSR waterfall fix)

- **What:** Remove blocking `await loadTourDates(PUBLIC_API_URL)` from SSR render of `index.astro`. Load tour data client-side after page renders.
- **Why:** Render free tier cold start = up to 30s. This `await` blocks HTML delivery until Render API wakes. Entire page delays for one section.
- **Context:** `index.astro:24` — `const tourDates = await loadTourDates(import.meta.env.PUBLIC_API_URL)`. Render API (mto-api) spins down after inactivity.
- **Solution:** Remove SSR await. Add `data-api-url` attr to `<TourTable>` component. In a `<script>` tag, fetch tour dates client-side after `DOMContentLoaded` with a 3s timeout fallback. On timeout/error, show "Próximas fechas no disponibles" gracefully. Alternative: `Promise.race([loadTourDates(url), timeout(2000)])` in SSR and render empty state if API slow.
- **Done When:** Homepage HTML delivers without waiting for tour API. TourTable shows loading state then populates. Lighthouse TTFB unaffected by Render cold start.
- **Effort:** S
- **Priority:** P1
- **Depends on:** Nothing.

### Perf — Self-host Google Fonts (remove render-blocking request)

- **What:** Replace Google Fonts CDN `<link>` in `MarketingLayout.astro` with locally served font files via `@fontsource` npm packages.
- **Why:** External `fonts.googleapis.com` request = extra DNS + RTT + render-blocking. Causes FOUT.
- **Context:** `MarketingLayout.astro:46-49` loads Cormorant Garamond + Inter + JetBrains Mono from googleapis.com synchronously.
- **Solution:** `bun add @fontsource/cormorant-garamond @fontsource/inter @fontsource/jetbrains-mono`. Import only needed weights in `MarketingLayout.astro` (e.g. `import '@fontsource/inter/400.css'`). Remove `<link rel="preconnect">` and googleapis `<link>` tags. DESIGN.md: JetBrains Mono only for tabular data — omit from marketing layout if unused on homepage.
- **Done When:** No external font requests in Network tab. Fonts load from same origin. FOUT eliminated. Lighthouse flags no render-blocking resources.
- **Effort:** S
- **Priority:** P1
- **Depends on:** Nothing.

### Perf — Convert member images to WebP + add lazy loading

- **What:** Re-export all `web/public/members/*.jpg` as WebP. Update `<img>` references in `MemberCard.astro`. Add `loading="lazy"` and explicit dimensions.
- **Why:** `dimora.jpg` = 717KB. Combined member images ~1.5MB unoptimized. No `width`/`height` attrs → CLS. WebP 30–50% smaller.
- **Context:** `web/public/members/` — 5 JPEGs (84KB–717KB). `MemberCard.astro` renders without dimensions.
- **Solution:** Batch convert: `for f in web/public/members/*.jpg; do cwebp -q 82 "$f" -o "${f%.jpg}.webp"; done`. Update `MemberCard.astro` to `<picture>` with WebP source + JPEG fallback. Add `width` + `height`. Add `loading="lazy"`. Keep originals for press kit download links only.
- **Done When:** Member images served as WebP. CLS < 0.1. Lighthouse image audit passes.
- **Effort:** S
- **Priority:** P2
- **Depends on:** Nothing.

### Perf — Remove/lazy-load AOS library

- **What:** Replace AOS with native CSS `@keyframes` + `IntersectionObserver`, or lazy-load after page interactive.
- **Why:** `import 'aos/dist/aos.css'` in critical CSS path. AOS JS synchronous on load. DESIGN.md explicitly bans "AOS zoom/flip" — library is the root cause.
- **Context:** `index.astro:21` imports AOS CSS globally. `index.astro:722` runs `AOS.init()` synchronously.
- **Solution:** Remove `import 'aos/dist/aos.css'` and `import AOS from 'aos'`. Replace `data-aos` attrs with CSS classes using `@keyframes` (fade-up, fade-in). Use `IntersectionObserver` to toggle `.is-visible`. Alternative: `const { default: AOS } = await import('aos')` after `load` event.
- **Done When:** No AOS CSS in critical path. Animations still work. Bundle size reduced (verify via Astro build output). DESIGN.md AOS violations cleared.
- **Effort:** S
- **Priority:** P2
- **Depends on:** Nothing.

### Infra — Distributed rate limiting for multiple API instances

**What:** Replace or back in-memory booking (and future route-scoped) rate limit stores with a shared limiter (e.g. Redis, Upstash) or document single-instance requirement in DEPLOY.md.
**Why:** `Map`-based limits in `rateLimit.ts` reset per process; multiple workers = weaker protection.
**Context:** Comments already warn about trusted `x-forwarded-for`; scaling horizontally adds a new gap.
**Solution:** Run a single Redis service in Coolify (same host/VPC as your apps). Add REDIS_URL (or host/port/password) to the API app’s env. Refactor booking (and any future route-scoped) rate limiting to use a shared Redis-backed fixed window (or sliding window) with distinct key prefixes (e.g. `rl:booking:`, `rl:health:`) so limits are consistent across all API replicas. Use INCR + EXPIRE (or a small Lua script for atomic window reset) keyed by the same client id logic as today (x-forwarded-for / x-real-ip behind a trusted proxy). Keep in-memory limiter as a dev fallback when REDIS_URL is unset so local dev stays simple. Document Coolify Redis wiring, env vars, and “single-instance API + SQLite vs multi-instance + Redis” in DEPLOY.md.
**Done When:** Production/staging API uses Redis when REDIS_URL is set; dev works without it. Booking (and other rate-limited public routes) still enforce their intended limits across processes (verified by tests with a mock Redis or testcontainer, not a live network). DEPLOY.md / .env.example describe Coolify Redis and the trust requirement for forwarded IP headers.
**Effort:** M
**Priority:** P2
**Depends on:** Decision to run more than one API instance/process; do when migrating to more robust hosting.

### Design — change band icon/logo from main section/web.

**What:** Replace current's one made with AI with the real one.
**Why:** It's looks like the band actually has a logo, so the one I created with AI is garbage.
**Context:** Watching bands Instagram page I looked at the original logo.
**Solution:** Drop replacement file at `web/public/icon/mafiatumbada.png` (same filename — no code changes needed; already referenced in `web/src/layouts/MarketingLayout.astro:63` and `web/src/pages/index.astro:117`). Source options: (1) ask band manager for transparent-background PNG ≥512×512px; (2) crop logo from Instagram post, upscale with Topaz Gigapixel or Adobe Firefly to ≥512×512px, export as PNG with transparent bg.
**Done When:** Web page shows band real logo.
**Effort:** S
**Priority:** P1
**Depends on:** Obtaining real logo file from band manager or Instagram.

### Design — Change confianza / testimonios section with real info.

**What:** Replace section placeholders with real customers review.
**Why:** Placeholders in place, so it looks fake.
**Context:** People are looking for live experiences or some tipe of review.
**Solution:** Drop replacement/update lines at `web/src/data/testimonials`.
**Done When:** Web page shows real testimonies for band appearances.
**Effort:** S
**Priority:** P1
**Depends on:** That the band managers give me some information on past presentations.

---

### Mobile — Real device QA on Android mid-range before v2 ship

**What:** Test hero video autoplay, TourTable horizontal layout, ArtworkShelf scroll-snap, and FilmStrip on actual Android device (not devtools emulation). Min breakpoints: 360px, 390px.
**Why:** Devtools lies. Android autoplay policy, scroll-snap behavior, and video rendering differ from Safari iOS and desktop Chrome. Currently only tested on iPhone.
**Context:** Found in grill session 2026-04-20. Ship blocker for v2 given Mexico audience is heavily Android mid-range.
**Solution:** Run `cd web && bun run test:e2e` with Playwright at 360px/390px viewports first (`--project=chromium` with `viewport: { width: 360, height: 780 }`). Then verify on real device or BrowserStack (Chrome Android, Galaxy A-series). Checklist: (1) hero `<video>` has `autoplay muted playsinline` attrs and `<img>` poster visible under `prefers-reduced-motion: reduce`; (2) TourTable has `overflow-x: auto` and no clipped columns at 360px; (3) ArtworkShelf `scroll-snap-type` fires on touch — test swipe in DevTools touch mode; (4) FilmStrip has `overflow: hidden` on parent, no `width: 100vw` bleed causing scroll. Fix overflow with `max-width: 100%` or `overflow-x: hidden` on offending containers. Run `bun run build` after fixes.
**Done When:** All four components verified at 360px and 390px on Chrome Android; no horizontal overflow; video poster fallback works; issues fixed and `bun run build` green.
**Effort:** S
**Priority:** P2
**Depends on:** feat/desegin-consultation-redo merged

---

### Tests — Unit tests for Stripe webhook verification helper

**What:** Add tests for `verifyWebhookSignature` / `getStripe` error paths (mock Stripe SDK) when the webhook route exists.
**Why:** Payment boundary should be covered before production traffic; helper is currently unused until POST /api/webhooks/stripe ships.
**Context:** Pair with **Payments — Implement Stripe webhook handler**; reintroduce `stripe` SDK + helper module when that route ships (no `src/lib/stripe.ts` in repo until then — removed 2026-04-10).
**Solution:** When Stripe SDK + helper restored, mock `stripe` module. Cover `verifyWebhookSignature`: valid signature → returns parsed event; bad signature → throws typed error; missing `STRIPE_WEBHOOK_SECRET` → throws with clear message; stale timestamp (replay window) → throws. Cover `getStripe` lazy init: first call instantiates, second returns same instance; missing `STRIPE_SECRET_KEY` → throws at call time, not module load. No live SDK traffic; all tests run offline.
**Done When:** `src/lib/stripe.test.ts` exists and covers the four verification paths + both init paths; `bun test` green; no network calls in CI; failures produce readable diffs (structured error codes, not raw Stripe messages).
**Effort:** S
**Priority:** P3
**Depends on:** Payments — Implement Stripe webhook handler

---

### Deploy — Migrate production to a VPS (future)

**What:** When/if you want a single host instead of Render + Vercel: provision VPS, point **DNS** for the band domain at the VPS (domain already owned; today DNS points at Vercel/Render as applicable), reverse proxy (nginx or Caddy), SSL (e.g. Let’s Encrypt), run API (Bun + SQLite on persistent path) and optionally serve the Astro app; document in DEPLOY.md.
**Why:** Optional consolidation — one bill, full box control, your own logs — not required while Render + Vercel + custom domain meet needs.
**Solution:** Pick VPS provider + sizing; define cutover order (API first vs frontend first); rehearse env migration checklist (`PRODUCTION_URL`, CORS, Clerk URLs, `PUBLIC_API_URL`, `PUBLIC_SITE_URL`, Resend SPF/DKIM if mail stays on same domain).
**Done When:** Production traffic for site + API serves from the VPS with TLS; Render/Vercel decommissioned or demoted to preview; DEPLOY.md describes the chosen layout.
**Context:** **2026-04-10:** Custom domain and HTTPS already in use on current stack; **Resend** verified + `RESEND_FROM_EMAIL` on Render (see Completed). This ticket is **backlog** until you explicitly want to leave managed hosts.
**Effort:** L
**Priority:** P3
**Depends on:** None

---

### Payments — Implement Stripe webhook handler

**What:** Create POST /api/webhooks/stripe endpoint
**Why:** Required to handle subscription lifecycle events when ticket sales or merch are added
**Context:** Add `bun add stripe`, lazy-init client + `constructEvent` verification (`STRIPE_WEBHOOK_SECRET`) before handling events. Idempotency keys for side effects. Prior stub `src/lib/stripe.ts` removed 2026-04-10 with unused dependency — restore pattern from git history or Stripe docs when implementing.
**Solution:** Re-add `stripe` dep. Restore `src/lib/stripe.ts` (`getStripe` lazy singleton, `verifyWebhookSignature` wrapping `stripe.webhooks.constructEvent`). Add `POST /api/webhooks/stripe` in a new `src/routes/webhooks.ts` (mounted under a non-Clerk-gated path, body parsed as raw text before JSON middleware). Flow: read raw body + `stripe-signature` header → verify → switch on `event.type` → dispatch to typed handlers (`checkout.session.completed`, `customer.subscription.*`, etc., stubs OK until shop ships). Idempotency via new `stripe_events` table keyed on `event.id` (PK) with `receivedAt`; insert-if-not-exists before side effects, skip if row already exists. Return 400 on bad signature, 200 on ignored/duplicate, 500 on handler failure (lets Stripe retry). Scrub logs — no PII, no card data, no full event body in prod. Production gated via `ALLOW_STRIPE_WEBHOOK=true` env flag (mirrors existing export gate pattern).
**Done When:** Route accepts signed test events via Stripe CLI (`stripe listen --forward-to localhost:3001/api/webhooks/stripe`); replay of same `event.id` returns 200 with no duplicate side effect; bad signature returns 400; disabled gate returns 503; `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `ALLOW_STRIPE_WEBHOOK` documented in `.env.example` and `DEPLOY.md`; idempotency table migration applied; `bun test` green with mocked SDK.
**Effort:** M
**Priority:** P3
**Depends on:** If we ever do a shop. STRIPE_WEBHOOK_SECRET in .env

---

### Monitoring — Sentry or similar; check logs after deploys

**What:** Add Sentry (or similar) for error tracking; ensure logs are checked after each deploy.
**Why:** Catch production errors and failed deploys early; avoid blind debugging.
**Context:** Root `**.env.example`** has optional `**SENTRY_DSN`** (API). Wire Sentry in API (Hono) and/or frontend (Astro). **On VPS:** check VPS logs (e.g. systemd/journald or your reverse proxy logs) after deploy. If still on Render/Vercel, check their logs. Same habit either way.
**Solution:** **(1) API (required for this ticket’s minimum):** Add `**@sentry/bun`** (or `**@sentry/node`** if Bun adapter lags), call `**Sentry.init({ dsn: process.env.SENTRY_DSN, environment: NODE_ENV, tracesSampleRate: 0 … })`** only when `**SENTRY_DSN`** is set, as early as possible in `**src/index.ts**` (before routes). Hook `**src/middleware/error.ts**` (or top-level Hono `**onError**`) to `**Sentry.captureException**` for **5xx** / unexpected errors; use `**beforeSend`** / `**ignoreErrors`** to strip `**Authorization`**, cookies, and known noisy client errors. Set `**SENTRY_DSN`** on Render (same service as API). (2) Web (optional same slice or follow-up): If SSR errors matter on Vercel, add `**@sentry/astro**` (or server-only `**Sentry.init`** in Astro middleware) with DSN from **Vercel env** — avoid shipping a **public** DSN unless you accept client replay budget. **(3) Process:** Add a short **“After deploy”** subsection to `**DEPLOY.md`**: open Render + Vercel deploy logs, confirm 200 on `**GET /health`** (API) and homepage, then skim **Sentry → Issues** for new spikes in the first 15–30 minutes. Same checklist applies later on a VPS (replace dashboard names with journald / proxy).
**Done When:** `**SENTRY_DSN`** documented in `**.env.example`** / `**DEPLOY.md`** as **Render** (and **Vercel** if web wired) secret; API sends at least one **verified** test event to Sentry (e.g. temporary `**throw`** behind a dev-only route or Sentry’s “send test” flow) without logging the DSN; production **5xx** from the global error path appear in Sentry with scrubbed headers; `**DEPLOY.md`** includes the **post-deploy log + Sentry** checklist; `**bun test`** still green (init must no-op when DSN unset in CI).
**Effort:** S
**Priority:** P4
**Depends on:** None, add Sentry when the first “invisible prod bug” costs you more than an hour or when adding more surface (webhooks, admin actions, payments) where failures are easy to miss in raw logs.

---

### N8N — Run local instance on VPS for scheduled tasks and integrations

**What:** Run N8N as a local instance on the VPS (Docker or systemd); use it for scheduled tasks, optional notifications, and external API workflows; keep booking and Stripe in the app.
**Why:** One place for cron-like and integration workflows without adding cron or a queue to the app; webhooks, emails/notifications, and external API glue live in N8N.
**Context:** Boundary: app = DB, auth, booking, Stripe, critical path; N8N = schedules, inbound webhooks from external systems, optional emails/notifications, API glue. Secure N8N (auth, no public exposure or admin-only). Document in DEPLOY.md.
**Solution:** Deploy N8N via Docker Compose on the VPS (image `n8nio/n8n`) behind the existing reverse proxy on a subdomain (e.g. `n8n.<band-domain>`). Auth: N8N basic auth + proxy IP allowlist, or front it with Tailscale/VPN for admin-only access (no public exposure). Persistent Docker volume for N8N's internal SQLite workflow DB. Env: `N8N_BASIC_AUTH_ACTIVE=true`, `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`, `N8N_HOST`, `WEBHOOK_URL`, `N8N_ENCRYPTION_KEY` (generated, stored in VPS secrets manager or `.env` on box). Initial workflows: (a) daily check for bookings with `pipeline_status=new` older than 48h → Slack/email nudge; (b) weekly lead digest to band email; (c) optional Resend bounce/complaint webhook sink. Boundary stays firm: app owns booking, auth, DB writes, Stripe; N8N only does schedules, integration glue, and optional notifications.
**Done When:** N8N reachable at subdomain with TLS and auth; one scheduled workflow running in production (nudge or digest); workflow volume included in VPS backup cron; DEPLOY.md documents subdomain, auth model, backup strategy, and the app-vs-N8N boundary; workflows exported to JSON and committed under `docs/n8n/` for disaster recovery.
**Effort:** M
**Priority:** P4
**Depends on:** None required; easiest co-location is after **Deploy — Migrate production to a VPS (future)** (same P3 backlog). N8N can also run on any other Docker-capable host if you do not migrate the app stack.

---

### Postgres (VPS) — Add migration support (separate folders)

**What:** Add PostgreSQL support for the API by:

- introducing a runtime DB switch (e.g. `DB_DIALECT=sqlite|postgres`)
- reading Postgres connection from `PG_HOST/PG_PORT/PG_USER/PG_PASSWORD/PG_DATABASE`
- running Postgres migrations from a separate folder (e.g. `drizzle-postgres/`) at startup (idempotent/safe to re-run)
**Why:** When the VPS is ready, production should use Postgres instead of the SQLite file to support better ops (backups/tooling/scaling).
**Context:** Current setup is SQLite-only (`drizzle.config.ts` uses `dialect: 'sqlite'`, `scripts/run-migration.ts` applies `drizzle/*.sql`, and `scripts/check-db.ts` checks SQLite system tables).
**Solution:** Introduce `DB_DIALECT` env var (`sqlite` | `postgres`, default `sqlite`). Add `postgres-js` + `drizzle-orm/postgres-js`. Separate Drizzle config `drizzle.config.pg.ts` pointing at `drizzle-postgres/` folder; existing `drizzle.config.ts` and `drizzle/` stay SQLite-only. Extend `src/db/detect.ts` to return a PG client when `DB_DIALECT=postgres` + `DATABASE_URL` (or `PG_*` vars) present; keep Turso/bun:sqlite paths untouched. Extract dialect-sensitive column types (timestamps as unix-int on SQLite vs `timestamp with time zone` on PG) into small helpers so `src/db/schema.ts` can emit both, or fork schema into `schema.sqlite.ts` + `schema.pg.ts` if cleaner. Update `scripts/run-migration.ts` and `scripts/check-db.ts` to branch on dialect (PG uses `information_schema.tables`). Keep SQLite default for dev + small VPS; switch to PG when ops requires it. Out of scope: live data migration from SQLite → PG (separate card with `sqlite3-to-postgres` or custom ETL).
**Done When:** `DB_DIALECT=postgres` + `DATABASE_URL` boots the API against a Postgres instance locally (Docker); `bun run db:migrate` applies PG migrations from `drizzle-postgres/`; `bun run check-db` validates `users` + `bookings` on both dialects; `bun test` still green on SQLite default; smoke test (boot API, submit booking, read via admin) documented in DEPLOY.md under a "Postgres mode" section; rollback documented (switch `DB_DIALECT` back, keep Turso/SQLite as fallback until data migration card closes).
**Effort:** L
**Priority:** P4
**Depends on:** “Postgres when we need multi-instance writes or ops wants a managed DB,” and keep SQLite as the default VPS path until then.

---

## Completed

### Design — `/contratacion` redesign: Veracruz Noir + photo hero behind Press Kit header (2026-04-26)

**What:** Redesign `/contratacion` to match updated `DESIGN.md` (deeper matte-black surfaces, metallic gold gradient CTAs, burgundy cinematic glow, turquoise demoted to links/focus). Add full-bleed photo/band-image hero behind the Press Kit header block ("Mafia Tumbada / Corridos tumbados y regional mexicano · Xalapa, Veracruz · Desde 2021").
**Done When:** `/contratacion` matches Veracruz Noir premium palette; photo hero behind Press Kit header; metallic gold gradient on primary CTA; burgundy cinematic glow on hover; turquoise only on links/focus; `bun run build` green; zero WCAG AA violations on text over photo scrim.

### Perf — Compress hero.mp4 (47MB → <5MB) (2026-04-26)

- **What:** Re-encode `web/public/video/hero.mp4` to H.264/AVC at target ≤5MB. Add WebM fallback. Update `<source>` tags in `index.astro`.
- **Done When:** hero.mp4 ≤5MB on disk. Page loads without waiting for video. LCP measurably improved via Lighthouse.

### Design — change profile pictures of members in integrantes section (2026-04-22)

**What:** Change placeholder images on members/integrantes section.
**Done When:** Integrantes section show profile pictures. ✅ Already showing.

### Frontend — ArtworkShelf CD cover art (2026-04-21)

**What:** Optional `**cover?: string**` on shelf items; `**ArtworkShelf.astro**` renders `**<img>**` (explicit width/height 80, `**loading="lazy"**`, `**decoding="async"**`) when set, else initials. `**web/src/styles/marketing-press.css**` — `**.artwork-shelf-img**` (`**object-fit: cover**`, `**border-radius: inherit**`). `**web/src/pages/index.astro**` — `**artworkShelfItems**` all six singles get CDN URLs (Spotify oEmbed thumbnails + Apple Music artwork for Corazón).
**Plan:** `**docs/superpowers/plans/2026-04-21-artwork-shelf-cd-covers.md**`.
**Done When:** Met — `**cd web && bun run build**` green; `**bun test**` (root) green.

### Design — Code-review fixes (Veracruz Noir / marketing) (2026-04-21)

**What:** Closed P1 review (2026-04-21) on `feat/desegin-consultation-redo`: removed hex fallbacks on **`BookingForm.astro`** / **`gracias.astro`**; **`--color-success`** / **`--color-error`** in **`DESIGN.md`** + **`web/src/styles/marketing-press.css`**; form + budget radii → **`var(--radius-card)`**; **`SOLD OUT`** tag + hydrate + DESIGN localisation note; **`todayIsoDateUtc()`** (`toISOString().slice(0, 10)`) in **`src/routes/tours.ts`**; **`.eyebrow`** → **`var(--tracking-eyebrow)`**; **`is:global`** comment; **`contratacion.astro`** / gracias spacing tokens; Marquee reduced-motion already in **`marketing-press.css`**; expanded **`web/e2e/tours.e2e.ts`** (mocked **`/api/tours/upcoming`** — run Playwright locally after **`playwright install`**).
**Done When:** Met for code + unit tests + **`web`** build; Lighthouse + axe on **`/`** and **`/contratacion`** remain pre-merge operator checklist per **`DESIGN.md`** §Verification.

### Design — Pre-merge polish (follow-up) (2026-04-21)

**What:** **`BookingForm.astro`** `option:checked` text color **`#0b0b0b`** → **`var(--bg)`**. Confirmed **`.eyebrow`** uses **`var(--tracking-eyebrow)`**; **`contratacion.astro`** has no remaining **`clamp()`** spacing (uses **`var(--space-lg)`** etc.); **`web/e2e/tours.e2e.ts`** already covers empty state, SOLD OUT, hydration mock.
**Done When:** Code items met; **`DESIGN.md`** §Verification (Lighthouse, Playwright + axe, reduced-motion, breakpoints) still operator-run before merge.

### Analytics — Plausible conversion tracking on booking funnel (2026-04-20)

**What:** Plausible when `**PUBLIC_PLAUSIBLE_DOMAIN**` is set: deferred `**script.js**` + queue stub in `**MarketingLayout.astro**`. Custom events: `**Booking Submit**` on successful booking `**POST**` in `**BookingForm.astro**` (`**trackPlausible**`); `**CTA Click**` / `**target: contratacion**` on `**#hero-cta-contratacion**`; `**Ticket CTA**` / `**venue**` on delegated `**a.tour-ticket-btn**` (venue from `**data-analytics-venue**` on TourTable + hydrate). `**web/.env.example**` documents the env var.
**Done When:** Code + tests in place; operator enables domain in Plausible and sets env for live dashboard events. Run `**bun test**` and `**bun run build**` in `**web/**` before ship.

### UX — `/contratacion` fan orientation signal (2026-04-20)

**What:** `**Eyebrow**` (“Para promotores y organizadores de eventos”) + ghost link “← Volver al sitio” → `**/**` in a slim strip above the press cover; `**--text-muted**` + small type on link (`**marketing-press.css**` tokens via scoped CSS).
**Code:** `**web/src/pages/contratacion.astro**`, `**web/src/lib/bookingPageCopy.test.ts**`.
**Done When:** Met — `**bun test**` green.

### Admin — Lead priority badges + default sort + filters (2026-04-20)

**What:** **Prioridad** column uses chips mapped from stored `**lead_priority**` (`**high**` / `**medium**` / `**low**`): **high** → **`--accent-hot`**, **medium** → **`--gold`**, **low** / unknown → **`--text-muted`**. **`GET /api/admin/bookings`** and admin JSON export order by priority rank then **`createdAt`** desc. Second pill row filters by priority; **`#admin-bookings-toolbar`** scopes active-state toggles so **fechas** pills are unaffected.
**Code:** `**src/routes/admin.ts**`, `**web/src/pages/admin.astro**`, `**web/src/lib/adminPipelinePageCounts.ts**` + tests (`**adminPipelinePageCounts.test.ts**`, `**adminPageTheme.test.ts**`, `**admin-bookings-pagination.test.ts**`).
**Done When:** Met — `**bun test**` green.

### Config — Move drip video URL + WhatsApp to env vars (2026-04-20)

**What:** Nurture Email 2 uses **`DRIP_VIDEO_URL`** from env (code fallback only when unset so local/tests never ship empty links). Email 3 primary CTA uses **`PUBLIC_WHATSAPP_URL`** (same as public site; already env-driven).
**Why:** Band manager can fix link rot (dead YouTube, rotated WhatsApp) on Render without redeploy.
**Code:** `**src/lib/dripEmails.ts**`, `**dripEmails.test.ts**`, `**.env.example**`, `**DEPLOY.md**` (Render env table + drip §5).
**Done When:** Met — `**bun test**` green.

### Admin — Bulk delete all booking records (danger zone) (2026-04-11)

**What:** Admin-only hard delete of **all** rows in `**bookings`** (including soft-deleted) in one action; optional dry-run count; phrase confirmation; env gate in production like export.
**Code:** `**POST /api/admin/bookings/delete-all`** in `**src/routes/admin.ts`**; `**src/lib/adminDeleteAllBookings.ts`**, `**adminDeleteAllBookings.test.ts**`; `**src/routes/admin-delete-all-bookings.test.ts**`; `**src/routes/admin-auth.test.ts**` (non-admin 403); relay `**web/src/pages/admin/delete-all-bookings.ts**`; `**web/src/pages/admin.astro`** (zona peligrosa + modal + banner `**bulkDeleted`**); `**adminPageTheme.test.ts`**. `**.env.example**` `**ALLOW_ADMIN_DELETE_ALL_BOOKINGS**`; `**README.md**`, `**DEPLOY.md**`, `**CHANGELOG.md**`, `**DECISIONS.md**`.
Done When: Met — UI + API + tests + docs; `**bun test**` green.

### DB — Turso (libsql) for production SQLite (2026-04-11)

**What:** API uses **Turso** (`@libsql/client` + `**drizzle-orm/libsql`**) when `**TURSO_DATABASE_URL`** + `**TURSO_AUTH_TOKEN**` are set without `**DB_PATH**` (Render); embedded replica when Turso env + `**DB_PATH**`; else `**bun:sqlite**` (tests, offline).
Code: `**src/db/detect.ts**`, `**detect.test.ts**`, `**src/db/index.ts**`, `**scripts/run-migration.ts**`, `**scripts/check-db.ts**`, `**src/lib/findMissingTables.ts**`, `**findMissingTables.test.ts**`; `**render.yaml**` (no disk); `**DEPLOY.md**`, `**.env.example**`, `**drizzle.config.ts**`, `**DECISIONS.md**`, `**CHANGELOG.md**`, `**README.md**`.
**Done When:** Met — operator sets Turso secrets on Render; migrate/check-db/start path documented; `**bun test`** green.

### Auth — Admin via `ADMIN_CLERK_ID` (no first-user heuristic) (2026-04-11)

**What:** Replaced “first `users` row is admin” SQL with `**ADMIN_CLERK_ID`** (trimmed) matching Clerk `**sub`** for `**is_admin`** on insert; when env is set, `**getOrCreateUser`** reconciles `**is_admin**` on read. Migration `**drizzle/0010_admin_explicit_clerk_ids.sql**` for known legacy `**clerk_id**` rows.
**Why:** Second signup could steal admin; registration order is not a security boundary.
**Code:** `**src/lib/adminClerkConfig.ts`**, `**adminClerkConfig.test.ts`**; `**src/lib/users.ts**`, `**users.test.ts**`; `**src/middleware/adminAuth.ts**` comment. `**.env.example**`, `**render.yaml**`, `**DEPLOY.md**`, `**README.md**`, `**CHANGELOG.md**`, `**DECISIONS.md**`.
Done When: Set `**ADMIN_CLERK_ID**` on API (local + Render) to the band Clerk user id; only that user passes admin middleware; other accounts stay non-admin; `**bun test**` green.

### Product roadmap — Lead generation & booking (P1 closed) (2026-04-11)

**What:** Umbrella for prioritized funnel + light CRM vertical slices **(1)–(4)** (budget already on booking form; marketing, post-submit, admin triage, drip).
**Done When (met):** All four slices recorded below; production path `**/`** → `**/booking`** → `**/booking/gracias`** + WhatsApp CTA → `**/admin`** (lead score, priority, `**pipeline_status**`); no parallel spreadsheet for core triage; `**bun test**` green end-to-end.

- **(1)** **Marketing — Video hero + packages + conversion blocks** (2026-04-11) — this section.
- **(2)** **Booking UX — Thank-you page + WhatsApp follow-up CTA** (2026-04-11) — this section.
- **(3)** **Booking — Workflow statuses / `pipeline_status`** (2026-04-10) — this section.
- **(4)** **Email — Follow-up sequence / nurture drip** (2026-04-11) — this section.
**Next:** New funnel or CRM scope → new **## Open** card (P2+ backlog continues below **## Open**).

### Content / SEO — Homepage & booking copy pass (2026-04-11)

- `**web/src/pages/index.astro`:** `**hero-blurb`** (band + contrataciones + cotización sin compromiso), `**trust-strip`** (`**.trust-grid`** / `**.trust-item`** + SVG icons) after stats bar; scoped `**.hero-blurb**`, `**.sr-only**`, trust strip layout. Hero CTA unchanged (`**#booking**` / material prensa).
- `**web/src/pages/booking.astro`:** `**booking-intro`**, `**h2.form-section-heading`** (“Datos de contacto” / “Detalles del evento”), `**faq-section**` with five `**<details>**` (respuesta, anticipación, cobertura, tipos de evento, anticipo/pago). Form script + `**POST**` URL untouched.
- **Tests:** `**homepageHero.test.ts`** (blurb + trust order), `**bookingPageCopy.test.ts`**. `**CHANGELOG.md`** [Unreleased].

### UI — Admin page: marketing layout & dark design system (2026-04-11)

- `**web/src/pages/admin.astro**` — `**MarketingLayout**` (same shell as `/`, `/booking`), `**robots="noindex,nofollow"**`, `**footer-bar**`; table / legend / banners / pagination / status pills use `**marketing-press.css**` tokens; export → `**btn-secondary**` (“Exportar JSON (depuración)”).
- **Tests:** `**web/src/lib/adminPageTheme.test.ts`** (markup regression). `**DECISIONS.md`**, `**CHANGELOG.md`** [Unreleased].

### UI — Booking thank-you: YouTube embed instead of local video (2026-04-11)

- `**web/src/pages/booking/gracias.astro**` — lazy **YouTube** iframe `**HTA31yUX41A`** (16:9, ~600px); `**prefers-reduced-motion: reduce`** → link to watch URL; no `**hero.mp4`** on gracias (`**hero.mp4`** stays on homepage only).
- `**web/src/lib/bookingThanksPresentation.ts**` + `**bookingThanksPresentation.test.ts**` — embed/watch URLs + iframe title.
- `**web/e2e/booking.e2e.ts**` — asserts embed `**src**`. `**CHANGELOG.md**` [Unreleased].

### Email — Follow-up sequence / nurture drip (2026-04-11)

- **DB:** `**drizzle/0009_booking_drip.sql`** — `**drip2_due_at`**, `**drip2_sent_at`**, `**drip3_due_at**`, `**drip3_sent_at**` on `**bookings**`; `**src/db/schema.ts**`.
- **Schedule:** `**src/lib/dripSchedule.ts`** + `**dripSchedule.test.ts`** — defaults **+24h** / **+72h** from booking; env `**DRIP_EMAIL_2_DELAY_HOURS`**, `**DRIP_EMAIL_3_DELAY_HOURS`**.
- **Content:** `**src/lib/dripEmails.ts`** + `**dripEmails.test.ts`** — Email 2 video via **`DRIP_VIDEO_URL`** (see **Config — Move drip video URL + WhatsApp to env vars** above); Email 3 urgency + `**/booking`** (+ optional `**PUBLIC_WHATSAPP_URL**`).
- **Worker:** `**src/lib/dripProcessor.ts`** + `**dripProcessor.test.ts`** — only `**status === 'sent'`**; idempotent `**drip*_sent_at`** after Resend OK; `**DRIP_BATCH_SIZE**`.
- **API:** `**POST /api/booking`** sets `**createdAt`** + due columns (`**src/routes/booking.ts`**). `**POST /api/internal/process-drip`** (`**src/routes/internal.ts**`, `**internal.test.ts**`) — Bearer `**DRIP_CRON_SECRET**`.
- **Deploy:** `**render.yaml`** — `**mto-drip-cron`** `**curl`**s `**DRIP_PROCESS_URL`**; web `**DRIP_CRON_SECRET**`. `**.env.example**`, `**DEPLOY.md**`, `**DECISIONS.md**`, `**CHANGELOG.md**`.

### Booking UX — Thank-you page + WhatsApp follow-up CTA (2026-04-11)

- `**web/src/lib/bookingThanksSession.ts**` + `**bookingThanksSession.test.ts**` — key `**mto_booking_thanks**`, `**normalizeBookingConfirmation**`, `**parseBookingThanksStored**`.
- `**web/src/lib/publicSiteUrl.ts**` — `**bookingThanksCanonical()**`; test in `**publicSiteUrl.test.ts**`.
- `**web/src/pages/booking.astro**` — success: `**sessionStorage**` + `**location.assign('/booking/gracias')**`; form `**data-api-url**` / `**data-budget-hints**` (client script imports; no `**define:vars**` with imports).
- `**web/src/pages/booking/gracias.astro**` — `**MarketingLayout**` + `**robots="noindex,nofollow"**`; client: invalid/missing session → `**/booking**`; **remove session after read**; copy branches match previous inline success; **YouTube** presentation embed (`**bookingThanksPresentation.ts`**, reduced-motion fallback link); WhatsApp primary iff `**PUBLIC_WHATSAPP_URL`**.
- `**MarketingLayout.astro**` — optional `**robots**` → `**Seo**`.
- `**web/e2e/booking.e2e.ts**` — `**sent**`, `**pending**`, redirect without session. `**CHANGELOG.md**`, `**DECISIONS.md**`.

### Marketing — Video hero + packages + conversion blocks (2026-04-11)

- **Video hero (earlier):** `[web/src/pages/index.astro](web/src/pages/index.astro)` + `[web/src/styles/marketing-press.css](web/src/styles/marketing-press.css)`; tests in `[web/src/lib/homepageHero.test.ts](web/src/lib/homepageHero.test.ts)`.
- **This slice:** **Repertorio** (`#repertorio`), **Testimonios** (placeholder), **Paquetes** (`#paquetes` — Básico / Completo destacado / Premium), **urgencia** (`.booking-urgency` en `#booking`). Datos editables: `**web/src/data/repertoire.ts`**, `**testimonials.ts`**, `**packages.ts**`. Nav móvil: Paquetes → `/#paquetes` en `**MarketingLayout.astro**`. `**CHANGELOG.md**` [Unreleased]; `**bun test**` green (incl. `marketing homepage conversion blocks`).

### Content / SEO — Global meta & Open Graph skeleton (2026-04-11)

- `**web/src/components/Seo.astro`:** OG + Twitter Card + `**theme-color`** + optional `**robots`** (prop or `**PUBLIC_ALLOW_INDEXING=false`**); default `**og:image`** via `**absoluteAssetUrl(canonicalUrl, '/icon/mafiatumbada.png')**`.
- `**MarketingLayout.astro**` / `**Layout.astro`:** use `**Seo`**; marketing `**theme-color`** `**#0b0b0b**`, app shell `**#ffffff**` default.
- `**web/src/lib/publicSiteUrl.ts`:** `**adminCanonical`**, `**absoluteAssetUrl`**; `**admin.astro**` passes `**canonicalUrl**`. Tests `**publicSiteUrl.test.ts**`. `**web/.env.example**` — `**PUBLIC_ALLOW_INDEXING**`. `**DECISIONS.md**`, `**CHANGELOG.md**` [Unreleased]. `**bun test**` 166 pass; `**bun run test:e2e**` green.

### Tests — Playwright smoke: public booking flow (2026-04-11)

- `**web/package.json`:** devDependency `**@playwright/test`**; scripts `**test:e2e`**, `**test:e2e:install**`.
- `**web/playwright.config.ts`:** Chromium project; `**webServer`** runs `**astro dev`** on **127.0.0.1:4329** with `**PUBLIC_API_URL=http://127.0.0.1:3001`** (avoids clash with dev on 4321).
- `**web/e2e/booking.e2e.ts`:** mocks `****/api/booking`** — success (**201** + `confirmation: sent` → `#form-status` success) and error (**400** + API message → error state). Files use `***.e2e.ts`** so `**bun test`** does not pick them up as `*.spec.ts`.
- **Root:** `**bun run test:e2e`** (`bun run --cwd web test:e2e`); `**.gitignore`** — `web/test-results/`, `web/playwright-report/`, `web/blob-report/`.
- **Docs:** `**README.md`** (E2E + scripts), `**DEPLOY.md`** (optional smoke note). `**CHANGELOG.md`** [Unreleased].

### API — DRY origins + `/users/me` success envelope (2026-04-11)

- `**src/lib/allowedOrigins.ts`** — raw origin list (localhost + `FRONTEND_URL` / `STAGING_URL` / `PRODUCTION_URL`).
- `**src/index.ts`** — `expandCorsAllowedOrigins(rawAllowedOrigins)` for CORS allowlist (unchanged behavior vs inline array).
- `**src/middleware/auth.ts**` — Clerk `**authorizedParties**` imports same module.
- `**src/routes/users.ts**` — `**GET /api/users/me**` → `**successResponse(c, user)**` (same JSON shape `**{ data }**`).
- `**CHANGELOG.md**` [Unreleased]. `**bun test**` green (163).

### Booking — Workflow statuses / `pipeline_status` (2026-04-10)

- **DB:** `**drizzle/0008_booking_pipeline_status.sql`** — `**pipeline_status`** on `**bookings`** (default `**new`**); `**src/db/schema.ts`**.
- **API:** `**POST /api/booking`** sets `**pipelineStatus: 'new'`**; `**PATCH /api/admin/bookings/:id`** — `**{ pipelineStatus }**` only; `**bookings.status**` unchanged (resend still `**pending**` only). `**src/lib/bookingPipeline.ts**` + `**bookingPipeline.test.ts**`.
- **Web:** `**web/src/pages/admin.astro`** — **Seguimiento** column + legend (**Correo** vs **Seguimiento**); `**web/src/pages/admin/update-pipeline.ts`** relay (Clerk server-side).
- **Tests:** `**src/routes/admin-bookings-pipeline.test.ts`** (SQLite + migrations; dynamic booking id). `**src/routes/booking.test.ts`** — default `**pipelineStatus`**. `**src/routes/admin-auth.test.ts`** — non-admin **PATCH** **403**.
- **Docs:** `**DECISIONS.md`** (two-axis model), `**CHANGELOG.md`** [Unreleased].

### Booking — Lead score + priority field (2026-04-10)

- **Lib:** `**src/lib/bookingLeadScore.ts`** — `computeBookingLeadScore` (budget / attendees / duration / city + extras); `**src/lib/bookingLeadScore.test.ts`**.
- **DB:** `**drizzle/0007_booking_lead_score.sql`** — `lead_score`, `lead_priority` on `**bookings`**; `**src/db/schema.ts`**.
- **API:** `**POST /api/booking`** persists score at insert (**frozen**, see `**DECISIONS.md`**). Admin `**GET`** list/export unchanged shape (`**select()**` picks up new columns).
- **Web:** `**web/src/pages/admin.astro`** — Prioridad + sortable Lead score.
- **Docs:** `**CHANGELOG.md`** [Unreleased], `**DECISIONS.md`**.

### Content / SEO — Canonical URLs & sitemap after custom domain (2026-04-10)

- **Canonical + `og:url`:** `MarketingLayout.astro` — `PUBLIC_SITE_URL` + `resolvePublicBaseUrl` / `homeCanonical` / `bookingCanonical` (`web/src/lib/publicSiteUrl.ts`); `**index.astro`** + `**booking.astro`** pass `canonicalUrl`.
- **Sitemap:** `web/src/pages/sitemap.xml.ts` — `GET` returns XML for `**/`** and `**/booking`** only (no `/admin`); base URL = same resolver as marketing pages (`PUBLIC_SITE_URL` or request origin). `**web/src/lib/publicSitemap.ts`** + `**publicSitemap.test.ts`**.
- **Docs:** `CHANGELOG.md` [Unreleased].

### Resend — Verify domain so confirmation emails reach any customer (2026-04-10)

- **Prod:** Domain verified in Resend; `**RESEND_FROM_EMAIL`** = `**noreply@mafiatumbada.com`** on Render (see `**STATE.md`**, `**README.md`** “Email (Resend)”).
- **BUGS:** `**BUGS.md`** — Resend deliverability entry marked **fixed** for production; dev without verified domain still Resend-limited.
- **Docs:** `CHANGELOG.md` [Unreleased].

### Code review — DEPLOY note: Render Node image + Bun (2026-04-10)

- **Docs:** `DEPLOY.md` §1 — new **“Bun on Render (Node runtime)”** subsection (assumption, upgrade checklist with `bun --version` / Shell, fallbacks `npx bun@latest` or Docker). Step 4 start line aligned with `**render.yaml`** (`migrate && check-db && start`).
- **Infra:** `render.yaml` — comments above `**runtime`** / `**startCommand`** point to that section.

### Code review — Centralize marketing social URLs (2026-04-11)

- **Data:** `web/src/data/socials.ts` — `**bandSocialUrls`** (`spotify`, `tiktok`, `youtube`, `instagram`, `facebook`, `appleMusic`). Per-member links stay in `**members.ts`**.
- **Consumers:** `web/src/layouts/MarketingLayout.astro`, `web/src/pages/index.astro` — import + `href={bandSocialUrls.*}`; removed duplicate `const …Url` blocks.
- **Docs:** `README.md` (project tree); `CHANGELOG.md` [Unreleased]; `DECISIONS.md`.

### Code review — Homepage Apple Music icon (nested `<svg>`) (2026-04-11)

- **Web:** `web/src/pages/index.astro` — Redes sociales Apple Music card: **one** `<svg>` with the existing `**<path>`**; removed inner `**<svg role="img">`**, `**xmlns**`, `**title**` (parent `**<a aria-label="Apple Music">**` unchanged; `**span.social-icon**` still `**aria-hidden="true"**`).
- **Tests:** `web/src/lib/homepageHero.test.ts` — asserts exactly one `<svg` in the Apple Music block.
- **Docs:** `CHANGELOG.md` [Unreleased]; `DECISIONS.md`.

### Code review — Lint/format baseline (Biome) (2026-04-11)

- **Tool:** `@biomejs/biome` at repo root; `**biome.json`** — `files.includes` → `src/**/*.ts`, `scripts/**/*.ts`, `web/src/**/*.ts`; `***.astro` excluded**; `suspicious.noControlCharactersInRegex` off (intentional ASCII-strip regex in `sanitizeResendDetail.ts`); `noNonNullAssertion` off.
- **VCS:** `**vcs.useIgnoreFile` on** again — `**.code-review-graph/`** in `**.gitignore`** so Biome skips that tree; `**bun run lint`** green.
- **Scripts:** `lint`, `format`, `lint:fix` in root `**package.json`**; baseline applied with `**biome check --write`** and `**--unsafe**` for `node:` import protocol.
- **Docs:** `README.md` (Lint and format + Scripts table); `CHANGELOG.md`, `DECISIONS.md`.

### Code review — GitHub Actions: no CI / no keep-alive (2026-04-11)

- **Removed:** `.github/workflows/keep-alive.yml` (scheduled Render ping).
- **Dropped open todo:** “CI: run tests on push/PR” — not using GitHub Actions for gates or uptime pings; run `**bun test`** locally before ship.
- **Docs:** `CHANGELOG.md` [Unreleased], `DECISIONS.md`, `STATE.md`.

### Code review — Remove `/api/auth/`* 501 stubs (2026-04-10)

- **Removed:** `src/routes/auth.ts`, `src/middleware/rateLimitAuth.ts`; `src/routes/index.ts` no longer mounts `/auth`.
- **Tests:** `src/routes/booking.test.ts` — `rate limit: returns 429 after 5 requests per IP` on `POST /api/booking` (mocked `db` + Resend; no real DB rows or Resend traffic).
- **Docs:** `CHANGELOG.md` [Unreleased], `README.md` (routes tree), `DECISIONS.md`; auth remains Clerk + `src/middleware/auth.ts` (`/api/users`, `/api/admin`).

### Code review — Web package: version, `preview`, health endpoints (2026-04-11)

- `**web/package.json`:** `version` aligned to root (`0.5.0`); `preview` script is `astro preview` (requires `bun run build` first).
- **Lib:** `web/src/lib/webAppVersion.ts` — `getWebAppVersion()` reads `web/package.json`; override order matches API: `APP_VERSION`, `RELEASE_VERSION`, then file. Tests: `web/src/lib/webAppVersion.test.ts`.
- **Routes:** `web/src/pages/health.ts`, `web/src/pages/api/health.ts` — use `getWebAppVersion()` instead of hardcoded `0.4.0`.
- **API:** `src/index.ts` — `GET /health` calls `getAppVersion()` per request (fixes stale module-load `APP_VERSION` and `src/health.test.ts`).
- **Docs:** `README.md` (versioning note), `web/.env.example` (optional overrides); `CHANGELOG.md` [Unreleased]; `DECISIONS.md`.

### Marketing — Admin signed-in banner: discrete styling (2026-04-11)

- **Web:** `web/src/pages/index.astro` — `.admin-notice` / `.admin-notice a` / `:hover` — dark translucent bar, subtle bottom border, small muted copy, gold link + hover (replaces full-width `--color-brand` strip).
- **Tests:** `web/src/lib/homepageHero.test.ts` — new case for admin strip tokens; hero/marketing expectations synced to shipped `hero.mp4` + `marketing-press.css` (video filter + scrim alphas).
- **Docs:** `CHANGELOG.md` [Unreleased].

### Code review — Resend client test hook (optional) (2026-04-10)

- **Lib:** `src/lib/resend.ts` — `resendOverride` + `setResendForTesting(Resend | null)` (tests-only); `getResend()` prefers override; `null` clears override and `_resend` singleton.
- **Tests:** `src/lib/resend.test.ts` — override skips `RESEND_API_KEY`; missing key throws when no override. `src/routes/booking.test.ts` — `beforeEach`/`afterEach` + per-test overrides; removed `mock.module('../lib/resend')`. `src/routes/admin-resend.test.ts` — shared mock + `resendBehavior` with `beforeEach`/`afterEach` instead of module mock.
- **Docs:** `CHANGELOG.md` [Unreleased]; `DECISIONS.md`.

### Code review — Stripe: remove dead code until webhook ships (2026-04-10)

- **Deps:** Removed `stripe` from root `package.json`; `bun install` refreshes lockfile.
- **Code:** Deleted unused `src/lib/stripe.ts` (`getStripe`, `verifyWebhookSignature` had no importers).
- **Rules:** `.cursor/rules/hono-template.mdc` — Stack + Stripe section updated (SDK when webhook/checkout ships; webhook checklist: `constructEvent`, secrets, idempotency).
- **TODOS:** **Payments** + **Tests — Stripe webhook verification** context lines point at re-add path when handler ships.
- **Docs:** `DECISIONS.md`, `CHANGELOG.md` [Unreleased].

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

- **Script:** `scripts/check-db.ts` — `REQUIRED_TABLES` `users` + `bookings`; supports Turso + file SQLite via `**detectDbMode()`**; success log for deploy visibility.
- **Lib:** `src/lib/findMissingTables.ts` — parameterized `sqlite_master` lookup.
- **Tests:** `src/lib/findMissingTables.test.ts` (`:memory:` SQLite).
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

- **API:** Render (Bun + Turso / libsql). Start: `bun run migrate && bun run check-db && bun run start`.
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
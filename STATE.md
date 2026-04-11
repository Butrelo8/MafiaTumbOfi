# Project State

## Current Position
- Phase: **Production live** (Vercel + Render + custom domain). **Email:** Resend — **From** `noreply@mafiatumbada.com`; band inbox **`BOOKING_NOTIFICATION_EMAIL`** = `bookinginfo@mafiatumbada.com` (Cloudflare Email Routing → `mafiatumbadaoficial@outlook.com`).
- **Last completed (2026-04-11):** **Marketing homepage** — **`web/src/pages/index.astro`**: **Repertorio** (`#repertorio`), **Testimonios** (placeholder), **Paquetes** (`#paquetes`, featured tier), **urgencia** (`.booking-urgency` in **`#booking`**). Data **`web/src/data/{repertoire,testimonials,packages}.ts`**; CSS **`marketing-press.css`**; nav **Paquetes** → `/#paquetes`; tests **`homepageHero.test.ts`**. **Booking thank-you** — **`/booking/gracias`**: **`sessionStorage`** key **`mto_booking_thanks`** (**`web/src/lib/bookingThanksSession.ts`**), redirect from **`booking.astro`**; **`bookingThanksCanonical`** in **`publicSiteUrl.ts`**; **`MarketingLayout`** optional **`robots`** → thank-you **`noindex,nofollow`**; form script uses **`data-api-url`** / **`data-budget-hints`** (no **`define:vars` + import** — fixes client bundle / E2E). E2E **`web/e2e/booking.e2e.ts`**: **`sent`**, **`pending`**, redirect sin session. Docs: **`CHANGELOG`**, **`DECISIONS`**, **`TODOS`** (Marketing + Booking UX → **Completed**). **`bun test`:** **175** pass; **`bun run test:e2e`:** **4** pass (last run).
- **Next up:** **`TODOS.md` → Open** — **Email drip** after booking (P3). **Monitoring / Sentry** — optional (P4); logs + health checks until pain justifies **`SENTRY_DSN`**. Roadmap **Done When** narrows to **Email drip** (Marketing + thank-you shipped).

## Accumulated Decisions
- **2026-04-11 — Booking thank-you (`/booking/gracias` + `sessionStorage`):** Stable thank-you URL; **`mto_booking_thanks`** JSON; remove after read → refresh/direct sin payload → **`/booking`**; **`noindex`**. Full write-up: **`DECISIONS.md`**.
- **2026-04-11 — Homepage marketing data modules:** Typed **`web/src/data/*`** for repertoire / testimonials / packages (same idea as **`members.ts`**). **`DECISIONS.md`**.
- **2026-04-11 — Shared SEO head (`Seo.astro`):** Single partial for OG + Twitter + **`theme-color`**; absolute **`og:image`** via **`absoluteAssetUrl`**; optional **`robots`** / **`PUBLIC_ALLOW_INDEXING`**. Full write-up: **`DECISIONS.md`**.
- **2026-04-11 — CORS + Clerk origins:** **`allowedOrigins`** raw list in **`src/lib/allowedOrigins.ts`**; CORS expands via **`expandCorsAllowedOrigins`**; Clerk uses same raw list.
- **2026-04-11 — Playwright vs Bun test:** E2E specs named **`*.e2e.ts`** + **`testMatch`** so **`bun test`** does not treat **`*.spec.ts`** as Bun tests.
- 2026-04-10: **Bookings: two axes** — **`status`** = confirmation / Resend path only; **`pipeline_status`** = operator triage. Admin updates pipeline via **`PATCH`** only; resend still gated on **`status === 'pending'`**. Rationale: no overload of **`status`**; full detail in **`DECISIONS.md`**.
- 2026-04-10 (session): **Prod Resend + inbox routing** — Render: `RESEND_FROM_EMAIL` = `noreply@mafiatumbada.com`; `BOOKING_NOTIFICATION_EMAIL` = `bookinginfo@mafiatumbada.com`. Cloudflare routes that address to **`mafiatumbadaoficial@outlook.com`** (band reads mail there).
- 2026-04-11: **Social icons markup** — Apple Music (and siblings): one outer `<svg>` only; decorative wrapper `aria-hidden="true"`; accessible name on the `<a aria-label="…">` only — avoids invalid nested `<svg>` and duplicate announcements.
- 2026-04-10 (session): **Band vs customer email** — band alert = `BOOKING_NOTIFICATION_EMAIL` only; confirmation = form `email`; **From** = `RESEND_FROM_EMAIL` or Resend default; production values = **Render API env**, not Resend dashboard alone — details in README “Email (Resend)”.
- 2026-04-10 (session): **Double-slash API URL** — env `PUBLIC_API_URL` with trailing `/` caused `//api/booking` 404; fix = normalize base URL in Astro before appending `/api/...`.
- 2026-04-10: Admin list uses **offset pagination** (default limit 50, max 200); export **caps rows** per request (`ADMIN_EXPORT_MAX_ROWS`, default 10k, hard max 50k) with **`truncated` / `warning`**; **`last24hCount`** via SQL, not in-memory filter — see `DECISIONS.md`.
- 2026-04-10: Rate limit refactor keeps **fixed-window** `count` + `resetAt` behavior (not sliding window) so limits match pre-refactor semantics; `createRateLimiter` + shared cleanup interval.
- 2026-04-10: Booking persist failures expose **`BOOKING_PERSIST_FAILED`** to clients; throws log **`BOOKING_INSERT_FAILED`**, empty `returning` logs **`INSERT_RETURN_EMPTY`** — same public code, distinct log codes for ops.
- 2026-04-10: `getClientId` documents **`unknown` single-bucket** for local dev without proxy; `DEPLOY.md` notes parallel.
- CORS www/apex + trailing-slash `PRODUCTION_URL` handling — see `DECISIONS.md` entry “CORS allowlist: normalize `PRODUCTION_URL` + www/apex pair”.
- **Earlier context (archived):** DEPLOY Bun-on-Render note (`DEPLOY.md` §1 + `render.yaml`); web `getWebAppVersion` + `/health`; **`GET /health`** uses **`getAppVersion()`** per request; removed `/api/auth/*` stubs; booking rate-limit tests; Resend test hook; Stripe removed until checkout; marketing sitemap + canonicals; lead score at insert.

## Blockers & Open Questions
- None for local dev: **`bun test`** **175** pass; **`bun run test:e2e`** **4** pass at last check.
- **Ops:** After next API deploy, confirm production SQLite received **`0008_booking_pipeline_status`** (same migrate path as **`0007`**); admin PATCH/UI expects the column.

## Session Notes
**Last session:** **2026-04-11**  
**Stopped at:** **`STATE.md`** save — **Marketing** conversion blocks + **Booking thank-you** **`/booking/gracias`** shipped; roadmap items **(1)** and **(2)** in **`TODOS`** marked **Completed**. **Monitoring:** Sentry still **optional** (P4).  
**Resume with:** **Email drip** (P3) or smaller **Open** tickets in **`TODOS.md`**; ops check **SQLite `0008_booking_pipeline_status`** post-deploy when applicable; re-run **`bun test`** + **`bun run test:e2e`** before ship.

Consider running `/dream` to fold session notes into topic files if you use that workflow.

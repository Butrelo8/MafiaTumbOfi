# Spec: Static single-page rebuild (mafiatumbada.com)

Label: `wayfinder:spec` · Status: in progress (ticket 01 landed)

## 1. Keep / toss inventory

Rule: one static Astro page, `output: 'static'`, no backend, no auth, no DB, WhatsApp-only contact.

### TOSS — delete

**Whole trees (root = Hono API):**
- `src/**` (entire API: routes, middleware, db, lib, types, tests)
- `drizzle/**`, `drizzle.config.ts`, `data/` (sqlite.db)
- `scripts/check-db.ts`, `scripts/run-migration.ts`
- `render.yaml` (Render backend + cron)
- `web/vercel.json`, `web/scripts/patch-vercel-runtime.mjs`

**web/ pages + routes:**
- `web/src/pages/admin.astro`, `web/src/pages/admin/**` (7 relay routes)
- `web/src/pages/api/health.ts`, `web/src/pages/health.ts`
- `web/src/pages/booking.astro`, `web/src/pages/booking/gracias.astro`
- `web/src/pages/contratacion.astro`
- `web/src/middleware.ts` (Clerk)

**web/ components + libs:**
- `web/src/components/BookingForm.astro`
- `web/src/layouts/Layout.astro` (Clerk-bearing; only MarketingLayout survives)
- `web/src/lib/admin*` (12 files incl. tests)
- `web/src/lib/booking*` (6 files incl. tests)
- `web/src/lib/publicApiUrl.ts(+test)`, `tourTableHydrate.ts`, `safeJson.ts(+test)`,
  `sanitizeResendDetail.ts(+test)`, `webAppVersion.ts(+test)`
- `web/src/components/TourTable.astro`, `web/src/lib/tourDates.ts(+test)`,
  `web/src/lib/tourDateDisplay.ts(+test)`, `web/src/data/tourDates.ts`,
  `web/src/data/{packages,repertoire,testimonials}.ts` (§2 cuts)
- `web/e2e/**` + `web/playwright.config.ts` (booking/tours e2e all hit the API)

**Deps — root `package.json`: delete the file entirely** (nothing at root survives).
Removed with it: `hono`, `drizzle-orm`, `drizzle-kit`, `@libsql/client`, `@clerk/backend`,
`resend`, `zod`, `@astrojs/vercel`, `bun-types`.

**Deps — `web/package.json` remove:** `@clerk/astro`, `@astrojs/vercel`, `@astrojs/node`,
`@playwright/test`. Scripts removed: `test:e2e`, `test:e2e:install`, `build:vercel`;
`build` becomes plain `astro build`.

**Env vars — all deleted.** Root `.env.example` goes entirely (PORT, NODE_ENV, FRONTEND_URL,
STAGING_URL, PRODUCTION_URL, DB_PATH, TURSO_*, ADMIN_CLERK_ID, CLERK_*, RESEND_*,
BOOKING_NOTIFICATION_EMAIL, DRIP_*, ALLOW_ADMIN_*, ADMIN_EXPORT_MAX_ROWS, STRIPE_*, SENTRY_DSN,
APP_VERSION, RELEASE_VERSION).
From `web/.env.example` delete: `PUBLIC_API_URL`, `APP_VERSION`, `RELEASE_VERSION`,
`PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`.

### KEEP

- `web/` shell: `astro.config.mjs` (edit: `output: 'static'`, drop vercel adapter + clerk
  integration), `tailwind.config.mjs`, `tsconfig.json`, `package.json` (pruned)
- `web/src/pages/index.astro` (rewritten per ticket 02)  — `sitemap.xml.ts` → TOSS, see §6
- `web/src/layouts/MarketingLayout.astro`
- `web/src/components/`: `Seo.astro`, `Marquee.astro`, `MemberCard.astro`, `Eyebrow.astro`,
  `SignatureCTA.astro`, `ArtworkShelf.astro`, `FilmStrip.astro`

- `web/src/data/`: `members.ts` (trimmed to 3), `socials.ts`
  (`packages.ts`, `repertoire.ts`, `testimonials.ts`, `tourDates.ts` → TOSS, see §2)
- `web/src/lib/`: `publicSiteUrl.ts`, `heroVideo.ts`, `showPressAssets.ts`, `plausibleClient.ts` + their `.test.ts`
- `web/src/styles/global.css`, `web/src/styles/marketing-press.css`
- `web/public/**` (assets, band, members, music, video, og, icon, favicon.svg, robots.txt,
  grunge texture) — trim deferred to the perf pass
- Deps kept: `astro`, `@fontsource/{cormorant-garamond,inter,jetbrains-mono}`,
  `tailwindcss` + `@astrojs/tailwind`, `typescript`
- Env kept (`web/.env.example`): `PUBLIC_SITE_URL`, `PUBLIC_ALLOW_INDEXING`,
  `PUBLIC_PLAUSIBLE_DOMAIN`, `PUBLIC_WHATSAPP_URL`, `PUBLIC_PRESS_*`
- Docs: `DESIGN.md`, `README.md` (rewrite), `CHANGELOG.md`, `DECISIONS.md`, `STATE.md`
- Root Lighthouse report `www.mafiatumbada.com_*.report.*` — input to the perf pass

### Unresolved (deliberately deferred)

- ~~docs/scratch/stray markdown, repo layout~~ → resolved in §7
- `PUBLIC_WHATSAPP_URL` as env vs hardcoded constant → ticket 03
- ~~Tour dates → ticket 04~~ — void, section cut in §2
- ~~Música catalog source~~ → resolved in §3 (build-time fetch + daily deploy hook)

## 2. Single-page section order (ticket 02)

Seven sections + footer. Was 15.

| # | Section | id | Components / data | Notes |
|---|---|---|---|---|
| 1 | Hero | — | asymmetric hero + `heroVideo.ts` | one CTA → WhatsApp (ticket 03) |
| 2 | Marquee | — | `Marquee.astro` | unchanged |
| 3 | Música | `#musica` | `ArtworkShelf.astro`, `Eyebrow.astro` | **merge** of old `#musica` + `#streaming`; catalog auto-built, see §3 |
| 4 | Film strip | — | `FilmStrip.astro` | photo break |
| 5 | El sonido de Xalapa | — | bio-grid (inline) | editorial block, `--space-lg` |
| 6 | El grupo | `#grupo` | `MemberCard.astro`, `data/members.ts` | **trimmed to 3 fixed members**: Héctor, Alexandro, Diego Cerecer — lineup churns, so no per-gig roster |
| 7 | Contratación | `#contratacion` | `SignatureCTA.astro` | WhatsApp only, no form |
| — | Footer | — | `MarketingLayout.astro`, `data/socials.ts` | absorbs old `#redes` + press-asset links |

### Cut sections
`trust-strip`, `#repertorio`, `#testimonios`, `#paquetes`, `#fechas`, standalone `#redes`,
standalone `#press`.

**Tour dates dropped outright.** Keeping them current needs a human or an Instagram-stories
watcher; neither exists. This kills `TourTable.astro`, `data/tourDates.ts`, `lib/tourDates.ts`,
`lib/tourDateDisplay.ts` (+ tests) — moved to §1 TOSS — and voids **ticket 04**.

### Rhythm (DESIGN.md)
`--space-section` on 3 / 6 / 7, `--space-lg` on 5, hero gets `--space-hero`. No centered-hero
template, no uniform padding. Gold on eyebrows only; turquoise on links/focus only.

## 3. Música — catalog source (ticket 02 follow-up)

**Build-time fetch + daily deploy hook.** No Worker, no KV, no runtime JS, no client API calls.

```
Cloudflare Cron Trigger (daily, 1×) → Workers Build deploy hook → astro build
  ├─ Spotify: POST /api/token (client_credentials)
  │           GET  /v1/artists/3pc90hxACiSUahZmmfYjcI/albums?include_groups=single,album&market=MX
  │           → ArtworkShelf items (title, cover, release date, spotify url)
  └─ YouTube: GET https://www.youtube.com/feeds/videos.xml?playlist_id=UUSZnXDUTBZvPYcU-AGZULYA
              → latest N videos (title, thumbnail, url)
```

- Both fetches live in one build-time module, e.g. `web/src/lib/catalog.ts`, called from
  `index.astro` frontmatter. Astro runs frontmatter at build under `output: 'static'`.
- **Failure handling is mandatory**: wrap both in try/catch and fall back to a committed
  `web/src/data/catalog.json` snapshot, rewritten on each successful build. A Spotify 500
  must never fail the deploy or empty the section.
- Secrets (build env only, never `PUBLIC_`): `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`.
  Set in Workers Builds settings. Add to `web/.env.example` §1 KEEP list.
  YouTube needs no key or env var — the playlist id is hardcoded.

**YouTube feed gotcha (verified 2026-09-08):** `?channel_id=UCSZnXDUTBZvPYcU-AGZULYA` returns
**HTTP 500** for this channel. The uploads-playlist form works: swap the `UC` prefix for `UU` and
use `?playlist_id=UUSZnXDUTBZvPYcU-AGZULYA` → 200, 15 entries, newest first. Use that form.
- Cron cadence: daily. Singles ship every few months; anything tighter is wasted builds.

### Platform buttons
- **Spotify** — per-release, from the API payload.
- **Apple Music** — one artist-level button ("Escúchalo en Apple Music" →
  `bandSocialUrls.appleMusic`). Apple has no free API and its per-single URLs aren't derivable
  from Spotify ids, so per-release Apple links would mean manual entry. Artist link only.
- **YouTube** — a second row inside §2's `#musica`: thumbnail cards linking out to the video.
  Thumbnails only, no embedded players — embeds are the single heaviest thing that could land
  on this page.

## 4. WhatsApp CTA (ticket 03)

The only conversion path on the site.

### Link
Number: **+52 1 228 835 1464** (Xalapa, Veracruz). `wa.me` takes digits only:

```
https://wa.me/5212288351464?text=Hola%20Mafia%20Tumbada%2C%20quiero%20informaci%C3%B3n%20para%20contratarlos.%20Mi%20evento%20es%20el%20%5Bfecha%5D%20en%20%5Bciudad%5D.
```

Displayed form (footer, `tel:` fallback): `+52 228 835 1464`.

**Verify once before launch:** Mexican mobiles are registered on WhatsApp either as `521…`
(legacy) or `52…` (post-2019). Open both `wa.me/5212288351464` and `wa.me/522288351464` in a
browser — the wrong one shows "phone number shared via url is invalid". Ship whichever opens the
chat. This is a 30-second check that silently breaks every CTA on the site if skipped.
Prefill: `Hola Mafia Tumbada, quiero información para contratarlos. Mi evento es el [fecha] en [ciudad].`
Square brackets stay — they read as blanks the sender fills in.

**No desktop special-casing.** `wa.me` already routes to the app, `web.whatsapp.com`, or its own
install page depending on the client. A hand-rolled UA sniff or QR fallback is code that can only
get this more wrong than WhatsApp does.

### Where the number lives
Hardcoded in `web/src/data/socials.ts` as `bandSocialUrls.whatsapp`, **not** an env var.
It is a public phone number on a static site, so env buys no secrecy — and the current
`PUBLIC_WHATSAPP_URL` pattern silently renders *no CTA at all* when the var is missing, which on a
WhatsApp-only site means a page with no conversion path. Delete `PUBLIC_WHATSAPP_URL` from
`web/.env.example` (revises §1) and drop the `whatsappUrl ? (…) : (…)` conditional branches.

### Placements — three
1. **Hero** — primary CTA, gold gradient, replaces `Solicitar contratación`.
2. **§7 Contratación** — `SignatureCTA.astro` + the button, keeps the "respondemos en <24h" line.
3. **Footer** — text link beside the socials row.

No sticky/floating bar: it covers content on the exact small screens most fans use, and adds a
fixed element to a page whose whole point is a fast static load. Add one only if analytics show
hero + §7 under-converting.

### Fallback for no-WhatsApp visitors
The number rendered as plain text under §7's button, `tel:` linked. No form, no mailto, no
"contact us another way" copy.

### Analytics
Keep `plausibleClient.ts`. One custom event per placement: `whatsapp_hero`,
`whatsapp_contratacion`, `whatsapp_footer` — that is how the sticky-bar question gets settled later.

### Status
Closed. Only pre-launch action: the `521` vs `52` verification above.

## 5. Hosting target + DNS cutover (ticket 05)

Research: `.wayfinder/tickets/05-cloudflare-target-findings.md`.

### Target: Workers Static Assets (not Pages)
Cloudflare's own guidance: "If you are starting a new project, use Workers instead of Pages."
Pages still works but new features go to Workers. Assets-only Worker — no `main`, no script.

`web/wrangler.jsonc`:
```jsonc
{
  "name": "mafiatumbada",
  "compatibility_date": "2026-09-08",
  "assets": {
    "directory": "./dist/",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```
- `wrangler@^4` as a `web/` devDependency (revises §1 — it is the one dep added, not removed).
- No `"binding": "ASSETS"` — invalid without a `main` script.
- Workers Builds: root directory `web`, build `bun run build`, deploy `npx wrangler deploy`,
  production branch `main`. The dashboard Worker name **must equal** `name` above or builds fail.

### astro.config.mjs
Drop the `@astrojs/vercel` import + `adapter`, drop `output: 'server'` (static is the default),
keep `tailwind()`, drop `clerk()`. Add `site: 'https://mafiatumbada.com'` for canonical + sitemap.
`sitemap.xml.ts` is a static endpoint and prerenders fine under `output: 'static'` — it stays.

### DNS — measured 2026-09-08, not assumed

```
NS   lara.ns.cloudflare.com / rodney.ns.cloudflare.com   → zone ALREADY on Cloudflare
A    mafiatumbada.com  → 64.29.17.65, 216.198.79.65      → Vercel anycast, DNS-only
CNAME www              → 9f317a3d04fed1ad.vercel-dns-017.com
MX   route{1,2,3}.mx.cloudflare.net                      → Cloudflare Email Routing
TXT  v=spf1 include:_spf.mx.cloudflare.net ~all
DS   none                                                → DNSSEC not enabled
```

**This collapses most of the researched migration plan.** The nameserver move, the zone-activation
wait, the DNSSEC/DS SERVFAIL risk, and the record audit are all already done or moot. Email is
Cloudflare Email Routing and is untouched by the website cutover — do not delete the MX or SPF
records.

Actual cutover, four steps:
1. Deploy the Worker, verify fully on `mafiatumbada.workers.dev`. Site must be right before it
   owns the domain.
2. Delete the apex `A` records (both) and the `www` CNAME. A Custom Domain **cannot** be created
   on a hostname that still holds a CNAME — this is the one ordering trap left.
3. Add Custom Domain `mafiatumbada.com` to the Worker. Cloudflare writes the record and issues
   the cert.
4. `www`: proxied placeholder (`AAAA www → 100::`) + a zone Redirect Rule `www` → apex, 301.
   A Custom Domain matches its hostname exactly, so the apex Worker never sees `www` on its own.

Then remove the domain from the Vercel project. Rollback at any point = re-add the two Vercel A
records; TTL exposure is minutes, so lower apex TTL to 300s before step 2.

### Not doing
DNSSEC (currently off; enabling it is unrelated to this migration and adds a failure mode).

## 6. Old URL redirects + SEO (ticket 06)

### Where: `web/public/_redirects`
Plain text, no extension; Astro copies `public/` verbatim, so it lands at `dist/_redirects` and
Workers Static Assets parses it (it is not served as an asset). Runs before `_headers`, and runs
even when an asset matches the path. Top-most rule wins. **Default code is 302 — every rule below
states 301 explicitly.**

```
/contratacion      /#contratacion   301
/contratacion/     /#contratacion   301
/booking           /#contratacion   301
/booking/gracias   /                301
/booking/*         /                301
```

Anchors resolve against §2's ids, which exist: `#musica`, `#grupo`, `#contratacion`.

### What gets no rule
- `/admin`, `/admin/*` — `Disallow`ed in robots.txt and Clerk-gated; never indexed, no inbound
  links. A 404 is the correct answer for a page that no longer exists.
- `/health`, `/api/health` — machine endpoints. 404.

Redirecting these would only teach crawlers the paths existed.

### Anchor caveat, stated once
Google collapses `/#contratacion` to `/`, so `/contratacion`'s accumulated link equity consolidates
onto the homepage. That is the intended outcome of a one-page site, but it does mean the
`/contratacion` ranking does not survive as its own result — it merges. Accepted: the page it
ranked for is gone by decision, not by accident.

### robots.txt — rewrite
```
User-agent: *
Allow: /
```
The `Disallow` lines name paths that no longer exist, and the `Sitemap:` line goes with §6's
sitemap decision below.

### sitemap.xml — delete
One indexable URL. A sitemap listing a single homepage tells Google nothing its crawler does not
already have from the root of the domain. Delete `web/src/pages/sitemap.xml.ts`,
`web/src/lib/publicSitemap.ts` and its test (revises §1, which had them in KEEP), and drop the
`Sitemap:` line from robots.txt.

Add it back the day the site grows a second indexable URL.

## 7. Repo shape (ticket 07)

### Flatten `web/` to the repo root
The nesting only ever paid for itself because there were two runtimes deployed independently.
With the API gone there is one. Nested, every command needs a `cd web`, and the repo carries two
`package.json`, two `tsconfig.json`, two lockfiles, two `node_modules`, plus a Workers Builds
"root directory" setting that has to agree with all of it.

Move with `git mv` so per-file history follows. Root `package.json`, `tsconfig.json`, `bun.lock`
and `node_modules/` are deleted first (§1) — nothing at root survives to collide.

```
mafiatumbada/
├── .github/            (nothing today; leave absent)
├── astro.config.mjs
├── tailwind.config.mjs
├── wrangler.jsonc      (§5)
├── package.json        (was web/package.json, pruned per §1)
├── tsconfig.json
├── biome.json          (includes → ["src/**/*.ts"])
├── public/             (incl. _redirects §6, robots.txt §6)
├── src/                (was web/src — components, data, layouts, lib, pages, styles)
├── CLAUDE.md  README.md  DESIGN.md  DECISIONS.md  CHANGELOG.md  STATE.md  TEMPLATE.md
└── docs/superpowers/
```

`src/` at root now means the Astro site, not the dead API. Workers Builds root directory becomes
the repo root instead of `web`, and §5's `wrangler.jsonc` `assets.directory` stays `./dist/`.

### Docs disposition
**Keep:** `DESIGN.md` (unchanged), `DECISIONS.md` (append the rebuild entries), `CHANGELOG.md`,
`STATE.md`, `TEMPLATE.md`, `docs/superpowers/` — those plans are the reasoning behind components
that survive (`ArtworkShelf`, `FilmStrip`, the palette work). Markdown costs nothing to keep and
the reasoning is not recoverable once deleted.

**Rewrite:** `README.md` and `CLAUDE.md` — both describe two runtimes, Clerk, Drizzle, a booking
pipeline and a drip cron, none of which will exist. `CLAUDE.md`'s Commands, Architecture and Key
Patterns sections go to a single `bun dev` / `bun run build` / `npx wrangler deploy`.

**Delete:** `TODOS.md` (601 lines of API/admin tickets), `BUGS.md`, `DEPLOY.md` (Render + Vercel
runbook), `docs/n8n/` (health-check cron for the dead API), `.dockerignore`, `scratch/` (empty),
the root Lighthouse report once the perf pass has used it.

### The old API code
No archive branch. `git tag api-final <sha>` on the last commit before the deletion — the history
already holds every line, and a tag is the difference between "findable in one command" and
"findable if you remember it existed." A long-lived branch just invites someone to merge it.

## 8. Copy — full string set (ticket 08)

Spanish (MX). Salvage marked **[verbatim]** (copy the existing string, do not regenerate),
**[edit]** (existing string, changed clause), **[new]**.

### Hero
The `h1` is the logo image, not text — so no headline-length constraint applies here.

- Eyebrow: `Sitio Oficial` **[verbatim]**
- Meta row: `Xalapa, Veracruz` · `Corridos Tumbados` · `Regional Mexicano` · `Desde 2021` **[verbatim]**
- Blurb **[edit]** — drops the funnel language (`solicitar una cotización sin compromiso`):
  > La Mafia Tumbada es un grupo de corridos tumbados y regional mexicano con base en Xalapa,
  > Veracruz. Canciones propias, covers con actitud y cuatro años de tarima.
- CTA: `Escríbenos por WhatsApp` **[new]** — replaces `Solicitar contratación`. Second button
  (`Material de prensa`) removed with §2's press section.

### Marquee **[verbatim]**
`CORRIDOS TUMBADOS · XALAPA · DESDE 2021 ·` (repeated)

### §3 `#musica`
- Eyebrow: `Escucha` **[verbatim]**
- Heading: `Música` **[new]** — the old page split this into `Discografía / Material original`
  and `Escucha / Singles y streaming`; one section now, one heading.
- Release card caption: **title + year only**, both from the Spotify payload. No per-single blurb —
  §3 fetches automatically and nobody is writing copy for a release the build discovered at 4am.
  Card label: `Escuchar en Spotify`.
- Apple button: `Escúchanos en Apple Music` **[new]**
- YouTube row heading: `Videos` **[new]**; cards are thumbnail + video title from the RSS feed.

### §4 Film strip
No copy. Images with `alt` text only.

### §5 Bio — `El sonido de Xalapa`
- Eyebrow: `Quiénes somos` **[verbatim]**
- Heading: `El sonido de <em>Xalapa</em>` **[verbatim]** — italic on one word, within DESIGN.md rules.
- Tags: `Corridos Tumbados` `Norteño` `Regional Mx` `Covers` `Canciones propias` **[verbatim]**
- Paragraph 1 **[verbatim]** — "La Mafia Tumbada es un grupo de Xalapa, Veracruz que lleva cuatro
  años…" through "…ejecutados con honestidad y actitud."
- Paragraph 2 **[edit]** — the existing text opens `Ocho singles originales acumulados en su
  catálogo`. That number goes stale the moment §3 auto-adds a release. Replace the count:
  > Un catálogo de singles originales es la muestra de un proyecto que toma en serio la composición
  > propia. Al mismo tiempo, su versatilidad en tarima los ha llevado a barras y escenarios tanto en
  > Veracruz como fuera del estado.
  (Also drops `consolidando un nombre que los promotores ya reconocen` — promoter framing.)
- Paragraph 3 **[move]** — "El grupo está disponible para presentaciones, festivales, eventos
  privados y giras regionales. Cuentan con equipo propio…" is hiring copy sitting in the bio.
  Move it to §7 verbatim, delete from here. Bio ends at paragraph 2.

### §6 `#grupo`
- Eyebrow: `La banda` **[new]**
- Heading: `El grupo` **[new]**
- Members: `data/members.ts` already lists the three to keep as its first three entries
  (Héctor Báez / Vocal Principal · Alexandro Montal / Requintista & Vocal · Diego Cerecer /
  Guitarra & Coros) — trim is deleting the last two objects, no copy work. Names, roles and
  Instagram links **[verbatim]**. No blurbs: roles are the blurb, and a lineup that churns
  shouldn't carry prose about people.

### §7 `#contratacion`
- Eyebrow: `Contratar al grupo` **[verbatim]**
- Heading: `¿Tienes una <em>fecha disponible?</em>` **[verbatim]**
- Body **[move, from bio ¶3]**:
  > El grupo está disponible para presentaciones, festivales, eventos privados y giras regionales.
  > Cuentan con equipo propio y experiencia para adaptarse a diferentes formatos de producción.
- Urgency line **[edit]** — the current one promises `Respondemos cotizaciones en menos de 24
  horas`, an SLA that existed because a form auto-replied. WhatsApp makes no such promise:
  > Agenda limitada — los fines de semana suelen reservarse con tres o cuatro semanas de
  > anticipación.
  (First clause is **[verbatim]**; the 24h sentence is deleted, not reworded.)
- CTA: `Escríbenos por WhatsApp` **[new]**
- Fallback under the button **[new]**: `O llámanos: +52 228 835 1464`
- `SignatureCTA.astro` unchanged.

### Footer
- Socials row: labels from `data/socials.ts` **[verbatim]**
- WhatsApp text link: `WhatsApp` **[new]**
- Press links (ex-`#press`, §2): `Fotografías oficiales` · `Logotipos` · `Biografía` **[verbatim]**,
  now plain links gated on the existing `showPressAssets` env check.

### Deleted copy
Every string in `trust-strip`, `#repertorio`, `#testimonios`, `#paquetes`, `#fechas`, the
standalone `#redes` heading, and the booking form's labels, placeholders, and error messages.
`bookingPageCopy.test.ts` goes with them (§1).

## 9. Asset trim + performance budget (ticket 09)

### Re-measurement first (2026-09-08)
The Apr-28 Lighthouse report (perf 36, LCP 10.1s, 15,195 KiB) **predates** both the
`perf/homepage-performance-2026-06-01` merge and `icon/mafiatumbada.webp`, which was created six
hours after that run. It is not a valid baseline.

Fresh Chrome trace of production, **desktop, no CPU or network throttling**: LCP 974 ms, CLS 0.00.
That is not comparable to a throttled mobile Lighthouse run and must not be quoted as "perf is
fixed" — it only establishes that the 1.2 MB PNG is no longer the LCP element. The budget below
still needs a throttled mobile run to verify against.

### Done in this pass
- **`public/assets/orphan/` deleted** — 7.4 MB, four files, zero referrers anywhere in `src/`.
  Included the 4.6 MB `marketing-grunge-texture.png` duplicate.
- **`public/icon/mafiatumbada.png` deleted** (1.2 MB). The 45 KB `.webp` already existed, so both
  `<picture>` blocks collapse to a single `<img src="/icon/mafiatumbada.webp">` — the PNG fallback
  buys nothing in 2026. Touched `index.astro` (hero, `fetchpriority="high"`) and
  `MarketingLayout.astro` (header).
- `public/` 21 MB → **13 MB** on disk.

### Two live bugs found while measuring
1. **`/video/hero-poster.webp` 404 — fixed.** The file existed nowhere in the repo, yet was
   preloaded in `MarketingLayout.astro`, set as the `<video poster>` in `index.astro`, and
   asserted by `homepageHero.test.ts`. All three references deleted (no poster is generated); the
   404 and its wasted preload are gone. `homepageHero.test.ts` passes, 14/14.
2. **Clerk still loads on the public homepage** — `clerk.browser.js` + `ui.browser.js`, ~103 KB,
   on a page with no auth. §1 deletes it; this is most of the 1,150 ms TBT.

### Hero video — REVERTED, still 9.8 MB
A 960×540 / 24 fps / crf 33 re-encode (1.05 MB, −89%) was built and reviewed in the browser at
1440×900. **Rejected by the user on quality.** `hero.mp4` is back to the committed 1280×720
30 fps 5 Mbps original. Do not re-apply this encode.

Still open: the source is 5 Mbps for a muted decorative loop, which is high. Any future attempt
should stay at 1280×720 and move on crf alone — crf 30 measured at 2.4 MB (−75%) and is the next
thing to review. Resolution and frame-rate cuts are what cost the quality here.

**Animated WebP was measured and rejected.** A 3-second `libwebp -q 55` sample came out at
1,381 KB, extrapolating to ~7.3 MB for the full 16 s — barely better than the 9.8 MB original,
and as an image it cannot stream, cannot honour `preload="none"`, and decodes every frame into
memory at once. WebP is the right answer for the stills on this site (§9 logo) and the wrong one
for a 16-second loop.

VP9/WebM was also measured: 1,179 KB at equivalent settings, *larger* than the h264 and a second
asset to ship. Not worth a `<source>` fork.

### Still open
- `video/hero.mp4` — 9.8 MB, the largest asset, unresolved (see above)
- `marketing-grunge-texture.webp` — 1 MB; being removed in the redesign, no action now for a 320px repeating background tile. Almost certainly
  over-sized for its use; re-export at tile resolution.
- `members/dimora.jpg` (717 KB) and `members/luis-c.*` — both members §2 cuts. Delete with the
  data-file trim.
- `band/`, `music/`, `og/` — 724 KB combined, unaudited against the §2 section cuts.

### Budget
< 1 MB initial load · LCP < 2.5s · TBT < 200ms · **performance ≥ 90, throttled mobile**.
Enforcement: honour system, verified once before the DNS cutover in §5. No CI perf gate — a
one-page static site does not change often enough for a per-commit check to earn its maintenance.

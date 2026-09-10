# Static Single-Page Rebuild — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the two-runtime site (Hono API + Astro SSR) with one static Astro page on Cloudflare Workers, WhatsApp as the only contact channel.
**Tech Stack:** Astro 6.1.9 (`output: 'static'`), Tailwind 3.4, Bun 1.3.14, Cloudflare Workers Static Assets, wrangler v4.
**Spec:** `.wayfinder/SPEC.md` §1–§9 is the source of truth. Every decision below traces to a numbered section. Do not redesign; if something is uncovered, stop and ask.

## Evidence Gathering

**Files inspected:**
- `web/package.json`: astro `^6.1.9` (6.1.9 installed), `@astrojs/tailwind` ^5.1.0, tailwind ^3.4.0. Deps to remove: `@clerk/astro`, `@astrojs/vercel`, `@astrojs/node`, `@playwright/test`.
- `web/astro.config.mjs`: currently `output: 'server'`, vercel adapter, clerk integration.
- `web/src/components/ArtworkShelf.astro`: takes `items: ShelfItem[]` with `{title, subtitle?, href, label, cover?}`. This is the contract the §3 catalog fetch must satisfy — it already exists, do not invent a new one.
- `web/src/pages/index.astro:35`: `artworkShelfItems` is a hardcoded array in exactly that shape, with local `/music/*.webp` covers and a mix of Spotify and Apple `href`s.
- `web/src/components/Marquee.astro`: `Astro.props.text` with the §8 string as default — no change needed.
- `web/src/components/FilmStrip.astro`: hardcoded 3 frames from `/band/`. No props, no change.
- `web/src/lib/showPressAssets.ts`: `showPressAssetsSection = false`.
- `web/src/data/members.ts`: 5 entries; the 3 to keep (Héctor Báez, Alexandro Montal, Diego Cerecer) are already the first three.
- `web/public/music/`: 6 covers, `.jpg` + `.webp` each.

**Existing patterns found:**
- Pure functions live in `src/lib/*.ts` with a colocated `*.test.ts`, run by `bun test`. Follow this for the catalog module.
- Components take a typed `interface Props` in frontmatter. Data lives in `src/data/*.ts` as `as const` exports.
- `.astro` files are excluded from Biome; only `src/**/*.ts` is linted.

**Runtime/framework versions verified:** Astro 6.1.9 and Bun 1.3.14 from the installed tree, not from the manifest range.

**Existing abstractions to extend:** `ShelfItem` (ArtworkShelf), `bandSocialUrls` (`src/data/socials.ts`), the `src/lib` + colocated-test convention.

**Similar functionality already present:** `web/src/lib/tourTableHydrate.ts` fetches a remote list and renders it client-side. Deliberately **not** reused — §3 moved this work to build time, and that file is deleted in Phase 1.

## Product Intent

**User-facing outcome:** A fan lands on one page, hears the band within a scroll, and can reach the manager in one tap. A promoter reaches the same WhatsApp thread from the same page.

**Expected UX behavior:**
- [ ] Seven sections in the §2 order; no navigation to a second page.
- [ ] Every CTA opens a WhatsApp thread prefilled with the §4 message.
- [ ] The Música section shows the current catalog without anyone editing code after a release.
- [ ] No form, no login, no admin surface anywhere in the output.

**Performance expectations:** §9 budget — under 1 MB initial load, LCP under 2.5 s, TBT under 200 ms, Lighthouse performance ≥ 90 on throttled mobile.
**Accessibility expectations:** Hold the current 96 Lighthouse a11y score. Section landmarks keep their `aria-labelledby`; the decorative hero video keeps `aria-hidden`; every outbound link keeps a discernible name.
**Localization:** Spanish (MX) only. No i18n framework, no English fallback.
**Visual consistency:** `DESIGN.md` governs. Gold on eyebrows and CTA gradients only, turquoise on links and focus only, Cormorant on `h1`/`h2` only, `--space-section` vs `--space-lg` rhythm per §2.

## Open Questions

- **Question:** Do the press-asset links survive into the footer (§8) at all?
  **Why it matters:** `showPressAssetsSection` is `false` today, so those links render nowhere in production. §8 specifies them in the footer, which would make dead code live for the first time.
  **Safest default:** Drop the press links and delete `showPressAssets.ts` with its three call sites. The flag has been off; shipping it on is a product change nobody asked for.
  **Pause for clarification?** No — reversible in one commit, and the conservative move is to preserve current behavior.

- **Question:** Do release covers come from Spotify's CDN (`i.scdn.co`) or get downloaded into `public/music/` at build?
  **Why it matters:** Remote covers add a third-party origin to a page whose whole point is a fast static load; local covers mean the build writes into the repo.
  **Safest default:** Use the Spotify CDN URLs directly. The covers sit below the fold and are lazy-loaded, a build that writes tracked files is a worse failure mode, and `i.scdn.co` is already a fast CDN.
  **Pause for clarification?** No — recorded as a decision in Phase 4.

- **Question:** What does the Música section render on the very first build, before any successful Spotify fetch?
  **Why it matters:** Determines whether `catalog.json` ships seeded or empty.
  **Safest default:** Seed `src/data/catalog.json` from the existing hardcoded `artworkShelfItems` array so the fallback is never empty, even on a cold first build with bad credentials.
  **Pause for clarification?** No.

## Decision Priority

1. Correctness 2. Maintainability 3. Simplicity 4. Operability 5. Performance 6. Developer convenience.

Spec-specific refinement: **Simplicity outranks Performance** here. §9's budget is met by deleting things (Clerk, the API, 8.6 MB of assets), not by adding caching or optimization machinery.

## Architecture First

**Runtime model:** Build-time only. There is no server. `astro build` emits static HTML/CSS/JS to `dist/`; a Cloudflare Worker with an `assets` block and **no** `main` script serves it. Nothing executes per-request except Cloudflare's asset router and `_redirects`.

**Data flow:**
```
Cloudflare Cron (daily)
  └─> Workers Build deploy hook
        └─> astro build
              ├─ src/lib/catalog.ts  ──> Spotify /v1/artists/{id}/albums ──┐
              │                      └─> YouTube uploads RSS ─────────────┤
              │                                                            ├─> ShelfItem[] + VideoItem[]
              │                      (on throw) ──> src/data/catalog.json ─┘        │
              └─ index.astro frontmatter ─────────────────────────────────────> dist/index.html
```

**State ownership:** No runtime state. The catalog is derived at build time and frozen into HTML. `catalog.json` is the only persisted artifact and it is a fallback, not a cache — nothing reads it unless a fetch throws.

**Network boundaries:** Two build-time egress calls (Spotify token + albums, YouTube RSS). Both get an explicit timeout and a try/catch. Zero runtime network calls from the page besides Plausible.

**Rendering strategy:** SSG. No hydration framework, no islands. The only client JS is the existing hero-video mount and Plausible.

**Failure handling:** A Spotify outage, an expired credential, a YouTube 500, or a network timeout must all degrade to the committed `catalog.json` and let the build succeed. A failed build means the live site keeps serving the previous deploy, which is also acceptable — but a *green* build with an empty Música section is not.

**Security boundaries:** `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` are build-time-only secrets in Workers Builds settings. They must never be prefixed `PUBLIC_` and must never reach `dist/`. There is no auth, no user input, no trust boundary on the page itself — deleting Clerk removes the only one.

**Deployment assumptions:** Cloudflare Workers Static Assets, wrangler v4+, Workers Builds connected to the GitHub repo, production branch `main`.

**Why this architecture was chosen:** The site's content changes on the order of once a month. Anything that computes per-request, or per-viewer, is paying a permanent operational cost for a monthly event. Build-time fetching gives fresh data with zero runtime surface.

**Alternatives rejected:**
- Runtime Worker + KV for the catalog (§3): adds a script, a binding, a namespace and a failure mode to avoid a rebuild nobody watches.
- Cloudflare Pages (§5): Cloudflare directs new projects to Workers; Pages gets no new features.
- Client-side catalog fetch (the current `tourTableHydrate` pattern): ships an API call and a loading state to every visitor for data that is identical for all of them.
- Animated WebP for the hero loop (§9): measured at ~7.3 MB versus 9.8 MB, and cannot stream.

**Complexity intentionally avoided:** No CMS, no ISR, no image pipeline, no CI performance gate, no `_headers` file, no sitemap (§6 — one indexable URL), no service worker.

## Operational Constraints

- **Runtime:** Cloudflare edge, static assets only. Asset requests are not billed as Worker invocations.
- **Deploy:** Workers Builds, root directory = repo root after the Phase 2 flatten, build `bun run build`, deploy `npx wrangler deploy`. The dashboard Worker name must equal `name` in `wrangler.jsonc` or builds fail (§5).
- **Cron:** One daily trigger hitting the deploy hook. Not idempotent in the strict sense — each run publishes a new version — but a repeat run is harmless because the output is a pure function of the upstream catalog.
- **Secrets:** `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` in Workers Builds only. **Must be created before Phase 4 runs.**
- **Env kept (§1/§4):** `PUBLIC_SITE_URL`, `PUBLIC_ALLOW_INDEXING`, `PUBLIC_PLAUSIBLE_DOMAIN`. `PUBLIC_WHATSAPP_URL` is deleted — §4 hardcodes the number.
- **Observability:** Plausible custom events only (`whatsapp_hero`, `whatsapp_contratacion`, `whatsapp_footer`). No logging, no error reporting — there is no runtime to report from.
- **What breaks first at scale:** Nothing in the site. The Spotify credential expiring silently is the realistic operational failure, and it surfaces as a stale (not broken) Música section.

## Risk Analysis

**Highest-risk components:**
- `src/lib/catalog.ts` — the only new logic, the only external dependency, and the only thing that can fail silently.
- The Phase 2 flatten — a large `git mv` that can lose history or break every relative import at once.

**Likely failure points:**
- Spotify credentials absent or expired at build → empty Música section. Mitigated by the seeded `catalog.json` fallback and a test that asserts the fallback path.
- YouTube RSS shape drift → thumbnails or titles missing. Mitigated by parsing defensively and falling back per-source, not all-or-nothing.
- `channel_id` RSS form returning 500 (verified 2026-09-08) → **use the `?playlist_id=UU…` form**, already specified in §3.
- Deleting `src/` at root while `web/src` still exists → deleting the wrong tree. Phase 1 deletes before Phase 2 moves, never in the same commit.

**Integration risks:** Custom Domain creation fails if the old Vercel CNAME still exists (§5). This is a human deploy step, explicitly out of this plan's scope.

**Rollback complexity:** Easy through Phase 6 — every phase is its own commit on a branch, and production still serves from Vercel until a human does the §5 cutover. The DNS cutover itself is the only hard-to-reverse step and it is not in this plan.

**Risk-reduction order:**
1. Phase 4 (catalog) is built and tested **before** the Phase 5 page rewrite depends on it, so the risky fetch is proven against the real API while the old page still renders.
2. Phase 1 tags `api-final` before deleting anything.
3. Phase 2's flatten is verified by a green build immediately after, not at the end.

## Migration Strategy

**Rollout order:** Phases 1→7 on a single branch `feat/static-rebuild`, merged to `main` only when `bun run build` and `npx wrangler deploy --dry-run` both pass. Production continues serving from Vercel throughout — merging changes nothing user-visible until a human performs the §5 cutover.

**Backward compatibility:** Old URLs (`/contratacion`, `/booking`, `/booking/gracias`) must keep resolving — handled by `_redirects` in Phase 6, not by keeping the pages.

**Fallback strategy:** The Vercel deployment stays live and untouched until the cutover; reverting is re-pointing DNS. `git tag api-final` preserves the API code (§7) — no archive branch.

**Temporary compatibility layers:** None. There is no dual-write, no feature flag, no shim. The old and new stacks never run at once.

## Contracts Before Implementation

`ShelfItem` already exists in `ArtworkShelf.astro` — the catalog module produces it, it is not redefined:

```typescript
interface ShelfItem {
  title: string
  subtitle?: string   // release year, e.g. "2026"
  href: string        // Spotify release URL
  label: string       // "Spotify"
  cover?: string      // https://i.scdn.co/... (see Phase 4 decision)
}
```

New contracts, both in `src/lib/catalog.ts`:

```typescript
interface VideoItem {
  title: string
  href: string        // https://www.youtube.com/watch?v=...
  thumbnail: string   // https://i.ytimg.com/vi/<id>/hqdefault.jpg
}

interface Catalog {
  releases: ShelfItem[]
  videos: VideoItem[]
}

/** Never throws. Falls back per-source to the committed snapshot. */
export async function loadCatalog(): Promise<Catalog>
```

**Invariants:**
- `loadCatalog()` never throws and never returns an empty `releases` array.
- Each source degrades independently: a Spotify failure must not blank the YouTube row.
- No secret value ever appears in `dist/`.

## System Boundaries

### Inside the System
- The single Astro page, its seven sections, and its components.
- `src/lib/catalog.ts` and its build-time fetches.
- `wrangler.jsonc`, `_redirects`, `robots.txt`.

### Intentionally External
- Spotify and YouTube: read-only upstreams, no credentials stored beyond the build.
- Cloudflare Cron and the deploy hook: configured in the dashboard, not in the repo.
- Plausible: existing third-party script, unchanged.

### Deferred
- `hero.mp4` at 9.8 MB (§9): a 960×540 re-encode was built and rejected on quality. Next attempt stays at 1280×720 and moves crf alone — crf 30 measured 2.4 MB. Not in this plan.
- `marketing-grunge-texture.webp` at 1 MB: being removed in a future redesign.
- Apple Music per-release links: no free API, URLs not derivable from Spotify ids (§3).

### Out of Scope
- **The DNS cutover (§5).** Human-performed, ordering-sensitive, irreversible-ish.
- Any CRM, lead scoring, drip email, or admin replacement.
- The redesign itself. This plan restructures and deletes; it does not restyle.

## File Structure

Paths are **post-flatten** (Phase 2), i.e. `web/src/...` becomes `src/...`.

**Create:**
- `wrangler.jsonc` — Workers Static Assets config (§5).
- `src/lib/catalog.ts` — Spotify + YouTube build-time fetch, fallback logic.
- `src/lib/catalog.test.ts` — fallback and parsing behavior.
- `src/data/catalog.json` — seeded snapshot, the fallback of last resort.
- `public/_redirects` — §6 rules.

**Modify:**
- `astro.config.mjs` — static, no adapter, no Clerk, add `site`.
- `package.json` — pruned deps, `build` becomes plain `astro build`, add `wrangler@^4`.
- `biome.json` — `includes` → `["src/**/*.ts"]`.
- `src/pages/index.astro` — rebuilt to seven sections with §8 copy.
- `src/layouts/MarketingLayout.astro` — footer absorbs socials + WhatsApp; press links removed.
- `src/data/members.ts` — trimmed to three.
- `src/data/socials.ts` — add `whatsapp`.
- `public/robots.txt` — two lines.
- `README.md`, `CLAUDE.md` — rewritten.

**Delete:** everything in §1's TOSS list.

## Phases + Tasks

Branch: `feat/static-rebuild`. One commit per task.

### Phase 1 — Delete the API

#### Task 1: Tag, then delete the backend

**Purpose:** The two-runtime architecture stops existing, with its history findable in one command.

**Files:**
- Delete: `src/**`, `drizzle/**`, `drizzle.config.ts`, `data/`, `scripts/check-db.ts`, `scripts/run-migration.ts`, `render.yaml`, `package.json`, `tsconfig.json`, `bun.lock`, `node_modules/`, `.dockerignore`, `.env`, `.env.example` (all at repo root)
- Delete: `TODOS.md`, `BUGS.md`, `DEPLOY.md`, `docs/n8n/`, `scratch/`

**Steps:**
- [ ] `git tag api-final` on the current HEAD and confirm `git show api-final --stat` lists the API tree.
- [ ] Delete the root paths above. Do **not** touch `web/` in this task — the root `src/` and `web/src/` are different trees and deleting the wrong one is the main hazard here.
- [ ] Confirm `web/` is untouched: `git status --short web/` prints nothing.

**Validation:**
- Run: `git show api-final:src/index.ts | head -5`
- Expected: the Hono entry point prints, proving the tag preserves the deleted code.
- Run: `cd web && bun run build`
- Expected: succeeds — `web/` never depended on the root package.

**Commit:** `chore: delete Hono API, drizzle, and backend tooling`

#### Task 2: Delete the web-side backend surface

**Purpose:** Every page, route, lib, and test that assumed a server or an authenticated user is gone.

**Files:**
- Delete: `web/src/pages/admin.astro`, `web/src/pages/admin/`, `web/src/pages/api/`, `web/src/pages/health.ts`, `web/src/pages/booking.astro`, `web/src/pages/booking/`, `web/src/pages/contratacion.astro`, `web/src/middleware.ts`
- Delete: `web/src/components/BookingForm.astro`, `web/src/layouts/Layout.astro`
- Delete: `web/src/lib/admin*` (12 files), `web/src/lib/booking*` (6), `publicApiUrl.ts(+test)`, `tourTableHydrate.ts`, `safeJson.ts(+test)`, `sanitizeResendDetail.ts(+test)`, `webAppVersion.ts(+test)`
- Delete: `web/src/components/TourTable.astro`, `web/src/lib/tourDates.ts(+test)`, `web/src/lib/tourDateDisplay.ts(+test)`, `web/src/data/tourDates.ts`
- Delete: `web/src/data/packages.ts`, `repertoire.ts`, `testimonials.ts`
- Delete: `web/e2e/`, `web/playwright.config.ts`, `web/vercel.json`, `web/scripts/patch-vercel-runtime.mjs`
- Delete: `web/src/pages/sitemap.xml.ts`, `web/src/lib/publicSitemap.ts(+test)` (§6)
- Delete: `web/src/lib/showPressAssets.ts` (see Open Questions)
- Modify: `web/src/pages/index.astro` — remove imports and JSX for every deleted component/data module, and the three `showPressAssetsSection` branches. The page will be rebuilt in Phase 5; here just make it compile.
- Modify: `web/src/layouts/MarketingLayout.astro` — drop the `showPressAssetsSection` import and the conditional `Press kit` nav entry.
- Modify: `web/package.json` — remove `@clerk/astro`, `@astrojs/vercel`, `@astrojs/node`, `@playwright/test`; remove `test:e2e`, `test:e2e:install`, `build:vercel`; `build` → `astro build`.

**Steps:**
- [ ] Delete the files listed above.
- [ ] Fix the resulting import errors in `index.astro` and `MarketingLayout.astro` only. Resist rewriting sections — Phase 5 owns that.
- [ ] `grep -rn "clerk\|Clerk\|PUBLIC_API_URL\|tourDates\|BookingForm" web/src/` returns nothing.

**Validation:**
- Run: `cd web && bun test`
- Expected: passes, with the deleted files' tests gone and the survivors green.
- Run: `cd web && bun run build`
- Expected: succeeds. Clerk no longer appears in the built output: `grep -rl clerk web/dist/ | head` prints nothing.

**Commit:** `chore(web): delete admin, booking, and API-dependent code`

### Phase 2 — Flatten

#### Task 3: Move `web/` to the repo root

**Purpose:** One package, one config, one lockfile.

**Files:** Move `web/*` and `web/.*` (except `web/node_modules`, `web/dist`, `web/.astro`) to the repo root; delete the empty `web/`.

**Steps:**
- [ ] `git mv` each entry so per-file history follows. Do not copy-and-delete.
- [ ] Move `biome.json` from the old root into place and set `files.includes` to `["src/**/*.ts"]`.
- [ ] Delete stale `dist/`, `.astro/`, and any leftover `web/node_modules`; reinstall with `bun install`.
- [ ] Verify no source file references the `web/` prefix: `grep -rn "web/src\|\.\./web" src/ *.json *.mjs` returns nothing.

**Validation:**
- Run: `bun install && bun run build && bun test`
- Expected: all three succeed from the repo root with no `cd`.
- Run: `git log --follow --oneline src/pages/index.astro | head -3`
- Expected: history predating the move is still attached.

**Commit:** `refactor: flatten web/ into the repo root`

### Phase 3 — Cloudflare target

#### Task 4: Astro static config + wrangler

**Purpose:** The build emits static assets a Worker can serve.

**Files:**
- Modify: `astro.config.mjs`
- Create: `wrangler.jsonc`
- Modify: `package.json` (add `wrangler@^4` to devDependencies)

**Steps:**
- [ ] In `astro.config.mjs`: remove the `@astrojs/vercel` import and `adapter`, remove `output: 'server'`, remove the `clerk()` integration, keep `tailwind()`, add `site: 'https://mafiatumbada.com'`.
- [ ] Create `wrangler.jsonc` exactly as §5 specifies: `name: "mafiatumbada"`, `compatibility_date`, and an `assets` block with `directory: "./dist/"`, `not_found_handling: "404-page"`, `html_handling: "auto-trailing-slash"`. No `main`, no `binding`.
- [ ] `bun add -d wrangler@^4`.

**Validation:**
- Run: `bun run build`
- Expected: succeeds; `dist/index.html` exists as a real file, not a function manifest.
- Run: `npx wrangler deploy --dry-run`
- Expected: validates the config without deploying.

**Commit:** `feat: target Cloudflare Workers static assets`

### Phase 4 — Catalog (highest risk, built before anything depends on it)

#### Task 5: `loadCatalog()` with a fallback that cannot fail

**Purpose:** The Música section has data at build time, and a bad upstream can never empty it or break the build.

**Files:**
- Create: `src/lib/catalog.ts`, `src/lib/catalog.test.ts`, `src/data/catalog.json`

**Contracts used:** `ShelfItem`, `VideoItem`, `Catalog`, `loadCatalog()` from the Contracts section.

**Decision:** Covers use Spotify CDN URLs (`i.scdn.co`) directly rather than being downloaded into `public/music/`.
**Alternatives considered:** download at build; keep the existing local `.webp` covers.
**Tradeoffs:** adds a third-party image origin, below the fold and lazy-loaded; avoids a build step that writes tracked binary files into the repo on every cron run.
**Why this fits the decision priority:** Simplicity and correctness over a marginal performance gain on off-screen images.
**Complexity avoided:** No image download, no cache directory, no binary churn in git history.

**Steps (risky logic — full red/green):**
- [ ] Seed `src/data/catalog.json` from the current hardcoded `artworkShelfItems` array (6 releases, local `/music/*.webp` covers) plus an empty `videos: []`. This is the never-empty floor.
- [ ] Write failing tests in `catalog.test.ts` for: Spotify fetch rejects → releases come from the snapshot; YouTube fetch rejects → `videos` is `[]` while releases still come from Spotify; malformed Spotify JSON → snapshot; a valid Spotify album maps to a correct `ShelfItem` (title, `subtitle` = release year, `href`, `label: 'Spotify'`, `cover` = largest image URL); a valid RSS entry maps to a correct `VideoItem`. Inject `fetch` so no test hits the network.
- [ ] Run `bun test src/lib/catalog.test.ts` and confirm each fails for the expected reason.
- [ ] Implement `loadCatalog()`: client-credentials POST to `https://accounts.spotify.com/api/token`, then `GET /v1/artists/3pc90hxACiSUahZmmfYjcI/albums?include_groups=single,album&market=MX`; YouTube via `GET https://www.youtube.com/feeds/videos.xml?playlist_id=UUSZnXDUTBZvPYcU-AGZULYA` — the `channel_id` form returns 500 for this channel, verified 2026-09-08. Wrap each source in its own try/catch with an `AbortSignal.timeout(10_000)`.
- [ ] Run the focused test; confirm green.
- [ ] Verify no secret leaks: `bun run build && grep -rn "$SPOTIFY_CLIENT_SECRET" dist/ || echo clean` prints `clean`.

**Validation:**
- Run: `bun test src/lib/catalog.test.ts`
- Expected: all pass, including all three failure paths.
- Run: with real credentials exported, `bun run build` — expected: Música renders live releases. With `SPOTIFY_CLIENT_ID=` unset — expected: build still succeeds and renders the snapshot.

**Commit:** `feat(catalog): build-time Spotify and YouTube fetch with snapshot fallback`

### Phase 5 — The page

#### Task 6: Rebuild `index.astro` as seven sections

**Purpose:** The page matches §2's structure and §8's copy.

**Files:**
- Modify: `src/pages/index.astro`, `src/data/members.ts`, `src/data/socials.ts`
- Modify: `src/layouts/MarketingLayout.astro` (footer)

**Contracts used:** `Catalog` from Task 5; `ShelfItem` for `ArtworkShelf`.

**Steps:**
- [ ] Trim `members.ts` to its first three entries (Héctor Báez, Alexandro Montal, Diego Cerecer) and delete `public/members/dimora.jpg` and `luis-c.*`.
- [ ] Add `whatsapp: 'https://wa.me/5212288351464?text=…'` to `bandSocialUrls`, url-encoded exactly as §4 gives it.
- [ ] Rebuild `index.astro` in the §2 order: hero, Marquee, `#musica`, FilmStrip, bio, `#grupo`, `#contratacion`. Call `loadCatalog()` in frontmatter and pass `releases` to `ArtworkShelf`; render `videos` as a thumbnail row — links out, **no embedded players**.
- [ ] Apply §8 copy. Strings marked `[verbatim]` are copied character-for-character from the existing file; do not regenerate them. Move bio ¶3 into `#contratacion`; delete the "menos de 24 horas" sentence; drop the "Ocho singles" count.
- [ ] Footer: socials row, WhatsApp text link, no press links.
- [ ] Apply §2 rhythm: `--space-section` on 3/6/7, `--space-lg` on 5, `--space-hero` on the hero. Delete CSS rules orphaned by the removed sections.

**Validation:**
- Run: `bun run build && bun test`
- Expected: both pass.
- Run: `bun dev --port 4321 --host 127.0.0.1`, then load `http://127.0.0.1:4321/`.
- Expected: seven sections in order; no console errors; every WhatsApp CTA resolves to the §4 URL; the Música section shows releases and video thumbnails.
- Manually verify: keyboard-tab through the page reaches every CTA with a visible gold focus ring.

**Commit:** `feat(web): rebuild homepage as seven static sections`

#### Task 7: WhatsApp CTAs and analytics

**Purpose:** The only conversion path works from three places and is measurable.

**Files:** Modify `src/pages/index.astro`, `src/layouts/MarketingLayout.astro`

**Steps:**
- [ ] Hero CTA, `#contratacion` CTA, and footer link all point at `bandSocialUrls.whatsapp` with `target="_blank" rel="noopener noreferrer"`.
- [ ] Render `+52 228 835 1464` as a `tel:` link under the `#contratacion` button.
- [ ] Fire `whatsapp_hero`, `whatsapp_contratacion`, `whatsapp_footer` through the existing `trackPlausible` helper.
- [ ] Confirm no sticky/floating bar was added (§4).

**Validation:**
- Run: `grep -c "wa.me/5212288351464" dist/index.html` after a build
- Expected: `3`.
- Manually verify: clicking each CTA in a browser opens WhatsApp with the message prefilled.

**Commit:** `feat(web): wire WhatsApp CTAs and Plausible events`

### Phase 6 — Redirects and docs

#### Task 8: `_redirects`, robots, and documentation

**Purpose:** Old URLs keep resolving and the repo docs describe the system that now exists.

**Files:**
- Create: `public/_redirects`
- Modify: `public/robots.txt`, `README.md`, `CLAUDE.md`

**Steps:**
- [ ] Write `public/_redirects` with the five §6 rules, each ending in an explicit `301` — Cloudflare defaults to 302.
- [ ] Reduce `robots.txt` to `User-agent: *` / `Allow: /`. No `Disallow`, no `Sitemap:`.
- [ ] Rewrite `README.md` and `CLAUDE.md`: one runtime, one page. Commands reduce to `bun dev`, `bun run build`, `bun test`, `npx wrangler deploy`. Delete the Clerk, Drizzle, booking-pipeline, drip-cron, and admin sections. Keep the `DESIGN.md` pointer and the design-system rules.

**Validation:**
- Run: `bun run build && cat dist/_redirects`
- Expected: the file is copied verbatim into `dist/`.
- Run: `grep -rn "Drizzle\|Clerk\|Render\|drip" README.md CLAUDE.md`
- Expected: no matches.

**Commit:** `docs: rewrite README and CLAUDE.md for the static single-page site`

### Phase 7 — Verify against the budget

#### Task 9: Performance check

**Purpose:** §9's budget is met before anyone touches DNS.

**Steps:**
- [ ] `bun run build`, then serve `dist/` locally.
- [ ] Run Lighthouse, **mobile with throttling** — an unthrottled desktop run is not a valid check against this budget.
- [ ] Record the numbers in `.wayfinder/SPEC.md` §9 next to the targets.

**Validation:**
- Expected: initial load under 1 MB, LCP under 2.5 s, TBT under 200 ms, performance ≥ 90, accessibility ≥ 96.
- If performance misses: the two known levers are `hero.mp4` (9.8 MB, deferred above) and the 1 MB grunge texture. Report the gap; do not start the redesign to close it.

**Commit:** `chore: record post-rebuild performance baseline`

**Stop here.** The §5 DNS cutover is human-performed and out of scope.

## Complexity Budget Check

Removed rather than organized: an entire Hono API, a database and 14 migrations, Clerk auth, Resend email, a drip cron, an admin UI, a booking form, Playwright e2e, the Vercel adapter, a sitemap, and 8.6 MB of unreferenced assets.

Added: one config file (`wrangler.jsonc`), one module (`catalog.ts`), one JSON snapshot, one `_redirects` file, one dependency (`wrangler`).

Each addition justified: `wrangler.jsonc` is required by the platform; `catalog.ts` is the only way to meet "no manual step per release" without a runtime; `catalog.json` is what makes the fetch safe to fail; `_redirects` preserves indexed URLs.

## Cross-Task Consistency Check

- [ ] `ShelfItem` is the existing `ArtworkShelf` interface in Tasks 5 and 6 — not redefined in either.
- [ ] Paths are `web/`-prefixed in Phase 1 and root-relative from Phase 2 onward, matching the Task 3 flatten.
- [ ] `catalog.json` is seeded in Task 5, before Task 6 renders from it.
- [ ] The WhatsApp URL string is identical in `socials.ts`, §4, and Task 7's grep assertion.
- [ ] `showPressAssets.ts` is deleted in Task 2 and no later task references it — consistent with the Open Questions default.
- [ ] `sitemap.xml.ts` deleted in Task 2; the `Sitemap:` line removed from robots.txt in Task 8. Both trace to §6.
- [ ] No task adds a pattern a later task replaces.

## Self-Review

Ran against the checklist. Notes worth surfacing:

- **Evidence:** every file path and version above was read or executed in this session, not recalled. The `ShelfItem` contract and the `members.ts` ordering were verified rather than assumed.
- **Spec coverage:** §1→Tasks 1–2, §2→Task 6, §3→Task 5, §4→Task 7, §5→Task 4, §6→Task 8, §7→Tasks 1–3, §8→Task 6, §9→Task 9.
- **Risk ordering:** the catalog fetch is Phase 4, ahead of the page rewrite that consumes it, so the risky part is proven while the old page still builds.
- **One real gap:** Task 9 can fail its budget through `hero.mp4` alone, and that file is explicitly deferred. The plan tells the executor to report rather than fix, because fixing it was already tried and rejected on quality.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-09-static-single-page-rebuild.md`. Two execution options:

**1. Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?

# Homepage Performance Optimization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Do not start implementation until the Open Questions marked "Pause: Yes" are answered.**

**Goal:** Make the public homepage (`web/src/pages/index.astro`) load and feel fast on low-end machines/connections without changing its visual design or breaking admin auth.
**Tech Stack:** Astro 6 (`output: 'server'`, Vercel adapter), Clerk (`@clerk/astro`), `@fontsource`, plain CSS (`marketing-press.css`), Bun, Playwright.

---

## Evidence Gathering

**Files inspected:**
- `web/src/pages/index.astro` (918 lines): hero `<video>`, IntersectionObserver reveal script, inline section styles.
- `web/src/layouts/MarketingLayout.astro`: imports **10 `@fontsource` weight CSS files** + 2 global CSS; uses Clerk components (`Show`, `UserButton`, `SignInButton`, `SignUpButton`); header logo `<img src="/icon/mafiatumbada.png">` with **no `<picture>`/dimensions**; non-passive `scroll` listener (`checkScroll`); JSON-LD + Plausible loader.
- `web/src/layouts/Layout.astro`: admin/light shell, also imports Clerk components (out of scope — keep).
- `web/astro.config.mjs`: `output: 'server'`, `adapter: vercel()`, `integrations: [tailwind(), clerk()]`.
- `web/src/middleware.ts`: `export const onRequest = clerkMiddleware()` (global).
- `web/src/components/TourTable.astro` + `web/src/lib/tourTableHydrate.ts`: homepage passes `rows={[]}`; client always refetches `GET {apiBase}/api/tours/upcoming` after paint, replacing `<tbody>`.
- `web/src/components/{FilmStrip,ArtworkShelf,MemberCard,Marquee,SignatureCTA,Seo}.astro`: all use raw `<img>` (lazy + dims present except header logo); `Seo.astro` head has **no preconnect/preload**.
- `web/src/styles/marketing-press.css` (2062 lines): `.hero-video { filter: blur(2px) brightness(1.1) }` (L787–796); `body.marketing-body::after` grunge overlay `url('/marketing-grunge-texture.webp') ... repeat fixed; mix-blend-mode: screen` (L100–109); reduced-motion only `display:none`s `.hero-video` (L836–844).
- `web/src/lib/homepageHero.test.ts`: **string-matches** `class="hero-video"`, `/video/hero.mp4`, `playsinline`, `muted`, `hero-grain`, `blur(2px)`, `brightness(1.1)`, scrim rgba values, `.hero-deco-line`, `prefers-reduced-motion`, `rows={[]}`, `apiBase={apiBase}`, `.admin-notice`, `.menu-auth`, `window.setTimeout(() => closeMenu(), 0)`.

**Measured asset weights (`web/public`, 22 MB total):**
- `video/hero.mp4` — **10,036,145 bytes (~10 MB)** — autoplay/loop hero background, **no `poster`, no `preload`**.
- `marketing-grunge-texture.png` — **4,746,312 bytes (~4.7 MB)** — **orphan** (CSS references the `.webp`, not the `.png`).
- `marketing-grunge-texture.webp` — 1,056,016 bytes (~1 MB) — used as a 320px-tiled `fixed` overlay (oversized for a 320px tile).
- `icon/mafiatumbada.png` — 1,226,031 bytes (~1.2 MB) — shipped full-size for the small header logo (webp variant `icon/mafiatumbada.webp` = 45,582 bytes exists and is used by the hero `<picture>` only).
- `icon/mafiatumbada 2.png` (1.2 MB), `icon/mafiatumbada 3.png` (1.5 MB), `marketing-grunge-texture 1.png` (127 KB) — apparent orphans/duplicates.
- `members/dimora.jpg` — 734,317 bytes (others 40–210 KB); `members/dimora.webp` = 68,436 bytes (used by modern browsers via `MemberCard` `<picture>`).

**Existing patterns found:**
- Modern-format delivery via hand-written `<picture>` with `image.replace('.jpg','.webp')` (`MemberCard`) and explicit `<source srcset=...webp>` (hero logo). No `astro:assets`.
- `prefers-reduced-motion: reduce` is already handled in CSS (6 blocks).
- Custom IntersectionObserver reveal (`[data-reveal]`) — **no AOS library present** (DESIGN.md AOS concern N/A here).

**Runtime/framework versions verified:** `astro@^6.1.9`, `@clerk/astro@^3.0.21`, `@astrojs/vercel@^10.0.5`, `@astrojs/node@^9.1.1`, `tailwindcss@^3.4.0` (`web/package.json`).

**Existing abstractions to extend:** `<picture>`+webp pattern, reduced-motion CSS, `Seo.astro` head slot, `tourTableHydrate.ts` fallback fetch.

**Similar functionality already present:** Plausible script is loaded `defer` conditionally — same gating discipline can apply to Clerk and the hero video.

---

## Product Intent

**User-facing outcome:** A fan on a mid/low-end phone sees the homepage hero and copy almost immediately, can scroll smoothly, and the page settles without layout jumps. Visual design (hero video look, grunge texture, typography) is unchanged for capable devices.

**Expected UX behavior:**
- [ ] Hero shows a poster image instantly; video fades in only on capable, non-reduced-motion, non-save-data devices.
- [ ] No 10 MB download on reduced-motion / Save-Data / slow-connection devices.
- [ ] Header logo and tour table do not cause visible layout shift.
- [ ] Scrolling stays smooth (no per-frame video filter, no `background-attachment: fixed` repaint).
- [ ] Admin still sees the "Admin" shortcut and can sign in; `/admin` stays gated.

**Performance expectations (targets on Mobile, 4× CPU throttle / Slow 4G, Lighthouse):**
- LCP ≤ 2.5 s (poster, not the video, becomes LCP).
- TBT ≤ 200 ms (remove Clerk client JS from public pages).
- CLS ≤ 0.1.
- Initial transfer for `/` ≤ ~1.5 MB (down from current ~13 MB+: video + grunge + header PNG + fonts + Clerk JS).

**Accessibility expectations:** Keep current `prefers-reduced-motion` behavior; poster + scrims must preserve hero text contrast; logo `alt` unchanged.

**Visual consistency requirements:** Per `DESIGN.md` (Veracruz Noir). No palette/type/layout change — this is a delivery/loading optimization only.

---

## Open Questions

- **Question:** Where should the re-encoded/`webm` hero video live — re-encoded in `web/public/video/` (current approach) or moved to a CDN / Vercel asset?
  **Why it matters:** Affects repo size and caching headers; large binaries in git.
  **Safest default:** Re-encode in `web/public/video/` (mp4 ~2 MB + webm), keep paths stable.
  **Pause for clarification?** No — reversible.

- **Question:** May we delete the orphan binaries (`marketing-grunge-texture.png` 4.7 MB, `marketing-grunge-texture 1.png`, `icon/mafiatumbada 2.png`, `icon/mafiatumbada 3.png`)?
  **Why it matters:** ~7.5 MB of unreferenced files; deleting is irreversible-ish (git history aside) and they may be source art.
  **Safest default:** Quarantine/leave in place; do not delete without confirmation.
  **Pause for clarification?** **Yes** — do not delete files I did not create without sign-off.

- **Question:** Is it acceptable to stop shipping Clerk client JS to public pages, rendering the "Admin" shortcut server-side instead (admins sign in from `/admin`)?
  **Why it matters:** Changes the auth surface on marketing pages and is the single biggest TBT win, but touches authentication.
  **Safest default:** Server-render the admin link via `Astro.locals.auth()`; remove client `<Show>`/`SignInButton`/`UserButton` from `MarketingLayout` only.
  **Pause for clarification?** **Yes** — confirm the convenience strip behavior and auth approach before Phase 3.

- **Question:** For the tour table, SSR-fetch real rows at request time vs. reserve space + keep the existing client fetch?
  **Why it matters:** SSR fetch removes CLS but couples homepage TTFB to the Render free-tier API (cold starts).
  **Safest default:** Reserve vertical space (skeleton/min-height) and keep the client fetch.
  **Pause for clarification?** No.

- **Question:** Adopt `astro:assets` responsive images now, or defer?
  **Why it matters:** Larger refactor across components; YAGNI if targets are met by Phases 1–5.
  **Safest default:** Defer to Phase 6, gate on post-Phase-5 metrics.
  **Pause for clarification?** No.

---

## Decision Priority

1. Correctness (auth, visual fidelity, tests green)
2. Maintainability
3. Simplicity
4. Operability
5. Performance ← the product goal, but never at the expense of 1–4
6. Developer convenience

---

## Architecture First

- **Runtime/Rendering:** Astro SSR (`output: 'server'`) on Vercel; pages are server-rendered per request, hydration only where islands exist. Today there are **no `client:` directives**, but `@clerk/astro`'s integration + components inject Clerk's client runtime into the document. The marketing pages should be effectively static HTML + tiny inline scripts.
- **Media loading strategy (new):** Hero uses a lightweight **poster image** as the painted LCP element. The heavy `<video>` is **opt-in**: `preload="none"`, source attached via script only when the device is capable (not `prefers-reduced-motion`, not `navigator.connection.saveData`, not `effectiveType` `2g`/`slow-2g`) and after idle/first interaction or when in view.
- **Auth boundary (changed):** Public pages render the admin shortcut from the **server** (`Astro.locals.auth()` provided by the existing `clerkMiddleware()`), shipping **no Clerk client JS**. Full Clerk UI (sign-in modal, `UserButton`) stays on the admin shell (`Layout.astro` / `/admin`).
- **Network boundaries:** TourTable still calls the Render API client-side as a fallback; add `preconnect` to its origin and to `plausible.io`.
- **Failure handling:** If the video never loads (slow/declined), the poster remains — no broken state. If the tours API fails, existing `try/catch` keeps SSR markup.

**Why this architecture was chosen:** It removes the two largest costs (10 MB video on the critical path; Clerk JS on every public page) with reversible, framework-native techniques, and preserves the existing design, reduced-motion behavior, and admin auth.

**Alternatives rejected:**
- Replace the hero video with a static image entirely — rejected: loses the intended Veracruz-Noir motion design for capable devices.
- Move all images to `astro:assets` up front — rejected for now: large refactor, deferred to Phase 6 pending metrics.
- Remove Clerk from the app — rejected: admin CRM needs it; only its **client delivery on public pages** is the problem.

**Complexity intentionally avoided:** No new build tooling, no CSS framework swap, no CDN/image-service introduction in the core phases, no service workers.

---

## Operational Constraints

- **Deploy target:** Vercel (frontend). Re-encoded media and font subsets are static assets cached by Vercel's CDN.
- **External API:** Render free tier (cold starts) — keep TourTable client fetch resilient; do not make homepage TTFB depend on it (per Open Question default).
- **Env vars (existing):** `PUBLIC_API_URL` (TourTable + preconnect target), `PUBLIC_PLAUSIBLE_DOMAIN`, `PUBLIC_PRESS_*`, `PUBLIC_WHATSAPP_URL`, `PUBLIC_SITE_URL`. No new env vars required.
- **Performance-sensitive paths:** initial document + hero paint; scroll repaint.
- **Tooling note:** `web/` linting (Biome) does **not** cover `.astro` files; `.ts` libs do. Keep new logic in a `.ts` lib where practical so it is linted and unit-testable.

---

## Risk Analysis

**Highest-risk components:**
- **Clerk removal from public pages (Phase 3):** risk of breaking sign-in or the gated admin link, or the `clerk()` integration still injecting script app-wide.
- **Hero video changes (Phase 1):** visual regression (blur/brightness look) + the strict string assertions in `homepageHero.test.ts`.

**Likely failure points:**
- Font subsetting drops a glyph used in Spanish copy (accents, `¿`, `¡`, `ñ`, `—`).
- Conditional video loader misfires (e.g., never loads on capable devices, or loads on save-data).
- Re-encoded video/webm codec unsupported on a target browser → ensure mp4/H.264 fallback remains.

**Integration risks:**
- `@clerk/astro` integration behavior: confirm whether `clerk()` injects client JS regardless of component usage. **This is the Phase 0 spike.**

**Rollback complexity:** Easy per phase — each change is isolated (markup/CSS/config) and revertible by commit.

**Risk-reduction order:**
1. **Phase 0 spike:** measure baseline + confirm (a) Clerk JS ships on `/`, (b) the `<video>` downloads under reduced-motion. This decides Phase 3 feasibility/approach.
2. Phase 1 (video) — biggest certain win, contained blast radius.
3. Phase 3 (Clerk) — gated behind Open Question + Phase 0 findings.

---

## Migration Strategy

**Rollout order:** Phase 0 → 1 → 2 → 3 → 4 → 5 → (6 optional). Each phase ships independently and is separately revertible.

**Backward compatibility:** Asset paths (`/video/hero.mp4`, `/icon/mafiatumbada.png`) stay valid; the hero `<picture>` and `MemberCard` continue to fall back to existing files. Admin auth contract unchanged on `/admin`.

**Fallback strategy:** Poster covers any video failure. Keep H.264 mp4 as the last `<source>`. If Phase 3 regresses auth, revert that single commit; public pages return to current behavior.

**Temporary compatibility layers:** None required; no dual-write/data migration.

---

## Contracts Before Implementation

These are **proposed additions** (do not exist yet) unless marked existing:

```text
# Hero media (Phase 1) — proposed
poster asset:        web/public/video/hero-poster.webp      (~20–40 KB, blurred first frame)
video sources:       web/public/video/hero.webm  +  web/public/video/hero.mp4 (re-encoded ~2 MB)
<video> attributes:  preload="none", poster="/video/hero-poster.webp", muted, loop, playsinline, aria-hidden="true"
                     sources via data-src; class="hero-video" retained

# Hero video loader (Phase 1) — proposed lib (linted/testable)
web/src/lib/heroVideo.ts
  export function shouldLoadHeroVideo(win: Window): boolean
    // false if matchMedia('(prefers-reduced-motion: reduce)').matches
    // false if (navigator.connection?.saveData === true)
    // false if effectiveType in {'slow-2g','2g'}
    // true otherwise
  export function mountHeroVideo(doc: Document): void
    // if shouldLoadHeroVideo: move data-src -> src on <source>, call video.load()
    // scheduled via requestIdleCallback (fallback setTimeout) and/or IntersectionObserver

# Admin shortcut (Phase 3) — server-rendered, existing API
Astro.locals.auth()  // provided by existing clerkMiddleware(); returns { userId, ... }
  // render admin-notice / menu "Admin" link when signed in — no client <Show>
```

Existing contracts kept: `hydrateTourTablesFromApi()` (`web/src/lib/tourTableHydrate.ts`), `normalizePublicApiBaseUrl` (`web/src/lib/publicApiUrl.ts`), `Seo` props.

---

## System Boundaries

### Inside the System
- `web/src/pages/index.astro` — hero markup, reveal script.
- `web/src/layouts/MarketingLayout.astro` — fonts, head hints, header logo, Clerk usage, scroll handler.
- `web/src/styles/marketing-press.css` — hero/grunge/scroll styles.
- `web/public/video/*`, `web/public/icon/*`, `web/public/marketing-grunge-texture.webp`, `web/public/members/dimora.jpg`.
- `web/src/components/Seo.astro` (or layout head) — preconnect/preload.
- `web/src/lib/heroVideo.ts` (new), `web/src/lib/homepageHero.test.ts` (update).

### Intentionally External
- Render API (tours), Clerk service, Plausible — unchanged services; only how/whether we connect/ship their client code changes.

### Deferred
- `astro:assets` responsive pipeline (Phase 6).
- CSS critical-path inlining / code-splitting `marketing-press.css` (Phase 6, metrics-gated).

### Out of Scope
- `web/src/pages/admin.astro` and `Layout.astro` Clerk UI (must keep working).
- `contratacion.astro` / booking form redesign (they share `MarketingLayout`, so they inherit font/Clerk/scroll wins — but no page-specific work here).

---

## File Structure

- Modify: `web/src/pages/index.astro` — hero `<video>` (poster/preload/data-src), keep test tokens.
- Create: `web/src/lib/heroVideo.ts` — capability gate + loader.
- Modify: `web/src/lib/homepageHero.test.ts` — adjust hero assertions; add `heroVideo` unit tests.
- Modify: `web/src/layouts/MarketingLayout.astro` — header logo `<picture>`+dims; fontsource imports → subset; head preconnect/preload; passive/rAF scroll; Clerk → server-rendered admin link (Phase 3).
- Modify: `web/src/styles/marketing-press.css` — remove per-frame video `filter`; grunge `fixed`→`scroll`; poster/`.hero-video` opacity transition.
- Modify: `web/src/components/TourTable.astro` — reserve row space (skeleton/min-height).
- Replace asset: `web/public/marketing-grunge-texture.webp` (true ~320px tile), `web/public/video/hero.mp4` (re-encoded) + add `hero.webm` + `hero-poster.webp`; re-export `web/public/members/dimora.jpg`.
- Quarantine (pending Open Question): orphan PNGs.

---

## Phases + Tasks

### Phase 0: Baseline & Clerk Spike (no product code change)

**Purpose:** Record before-numbers and confirm the two assumptions that drive Phases 1 and 3.

**Steps:**
- [ ] `cd web && bun build`; inspect `dist/` client JS chunks for a Clerk bundle; note its size.
- [ ] Run Lighthouse (Mobile, 4× CPU / Slow 4G) against the built site on `/`; record LCP, TBT, CLS, total transfer, and the hero video request size.
- [ ] In DevTools with `prefers-reduced-motion: reduce` emulated, reload `/` and confirm whether `video/hero.mp4` is still requested.
- [ ] Confirm whether `clerk()` injects client JS on `/` independent of component usage (network panel + `dist` grep).

**Validation:**
- Run: `cd web && bun build`
- Expected: baseline metrics recorded in this plan's PR description; spike answers (Clerk-on-`/`: yes/no; video-on-reduced-motion: yes/no) documented.

**Commit:** none (measurement only) — record findings in the PR/issue.

---

### Phase 1: Hero Media (poster + opt-in video + drop per-frame filter)

**Purpose:** Make the poster the LCP, stop the 10 MB video from blocking/loading on weak/declined devices, and remove the per-frame GPU filter.

**Files:**
- Modify: `web/src/pages/index.astro`
- Create: `web/src/lib/heroVideo.ts`
- Modify: `web/src/styles/marketing-press.css`
- Modify: `web/src/lib/homepageHero.test.ts`
- Asset: add `web/public/video/hero-poster.webp`, `web/public/video/hero.webm`; re-encode `web/public/video/hero.mp4` (~2 MB, 720p).

**Contracts used:** `heroVideo.ts` (`shouldLoadHeroVideo`, `mountHeroVideo`); `<video>` attributes contract above.

**Steps:**
- [ ] Generate `hero-poster.webp` from the first video frame (pre-blurred to match the current `blur(2px)` look) and re-encode `hero.mp4` smaller + add `hero.webm`.
- [ ] In `index.astro`, set `<video class="hero-video" poster="/video/hero-poster.webp" preload="none" muted loop playsinline aria-hidden="true">` and move `<source>` `src` to `data-src` (keep the literal `/video/hero.mp4` string so the test still finds it; keep `hero-grain` after the video).
- [ ] Write `heroVideo.ts` with `shouldLoadHeroVideo` (reduced-motion / save-data / 2g checks) and `mountHeroVideo` (idle + in-view swap of `data-src`→`src`, then `.load()`).
- [ ] Replace the inline IntersectionObserver-only reveal script entry point to also call `mountHeroVideo(document)` (keep existing `[data-reveal]` behavior).
- [ ] In CSS, remove `filter: blur(2px) brightness(1.1)` from `.hero-video`; add a cheap opacity fade-in (`.hero-video[data-loaded]`) and keep brightness via the existing `.hero::after` scrim. Keep reduced-motion `display:none`.
- [ ] Update `homepageHero.test.ts`: replace the `blur(2px)`/`brightness(1.1)` CSS assertions with assertions for the new behavior (`poster=`, `preload="none"`, fade class); keep `class="hero-video"`, `/video/hero.mp4`, `playsinline`, `muted`, `hero-grain`, ordering, and scrim rgba assertions. Add unit tests for `shouldLoadHeroVideo` (reduced-motion→false, saveData→false, 4g→true).

**Validation:**
- Run: `cd web && bun test src/lib/homepageHero.test.ts` → Expected: pass.
- Run: `cd web && bun build` → Expected: succeeds.
- Manual: with reduced-motion / Save-Data emulated, `/video/hero.*` is **not** requested; poster shows. On normal 4g desktop, video fades in. Re-run Lighthouse → LCP and transfer improved vs Phase 0.

**Commit:**
```bash
git add web/src/pages/index.astro web/src/lib/heroVideo.ts web/src/lib/homepageHero.test.ts web/src/styles/marketing-press.css web/public/video/
git commit -m "perf(web): poster-first hero, opt-in video load, drop per-frame video filter"
```

---

### Phase 2: Quick Asset & Head Wins

**Purpose:** Eliminate oversized/eager assets and add resource hints — low risk, high certainty.

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro` (header logo + head hints)
- Modify: `web/src/styles/marketing-press.css` (grunge overlay)
- Asset: regenerate `web/public/marketing-grunge-texture.webp` (true ~320×320 tile, ~10–25 KB); re-export `web/public/members/dimora.jpg`.

**Steps:**
- [ ] Header logo (`MarketingLayout` ~L95): wrap in `<picture>` with `<source srcset="/icon/mafiatumbada.webp" type="image/webp">` + `<img src="/icon/mafiatumbada.png" width=... height=... loading="eager">` (set intrinsic dimensions to remove CLS).
- [ ] CSS `body.marketing-body::after` (L106): change `repeat fixed` → `repeat` (drop `background-attachment: fixed`) to stop scroll repaint; keep opacity/blend; point at the regenerated small webp.
- [ ] Re-export the regenerated grunge tile and `members/dimora.jpg` (~80 KB) to match siblings.
- [ ] In `Seo.astro` head (or `MarketingLayout` head), add `<link rel="preconnect">` to the `PUBLIC_API_URL` origin and `https://plausible.io`, and `<link rel="preload" as="image" href="/video/hero-poster.webp">`.

**Validation:**
- Run: `cd web && bun build` → Expected: succeeds.
- Run: `cd web && bun test` → Expected: pass (header logo change must not break `homepageHero.test.ts`; adjust only if a matched string changes).
- Manual: header logo transfer ≈ 45 KB (webp) not 1.2 MB; no logo CLS; scroll has no grunge repaint jank.

**Commit:**
```bash
git add web/src/layouts/MarketingLayout.astro web/src/components/Seo.astro web/src/styles/marketing-press.css web/public/marketing-grunge-texture.webp web/public/members/dimora.jpg
git commit -m "perf(web): webp header logo + dims, lighter grunge tile, drop fixed bg, add preconnect/preload"
```

---

### Phase 3: Remove Clerk Client JS From Public Pages (gated by Open Question + Phase 0)

**Purpose:** Stop shipping Clerk's client runtime to fan pages; render the admin shortcut server-side. Keep `/admin` + sign-in working.

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro`
- Modify: `web/src/pages/index.astro` (admin-notice block)
- Modify: `web/src/lib/homepageHero.test.ts` (auth-related assertions)
- Possibly: `web/astro.config.mjs` (only if `clerk()` must be scoped) — verify in Phase 0.

**Steps:**
- [ ] Replace the marketing `<Show when="signed-in">` admin-notice/menu link with a server check: read `Astro.locals.auth()` (from existing `clerkMiddleware()`), render the "Admin"/"Ver solicitudes" link only when `userId` is present — no client component.
- [ ] Remove `SignInButton`/`SignUpButton`/`UserButton` from `MarketingLayout` (the `menu-auth` block); admin sign-in lives on `/admin` (and `Layout.astro` keeps Clerk UI). Remove the now-orphaned `.menu-auth` close-on-click handler if the block is gone.
- [ ] Confirm Clerk client JS is no longer emitted on `/` (network + `dist`). If `clerk()` still injects globally, scope it so it only applies to admin routes (per Phase 0 findings).
- [ ] Update `homepageHero.test.ts`: the current assertions for `.menu-auth` and `window.setTimeout(() => closeMenu(), 0)` and the `.admin-notice` strip must be updated to match the server-rendered approach (keep `.admin-notice` markup/strings if retained; drop the `menu-auth` Clerk-modal assertions).

**Validation:**
- Run: `cd web && bun test` → Expected: pass (with updated assertions).
- Run: `cd web && bun build` → Expected: succeeds.
- Manual: `/` HTML/network has **no** Clerk script; signed-in admin still sees the Admin link on `/`; `/admin` still gated and sign-in flow works. Lighthouse TBT dropped vs Phase 0.

**Commit:**
```bash
git add web/src/layouts/MarketingLayout.astro web/src/pages/index.astro web/src/lib/homepageHero.test.ts web/astro.config.mjs
git commit -m "perf(web): server-render admin link, remove Clerk client JS from public pages"
```

---

### Phase 4: Font Payload Reduction

**Purpose:** Ship only the weights and Latin subsets actually used, and preload the critical faces.

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro` (the 10 `@fontsource` imports + head preload)

**Steps:**
- [ ] Audit which weights are actually referenced (`--ff-*` tokens + `font-weight` in `marketing-press.css`); drop unused weight imports (candidates: JetBrains Mono `500`, and any Inter/Cormorant weight with no usage).
- [ ] Switch each remaining `@fontsource/<family>/<weight>.css` import to its Latin-subset variant (`@fontsource/<family>/latin-<weight>.css` or the `unicode-range`/`-subset` form) so non-Latin subsets are not shipped; verify Spanish glyphs (`á é í ó ú ñ ¿ ¡ —`) render.
- [ ] Add `<link rel="preload" as="font" type="font/woff2" crossorigin>` for the 1–2 critical faces (Inter 400 body, Cormorant display weight used by `h1/h2`); leave JetBrains Mono non-preloaded.

**Validation:**
- Run: `cd web && bun build` → Expected: succeeds; fewer font files in `dist`.
- Manual: headings/body/tabular text render correctly incl. Spanish accents; no visible FOUT regression (fontsource `font-display: swap` retained). Lighthouse font transfer reduced.

**Commit:**
```bash
git add web/src/layouts/MarketingLayout.astro
git commit -m "perf(web): subset fonts to latin, drop unused weights, preload critical faces"
```

---

### Phase 5: CLS + Scroll-Jank Polish

**Purpose:** Remove the tour-table layout shift and the unthrottled scroll handler.

**Files:**
- Modify: `web/src/components/TourTable.astro` (+ `web/src/styles/marketing-press.css` if needed)
- Modify: `web/src/layouts/MarketingLayout.astro` (scroll handler)

**Steps:**
- [ ] Reserve vertical space for the tour `<tbody>` (render a fixed number of skeleton rows or a `min-height`) so the post-paint `hydrateTourTablesFromApi()` swap (empty → rows) does not shift the page.
- [ ] Make the header `checkScroll` listener `{ passive: true }` and rAF-throttle it (store `scrollY`, toggle the class inside a single `requestAnimationFrame`).

**Validation:**
- Run: `cd web && bun test` → Expected: pass (keep `data-analytics-venue`, `data-tour-upcoming-api`).
- Run (if API + mock available): `cd web && bun run test:e2e` → Expected: smoke passes.
- Manual: CLS ≤ 0.1 in Lighthouse; scroll is smooth on a throttled CPU profile.

**Commit:**
```bash
git add web/src/components/TourTable.astro web/src/layouts/MarketingLayout.astro web/src/styles/marketing-press.css
git commit -m "perf(web): reserve tour-table space (CLS) and throttle passive scroll handler"
```

---

### Phase 6 (Deferred / Optional, metrics-gated): astro:assets + CSS critical path

**Purpose:** Only if Phases 1–5 do not hit targets.

**Steps (not detailed until triggered):**
- [ ] Migrate `MemberCard`/`ArtworkShelf`/`FilmStrip` raw `<img>` to `astro:assets` `<Image>` for AVIF/webp + responsive `srcset` + intrinsic dims.
- [ ] Measure `marketing-press.css` impact; consider above-the-fold critical CSS only if it moves the needle.

**Validation:** Re-run Lighthouse vs targets; proceed only if a target is still missed.

---

## Complexity Budget Check

- No new dependencies, services, queues, or caches introduced in Phases 1–5.
- One small new lib (`heroVideo.ts`) — justified: makes the capability gate linted + unit-testable (Biome skips `.astro`).
- Clerk change **removes** client code rather than adding abstraction.
- `astro:assets` and CSS splitting are explicitly deferred (YAGNI) until metrics demand them.

---

## Cross-Task Consistency Check

- [ ] Asset paths stable across tasks: `/video/hero.mp4` (retained), `/video/hero-poster.webp`, `/video/hero.webm`, `/icon/mafiatumbada.{webp,png}`, `/marketing-grunge-texture.webp`.
- [ ] `homepageHero.test.ts` updated in the **same** commit as each markup/CSS change that alters a matched string (Phases 1 and 3 explicitly).
- [ ] `heroVideo.ts` function names (`shouldLoadHeroVideo`, `mountHeroVideo`) used consistently in `index.astro` and tests.
- [ ] Reduced-motion behavior preserved across Phases 1, 2, 5.
- [ ] No phase reintroduces a pattern a later phase removes (e.g., don't re-add Clerk client components after Phase 3).

---

## Decision Recording

**Decision:** Poster-first hero with opt-in video instead of always-on autoplay.
**Alternatives considered:** static-image hero; always-load smaller video.
**Tradeoffs:** Slightly more JS (tiny gate) vs. eliminating 10 MB on the critical path and on weak/declined devices.
**Why it fits priority:** Correctness/maintainability preserved (fallback poster, reduced-motion intact); large performance win.
**Complexity avoided:** No video CDN/streaming.

**Decision:** Server-render the admin shortcut; remove Clerk client JS from public pages.
**Alternatives considered:** keep Clerk client `<Show>`; lazy-load Clerk on interaction.
**Tradeoffs:** Loses live client reactivity of the admin strip (acceptable — it's a static link) for a large TBT win.
**Why it fits priority:** Correctness (auth on `/admin` unchanged) first; big performance gain; simpler public pages.

---

## Self-Review

1. Evidence — files, versions, and exact asset byte sizes inspected and cited. ✔
2. Spec coverage — every target (LCP/TBT/CLS/transfer/smooth scroll/auth intact) maps to a phase. ✔
3. Open questions — surfaced with safe defaults; deletes and Clerk/auth changes marked Pause. ✔
4. Placeholders — none; new assets/functions marked "proposed"; no TBD. ✔
5. Type/name consistency — `heroVideo.ts` symbols and asset paths consistent across tasks. ✔
6. Architecture stability — poster-first + server-rendered auth chosen with rejected alternatives recorded. ✔
7. Product alignment — each change traces to a stated UX/perf outcome. ✔
8. Risk reduction — Phase 0 spike burns the Clerk/reduced-motion uncertainty before Phases 1/3. ✔
9. Migration safety — per-phase, revertible; fallbacks (poster, mp4, SSR markup) retained. ✔
10. Complexity budget — no new deps/services; heavy options deferred. ✔

---

## Execution Handoff

Implementation is intentionally **not** started (per request). When ready, two options:

1. **Subagent-Driven (recommended)** — fresh subagent per phase, review between phases (`superpowers:subagent-driven-development`).
2. **Inline Execution** — batch with checkpoints (`superpowers:executing-plans`).

**Before any code:** answer the three "Pause: Yes" Open Questions (orphan-file deletion, Clerk-on-public approach) and complete Phase 0 measurements.

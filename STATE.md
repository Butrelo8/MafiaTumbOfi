# Project State

## Current Position
- **Branch:** `feat/desegin-consultation-redo`
- **Phase:** Veracruz Noir / design-consultation marketing pass — **DESIGN.md** as source of truth; OKLCH tokens, Inter + Cormorant + JetBrains Mono; homepage asymmetric hero with **full-bleed background video** (grain + scrims + copy layered on top); **Marquee**, **TourTable** (`upcomingTourDates` from **`web/src/data/tourDates.ts`** — static data, CMS/API later), **ArtworkShelf**, **FilmStrip**, **SignatureCTA**; canonical booking **`/contratacion`** with **`/booking`** → redirect; thank-you stays **`/booking/gracias`**; sitemap + unit tests + Playwright e2e paths updated.
- **Recently shipped (code, uncommitted):** **Fullscreen mobile menu** — **`web/src/layouts/MarketingLayout.astro`**: overlay dialog, numbered **`ol.menu-nav`**, meta column (socials, CTA, Clerk), **`button.menu-close-btn#menu-close-btn`** (Escape + link click close). **`marketing-press.css`**: hamburger morph, grain, grid, stagger; **primary nav hovers** use **`translateY(-2px)`** + **gold gradient** underline on **`.menu-label::after`** (not **`--accent`**); **`.menu-link:link` / `:visited` / `:hover` / `:focus-visible`** pinned to **`var(--text)`** so mains don’t read turquoise; social row stays gold-border + text. **FilmStrip** + token pass as before.
- **Last completed:** Fullscreen menu redesign (plan **`docs/superpowers/plans/2026-04-22-fullscreen-menu-redesign.md`**) + nav hover color alignment (gold underline, explicit link colors).
- **Next up:** **`git status`** / commit scoped chunks; optional breakpoint + **`prefers-reduced-motion`** QA from plan; replace **`web/public/band/*.jpg`** and **`web/public/members/*.jpg`** when final assets arrive; re-run **`bun test`** + **`cd web && bun run build`** before PR.
- **Tests:** Last verified **2026-04-22:** **`cd web && bun run build`**, targeted **`bun test`** (**`homepageHero`**, **`adminPageTheme`**) green; re-run full **`bun test`** at repo root after more edits.
- **Working tree:** Large diff — many modified + untracked (tours API, `DESIGN.md`, marketing components, admin, Plausible, etc.). Review **`git status`** before committing; scope PR intentionally.

## Accumulated Decisions
- **2026-04-22 (fullscreen menu nav):** Inside **`.mobile-menu`**, primary **`.menu-link`** hovers use **motion + gold underline** only; **do not** use **`--accent`** for large nav type or underline — keeps Veracruz Noir hierarchy; socials use gold-border hover + **`--text`**.
- **2026-04-22 (marketing-press :root):** **`marketing-press.css`** defines the same OKLCH marketing tokens as **`DESIGN.md`** (surfaces, gold 4-stop, burgundy glow + hot, border, focus ring, semantic colors). **CTA surfaces** use **`--gold-gradient`** / gold vars; **`.tour-ticket-btn`** matches primary button treatment; **turquoise (`--accent`)** for links and focus, not primary ticket/CTA chrome.
- **2026-04-22 (marketing tokens):** Shared **`<Eyebrow />`** styling (**.eyebrow**) uses **`var(--gold)`** for uppercase section labels so they stay on Veracruz Noir; reserve **`var(--accent)`** for links/controls where turquoise is intentional — do not revert eyebrows to accent without a scoped modifier class.
- **2026-04-21 (marketing assets):** Member **`image`** URLs are **local** under **`web/public/members/`** only (no **`ui-avatars`** at runtime). ArtworkShelf singles use optional **`cover`** + CDN URLs in **`index.astro`** (Spotify / Apple); initials fallback if omitted.
- **2026-04-20 (analytics):** Plausible is **opt-in** via **`PUBLIC_PLAUSIBLE_DOMAIN`**; client events use **`trackPlausible`** / layout inline handlers; operator confirms events in Plausible dashboard after deploy.
- **2026-04-18 (design):** Hero video is **section background** (not a right column); **`DESIGN.md`** layout + Hero component bullets updated to match full-bleed + layered copy.
- **2026-04-18:** **`bookingCanonical`** → **`/contratacion`**; legacy **`/booking`** redirects; form still **`POST /api/booking`**; **`BookingForm.astro`** holds `/api/booking` string (tests read that file, not `contratacion.astro`).
- **2026-04-18:** Press kit visibility — **`showPressAssetsSection`** in **`web/src/lib/showPressAssets.ts`** (homepage `#press`, hero CTA, nav).
- **2026-04-11 / prior:** Admin CRM, Drizzle `internal_notes` / `deleted_at`, Turso, Clerk — see **`DECISIONS.md`** / git history as needed.

## Blockers & Open Questions
- **Commit scope:** One feature branch has many files — split commits or one cohesive “marketing redesign” PR per team preference.
- **Ship gate:** DB migrations / deploy per **`DEPLOY.md`** if touching API; prod parity not assumed until merged.
- **E2E:** Run **`cd web && bunx playwright test`** when dev server available if you need full confidence beyond unit tests.

## Session Notes
- **Saved:** **2026-04-22** — **save state** after **fullscreen menu** (**`MarketingLayout.astro`** + **`marketing-press.css`**) and **nav hover fix** (gold underline, **`.menu-link`** explicit **`var(--text)`** so numbered mains aren’t turquoise; close button + script). Working tree still large (**`git status`**). Next: commits / PR scope, full **`bun test`**, optional E2E, asset swaps.
- **Saved:** **2026-04-22** — **save state** after **FilmStrip** (**`web/public/band/`**, imgs + **`.film-strip-img`**) and **DESIGN.md** **`marketing-press.css`** token + CTA pass (replaces earlier same-day save: eyebrow → gold, FilmStrip plan pending). Next: **fullscreen menu** plan **`docs/superpowers/plans/2026-04-22-fullscreen-menu-redesign.md`**, commits, asset swaps.
- **Saved:** **2026-04-21** — **save state** after **ArtworkShelf CD covers** + **member local photos** (placeholders) + **TODOS** / **`CHANGELOG`** / **`DESIGN`** / spec doc updates; **`git status`** still large (many **`??`** marketing + tours + `DESIGN.md`).
- **Saved:** 2026-04-20 — Plausible funnel tracking + TODOS completion + regression tests; prior **2026-04-18** Veracruz Noir / hero video / `tourDates.ts`.
- **Stopped at:** State file updated; working tree unchanged by this save.
- **Resume with:** **`bun test`** (repo root) → **`cd web && bun run build`** → **`git status`** / **`git diff --stat`** → commit scoped chunks or one marketing PR → optional **`cd web && bunx playwright test`** → replace **`web/public/band/*.jpg`** / **`web/public/members/*.jpg`** when assets ready → menu plan QA (keyboard, breakpoints, reduced motion).
- Optional: **`/context-restore`** (gstack) or reread this file next session.

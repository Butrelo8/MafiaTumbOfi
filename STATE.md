# Project State

## Current Position
- **Branch:** `main` (Recent critical security fixes)
- **Phase:** Security Hardening & Astro v6 Migration — Fixed GHSA-j687-52p2-xcff (Astro XSS) and Rate Limit IP spoofing.
- **Recently shipped (code):** 
  - **Astro v6 Upgrade:** Migrated from Astro 4.16.19 to 6.1.9; updated `@astrojs/vercel` (import path fix) and `@astrojs/node` adapters.
  - **XSS Fix (Astro/GHSA-j687-52p2-xcff):** Removed unused `define:vars` from `MarketingLayout.astro`.
  - **XSS Fix (Stored):** Created `safeJsonForScript` helper to escape `<`, `>`, and `&` in JSON script tags; applied to `admin.astro` to prevent admin session hijacking.
  - **Dependency Upgrade:** Bumped `drizzle-orm` to `v0.45.2` to fix SQL injection vulnerability (GHSA-gpj5-g38j-94v9).
- **Last completed:** drizzle-orm security upgrade (2026-04-28).
- **Next up:** SEO improvements (OG image) or continuing with the design consultation redo PR.
- **Tests:** Last verified **2026-04-28:** `cd web && bun run build` passed cleanly with Astro v6. `bun test` in API root also passing.
- **Working tree:** Mostly clean after commits.

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
- **Saved:** **2026-04-28** — **drizzle-orm upgrade** to `v0.45.2` completed. Fixes GHSA-gpj5-g38j-94v9.
- **Saved:** **2026-04-28** — **Stored XSS Fix** in `admin.astro` completed.
- **Saved:** **2026-04-28** — **Astro v6 Upgrade** completed.
- **Saved:** **2026-04-27** — **Rate Limit Fix** shipped. Prevents IP spoofing on Render proxy. Added `Retry-After`.
- **Saved:** **2026-04-22** — **save state** after **fullscreen menu** redesign.
- **Resume with:** SEO — Create OG image at 1200×630 + add dimension meta (TODOS P1).

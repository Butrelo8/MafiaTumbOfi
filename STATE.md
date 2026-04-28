# Project State

## Current Position
- **Branch:** `main`
- **Phase:** QA/SEO/Perf pass complete — security hardening done; image optimization, form UX, and OG card all shipped.
- **Recently shipped (code):**
  - **OG Social Card:** `web/public/og/og-default.jpg` 1200×630; `Seo.astro` now emits `og:image:width/height/type` meta tags (bb12da2).
  - **WebP Image Optimization:** `marketing-grunge-texture.png` (4.5 MB) + `mafiatumbada.png` (1.2 MB) → WebP; logo resized to display dimensions (5492f6e).
  - **Album Art (local):** 6 cover images downloaded, hosted at `web/public/music/`; Spotify/Apple CDN URLs removed from `index.astro` (92a0ee5).
  - **Form Validation:** Client-side name+email guard before `fetch()`; per-field error `<span>` with `aria-describedby` on each required input (0ec3925).
  - **Security (prior):** drizzle-orm 0.45.2 (GHSA-gpj5-g38j-94v9), stored XSS in `admin.astro`, Astro v6 (GHSA-j687-52p2-xcff), rate-limit IP-spoofing fix.
- **Last completed:** form client-side validation + per-field errors (2026-04-28).
- **Next up:** Design — change band icon/logo (TODOS open). Design — Confianza/Testimonios real content. Mobile QA on Android mid-range.
- **Tests:** Last verified **2026-04-28:** `cd web && bun run build` green. `bun test` passing.
- **Working tree:** Unstaged changes in `src/middleware/` (rate limit refactor in progress); untracked `web/.astro/` generated files.

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
- **Saved:** **2026-04-28** — **OG card** (1200×630), **WebP images**, **local album art**, **form validation + per-field errors** all shipped.
- **Saved:** **2026-04-28** — **drizzle-orm upgrade** to `v0.45.2` completed. Fixes GHSA-gpj5-g38j-94v9.
- **Saved:** **2026-04-28** — **Stored XSS Fix** in `admin.astro` completed.
- **Saved:** **2026-04-28** — **Astro v6 Upgrade** completed.
- **Saved:** **2026-04-27** — **Rate Limit Fix** shipped. Prevents IP spoofing on Render proxy. Added `Retry-After`.
- **Saved:** **2026-04-22** — **save state** after **fullscreen menu** redesign.
- **Resume with:** Design — change band icon/logo or Confianza/Testimonios real content (next open TODOS).

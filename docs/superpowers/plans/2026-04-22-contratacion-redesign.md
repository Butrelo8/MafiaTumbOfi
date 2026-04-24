# `/contratacion` Veracruz Noir Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate `/contratacion` to match the updated Veracruz Noir premium palette — add a full-bleed band photo hero behind the Press Kit header, fix social link colors to comply with new turquoise-demoted rules, and deepen the surface feel to match `DESIGN.md`.

**Architecture:** All changes confined to `web/src/pages/contratacion.astro` scoped `<style>` block. No new components, no new global CSS. Band photo referenced as CSS `background-image` on `.press-cover` so it degrades gracefully to `--bg-sunk` when file is absent. Scrim overlay is a CSS `::before` pseudo-element on `.press-cover`. Global tokens (`--bg`, `--bg-sunk`, `--gold-gradient`, `--burgundy-glow`) are already updated in `web/src/styles/marketing-press.css` — only scoped page styles need updating.

**Tech Stack:** Astro 4 (existing), vanilla CSS scoped `<style>` block, band photo at `web/public/band/cover.jpg` (provided by band manager; fallback is solid `--bg-sunk`).

**Context — already correct, no changes needed:**
- `--bg: oklch(8%)`, `--bg-sunk: oklch(5%)`, `--gold-gradient`, `--burgundy-glow` already in `marketing-press.css` ✅
- `.btn-primary` already uses `var(--gold-gradient)` + burgundy glow on hover ✅
- `.btn-secondary` (WhatsApp CTA) already styled correctly ✅
- `.press-cover` already has `position: relative`, grain overlay, `var(--bg-sunk)` background ✅

**What needs fixing:**
- `.press-cover`: taller `min-height` + `background-image` photo + `::before` scrim
- `.press-social-row a`: default `var(--accent)` turquoise → `var(--text-muted)`; turquoise moves to hover/focus only

---

## File Structure

**Modified files:**
- `web/src/pages/contratacion.astro:187-196` — `.press-cover` rule: add photo bg + taller height
- `web/src/pages/contratacion.astro` — add `.press-cover::before` scrim rule (new)
- `web/src/pages/contratacion.astro:260-267` — `.press-social-row a` + `:hover` rules: swap colors

**Photo asset (operator task):**
- `web/public/band/cover.jpg` — drop real band photo here. CSS `background-image` degrades to `--bg-sunk` if absent; no build error, no broken layout.

**No new files. No global CSS changes.**

---

## Task 1: Deepen `.press-cover` and add photo background

**Files:**
- Modify: `web/src/pages/contratacion.astro` — `.press-cover` rule + add `.press-cover::before`

- [ ] **Step 1: Replace `.press-cover` rule**

In `web/src/pages/contratacion.astro`, inside `<style>`, find `.press-cover` (currently around line 187) and replace the entire rule:

```css
.press-cover {
  position: relative;
  min-height: min(65vh, 600px);
  display: flex;
  align-items: flex-end;
  padding-block: var(--space-lg);
  background-color: var(--bg-sunk);
  background-image: url('/band/cover.jpg');
  background-size: cover;
  background-position: center 30%;
  border-bottom: 1px solid var(--border);
  overflow: hidden;
}
```

Notes:
- `background-color: var(--bg-sunk)` stays as fallback — if `cover.jpg` missing, solid near-void black, no layout break.
- `background-position: center 30%` favors upper portion of photo (faces visible, not feet).
- `min-height` increased from `min(42vh, 420px)` → `min(65vh, 600px)` for hero-level presence.

- [ ] **Step 2: Add `.press-cover::before` scrim immediately after `.press-cover` rule**

```css
.press-cover::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(
    to bottom,
    oklch(5% 0 0 / 0.55) 0%,
    oklch(5% 0 0 / 0.75) 55%,
    oklch(5% 0 0 / 0.96) 100%
  );
  pointer-events: none;
}
```

Notes:
- `z-index: 0` — sits above photo, below `.press-cover-grain` (no z-index, stacks after in DOM) and below `.press-cover-inner` (`z-index: 1`). Text stays on top. ✅
- Gradient fades to near-opaque at bottom where `align-items: flex-end` places the text — full legibility.

- [ ] **Step 3: Verify dev server**

Run: `cd web && bun dev`
Open `http://localhost:4321/contratacion`.

With `web/public/band/cover.jpg` present: photo fills header section; scrim darkens toward bottom; "Mafia Tumbada" + lede legible.
Without photo: solid `--bg-sunk` near-void black — no broken icon, no layout shift, text legible.

- [ ] **Step 4: Commit**

```bash
git add web/src/pages/contratacion.astro
git commit -m "feat(contratacion): full-bleed photo hero with gradient scrim on press-cover"
```

---

## Task 2: Fix `.press-social-row a` turquoise violation

**Files:**
- Modify: `web/src/pages/contratacion.astro` — `.press-social-row a` + `.press-social-row a:hover` rules

Current violation — turquoise as default link color:
```css
/* BEFORE — violates DESIGN.md: turquoise is hover-only */
.press-social-row a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.press-social-row a:hover {
  color: var(--gold);
}
```

- [ ] **Step 1: Replace `.press-social-row a` rule**

```css
.press-social-row a {
  color: var(--text-muted);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  padding-bottom: 2px;
  transition: color 200ms ease, border-color 200ms ease;
}
```

- [ ] **Step 2: Replace `.press-social-row a:hover` rule**

```css
.press-social-row a:hover,
.press-social-row a:focus-visible {
  color: var(--accent);
  border-color: var(--accent);
}
```

Turquoise now appears only on hover/focus — compliant with `DESIGN.md`.

- [ ] **Step 3: Verify**

In dev at `http://localhost:4321/contratacion`, scroll to "Escucha" social row (Spotify · Apple Music · YouTube). Confirm:
- Default: muted gray text, no underline
- Hover: turquoise text + turquoise underline border reveals
- Tab to each link: same turquoise focus state visible (gold focus-ring from `.press-social-row a:focus-visible` — no hidden focus)

- [ ] **Step 4: Commit**

```bash
git add web/src/pages/contratacion.astro
git commit -m "fix(contratacion): turquoise on social links hover/focus only per DESIGN.md"
```

---

## Task 3: Cross-breakpoint visual verification + build

**Files:** none modified — verification only.

- [ ] **Step 1: Check at 320 / 375 / 768 / 1024 / 1440**

In Chrome devtools device toolbar at `http://localhost:4321/contratacion`:

- 320 / 375: `.press-cover` fills top of viewport. "Mafia Tumbada" heading readable. No horizontal overflow. Photo (if present) fills without skew — `background-size: cover` handles it.
- 768: `.booking-layout` may still be stacked — verify no layout shift from taller `.press-cover`. No overflow.
- 1024 / 1440: Two-column layout visible. Press Kit cover takes ~60% viewport height. Scrim opaque enough that heading/lede pass contrast.

- [ ] **Step 2: Contrast audit with photo**

If `cover.jpg` is present: open axe DevTools extension on `/contratacion`. Confirm `.press-cover-title` (warm white `--text`) over scrim at `oklch(5% 0 0 / 0.96)` passes WCAG AA. Scrim bottom at 96% opacity over any photo is effectively near-black — passes trivially.

- [ ] **Step 3: Scan for stale `--accent-hot` references**

Run: `grep -n "accent-hot" web/src/pages/contratacion.astro`
Expected: no matches. If any found, replace with `var(--burgundy-hot)`.

- [ ] **Step 4: Run build**

Run: `cd web && bun run build`
Expected: exits 0. `url('/band/cover.jpg')` in CSS does not cause a build error when file is absent — Astro/Vite does not statically resolve CSS background-image URLs.

- [ ] **Step 5: Run tests**

Run: `bun test` (from repo root)
Expected: all pass. No test covers `.press-cover` styling — purely visual change.

- [ ] **Step 6: Commit if any fixes applied**

```bash
git add web/src/pages/contratacion.astro
git commit -m "fix(contratacion): responsive polish after visual verification"
```

If nothing to fix: skip.

---

## Task 4: Drop band photo (operator task)

**Files:**
- Add: `web/public/band/cover.jpg`

- [ ] **Step 1: Obtain photo from band manager**

Requirements:
- Landscape orientation, min 1400 × 900px
- Format: JPG, ≤400KB compressed (use Squoosh or ImageOptim)
- Composition: band members in upper half; sky/dark background in lower half preferred — gradient scrim fades from top (lighter) to bottom (near-opaque), so upper region shows most photo detail

- [ ] **Step 2: Save to correct path**

Save file to: `web/public/band/cover.jpg`

This exact path matches `url('/band/cover.jpg')` in the CSS. No code change needed.

- [ ] **Step 3: Verify in dev**

Run: `cd web && bun dev`
Open `http://localhost:4321/contratacion`. Confirm:
- Photo fills `.press-cover` section
- "Press kit" gold eyebrow visible
- "Mafia Tumbada" heading legible
- Lede "Corridos tumbados y regional mexicano · Xalapa, Veracruz · Desde 2021" legible at all breakpoints

- [ ] **Step 4: Run final build**

Run: `cd web && bun run build`
Expected: exits 0. Confirm `web/dist/band/cover.jpg` present in build output.

- [ ] **Step 5: Commit photo**

```bash
git add web/public/band/cover.jpg
git commit -m "assets(contratacion): band cover photo for press hero"
```

---

## Self-review notes

**Spec coverage:**
- Deeper matte-black surfaces ✅ — tokens already in CSS; page uses `var(--bg-sunk)` (`oklch(5%)`)
- Full-bleed photo hero behind Press Kit header ✅ — Task 1
- Gradient scrim for legibility ✅ — Task 1 `::before`
- Film grain ✅ — `.press-cover-grain` already in markup, untouched
- Metallic gold gradient on primary CTA ✅ — `.btn-primary` already uses `var(--gold-gradient)` in global CSS
- Burgundy cinematic glow on CTA hover ✅ — `.btn-primary:hover` already has `box-shadow` with `var(--burgundy-glow)` in global CSS
- Turquoise demoted to hover-only ✅ — Task 2
- Build green ✅ — Task 3 Step 4

**Placeholder scan:** None found.

**Selector consistency:** `.press-cover`, `.press-cover::before`, `.press-social-row a` used identically in markup inspection and all plan steps.

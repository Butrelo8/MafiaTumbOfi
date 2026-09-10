# Gótico Tumbado Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Veracruz Noir visual system with Gótico Tumbado (black + gold gothic + red neon) across the single marketing page, swapping the header logo image for an M⚡T monogram and keeping the logo as the hero `<h1>` over the existing hero video.

**Tech Stack:** Astro 6, Tailwind 3 (base/components/utilities only), plain CSS custom properties in `src/styles/marketing-press.css`, `@fontsource/*` self-hosted fonts, Cloudflare Workers Static Assets.

## Evidence Gathering

**Files inspected:**
- `src/styles/marketing-press.css` (1946 lines): holds the entire `:root` token block and every marketing selector. Token call-site counts: `--gold` 60, `--ff-display` 17, `--gold-dim` 13, `--ff-body` 8, `--gold-mid` 5, `--burgundy-glow` 4, `--gold-shadow` 4, `--text-faint` 3, `--accent` 2, `--burgundy-hot` 2.
- `src/layouts/MarketingLayout.astro`: owns `<header class="site-header">` with `.header-logo` → `<img class="header-logo-img" src="/icon/mafiatumbada.webp" width="200" height="60">`. Also owns the fullscreen `#mobile-menu`, the scroll listener that toggles `.is-scrolled`, and all `@fontsource` imports.
- `src/pages/index.astro`: hero is inline (not a component); `<h1 class="hero-title">` already wraps `<img class="hero-logo-img">`. Hero video is `<video class="hero-video">` with `<source data-src="/video/hero.mp4">`. Page-scoped `<style>` sets `.video-row span, .music-link, .booking-copy a:not(.btn-primary), .footer-socials a { color: var(--accent) }`.
- `src/lib/heroVideo.ts` is imported and called as `mountHeroVideo(document)` — the `data-src` → `src` promotion already exists.
- `src/components/Eyebrow.astro`: renders `<p class="eyebrow">`. `src/components/Marquee.astro`: renders `.marquee-wrap > .marquee-track > .marquee-text ×2`.
- `package.json`: deps are `@fontsource/cormorant-garamond`, `@fontsource/inter`, `@fontsource/jetbrains-mono`, `astro`. No CSS framework beyond Tailwind's base layer.
- `src/lib/catalog.test.ts`, `plausibleClient.test.ts`, `publicSiteUrl.test.ts` — 21 tests, all logic-level. **None assert styling.**
- `e2e/` exists but is **empty**. There is no Playwright config and no axe-core dependency.

**Existing patterns found:**
- Design tokens are plain custom properties on `:root` in one file; components consume them via `var()`. There is no Tailwind theme mapping for these tokens.
- The header logo and hero logo both use `mix-blend-mode: screen` plus layered `drop-shadow()` in raw `rgba()`, not tokens, plus a `logo-shimmer-*` keyframe animation.
- Selectors are flat and BEM-ish (`.hero-eyebrow`, `.header-socials a`); no nesting, no CSS modules.

**Runtime/framework versions verified:**
- Astro `^6.1.9`, Tailwind `^3.4.0`, Bun as runner (`bun run build`, `bun test`).
- `@fontsource/grenze-gotisch@5.3.0` and `@fontsource/archivo@5.3.0` both exist on npm and both ship `latin-{100..900}.css` and `latin-ext-*.css`. Verified against the unpkg file manifest.

**Existing abstractions to extend:**
- The `:root` token block: extend by redefining values under the **same names** wherever possible, so the 60 `--gold` call sites and 17 `--ff-display` call sites need no edits.
- `<Eyebrow>`: already the single owner of eyebrow markup, so the red rule can be added in one place.

**Similar functionality already present:**
- `.hero-logo-img` already implements exactly the treatment the new hero needs (screen blend + gold/red drop-shadows). Reuse it; do not write a second one.
- `.site-header.is-scrolled` already provides the blur-on-scroll behaviour the spec calls for. Reuse it.

## Product Intent

**User-facing outcome:** The site reads as a corridos tumbados act at a glance — black, gold gothic lettering, red neon accents — instead of an editorial serif page, while the band's actual logo still leads the hero over the live video.

**Expected UX behavior:**
- [ ] Header shows an M⚡T gold gothic monogram; no logo image in the header
- [ ] Hero shows the existing logo image over the looping hero video, unchanged in behaviour
- [ ] Section headings, release titles and the monogram render in blackletter
- [ ] Body copy, buttons and nav remain in a plain sans and stay fully legible
- [ ] Every eyebrow is preceded by a short red rule
- [ ] The marquee strip is red, not burgundy

**Performance expectations:** No LCP regression. The hero video must keep its `data-src` deferral. Font payload must not grow: two families are removed as two are added, and only the weights actually used are imported.

**Accessibility expectations:** Every text token holds WCAG AA against `--bg` (measured table in `DESIGN.md`). The M⚡T monogram carries an accessible name. Blackletter never carries body copy, labels or form fields. Touch targets stay ≥44px.

**Localization/i18n needs:** Spanish-first. Both new faces must render `á é í ó ú ñ ü ¿ ¡`. The `latin` subset covers these; `latin-ext` is not required for Spanish.

**Visual consistency requirements:** `DESIGN.md` is the contract. Any divergence updates the file in the same commit.

## Open Questions

- **Question:** `DESIGN.md` as written drops `--gold-dim`, but the stylesheet uses it 13 times for hairline dividers.
  **Why it matters:** Removing the token forces 13 unrelated edits into a restyle commit and risks visual drift in sections nobody is reviewing.
  **Safest default:** Keep `--gold-dim` as a real token and add it back to `DESIGN.md`. Do not migrate the 13 call sites.
  **Pause for clarification?** No — reversible, and the alternative is gratuitous churn.

- **Question:** `DESIGN.md` §Verification requires "Playwright + axe-core — zero serious violations", but `e2e/` is empty and neither dependency is installed.
  **Why it matters:** The spec mandates a gate that cannot run, so either the gate is aspirational or this plan must stand up the harness.
  **Safest default:** Treat it as out of scope for this plan and verify accessibility manually against the listed criteria. Flag the gap rather than silently skipping it.
  **Pause for clarification?** No — but it is called out in System Boundaries as deferred.

- **Question:** Does `--ff-display` appear on any small or body-adjacent text among its 17 call sites?
  **Why it matters:** Blackletter below 24px is illegible; a blind value swap could ruin a caption.
  **Safest default:** Task 3 audits all 17 sites before the swap lands and reassigns any under 24px to `--ff-body`.
  **Pause for clarification?** No — the audit is a plan step.

## Decision Priority

1. Correctness
2. Maintainability
3. Simplicity
4. Operability
5. Performance
6. Developer convenience

Spec-specific refinement: **accessibility is treated as correctness**, not as a later polish pass. A contrast or legibility regression fails the task.

## Architecture First

**Runtime model:** Build-time static generation. Astro renders one `index.html`; Cloudflare Workers Static Assets serves `dist/`. All styling is a single stylesheet plus one page-scoped `<style>` block. No runtime theming, no CSS-in-JS, no design-token build step.

**Rendering strategy:** SSG. The only client JS is the menu toggle, the scroll listener, the reveal observer, Plausible, and the hero video mount. None of it touches the token layer.

**Failure handling approach:**
- Gold gradient text uses `background-clip: text`. Where unsupported, or where a user forces colors, the fill would be transparent. Every `.goldtext` rule therefore declares a solid `color` **before** the transparent fill so the fallback cascade produces visible text.
- The logo images rely on `mix-blend-mode: screen`, which needs dark pixels beneath. The hero's first scrim guarantees this; the header no longer carries an image at all, removing that dependency.
- Fonts are self-hosted via `@fontsource`, so there is no third-party font host to fail. `font-display` defaults to `swap`; the fallback stack must be metrically reasonable.

**Why this architecture was chosen:** The existing system already centralises every visual decision in one `:root` block. Redefining values under existing names converts what looks like a 90-file restyle into a token edit plus four targeted component changes. This is the smallest change that delivers the whole direction.

**Alternatives rejected:**
- *Map tokens into `tailwind.config.js` theme and restyle with utilities*: rejected. The project uses Tailwind only for its base reset; adopting utilities now means rewriting markup that is not otherwise changing.
- *Rename tokens to match the new direction (`--accent` → `--red-link` everywhere, etc.)*: rejected for `--gold*`, accepted only for `--accent` and `--burgundy-*`, which have 8 call sites between them. Renaming `--gold` would touch 60 sites for zero user-visible benefit.
- *New stylesheet alongside the old one, switched by a body class*: rejected. There is one page and one direction; a dual system is complexity with no consumer.

**Complexity intentionally avoided:**
- No design-token pipeline (Style Dictionary and similar). One `:root` block is the right size for one page.
- No `<Monogram>` component. The mark appears in exactly one place.
- No theme switcher. The site is dark-only by design.

## Operational Constraints

- **Runtime:** Cloudflare Workers Static Assets, config in `wrangler.jsonc`. Deploy via `npx wrangler deploy`.
- **Build:** `bun run build`. The build fetches Spotify (credential-gated) and the YouTube feed; both fall back to `src/data/catalog.json` on failure. Restyle work must not touch that path.
- **Performance-sensitive path:** the hero. LCP is the hero logo image. The video must keep `preload="none"` and `data-src`; the logo keeps `fetchpriority="high"` and `loading="eager"`.
- **Font payload:** currently 4 Cormorant + 4 Inter + 2 JetBrains Mono = 10 weight files. Target: 3 Grenze Gotisch + 4 Archivo + 2 JetBrains Mono = 9. Net reduction.
- **No env or secret changes.** No new runtime dependencies — both new packages are build-time font assets.

## Risk Analysis

**Highest-risk components:**
- The `--ff-display` value swap: 17 call sites inherit blackletter at once. Any of them under 24px becomes illegible.
- `background-clip: text` gold gradient: silent failure mode is invisible text, which no build step catches.

**Likely failure points:**
- A Grenze Gotisch weight is imported that the package ships but the design never uses, inflating payload.
- The header monogram's accessible name regresses when the `<img alt="Mafia Tumbada">` is removed — the link would otherwise announce as "M T".
- `.hero-title` styling assumes a text child in some rules; it currently wraps an image.

**Integration risks:**
- `src/pages/index.astro`'s scoped `<style>` references `var(--accent)`. If `--accent` is deleted from `:root` without updating that block, four link groups silently fall back to `currentColor`.

**Concurrency or state risks:** None. Static page, no shared state.

**Data corruption risks:** None. No data layer is touched.

**Rollback complexity:** Easy. Every change is confined to two style surfaces, one layout file and one page file; `git revert` of the phase commits restores the prior look with no data or schema implications.

**Risk-reduction order:**
1. Audit the 17 `--ff-display` call sites **before** changing its value (Task 3).
2. Land the token block with a solid-color fallback rule for gradient text (Task 2), so the riskiest CSS feature is proven before it is used widely.
3. Replace the header mark and confirm its accessible name (Task 4) — the only accessibility regression this plan can cause.

## Migration Strategy

**Rollout order:**
1. Add fonts (additive; nothing renders differently yet).
2. Redefine tokens and add the gradient utility.
3. Retarget typography.
4. Replace the header mark.
5. Apply accents (eyebrow rule, marquee, links).
6. Remove dead fonts and tokens.
7. Reconcile `DESIGN.md`.

**Backward compatibility:** `--gold`, `--gold-mid`, `--gold-shadow`, `--gold-dim`, `--ff-display`, `--ff-body`, `--ff-mono`, `--bg*`, `--text*`, `--border` all keep their names, so every existing `var()` keeps resolving throughout the migration. Only `--accent`, `--burgundy-glow` and `--burgundy-hot` are retired, and their 8 call sites are migrated in the same task that removes them.

**Migration sequencing:** Fonts land before the typography swap so no intermediate commit renders a missing face. Retired tokens are removed **after** their replacements are in use, never before.

**Fallback strategy:** Each phase is an independently revertible commit. Reverting any single phase leaves a coherent page.

**Temporary compatibility layers:** None required. The rename set is small enough to migrate atomically within its own task.

## Contracts Before Implementation

### Token contract (`src/styles/marketing-press.css`, `:root`)

```css
/* Surfaces */
--bg: oklch(7% 0 0);
--bg-raised: oklch(11% 0.006 60);
--bg-sunk: oklch(5% 0 0);

/* Ink */
--text: oklch(95% 0.008 85);
--text-muted: oklch(82% 0.008 85);
--text-faint: oklch(58% 0.01 85);

/* Gold — identity */
--gold-peak: oklch(88% 0.14 88);   /* NEW */
--gold: oklch(78% 0.15 85);        /* value changed, name kept */
--gold-mid: oklch(66% 0.13 80);    /* value changed, name kept */
--gold-shadow: oklch(50% 0.10 78); /* value changed, name kept */
--gold-dim: oklch(38% 0.07 75);    /* KEPT as-is: 13 hairline call sites */

/* Red neon — replaces --accent and --burgundy-* */
--red: oklch(62% 0.22 30);         /* NEW */
--red-link: oklch(72% 0.19 32);    /* NEW */
--red-glow: oklch(52% 0.20 28);    /* NEW */

--border: oklch(19% 0.006 85);
--focus-ring: oklch(78% 0.15 85 / 0.7);

--gold-gradient: linear-gradient(135deg, var(--gold-shadow), oklch(82% 0.15 86), var(--gold-mid));
--gold-text-gradient: linear-gradient(168deg, var(--gold-shadow) 0%, var(--gold-peak) 38%, oklch(72% 0.15 82) 62%, oklch(48% 0.09 76) 100%);

--ff-display: 'Grenze Gotisch', Georgia, serif;
--ff-body: 'Archivo', system-ui, -apple-system, sans-serif;
--ff-mono: 'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace;
```

**Removed:** `--accent`, `--burgundy-glow`, `--burgundy-hot`.

### Gold gradient text utility

```css
.gold-text {
  color: var(--gold);              /* fallback FIRST — never remove */
  background-image: var(--gold-text-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

@supports not ((background-clip: text) or (-webkit-background-clip: text)) {
  .gold-text { -webkit-text-fill-color: currentColor; }
}
```

**Invariant:** `color` is always declared before the transparent fill.

### Header mark markup contract (`src/layouts/MarketingLayout.astro`)

```html
<a href="/" class="header-mark gold-text" aria-label="Mafia Tumbada — Inicio">
  <span aria-hidden="true">M</span>
  <svg class="header-mark-bolt" viewBox="0 0 46 86" aria-hidden="true" focusable="false">
    <path d="M28 2L6 48h14L16 84l24-48H26L28 2z" fill="currentColor" />
  </svg>
  <span aria-hidden="true">T</span>
</a>
```

**Invariants:**
- The link's accessible name comes from `aria-label`, never from the glyphs.
- The bolt is `currentColor` so it inherits, and is overridden to `--red` in CSS.
- The bolt is inline SVG — never an emoji, glyph or image file.

### Eyebrow contract (`src/components/Eyebrow.astro`)

Markup is unchanged. The red rule is a `::before` on `.eyebrow`:

```css
.eyebrow::before {
  content: '';
  display: inline-block;
  width: 28px;
  height: 2px;
  margin-right: 12px;
  vertical-align: middle;
  background: var(--red);
}
```

## System Boundaries

### Inside the System
- `src/styles/marketing-press.css`: tokens, typography, header mark, eyebrow rule, marquee, hero scrims
- `src/layouts/MarketingLayout.astro`: font imports, header mark markup
- `src/pages/index.astro`: scoped `<style>` accent-token migration
- `package.json`: font dependency swap
- `DESIGN.md`: reconciliation

### Intentionally External
- `src/lib/catalog.ts` and the Spotify/YouTube fetch path: data, not presentation
- `src/lib/heroVideo.ts`: the deferral mechanism already satisfies the spec
- `public/media/harvest/`: raw source assets, not shipped by the page

### Deferred
- Playwright + axe-core harness for the `DESIGN.md` verification gate: `e2e/` is empty and no dependency exists. Needs its own plan.
- Replacing the hero video or logo with harvested photography: asset selection is a separate decision.
- Restoring the two dropped members in `members.ts`: explicitly declined by the user.
- A fechas section: explicitly declined by the user.

### Out of Scope
- `.wayfinder/SPEC.md` and `MAP.md` phone-number staleness: documentation debt, unrelated to the restyle.
- `src/styles/global.css` (`--color-brand`, Tailwind base): not consumed by the marketing page.

## File Structure

```
package.json                          modify  swap font deps
src/layouts/MarketingLayout.astro     modify  font imports; header mark markup
src/styles/marketing-press.css        modify  tokens, type, header mark, eyebrow, marquee, hero
src/pages/index.astro                 modify  scoped <style>: --accent → --red-link
DESIGN.md                             modify  reinstate --gold-dim; note the deferred a11y harness
```

No files created. No files deleted.

## Phases + Tasks

### Phase 1 — Foundations

#### Task 1: Add the new typefaces

**Purpose:** Both new faces are available to CSS before anything references them.

**Files:**
- Modify: `package.json`
- Modify: `src/layouts/MarketingLayout.astro`

**Contracts used:** Token contract (`--ff-display`, `--ff-body` fallback stacks).

**Steps:**
- [ ] `bun add @fontsource/grenze-gotisch@^5.3.0 @fontsource/archivo@^5.3.0`
- [ ] Add imports to `MarketingLayout.astro`, alongside the existing ones: `grenze-gotisch/latin-{400,600,700}.css` and `archivo/latin-{400,500,600,700}.css`.
- [ ] Leave the Cormorant and Inter imports in place for now — removal is Task 8.

**Validation:**
- Run: `bun run build`
- Expected: build completes; `dist/_astro/` contains `grenze-gotisch-latin-*` and `archivo-latin-*` woff2 files.

**Commit:**
```bash
git add package.json bun.lock src/layouts/MarketingLayout.astro
git commit -m "build(fonts): add Grenze Gotisch and Archivo"
```

#### Task 2: Redefine the token block and add the gradient utility

**Purpose:** The palette becomes Gótico Tumbado while every existing `var()` still resolves.

**Files:**
- Modify: `src/styles/marketing-press.css`

**Contracts used:** Token contract; gold gradient text utility.

**Steps:**
- [ ] Replace the `:root` color values per the token contract, keeping `--gold`, `--gold-mid`, `--gold-shadow`, `--gold-dim`, `--bg*`, `--text*`, `--border` names intact.
- [ ] Add `--gold-peak`, `--red`, `--red-link`, `--red-glow`, `--gold-text-gradient`.
- [ ] Update `--gold-gradient` and `--focus-ring` to the new values.
- [ ] Add the `.gold-text` utility with the `color` fallback declared first and the `@supports not` guard.
- [ ] Do **not** yet remove `--accent`, `--burgundy-glow`, `--burgundy-hot` — their call sites migrate in Task 6.

**Validation:**
- Run: `bun run build && grep -c "oklch(62% 0.22 30)" dist/_astro/*.css`
- Expected: build succeeds; at least one match confirming `--red` shipped.
- Manually: open `bun dev`, confirm the page still renders with no unstyled or invisible regions.

**Commit:**
```bash
git add src/styles/marketing-press.css
git commit -m "style(tokens): redefine palette as Gótico Tumbado"
```

### Phase 2 — Typography

#### Task 3: Audit and retarget display type

**Purpose:** Blackletter lands only where it is legible; nothing under 24px inherits it.

**Files:**
- Modify: `src/styles/marketing-press.css`

**Contracts used:** Token contract (`--ff-display`, `--ff-body`).

**Steps:**
- [ ] List every `--ff-display` call site: `grep -n "ff-display" src/styles/marketing-press.css`.
- [ ] For each, record the computed `font-size` at the 1280px breakpoint. Any site whose size resolves below 24px is reassigned to `var(--ff-body)` in this task, with a one-line comment naming the reason.
- [ ] Change `--ff-display` to `'Grenze Gotisch', Georgia, serif` and `--ff-body` to `'Archivo', system-ui, -apple-system, sans-serif`.
- [ ] Raise display `font-weight` to 600–700 where the previous Cormorant weight was 300–400; blackletter at 300 renders spindly.
- [ ] Apply `.gold-text` to `.section-heading` and release titles.

**Validation:**
- Run: `bun run build`
- Expected: build succeeds.
- Manually at 320 / 768 / 1280 / 1920: no blackletter under 24px; `¿`, `á`, `ñ`, `ó` render correctly in every heading; headings are gold-gradient with visible text.
- Manually: with DevTools, disable `background-clip` on a heading and confirm the solid `--gold` fallback appears rather than transparent text.

**Commit:**
```bash
git add src/styles/marketing-press.css
git commit -m "style(type): swap display and body faces to Grenze Gotisch and Archivo"
```

### Phase 3 — Header and hero

#### Task 4: Replace the header logo with the M⚡T monogram

**Purpose:** The header carries the band's own monogram instead of a logo image, without losing its accessible name.

**Files:**
- Modify: `src/layouts/MarketingLayout.astro`
- Modify: `src/styles/marketing-press.css`

**Contracts used:** Header mark markup contract.

**Steps:**
- [ ] Replace the `.header-logo` anchor and its `<img>` with the header mark markup contract exactly as specified.
- [ ] Add `.header-mark` styles: `--ff-display`, `font-size: var(--fs-monogram)`, `font-weight: 700`, flex row, `align-items: center`, `gap: 0.1em`, `line-height: 1`.
- [ ] Add `.header-mark-bolt`: `width: 0.34em; height: 0.62em; color: var(--red); filter: drop-shadow(0 0 10px var(--red-glow));`
- [ ] Delete the now-orphaned `.header-logo`, `.header-logo-img`, its `@media (min-width: 640px)` override, and the `logo-shimmer-header` keyframes. Leave `logo-shimmer-hero` and `.hero-logo-img` untouched — the hero still uses them.
- [ ] Confirm the mark's tap target is ≥44px.

**Validation:**
- Run: `bun run build && grep -c "header-logo-img" dist/index.html`
- Expected: `0`.
- Run: `grep -c "header-mark" dist/index.html` → at least `1`.
- Manually: inspect the link in DevTools accessibility pane; the computed name must be `Mafia Tumbada — Inicio`, not `M T`.
- Manually: tab to the mark and confirm a visible focus ring.

**Commit:**
```bash
git add src/layouts/MarketingLayout.astro src/styles/marketing-press.css
git commit -m "feat(header): replace logo image with M⚡T gothic monogram"
```

#### Task 5: Apply the hero scrim stack

**Purpose:** The hero matches the spec's three-layer scrim so the screen-blended logo always has dark pixels beneath it.

**Files:**
- Modify: `src/styles/marketing-press.css`

**Contracts used:** `DESIGN.md` §Hero anatomy and §Hero scrim stack.

**Steps:**
- [ ] Update `.hero::before` / `.hero::after` to the three-layer stack: the 90deg copy-legibility scrim, the 0deg base blend, and the inset red glow.
- [ ] Retune `.hero-logo-img`'s `drop-shadow()` stack to the new gold and red values, replacing the hard-coded `rgba(196,154,42,…)` and `rgba(114,47,55,…)` with `--gold` and `--red-glow`.
- [ ] Verify `.hero-video` keeps `preload="none"`, `object-fit: cover`, and that no change touches `data-src`.
- [ ] Confirm the existing `prefers-reduced-motion` block still suppresses hero autoplay and `logo-shimmer-hero`.

**Validation:**
- Run: `bun run build && grep -c 'data-src="/video/hero.mp4"' dist/index.html`
- Expected: `1` — the deferral survived.
- Manually with reduced-motion forced on: no autoplay, no shimmer, poster visible.
- Manually: the logo reads clearly against the brightest frame of the video.

**Commit:**
```bash
git add src/styles/marketing-press.css
git commit -m "style(hero): apply Gótico Tumbado scrim stack and logo glow"
```

### Phase 4 — Accents and cleanup

#### Task 6: Migrate accent tokens and apply red accents

**Purpose:** `--accent` and `--burgundy-*` are gone; links, eyebrow rules and the marquee use the red tokens.

**Files:**
- Modify: `src/styles/marketing-press.css`
- Modify: `src/pages/index.astro`

**Contracts used:** Token contract; eyebrow contract.

**Steps:**
- [ ] Replace both `--accent` uses in `marketing-press.css` with `var(--red-link)`.
- [ ] Replace `var(--accent)` in the `index.astro` scoped `<style>` (the `.video-row span, .music-link, .booking-copy a:not(.btn-primary), .footer-socials a` rule) with `var(--red-link)`.
- [ ] Replace the 4 `--burgundy-glow` uses with `var(--red-glow)` and the 2 `--burgundy-hot` uses with `var(--red)`.
- [ ] Add the `.eyebrow::before` red rule per the eyebrow contract.
- [ ] Delete `--accent`, `--burgundy-glow`, `--burgundy-hot` from `:root`.

**Validation:**
- Run: `grep -rn -- "--accent\|--burgundy" src/ | grep -v node_modules`
- Expected: no output.
- Run: `bun run build` — succeeds.
- Manually: every eyebrow shows a red rule; the marquee is red; links are red and legible.

**Commit:**
```bash
git add src/styles/marketing-press.css src/pages/index.astro
git commit -m "style(accent): replace turquoise and burgundy with red neon tokens"
```

#### Task 7: Verify contrast against the shipped stylesheet

**Purpose:** The measured table in `DESIGN.md` reflects what actually ships, not what was drafted.

**Files:**
- Modify: `DESIGN.md` (only if a measured value differs)

**Contracts used:** `DESIGN.md` §Measured contrast.

**Steps:**
- [ ] For each token pair in the `DESIGN.md` contrast table, recompute the ratio from the values now in `:root`.
- [ ] Confirm `--text`, `--text-muted`, `--text-faint`, `--gold`, `--gold-peak`, `--red-link`, `--red` all meet ≥4.5:1 against `--bg`.
- [ ] Confirm ink-on-gold-CTA and ink-on-red-marquee both meet ≥4.5:1.
- [ ] Confirm no rule uses `--gold-shadow` as a text color: `grep -n "color: var(--gold-shadow)" src/styles/marketing-press.css` must return nothing.
- [ ] If any computed value differs from the table, correct the table.

**Validation:**
- Run: the contrast computation over the shipped `:root` values.
- Expected: every row ≥4.5:1 except `--gold-shadow`, which must appear only in gradients and hairlines.

**Commit:**
```bash
git add DESIGN.md
git commit -m "docs(design): verify contrast table against shipped tokens"
```

#### Task 8: Remove the retired typefaces

**Purpose:** Cormorant and Inter stop shipping.

**Files:**
- Modify: `package.json`
- Modify: `src/layouts/MarketingLayout.astro`

**Steps:**
- [ ] Remove the 4 Cormorant and 4 Inter `@fontsource` imports from `MarketingLayout.astro`.
- [ ] `bun remove @fontsource/cormorant-garamond @fontsource/inter`
- [ ] `grep -rn "Cormorant\|[^a-z]Inter[^a-z]" src/` — expect no font references (the word may legitimately appear in prose).

**Validation:**
- Run: `bun run build && ls dist/_astro/ | grep -c "cormorant\|inter-latin"`
- Expected: `0`.
- Run: `bun test` → 21 pass.
- Manually: no fallback-serif flash on load.

**Commit:**
```bash
git add package.json bun.lock src/layouts/MarketingLayout.astro
git commit -m "build(fonts): drop Cormorant Garamond and Inter"
```

### Phase 5 — Reconciliation

#### Task 9: Reconcile DESIGN.md with the shipped code

**Purpose:** Spec and code agree, as `CLAUDE.md` requires.

**Files:**
- Modify: `DESIGN.md`

**Steps:**
- [ ] Reinstate `--gold-dim: oklch(38% 0.07 75)` in the token block, documented as hairline-dividers-only.
- [ ] Add `--gold-text-gradient` and the `.gold-text` utility to the tokens section, including the fallback-first invariant.
- [ ] Amend §Verification step 3 to record that the Playwright + axe-core harness does not exist yet and that accessibility was verified manually against the listed criteria.
- [ ] Confirm every token named in `DESIGN.md` exists in `:root` and vice versa.

**Validation:**
- Run: extract token names from both files and diff them.
- Expected: identical sets.

**Commit:**
```bash
git add DESIGN.md
git commit -m "docs(design): reconcile spec with shipped Gótico Tumbado tokens"
```

## Complexity Budget Check

- Two dependencies added, two removed. Net font weight files: 10 → 9.
- No new build step, no token pipeline, no component extracted for a single-use mark.
- No new abstraction: the change reuses the existing `:root` block, the existing `.is-scrolled` header behaviour, and the existing `.hero-logo-img` treatment.
- Token renames limited to the 8 call sites that must change; the 60 `--gold` sites are untouched by design.
- Deferred rather than built: the Playwright/axe harness, which would triple this plan's size for a gate unrelated to the restyle.

## Cross-Task Consistency Check

- [x] `--red`, `--red-link`, `--red-glow` are spelled identically in the token contract, Tasks 2 and 6, and `DESIGN.md`
- [x] `.gold-text` is defined in Task 2 before Task 3 applies it
- [x] Fonts land (Task 1) before `--ff-display` changes (Task 3) and are removed (Task 8) only after nothing references them
- [x] `--gold-dim` is kept in Task 2 and documented in Task 9 — no task deletes it
- [x] `.header-mark` markup in the contract matches the selectors styled in Task 4
- [x] `logo-shimmer-hero` and `.hero-logo-img` survive Task 4 and are retuned in Task 5 — no task removes what a later task edits
- [x] `--accent` removal (Task 6) migrates the `index.astro` call site in the same task
- [x] The contrast table is verified (Task 7) after all token values are final

## Decision Recording

**Decision:** Redefine token *values* under existing *names* rather than renaming to match the new direction.
**Alternatives considered:** Full rename to direction-neutral semantics; Tailwind theme mapping.
**Tradeoffs:** The name `--gold` now describes a slightly different gold, and `--gold-dim` outlives the direction that named it. Against that, 60 call sites and the entire component layer need no edits, and every intermediate commit renders correctly.
**Why this fits the decision priority:** Correctness and maintainability over developer convenience — a smaller diff is a reviewable diff, and every phase stays independently revertible.
**Complexity avoided:** A 60-site mechanical rename with no user-visible effect.

**Decision:** Keep the logo as the hero `<h1>` rather than setting the band name in blackletter.
**Alternatives considered:** Gothic wordmark hero (drafted and shown in the canvas).
**Tradeoffs:** The gothic wordmark was more striking but discarded the band's existing logo asset and its recognition. Blackletter still sets the tone via headings and the monogram.
**Why this fits the decision priority:** Product intent — the logo is the band's established mark; the site should not invent a competing one.
**Complexity avoided:** Commissioning or hand-drawing a wordmark.

## Self-Review

1. **Evidence** — every file, call-site count, font-package version and file manifest in this plan was read or fetched directly, not assumed.
2. **Spec coverage** — each `DESIGN.md` section maps to a task: tokens → 2, type → 3, header → 4, hero → 5, decoration/accents → 6, accessibility → 7, IA → unchanged.
3. **Open questions** — three surfaced, all with reversible defaults; none blocks starting.
4. **Placeholder scan** — no TBDs; every validation names an exact command and expected result.
5. **Type consistency** — token names cross-checked between the contract, tasks and `DESIGN.md`.
6. **Architecture stability** — one architecture, two alternatives rejected with reasons, complexity avoided listed.
7. **Product alignment** — the header mark, hero and blackletter constraints all trace to Product Intent.
8. **Risk reduction** — the `--ff-display` audit and the gradient fallback both land before wide application; the accessible-name check is in the task that can break it.
9. **Migration safety** — additive-then-subtractive ordering; no task deletes something a later task needs.
10. **Complexity budget** — dependencies net-negative; nothing speculative added.

**One weakness I could not resolve within scope:** `DESIGN.md` mandates an axe-core gate that does not exist. Task 9 records the gap honestly rather than deleting the requirement or pretending it ran.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-09-gotico-tumbado-restyle.md`. Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — execute tasks in this session with checkpoints for review

Which approach?

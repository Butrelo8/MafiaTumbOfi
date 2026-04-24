# Logo Gold Treatment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the AI placeholder logo with the real band logo and apply a Veracruz Noir visual treatment: matte black context, shiny gold logo, burgundy glow details, white small text.

**Architecture:** CSS-only treatment applied to the existing `<img>` tags in `MarketingLayout.astro` (header) and `index.astro` (hero). No new components — the two existing CSS classes `header-logo-img` and `hero-logo-img` in `marketing-press.css` are updated. Logo file swapped at same path so no markup changes needed.

**Tech Stack:** CSS `filter`, `drop-shadow`, `@keyframes` shimmer, existing Astro/CSS setup.

---

## File Map


| Action      | File                                         | Responsibility                                                 |
| ----------- | -------------------------------------------- | -------------------------------------------------------------- |
| **Modify**  | `web/src/styles/marketing-press.css:114–138` | Replace both logo filter stacks with gold + burgundy treatment |
| **Replace** | `web/public/icon/mafiatumbada.png`           | Swap in real band logo (PNG, transparent bg, ≥512×512px)       |


No other files change.

---

### Task 1: Swap the logo asset

**Files:**

- Replace: `web/public/icon/mafiatumbada.png`
- **Step 1: Obtain real logo file**
Source priority:
  1. Ask band manager for PNG with transparent background, ≥512×512px.
  2. If unavailable: screenshot from Instagram, crop tight to logo marks, run through [Topaz Gigapixel](https://www.topazlabs.com/gigapixel-ai) or Adobe Firefly upscale → export as PNG with transparency (remove background via remove.bg or Photoshop).
  Logo must be: **white or light-colored marks on transparent background** — the CSS filter will colorize it to gold. A dark-on-white logo will invert incorrectly.
- **Step 2: Replace file**
  ```bash
  cp ~/Downloads/mafiatumbada-real.png web/public/icon/mafiatumbada.png
  ```
  Verify dimensions:
  ```bash
  file web/public/icon/mafiatumbada.png
  # Expected: PNG image data, NNN x NNN, 8-bit/color RGBA
  ```
- **Step 3: Commit**
  ```bash
  git add web/public/icon/mafiatumbada.png
  git commit -m "assets: replace AI placeholder logo with real band logo"
  ```

---

### Task 2: Apply gold + burgundy CSS treatment

**Files:**

- Modify: `web/src/styles/marketing-press.css:114–138`

**Visual targets:**

- `--gold: #c49a2a` (existing token) — base gold hue
- Shiny highlight: bright gold drop-shadow `rgba(196, 154, 42, 0.9)` near
- Burgundy glow: `rgba(114, 47, 55, 0.5)` spread outer shadow
- Matte black is already the site background (`#0d0d0d` / `--surface`)
- Small text in white: hero eyebrow + meta already near-white; verify they stay white
- **Step 1: Replace logo CSS in `web/src/styles/marketing-press.css`**
Replace the block from `.header-logo-img` through the closing `}` of `.hero-logo-img` (lines 114–138):
  ```css
  /* ── Header logo — compact gold mark ─────────────────────── */
  .header-logo-img {
    height: 60px;
    width: auto;
    max-width: 200px;
    object-fit: contain;
    display: block;
    transition: height 0.3s ease, filter 0.3s ease;
    filter:
      brightness(0) sepia(1) saturate(6) hue-rotate(2deg) brightness(1.35)
      drop-shadow(0 0 6px rgba(196, 154, 42, 0.85))
      drop-shadow(0 0 18px rgba(196, 154, 42, 0.35))
      drop-shadow(0 0 32px rgba(114, 47, 55, 0.45))
      drop-shadow(0 3px 8px rgba(0, 0, 0, 0.9));
    animation: logo-shimmer 4s ease-in-out infinite;
  }

  @media (min-width: 640px) {
    .header-logo-img {
      height: 100px;
      max-width: 300px;
    }
  }

  /* ── Hero logo — large gold centerpiece ──────────────────── */
  .hero-logo-img {
    display: block;
    width: min(400px, 70vw);
    height: auto;
    object-fit: contain;
    opacity: 0.97;
    filter:
      brightness(0) sepia(1) saturate(6) hue-rotate(2deg) brightness(1.45)
      drop-shadow(0 0 10px rgba(196, 154, 42, 0.95))
      drop-shadow(0 0 30px rgba(196, 154, 42, 0.5))
      drop-shadow(0 0 60px rgba(114, 47, 55, 0.55))
      drop-shadow(0 4px 12px rgba(0, 0, 0, 0.95));
    animation: logo-shimmer 4s ease-in-out infinite;
  }

  /* ── Shimmer: subtle gold pulse ──────────────────────────── */
  @keyframes logo-shimmer {
    0%   { filter:
      brightness(0) sepia(1) saturate(6) hue-rotate(2deg) brightness(1.45)
      drop-shadow(0 0 10px rgba(196, 154, 42, 0.95))
      drop-shadow(0 0 30px rgba(196, 154, 42, 0.5))
      drop-shadow(0 0 60px rgba(114, 47, 55, 0.55))
      drop-shadow(0 4px 12px rgba(0, 0, 0, 0.95)); }
    50%  { filter:
      brightness(0) sepia(1) saturate(7) hue-rotate(2deg) brightness(1.65)
      drop-shadow(0 0 14px rgba(220, 175, 60, 1))
      drop-shadow(0 0 40px rgba(220, 175, 60, 0.6))
      drop-shadow(0 0 70px rgba(140, 30, 45, 0.65))
      drop-shadow(0 4px 12px rgba(0, 0, 0, 0.95)); }
    100% { filter:
      brightness(0) sepia(1) saturate(6) hue-rotate(2deg) brightness(1.45)
      drop-shadow(0 0 10px rgba(196, 154, 42, 0.95))
      drop-shadow(0 0 30px rgba(196, 154, 42, 0.5))
      drop-shadow(0 0 60px rgba(114, 47, 55, 0.55))
      drop-shadow(0 4px 12px rgba(0, 0, 0, 0.95)); }
  }

  /* Respect reduced-motion: freeze shimmer */
  @media (prefers-reduced-motion: reduce) {
    .header-logo-img,
    .hero-logo-img {
      animation: none;
    }
  }
  ```
  > **Filter stack explained:** `brightness(0)` flattens source to black. `sepia(1) saturate(6) hue-rotate(2deg)` maps to rich amber-gold. `brightness(1.45)` lifts highlights toward near-white gold. Drop-shadows layer: tight gold halo → wide gold bloom → outer burgundy atmospheric glow → hard black drop shadow beneath.
- **Step 2: Start dev server and verify visually**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321
  ```
  Checklist:
  - Hero logo: shiny gold, burgundy outer glow visible, hard shadow underneath
  - Header logo: same gold treatment, clean at small size
  - Shimmer: subtle 4s pulse, not distracting
  - Reduced-motion: DevTools → Rendering → `prefers-reduced-motion: reduce` → animation frozen
  - `hero-eyebrow` text (`.hero-eyebrow`) and `.hero-meta` spans remain white
  - No horizontal overflow at 360px mobile (resize DevTools)
- **Step 3: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```
- **Step 4: Commit**
  ```bash
  git add web/src/styles/marketing-press.css
  git commit -m "style: gold + burgundy logo treatment with shimmer animation"
  ```

---

## Self-Review

**Spec coverage:**

- ✅ Matte black background — site bg already `#0d0d0d`; no CSS change needed
- ✅ Shiny gold logo — filter stack + shimmer `@keyframes`
- ✅ Burgundy details — outer `drop-shadow rgba(114, 47, 55, 0.55)` glow
- ✅ Small text in white — hero eyebrow/meta already white; no override
- ✅ Real logo asset — Task 1 covers file swap

**Placeholder scan:** No TBD/TODO. All code blocks complete.

**Type consistency:** No functions. CSS class names consistent: `header-logo-img`, `hero-logo-img` across both tasks.
# Background Gradient & Texture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Skip all git steps — no commits.**

**Goal:** Add atmospheric depth to the marketing site's page background — layered radial gradients (gold/burgundy light leaks) and a full-page SVG grain texture — so non-hero sections no longer feel like a flat black void.

**Architecture:** All changes are in `web/src/styles/marketing-press.css`. The `body.marketing-body` rule gets a multi-layer `background` with a fixed grain SVG + radial gradient light leaks. A `body.marketing-body::before` pseudo-element carries a vignette layer so the gradients don't fight existing section backgrounds. No new files, no markup changes.

**Tech Stack:** CSS `background-image` stacking, SVG `feTurbulence` noise (inline data URI, same technique as existing `.hero-grain` at line 1276), `radial-gradient`, `background-blend-mode`.

---

## File Map


| Action     | File                                       | Responsibility                                                       |
| ---------- | ------------------------------------------ | -------------------------------------------------------------------- |
| **Modify** | `web/src/styles/marketing-press.css:65–74` | Add gradient + grain layers to `body.marketing-body` background      |
| **Modify** | `web/src/styles/marketing-press.css:74`    | Add `body.marketing-body::before` vignette block after the body rule |


No other files change.

---

### Task 1: Add gradient light leaks + grain to body background

**Files:**

- Modify: `web/src/styles/marketing-press.css:65–74`

**Design intent:**

- Base: `var(--bg)` = `oklch(12% 0 0)` — near-black, stays dominant
- Top-left corner: faint burgundy bloom — like a stage light from offstage left
- Bottom-right corner: faint gold bleed — warm undertone, not distracting
- Grain sits on top at low opacity to unify everything with film texture atmosphere
- **Step 1: Replace the `background` property inside `body.marketing-body`**
In `web/src/styles/marketing-press.css`, find the `body.marketing-body` block (lines 65–74). Replace only the `background: var(--bg);` line — leave all other properties untouched:
  ```css
  body.marketing-body {
    min-height: 100vh;
    background:
      url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='0.45'/%3E%3C/svg%3E")
        repeat fixed,
      radial-gradient(ellipse 70% 55% at 0% 0%, oklch(28% 0.08 10 / 0.55) 0%, transparent 65%),
      radial-gradient(ellipse 60% 50% at 100% 100%, oklch(22% 0.06 82 / 0.45) 0%, transparent 65%),
      var(--bg);
    background-blend-mode: overlay, normal, normal, normal;
    color: var(--text);
    font-family: var(--ff-body);
    font-weight: 400;
    font-size: var(--fs-body);
    line-height: var(--lh-body);
    -webkit-font-smoothing: antialiased;
  }
  ```
  > **Layer order (top → bottom):** grain SVG (overlay blend) → burgundy top-left radial → gold bottom-right radial → solid `--bg`. The grain is `fixed` so it doesn't scroll with content — static film texture effect. `background-blend-mode: overlay` on the grain makes it interact with the gradients below it rather than just sitting flat on top.
- **Step 2: Add vignette pseudo-element immediately after the `body.marketing-body` closing brace**
  ```css
  body.marketing-body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(ellipse 100% 100% at 50% 0%, transparent 40%, oklch(8% 0 0 / 0.6) 100%);
  }
  ```
  > Darkens outer edges of every page view — classic vignette. `position: fixed` + `z-index: 0` ensures it sits below all page content (sections use `position: relative; z-index: 1` or higher).
- **Step 3: Start dev server and verify visually**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321
  ```
  Checklist:
  - Page background shows subtle texture — not smooth flat black
  - Top-left has faint reddish/burgundy warmth
  - Bottom-right has faint amber warmth
  - Neither gradient is dominant — reads as dark/atmospheric, not colorful
  - Grain stays fixed when scrolling (does not scroll with page content)
  - Vignette: edges visibly darker than center on all sections
  - Hero section looks unchanged (its layers sit at `z-index: 1–4`, above body pseudo-element)
  - Body text contrast not degraded — check with DevTools accessibility panel
- **Step 4: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```

---

### Task 2: Visual polish — tune intensity

**Files:**

- Modify: `web/src/styles/marketing-press.css` (the `body.marketing-body` block from Task 1)

After seeing the result in-browser, use this table to dial intensity up or down:


| Knob              | Where                               | Subtle       | Medium (default) | Strong       |
| ----------------- | ----------------------------------- | ------------ | ---------------- | ------------ |
| Grain opacity     | `opacity='X'` in SVG data URI       | `0.25`       | `0.45`           | `0.65`       |
| Grain blend       | `background-blend-mode` first value | `soft-light` | `overlay`        | `hard-light` |
| Burgundy strength | `oklch(28% 0.08 10 / X)` alpha      | `0.3`        | `0.55`           | `0.75`       |
| Gold strength     | `oklch(22% 0.06 82 / X)` alpha      | `0.25`       | `0.45`           | `0.65`       |
| Vignette depth    | `oklch(8% 0 0 / X)` in `::before`   | `0.3`        | `0.6`            | `0.8`        |


- **Step 1: Apply adjustments based on visual review**
Example — softer gradients, more grain:
  ```css
  background:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='0.55'/%3E%3C/svg%3E")
      repeat fixed,
    radial-gradient(ellipse 70% 55% at 0% 0%, oklch(28% 0.08 10 / 0.35) 0%, transparent 65%),
    radial-gradient(ellipse 60% 50% at 100% 100%, oklch(22% 0.06 82 / 0.3) 0%, transparent 65%),
    var(--bg);
  background-blend-mode: soft-light, normal, normal, normal;
  ```
- **Step 2: Check reduced-motion (grain + gradients are static — confirm no animation)**
DevTools → Rendering → `prefers-reduced-motion: reduce` → page looks identical. No animation to disable here.
- **Step 3: Check mobile at 360px**
Resize DevTools to 360px. Verify:
  - No horizontal overflow introduced by `background: fixed`
  - Grain visible at mobile size
  - Gradient light leaks present at small viewport

---

## Self-Review

**Spec coverage:**

- ✅ Gradient on background — multi-layer radial gradients in `body.marketing-body`
- ✅ Texture — SVG fractalNoise grain, same technique as existing `.hero-grain` (line 1276)
- ✅ Veracruz Noir direction — dark base, burgundy/gold tones only, no bright colors
- ✅ Vignette depth — `::before` pseudo-element

**Placeholder scan:** No TBD/TODO. All CSS values concrete. Tuning table gives exact ranges.

**Type consistency:** No functions. CSS selectors consistent: `body.marketing-body` and `body.marketing-body::before` across both tasks.
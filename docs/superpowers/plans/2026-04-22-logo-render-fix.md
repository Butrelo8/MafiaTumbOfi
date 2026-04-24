# Logo Render Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Skip all git steps — no commits.**

**Goal:** Make the MT logo render with its actual design intact — gold outline, dark textured interior, 3D depth — instead of the current flat colorized silhouette that destroys the original artwork.

**Root cause:** `filter: brightness(0)` in both `.header-logo-img` and `.hero-logo-img` reduces every pixel to pure black before recolorizing. This obliterates the gold outline, dark fill, speckle texture, and 3D bevel — producing a flat cream/yellow shape. The logo PNG has a solid black background, so the fix is `mix-blend-mode: screen` on the `<img>`: black pixels (0,0,0) screen against a dark page = transparent, while gold and bright pixels stay visible. Original artwork preserved, no color destruction.

**Architecture:** Two CSS block replacements in `web/src/styles/marketing-press.css`. Remove `brightness(0) sepia(1) saturate(6) hue-rotate(2deg)` chain from both logo classes. Add `mix-blend-mode: screen`. Keep only `drop-shadow` filters for atmospheric glow. Shrink hero logo from `min(400px, 70vw)` to `min(320px, 55vw)` — current size overflows the hero frame. Rename animation from `logo-shimmer` to `logo-pulse` to avoid stale keyframe collision.

**Tech Stack:** CSS `mix-blend-mode`, `filter: drop-shadow()`, `@keyframes`.

---

## File Map


| Action     | File                                         | Responsibility                                                           |
| ---------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| **Modify** | `web/src/styles/marketing-press.css:114–138` | Replace filter stacks on both logo classes, add `mix-blend-mode: screen` |


No other files change.

---

### Task 1: Fix header logo

**Files:**

- Modify: `web/src/styles/marketing-press.css:114–129`
- **Step 1: Replace `.header-logo-img` block**
Find `.header-logo-img` at line 114. Replace the entire block (through the `@media (min-width: 640px)` closing brace):
  ```css
  .header-logo-img {
    height: 60px;
    width: auto;
    max-width: 200px;
    object-fit: contain;
    display: block;
    mix-blend-mode: screen;
    transition: height 0.3s ease, filter 0.3s ease;
    filter:
      drop-shadow(0 0 8px rgba(196, 154, 42, 0.7))
      drop-shadow(0 0 24px rgba(114, 47, 55, 0.4))
      drop-shadow(0 3px 8px rgba(0, 0, 0, 0.9));
  }

  @media (min-width: 640px) {
    .header-logo-img {
      height: 80px;
      max-width: 260px;
    }
  }
  ```
  > `mix-blend-mode: screen` makes the black PNG background transparent against the dark page. Gold outline and interior textures render intact. `drop-shadow` adds gold halo + burgundy atmospheric glow without touching logo colors. No `brightness(0)` — no color destruction.
- **Step 2: Start dev server, verify header logo**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321
  ```
  Expected in header:
  - Logo shows gold outline with dark textured interior (matches first image in spec)
  - Black PNG background invisible — blends away against dark header
  - Faint gold glow visible around logo edges
  - Logo does NOT appear as flat cream/yellow silhouette

---

### Task 2: Fix hero logo

**Files:**

- Modify: `web/src/styles/marketing-press.css:131–138` (`.hero-logo-img` + `@keyframes logo-shimmer`)
- **Step 1: Replace `.hero-logo-img` block and animation keyframes**
Find `.hero-logo-img` at line 131. Replace the entire block including `@keyframes logo-shimmer`:
  ```css
  .hero-logo-img {
    display: block;
    width: min(320px, 55vw);
    height: auto;
    object-fit: contain;
    mix-blend-mode: screen;
    filter:
      drop-shadow(0 0 12px rgba(196, 154, 42, 0.9))
      drop-shadow(0 0 40px rgba(196, 154, 42, 0.45))
      drop-shadow(0 0 70px rgba(114, 47, 55, 0.5))
      drop-shadow(0 5px 14px rgba(0, 0, 0, 0.95));
    animation: logo-pulse 5s ease-in-out infinite;
  }

  @keyframes logo-pulse {
    0%   { filter:
      drop-shadow(0 0 12px rgba(196, 154, 42, 0.9))
      drop-shadow(0 0 40px rgba(196, 154, 42, 0.45))
      drop-shadow(0 0 70px rgba(114, 47, 55, 0.5))
      drop-shadow(0 5px 14px rgba(0, 0, 0, 0.95)); }
    50%  { filter:
      drop-shadow(0 0 18px rgba(220, 175, 60, 1))
      drop-shadow(0 0 55px rgba(220, 175, 60, 0.55))
      drop-shadow(0 0 90px rgba(140, 30, 45, 0.65))
      drop-shadow(0 5px 14px rgba(0, 0, 0, 0.95)); }
    100% { filter:
      drop-shadow(0 0 12px rgba(196, 154, 42, 0.9))
      drop-shadow(0 0 40px rgba(196, 154, 42, 0.45))
      drop-shadow(0 0 70px rgba(114, 47, 55, 0.5))
      drop-shadow(0 5px 14px rgba(0, 0, 0, 0.95)); }
  }

  @media (prefers-reduced-motion: reduce) {
    .hero-logo-img {
      animation: none;
    }
  }
  ```
  > Width `min(320px, 55vw)` — down from `min(400px, 70vw)`. Current dev screenshot shows logo oversized and bleeding into video frame. `mix-blend-mode: screen` makes black PNG bg disappear. Animation renamed `logo-pulse` — avoids stale `logo-shimmer` keyframe collision from previous plan.
- **Step 2: Verify hero logo in browser**
With dev server still running at `http://localhost:4321`:
Expected:
  - Logo shows gold outline + dark textured interior — matches first image
  - Sized at ~320px wide, left-aligned with hero copy
  - Gold glow halo + outer burgundy bloom visible
  - Subtle 5s pulse animation — glow brightens and returns
  - Black PNG background invisible
- **Step 3: Check reduced-motion**
DevTools → Rendering → `prefers-reduced-motion: reduce` → animation frozen, logo still renders correctly with static glow.
- **Step 4: Check mobile 360px**
Resize DevTools to 360px. Verify:
  - Logo respects `55vw` cap — no horizontal overflow
  - `mix-blend-mode: screen` renders correctly (universal browser support)
- **Step 5: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```

---

## Self-Review

**Spec coverage:**

- ✅ Header logo — original gold design preserved via `mix-blend-mode: screen`, gold + burgundy glow
- ✅ Hero logo — original gold design preserved, correct size, pulse animation
- ✅ Root cause fixed — `brightness(0)` removed from both classes
- ✅ Reduced-motion — animation disabled
- ✅ Mobile — `55vw` cap prevents overflow

**Placeholder scan:** No TBD/TODO. All CSS concrete.

**Type consistency:** Animation `logo-pulse` used consistently in `.hero-logo-img` and `@keyframes`. No reference to old `logo-shimmer`.
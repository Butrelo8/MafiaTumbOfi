# Grunge Texture Visibility Fix Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Skip all git steps — no commits.**

**Goal:** Make `marketing-grunge-texture.png` visibly show on the page background — currently invisible because `multiply` blend mode on a near-black base cancels dark texture pixels.

**Root cause:** `background-blend-mode: multiply` composites layers by multiplying color values. Dark texture (≈0.1) × dark base (≈0.05) ≈ 0.005 — effectively black. The file loads fine; the blend mode erases it.

**Architecture:** Move the grunge PNG out of the `background` stack and into a `body.marketing-body::after` pseudo-element where `opacity` can be set directly. This is the only reliable way to control a dark texture's intensity on a dark background. One CSS property change + one new CSS block. No new files, no markup changes.

**Tech Stack:** CSS `background-blend-mode`, `mix-blend-mode`, `opacity`.

---

## File Map


| Action     | File                                     | Responsibility                                      |
| ---------- | ---------------------------------------- | --------------------------------------------------- |
| **Modify** | `web/src/styles/marketing-press.css:68`  | Remove grunge PNG from `background` stack           |
| **Modify** | `web/src/styles/marketing-press.css:74`  | Remove first blend-mode value (`multiply`)          |
| **Modify** | `web/src/styles/marketing-press.css:83+` | Add `::after` pseudo-element with texture + opacity |


---

### Task 1: Move texture to `::after` pseudo-element

**Files:**

- Modify: `web/src/styles/marketing-press.css:65–81`
- Modify: `web/src/styles/marketing-press.css:83+`
- **Step 1: Remove grunge PNG from `body.marketing-body` background stack**
Current `body.marketing-body` background (lines 67–74):
  ```css
  background:
    url('/marketing-grunge-texture.png') center / 320px 320px repeat fixed,
    url("data:image/svg+xml,...") repeat fixed,
    radial-gradient(ellipse 70% 55% at 0% 0%, oklch(28% 0.08 10 / 0.45) 0%, transparent 65%),
    radial-gradient(ellipse 60% 50% at 100% 100%, oklch(22% 0.06 82 / 0.35) 0%, transparent 65%),
    #0b0b0b;
  background-blend-mode: multiply, overlay, normal, normal, normal;
  ```
  Replace with (grunge PNG line deleted, first blend-mode value deleted):
  ```css
  background:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='0.08'/%3E%3C/svg%3E")
      repeat fixed,
    radial-gradient(ellipse 70% 55% at 0% 0%, oklch(28% 0.08 10 / 0.45) 0%, transparent 65%),
    radial-gradient(ellipse 60% 50% at 100% 100%, oklch(22% 0.06 82 / 0.35) 0%, transparent 65%),
    #0b0b0b;
  background-blend-mode: overlay, normal, normal, normal;
  ```
- **Step 2: Add `::after` pseudo-element for the grunge texture**
After the existing `body.marketing-body::before` block, add:
  ```css
  body.marketing-body::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background: url('/marketing-grunge-texture.png') center / 320px 320px repeat;
    opacity: 0.18;
    mix-blend-mode: screen;
  }
  ```
  > `opacity: 0.18` + `mix-blend-mode: screen` — the gray-white stone speckles in the texture punch through the dark base visibly without overwhelming it. `position: fixed` keeps it stationary while page scrolls. `z-index: 0` keeps it below all page content (sections are `z-index: 1+`).
- **Step 3: Start dev server and verify**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321
  ```
  Expected: rough dark stone texture visible across page. Should feel like weathered stone — not flat black, not gray. Scroll down: texture stays fixed (doesn't scroll).
  If **too subtle** (barely visible): raise `opacity` toward `0.28`.
  If **too strong** (gray dominates): lower `opacity` toward `0.10`.
- **Step 4: Check text contrast**
DevTools → Accessibility → verify body copy (`oklch(94% 0.01 90)`) contrast ratio ≥ 4.5:1 against textured background.
- **Step 5: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```

---

### Task 2: Tune opacity (visual polish pass)

**Files:**

- Modify: `web/src/styles/marketing-press.css` — `body.marketing-body::after` `opacity` value


| Feel                           | `opacity` value |
| ------------------------------ | --------------- |
| Very subtle — atmosphere only  | `0.08`          |
| Subtle — visible on close look | `0.12`          |
| **Default — clearly stone**    | `0.18`          |
| Strong — rough noir stone      | `0.28`          |
| Too much — gray dominates      | `0.40+`         |


- **Step 1: Set final opacity value after visual review**
Edit `body.marketing-body::after` opacity in `web/src/styles/marketing-press.css`:
  ```css
  opacity: 0.18; /* adjust to taste using table above */
  ```
- **Step 2: Check 360px mobile**
Resize DevTools to 360px. Verify:
  - No horizontal overflow
  - Texture still visible at small viewport
  - No performance jank on scroll (texture is `fixed`, so GPU-composited)

---

## Self-Review

**Spec coverage:**

- ✅ Root cause fixed — `multiply` on dark = invisible; moved to `::after` with `opacity`
- ✅ `screen` blend mode shows light stone pixels on dark base
- ✅ Opacity tuning table for polish pass
- ✅ Contrast check included
- ✅ Mobile check included

**Placeholder scan:** No TBD/TODO. All values concrete.

**Type consistency:** CSS selectors consistent: `body.marketing-body`, `body.marketing-body::before`, `body.marketing-body::after`.
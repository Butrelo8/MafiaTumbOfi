# Palette Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Skip all git steps — no commits.**

**Goal:** Elevate the Veracruz Noir palette to premium — deeper matte black base, metallic gradient gold on CTAs, burgundy used only as cinematic glow never as flat fill, turquoise accent retired from primary buttons.

**Architecture:** Two targeted edits in `web/src/styles/marketing-press.css`. `:root` tokens get a darker `--bg`, new `--gold-gradient` and `--burgundy-glow` tokens. `.btn-primary` switches from flat turquoise `--accent` to gradient gold. `.btn-secondary` hover switches from turquoise to gold. No markup changes.

**Tech Stack:** CSS custom properties, `linear-gradient`, `box-shadow`.

**Design rules enforced:**

- Gold: CTAs + hover accents only — nowhere else
- Burgundy: `box-shadow` / `radial-gradient` only — never flat `background` fill
- Texture must breathe — no heavy color layers smothering the grunge PNG

---

## File Map


| Action     | File                                         | Responsibility                                                       |
| ---------- | -------------------------------------------- | -------------------------------------------------------------------- |
| **Modify** | `web/src/styles/marketing-press.css:3–51`    | Deepen `--bg`, add `--gold-gradient` and `--burgundy-glow` tokens    |
| **Modify** | `web/src/styles/marketing-press.css:907–968` | Swap `.btn-primary` to gradient gold, `.btn-secondary` hover to gold |


---

### Task 1: Refine CSS tokens

**Files:**

- Modify: `web/src/styles/marketing-press.css:3–51`
- **Step 1: Replace the full `:root` block**
Find the `:root` block starting at line 3. Replace it entirely with:
  ```css
  :root {
    /* Veracruz Noir — see DESIGN.md */
    --bg: oklch(7% 0 0);
    --bg-raised: oklch(11% 0 0);
    --bg-sunk: oklch(5% 0 0);
    --text: oklch(94% 0.01 90);
    --text-muted: oklch(65% 0.01 90);
    --text-faint: oklch(45% 0.01 90);
    --gold: oklch(72% 0.14 82);
    --gold-dim: oklch(55% 0.1 82);
    --gold-gradient: linear-gradient(120deg, #d4af37 0%, #f6e27a 50%, #d4af37 100%);
    --burgundy-glow: rgba(122, 30, 44, 0.4);
    --burgundy-glow-strong: rgba(122, 30, 44, 0.65);
    --accent: oklch(68% 0.14 200);
    --accent-hot: oklch(60% 0.22 30);
    --border: oklch(24% 0.005 90);
    --focus-ring: oklch(72% 0.14 82 / 0.6);
    --color-success: oklch(62% 0.16 145);
    --color-error: oklch(60% 0.22 30);

    --ff-display: 'Cormorant Garamond', 'Playfair Display', Georgia, serif;
    --ff-body: 'Inter', system-ui, -apple-system, sans-serif;
    --ff-mono: 'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace;

    --fs-eyebrow: 0.75rem;
    --fs-body: clamp(1rem, 0.95rem + 0.2vw, 1.125rem);
    --fs-lede: clamp(1.25rem, 1rem + 0.8vw, 1.5rem);
    --fs-h3: clamp(1.5rem, 1.2rem + 1vw, 2rem);
    --fs-h2: clamp(2.5rem, 1.8rem + 3vw, 4rem);
    --fs-h1: clamp(3.5rem, 2rem + 8vw, 9rem);
    --lh-tight: 0.95;
    --lh-body: 1.55;
    --tracking-eyebrow: 0.18em;
    --tracking-display: -0.02em;

    --space-xs: 0.5rem;
    --space-sm: 1rem;
    --space-md: clamp(1.5rem, 1rem + 1vw, 2rem);
    --space-lg: clamp(3rem, 2rem + 3vw, 5rem);
    --space-section: clamp(4rem, 3rem + 4vw, 8rem);
    --space-hero: clamp(6rem, 4rem + 6vw, 12rem);
    --container: min(1280px, 92vw);
    --container-narrow: min(720px, 92vw);
    --radius-card: 0;
    --radius-pill: 999px;

    --surface: var(--bg-raised);
    --surface2: oklch(14% 0.005 90);
    --muted: var(--text-muted);
    --color-brand: var(--gold);
    --color-border: var(--border);
  }
  ```
  > `--bg` drops from `oklch(12%)` (~~`#1c1c1c`) to `oklch(7%)` (~~`#0b0b0b`). `--gold-gradient` used via `background: var(--gold-gradient)` on buttons. `--burgundy-glow` replaces any hardcoded `rgba(122,30,44,X)` in future rules.
- **Step 2: Verify background is deeper**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321
  ```
  Expected: page background noticeably darker — closer to true black. Grunge texture should stand out more against it.

---

### Task 2: Gradient gold buttons

**Files:**

- Modify: `web/src/styles/marketing-press.css:907–968`
- **Step 1: Replace `.btn-primary` block**
Find `.btn-primary` at line 907. Replace through `.btn-primary:focus-visible` closing brace:
  ```css
  .btn-primary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: var(--gold-gradient);
    color: oklch(9% 0 0);
    font-family: var(--ff-body);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 1rem 1.8rem;
    border: none;
    border-radius: var(--radius-pill);
    cursor: pointer;
    transition:
      transform 200ms cubic-bezier(0.16, 1, 0.3, 1),
      box-shadow 200ms ease,
      filter 200ms ease;
    text-decoration: none;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    filter: brightness(1.12);
    box-shadow:
      0 4px 20px rgba(212, 175, 55, 0.45),
      0 0 40px var(--burgundy-glow);
  }

  .btn-primary:focus-visible {
    outline: 2px solid var(--focus-ring);
    outline-offset: 4px;
  }
  ```
  > `background: var(--gold-gradient)` = metallic `#d4af37 → #f6e27a → #d4af37` sweep. `color: oklch(9% 0 0)` = near-black text on gold (~8.5:1 contrast ratio — passes WCAG AA). Hover: `filter: brightness(1.12)` brightens gradient + gold glow + burgundy atmospheric shadow underneath.
- **Step 2: Replace `.btn-secondary` block**
Find `.btn-secondary` at line 939. Replace through `.btn-secondary:focus-visible` closing brace:
  ```css
  .btn-secondary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: transparent;
    color: var(--text);
    font-family: var(--ff-body);
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.9rem 1.8rem;
    border: 1px solid var(--border);
    cursor: pointer;
    transition:
      border-color 200ms ease,
      color 200ms ease,
      transform 200ms cubic-bezier(0.16, 1, 0.3, 1),
      box-shadow 200ms ease;
    text-decoration: none;
  }

  .btn-secondary:hover {
    border-color: var(--gold);
    color: var(--gold);
    transform: translateY(-2px);
    box-shadow: 0 0 16px rgba(196, 154, 42, 0.25);
  }

  .btn-secondary:focus-visible {
    outline: 2px solid var(--focus-ring);
    outline-offset: 4px;
  }
  ```
  > Hover now uses `--gold` not `--accent` (turquoise). Gold border + gold text + faint gold glow. Consistent with "gold for hover states" rule.
- **Step 3: Verify both buttons in browser**
With dev server at `http://localhost:4321`, scroll to hero CTAs ("Solicitar contratación" + "Material de prensa").
Expected `.btn-primary`:
  - Gold gradient background visible — metallic sheen left-to-right
  - Dark near-black text (readable)
  - Hover: gradient brightens, gold + burgundy shadow visible beneath
  Expected `.btn-secondary`:
  - Transparent bg, gray border, white text at rest
  - Hover: border + text turn gold, faint gold glow
- **Step 4: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```

---

## Self-Review

**Spec coverage:**

- ✅ Matte black deepened — `--bg` from `oklch(12%)` → `oklch(7%)` (`#0b0b0b`)
- ✅ Gradient gold — `--gold-gradient` token + applied to `.btn-primary`
- ✅ Flat gold avoided — uses `#d4af37 / #f6e27a` gradient sweep, no `#FFD700`
- ✅ Burgundy as glow only — `--burgundy-glow` token used in `box-shadow` only; no flat burgundy fills
- ✅ Gold not overused — only on `.btn-primary` bg and `.btn-secondary` hover
- ✅ Texture breathes — no new body-level color layers

**Placeholder scan:** No TBD/TODO. All CSS concrete.

**Type consistency:** `--gold-gradient` defined in Task 1 `:root`, used in Task 2 `.btn-primary`. `--burgundy-glow` defined in Task 1, used in Task 2 hover. No forward references.
# Fullscreen Menu Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic centered fullscreen mobile/desktop overlay menu in `MarketingLayout.astro` with an editorial Veracruz-Noir split-layout overlay that matches `DESIGN.md` (numbered nav, mono prefixes, Cormorant italic on hover, gold hairline divider, film grain, animated hamburger morph, staggered link reveal, reduced-motion respected, mobile-first).

**Architecture:** Pure markup + CSS rewrite inside `web/src/layouts/MarketingLayout.astro` (menu block lines 102–203) and the menu styles in `web/src/styles/marketing-press.css` (lines ~254–345). No new components, no new dependencies. Hamburger button gains `is-open` class to morph into an X via CSS transforms. Menu uses CSS Grid: left column = numbered links (font-display, italic hover), right column (desktop) / bottom strip (mobile) = meta block with eyebrow, socials, signature CTA. Stagger animation via per-item `transition-delay` with `is-open` parent class. SVG noise overlay placed inside menu container for grain. Reduced-motion media query disables stagger + grain animation.

**Tech Stack:** Astro 4 (existing), vanilla CSS, vanilla JS (existing inline `<script>` in layout), Clerk components (`SignInButton`, `SignUpButton`, `UserButton`, `Show`).

**Design tokens used (from `DESIGN.md`):**

- `--bg-sunk` (menu canvas = `oklch(5%)` near-void), `--text`, `--text-muted`, `--text-faint`
- `--gold` (eyebrow labels, hairlines, hover numerals), `--gold-mid`, `--gold-shadow` (metallic gradient range — CTA label), `--gold-dim` (subtle dividers)
- `--burgundy-glow` (cinematic `box-shadow` on CTA hover ONLY — never flat fill)
- `--accent` (turquoise — link hover + focus ring ONLY, NOT on CTA backgrounds)
- `--ff-display` (Cormorant — link labels), `--ff-body` (Inter — eyebrows), `--ff-mono` (JetBrains — numerals + meta)
- `--space-lg`, `--tracking-eyebrow`, `--lh-tight`, `--container`
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` per design system

---

## File Structure

**Modified files:**

- `web/src/layouts/MarketingLayout.astro` — replace menu block (lines 102–132) and extend the inline `<script>` (lines 138–201) with hamburger morph toggle. Numbered nav data inlined as `const navItems = [...]` in frontmatter for clean templating.
- `web/src/styles/marketing-press.css` — replace `.hamburger-btn`, `.hamburger-line`, `.mobile-menu`, `.menu-close-btn`, `.menu-nav`, `.menu-link`, `.menu-auth` rules (lines ~254–345). Add new rules: `.hamburger-btn.is-open .hamburger-line`, `.menu-grid`, `.menu-numbers`, `.menu-meta`, `.menu-eyebrow`, `.menu-socials`, `.menu-cta`, `.menu-grain`, link stagger keyframes/transitions.

**No new files. No new components.** Single layout + single stylesheet keeps cohesion with existing surface.

---

## Task 1: Refactor menu markup in `MarketingLayout.astro`

**Files:**

- Modify: `web/src/layouts/MarketingLayout.astro:102-132` (replace menu block)
- Modify: `web/src/layouts/MarketingLayout.astro:19` (add `navItems` const in frontmatter)
- **Step 1: Add nav data to frontmatter**

Add inside the frontmatter block, just below the existing `const { title, ... } = Astro.props` line (around line 19):

```ts
const navItems = [
  { href: '/', label: 'Inicio' },
  { href: '/#redes', label: 'Redes' },
  { href: '/#musica', label: 'Música' },
  { href: '/#grupo', label: 'Integrantes' },
  ...(showPressAssetsSection ? [{ href: '/#press', label: 'Press kit' }] : []),
  { href: '/#paquetes', label: 'Paquetes' },
  { href: '/contratacion', label: 'Contrataciones' },
]
```

- **Step 2: Replace the entire `<!-- ─── FULLSCREEN MENU ─── -->` block (current lines 102–132)**

Replace with:

```astro
    <!-- ─── FULLSCREEN MENU ────────────────────────────────── -->
    <div class="mobile-menu" id="mobile-menu" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Menú principal">
      <div class="menu-grain" aria-hidden="true"></div>

      <div class="menu-grid">
        <nav class="menu-numbers" aria-label="Navegación">
          <ol class="menu-nav">
            {navItems.map((item, i) => (
              <li class="menu-item" style={`--i:${i}`}>
                <a href={item.href} class="menu-link">
                  <span class="menu-num">{String(i + 1).padStart(2, '0')}</span>
                  <span class="menu-label">{item.label}</span>
                </a>
              </li>
            ))}
            <Show when="signed-in">
              <li class="menu-item" style={`--i:${navItems.length}`}>
                <a href="/admin" class="menu-link">
                  <span class="menu-num">{String(navItems.length + 1).padStart(2, '0')}</span>
                  <span class="menu-label">Admin</span>
                </a>
              </li>
            </Show>
          </ol>
        </nav>

        <aside class="menu-meta">
          <p class="menu-eyebrow">Mafia Tumbada · Xalapa, Ver.</p>
          <p class="menu-tagline">Corridos tumbados<br/><em>desde 2021.</em></p>

          <nav class="menu-socials" aria-label="Redes sociales">
            <a href={bandSocialUrls.instagram} target="_blank" rel="noopener noreferrer">Instagram</a>
            <a href={bandSocialUrls.tiktok} target="_blank" rel="noopener noreferrer">TikTok</a>
            <a href={bandSocialUrls.spotify} target="_blank" rel="noopener noreferrer">Spotify</a>
            <a href={bandSocialUrls.youtube} target="_blank" rel="noopener noreferrer">YouTube</a>
          </nav>

          <a href="/contratacion" class="menu-cta">
            <span class="menu-cta-eyebrow">Contrataciones</span>
            <span class="menu-cta-label">Contrátanos<em>.</em></span>
          </a>

          <div class="menu-auth">
            <Show when="signed-out">
              <SignInButton mode="modal" />
              <SignUpButton mode="modal" />
            </Show>
            <Show when="signed-in">
              <UserButton />
            </Show>
          </div>
        </aside>
      </div>
    </div>
```

Notes:

- Existing `<button class="menu-close-btn" id="menu-close-btn">` is **removed**. Closing handled by clicking the (now morphed-into-X) hamburger button. Step 4 below updates the close JS handler.
- `role="dialog" aria-modal="true"` upgrades a11y semantics for a fullscreen overlay.
- `style="--i:${i}"` exposes per-item index for CSS stagger delay.
- **Step 3: Verify Astro template compiles**

Run: `cd web && bun astro check`
Expected: 0 errors related to `MarketingLayout.astro`.

---

## Task 2: Update inline JS in `MarketingLayout.astro` for hamburger morph + close-button removal

**Files:**

- Modify: `web/src/layouts/MarketingLayout.astro:138-201` (inline `<script>`)
- **Step 1: Replace open/close handlers**

Inside the `<script>` block, replace the `openMenu` / `closeMenu` definitions and the listener setup that references `closeBtn` with:

```ts
const hamburgerBtn = document.getElementById('hamburger-btn');
const menu = document.getElementById('mobile-menu');

function openMenu() {
  menu?.classList.add('is-open');
  menu?.setAttribute('aria-hidden', 'false');
  hamburgerBtn?.classList.add('is-open');
  hamburgerBtn?.setAttribute('aria-expanded', 'true');
  hamburgerBtn?.setAttribute('aria-label', 'Cerrar menú');
  document.body.style.overflow = 'hidden';
}

function closeMenu() {
  menu?.classList.remove('is-open');
  menu?.setAttribute('aria-hidden', 'true');
  hamburgerBtn?.classList.remove('is-open');
  hamburgerBtn?.setAttribute('aria-expanded', 'false');
  hamburgerBtn?.setAttribute('aria-label', 'Abrir menú');
  document.body.style.overflow = '';
}

hamburgerBtn?.addEventListener('click', () => {
  if (menu?.classList.contains('is-open')) closeMenu();
  else openMenu();
});
```

Remove these now-dead lines:

- `const closeBtn = document.getElementById('menu-close-btn');`
- `closeBtn?.addEventListener('click', closeMenu);`
- **Step 2: Keep existing handlers intact**

Do NOT touch:

- `header` scroll listener (lines ~157–168)
- `.menu-auth` click listener (lines ~175–177)
- `.menu-link` close-on-click listener (lines ~180–182) — still works against the new markup
- Escape key handler (lines ~185–187)
- `hero-cta-contratacion` plausible handler
- `tour-ticket-btn` plausible delegation
- **Step 3: Manual smoke test**

Run: `cd web && bun dev`
Open `http://localhost:4321/`. Click hamburger → menu opens, button shows X. Click X → menu closes, button shows hamburger. Press Esc when open → closes. Click any link → closes + navigates.

---

## Task 3: Replace menu CSS in `marketing-press.css`

**Files:**

- Modify: `web/src/styles/marketing-press.css:254-345` (replace existing hamburger + menu rules)
- **Step 1: Replace lines ~254–345 with the new ruleset**

Delete the existing `.hamburger-btn`, `.hamburger-line`, `.hamburger-btn:hover .hamburger-line`, `.mobile-menu`, `.mobile-menu.is-open`, `.menu-close-btn`, `.menu-close-btn:hover`, `.menu-nav`, `.menu-link`, `.menu-link:hover`, `.menu-auth` blocks. Insert this in their place:

```css
/* ── Hamburger ──────────────────────────────────────────── */
.hamburger-btn {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  padding: 6px;
  width: 36px;
  height: 36px;
  z-index: 210; /* above .mobile-menu */
}

.hamburger-line {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--gold);
  border-radius: 0;
  transform-origin: center;
  transition:
    transform 320ms cubic-bezier(0.16, 1, 0.3, 1),
    opacity 200ms ease,
    background-color 200ms ease;
}

.hamburger-btn:hover .hamburger-line { background: var(--text); }

.hamburger-btn.is-open .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger-btn.is-open .hamburger-line:nth-child(2) { opacity: 0; }
.hamburger-btn.is-open .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.hamburger-btn:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 4px;
}

/* ── Fullscreen overlay menu ───────────────────────────── */
.mobile-menu {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--bg-sunk, #0a0a0a);
  color: var(--text);
  opacity: 0;
  visibility: hidden;
  transition: opacity 380ms cubic-bezier(0.16, 1, 0.3, 1), visibility 380ms;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.mobile-menu.is-open { opacity: 1; visibility: visible; }

.menu-grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.6 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
  opacity: 0.06;
  mix-blend-mode: overlay;
}

/* Grid: left numbered nav, right meta column. Mobile stacks. */
.menu-grid {
  position: relative;
  z-index: 1;
  min-height: 100%;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr auto;
  gap: var(--space-lg);
  padding: clamp(5rem, 8vw, 8rem) clamp(1.5rem, 6vw, 5rem) clamp(2rem, 5vw, 4rem);
  width: var(--container);
  margin-inline: auto;
}

@media (min-width: 880px) {
  .menu-grid {
    grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
    grid-template-rows: 1fr;
    align-items: center;
    gap: clamp(3rem, 6vw, 6rem);
  }
  .menu-meta {
    border-left: 1px solid color-mix(in oklab, var(--gold-dim) 60%, transparent);
    padding-left: clamp(2rem, 4vw, 4rem);
    align-self: stretch;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

/* ── Numbered nav ──────────────────────────────────────── */
.menu-nav {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(0.4rem, 1vw, 0.9rem);
}

.menu-item {
  opacity: 0;
  transform: translateY(14px);
  transition:
    opacity 520ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 520ms cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: calc(60ms * var(--i, 0) + 120ms);
}

.mobile-menu.is-open .menu-item {
  opacity: 1;
  transform: translateY(0);
}

.menu-link {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: baseline;
  column-gap: clamp(0.75rem, 2vw, 1.5rem);
  text-decoration: none;
  color: var(--text);
  padding: 0.25rem 0;
  border-bottom: 1px solid transparent;
  transition: border-color 200ms ease, color 200ms ease;
}

.menu-num {
  font-family: var(--ff-mono);
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  color: var(--text-faint);
  font-feature-settings: 'tnum' 1;
}

.menu-label {
  font-family: var(--ff-display);
  font-weight: 600;
  font-size: clamp(2.25rem, 7vw, 4.75rem);
  line-height: var(--lh-tight, 0.95);
  letter-spacing: var(--tracking-display, -0.02em);
  text-wrap: balance;
}

.menu-link:hover .menu-label,
.menu-link:focus-visible .menu-label {
  font-style: italic;
  color: var(--accent);
}

.menu-link:hover .menu-num,
.menu-link:focus-visible .menu-num { color: var(--gold); }

.menu-link:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 6px;
}

/* ── Meta column ───────────────────────────────────────── */
.menu-meta {
  display: flex;
  flex-direction: column;
  gap: clamp(1rem, 2.5vw, 1.75rem);
  opacity: 0;
  transform: translateY(14px);
  transition:
    opacity 520ms cubic-bezier(0.16, 1, 0.3, 1) 360ms,
    transform 520ms cubic-bezier(0.16, 1, 0.3, 1) 360ms;
}

.mobile-menu.is-open .menu-meta { opacity: 1; transform: translateY(0); }

.menu-eyebrow {
  font-family: var(--ff-body);
  font-size: var(--fs-eyebrow, 0.75rem);
  letter-spacing: var(--tracking-eyebrow, 0.18em);
  text-transform: uppercase;
  color: var(--gold);
  margin: 0;
}

.menu-tagline {
  font-family: var(--ff-display);
  font-weight: 300;
  font-size: clamp(1.25rem, 2.4vw, 1.75rem);
  line-height: 1.15;
  color: var(--text-muted);
  margin: 0;
}
.menu-tagline em { font-style: italic; color: var(--text); }

.menu-socials {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1.25rem;
  font-family: var(--ff-mono);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.menu-socials a {
  color: var(--text-muted);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  padding-bottom: 2px;
  transition: color 200ms ease, border-color 200ms ease;
}
.menu-socials a:hover,
.menu-socials a:focus-visible {
  color: var(--accent);
  border-color: var(--accent);
}

.menu-cta {
  display: inline-flex;
  flex-direction: column;
  gap: 0.25rem;
  text-decoration: none;
  padding: 0.75rem 0;
  border-top: 1px solid color-mix(in oklab, var(--gold-dim) 60%, transparent);
  border-bottom: 1px solid color-mix(in oklab, var(--gold-dim) 60%, transparent);
  width: max-content;
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1), box-shadow 400ms ease;
}
.menu-cta:hover,
.menu-cta:focus-visible {
  transform: translateY(-2px);
  /* cinematic burgundy glow — box-shadow only, never flat fill */
  filter: drop-shadow(0 0 28px var(--burgundy-glow));
}

.menu-cta-eyebrow {
  font-family: var(--ff-body);
  font-size: var(--fs-eyebrow, 0.75rem);
  letter-spacing: var(--tracking-eyebrow, 0.18em);
  text-transform: uppercase;
  color: var(--text-faint);
}
.menu-cta-label {
  font-family: var(--ff-display);
  font-weight: 600;
  font-style: italic;
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  line-height: 1;
  /* metallic gold gradient text — turquoise retired from CTAs */
  background: linear-gradient(135deg, var(--gold-shadow), var(--gold), var(--gold-mid));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.menu-cta-label em {
  font-style: normal;
  /* em punct inherits gradient — no override needed */
}

.menu-auth {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

/* ── Reduced motion ────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .mobile-menu,
  .menu-item,
  .menu-meta,
  .hamburger-line,
  .menu-cta {
    transition: opacity 120ms linear, visibility 120ms;
    transform: none !important;
    transition-delay: 0ms !important;
  }
  .menu-grain { display: none; }
}

/* ── Mobile tightening (≤640px) ────────────────────────── */
@media (max-width: 640px) {
  .menu-grid { padding-top: 4.5rem; }
  .menu-label { font-size: clamp(2rem, 9vw, 3.25rem); }
  .menu-meta { gap: 1rem; }
  .menu-socials { font-size: 0.72rem; gap: 0.25rem 1rem; }
}
```

- **Step 2: Verify CSS parses + dev server reloads**

Run: `cd web && bun dev`
Open the page. Click hamburger. Confirm:

- Two-column layout at ≥880px (numbered nav left, meta right with gold hairline divider)
- Single-column stack on mobile
- Numbers `01`, `02`... in mono
- Nav labels go italic + turquoise on hover (link hover — correct per DESIGN.md)
- CTA label "Contrátanos." shows metallic gold gradient text (NOT turquoise)
- CTA hover shows deep burgundy cinematic glow via `filter: drop-shadow`
- Hamburger morphs into X
- Visible film grain at low opacity

---

## Task 4: Cross-breakpoint visual verification

**Files:** none modified — verification only.

- **Step 1: Run dev server**

Run: `cd web && bun dev`

- **Step 2: Manually check at 320 / 375 / 768 / 1024 / 1440 / 1920**

In Chrome devtools device toolbar, open menu at each width. Verify:

- 320 / 375: stacked single column, no horizontal overflow, all links tappable (≥44px target — Cormorant size + line padding qualifies)
- 768: still stacked (breakpoint is 880px), comfortable padding
- 1024 / 1440 / 1920: two columns, gold hairline divider visible, meta block vertically centered, labels do not wrap awkwardly
- **Step 3: Keyboard tab-through**

Open menu, tab through every link. Confirm:

- Focus ring (2px gold, 4px offset) visible on every link, social, CTA, auth button
- Tab order: nav links top→bottom → socials → CTA → auth
- Esc closes menu and returns focus to hamburger button (already wired in existing Esc handler — verify still works)
- **Step 4: Reduced-motion check**

In Chrome devtools rendering tab, emulate `prefers-reduced-motion: reduce`. Open menu. Confirm:

- No stagger animation (links appear instantly)
- No grain overlay
- Hamburger line transition still snaps but no bounce
- **Step 5: Contrast audit**

Run axe-core extension or Lighthouse on the page with menu open. Confirm zero serious contrast violations against `--bg-sunk`. Tokens already meet WCAG AA per `DESIGN.md` — flag anything new.

---

## Task 5: Update existing E2E booking smoke test if menu selectors changed

**Files:**

- Inspect: `web/e2e/booking.e2e.ts`
- Inspect: `web/e2e/tours.e2e.ts`
- **Step 1: Search for menu selectors in existing E2E tests**

Run: `cd web && grep -RIn -E "menu-close-btn|hamburger-btn|menu-link|mobile-menu" e2e/`
Expected: any references — usually only `hamburger-btn` and `menu-link` survive; `menu-close-btn` is now removed.

- **Step 2: If `menu-close-btn` is referenced, update to use `hamburger-btn` toggle instead**

Replace any selector like `page.locator('#menu-close-btn').click()` with `page.locator('#hamburger-btn').click()` (the same button now closes the menu when in `is-open` state).

- **Step 3: Run E2E**

Run: `cd web && bun run test:e2e`
Expected: PASS.

---

## Task 6: Final review + branch wrap-up

- **Step 1: Build**

Run: `cd web && bun run build`
Expected: build succeeds (Vercel adapter), 0 type errors.

- **Step 2: Diff review**

Run: `git diff main -- web/src/layouts/MarketingLayout.astro web/src/styles/marketing-press.css`
Confirm:

- Deleted: `.menu-close-btn` rules + button markup
- Added: `.menu-grid`, `.menu-numbers`, `.menu-meta`, `.menu-grain`, hamburger morph rules, stagger transitions, reduced-motion block
- Existing scroll/header/auth handlers untouched
- **Step 3: Reconcile against `DESIGN.md`**

Tick each:

- Cormorant only on labels (yes — `.menu-label`, `.menu-tagline`, `.menu-cta-label`)
- Inter on eyebrows (`.menu-eyebrow`, `.menu-cta-eyebrow`)
- JetBrains Mono on numerals + socials (yes)
- Gold reserved for eyebrow + hairline + hover number (no body gold)
- Turquoise (`--accent`) = link hover + focus ONLY — NOT on CTA label or backgrounds (yes — `.menu-label` italic hover uses `--accent`, `.menu-cta-label` uses metallic gold gradient)
- Burgundy = `filter: drop-shadow` on `.menu-cta:hover` ONLY — never flat fill (yes)
- No drop shadows on UI (confirm — only `filter: drop-shadow` on CTA hover, atmospheric per DESIGN.md)
- No gradient blobs (confirm)
- No AOS zoom/flip used (confirm — pure CSS transitions)
- Grain only inside menu surface (yes — `.menu-grain`)
- **Step 4: Push branch + open PR**

```bash
git push -u origin feat/desegin-consultation-redo
gh pr create --title "feat(menu): editorial fullscreen menu redesign" --body "$(cat <<'EOF'
## Summary
- Replace centered fullscreen overlay menu with split editorial layout (numbered nav + meta column)
- Hamburger morphs into X via CSS transforms; close button removed
- Nav labels go italic + turquoise on hover; CTA label uses metallic gold gradient; burgundy cinematic glow on CTA hover
- Mono numerals; gold hairline divider; SVG film grain
- Mobile-first stack, two-column at ≥880px, full a11y (role=dialog, aria-modal, focus rings, reduced-motion honored)

## Test plan
- [ ] Manual visual check at 320 / 375 / 768 / 1024 / 1440 / 1920
- [ ] Keyboard tab-through with focus ring visible
- [ ] Esc closes menu
- [ ] `prefers-reduced-motion` disables stagger + grain
- [ ] axe-core: 0 serious violations
- [ ] `bun run test:e2e` passes
EOF
)"
```

---

## Self-review notes

- Spec coverage: fancier menu ✅, matches `DESIGN.md` aesthetic ✅, mobile considered ✅, hamburger interaction preserved ✅.
- No placeholders — every code block is the literal content to paste.
- Type/selector consistency: `is-open` class used identically across `mobile-menu` and `hamburger-btn`. `menu-link` retained so the existing `menu?.querySelectorAll('.menu-link')` close-on-click handler keeps working without JS changes.
- `--bg-sunk`, `--gold-dim`, `--text-faint` are all defined in `DESIGN.md` — verified.
- `color-mix(in oklab, ...)` is supported in modern browsers Astro targets; if stricter fallback needed, swap to `rgba(184, 151, 58, 0.4)` literal.


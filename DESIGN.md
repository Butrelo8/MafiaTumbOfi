# Mafia Tumbada — Design System

> Source of truth for visual direction, design tokens, components, and motion rules.
> Any PR that touches the marketing site must reconcile with this file.
> If this file and the code disagree, update one, do not drift.

## Direction

**Veracruz Noir** — editorial press kit × regional mexicano × gulf-coast noir.

Black-on-black canvas, 35mm film grain on photo sections, Cormorant Garamond held as signature headline type (not body), turquoise hot accent for CTAs, gold reserved for section labels and logo.

Why this direction and not generic dark-luxury: Mafia Tumbada is from Xalapa, Veracruz — gulf coast, not Sinaloa desert. The genre's visual default (Fuerza Regida, Peso Pluma, Rancho Humilde) is black + red + truck-cholo + desert. MTO differentiates with a coastal accent (turquoise), editorial press-kit discipline, and one-signature-font restraint. Feels like a magazine pitch, not a template.

## Audience

- **Primary: fans** — music, tour dates, BTS photos, socials land above the fold
- **Secondary: promoters** — deep-link to `/contratacion` press-kit spread from IG bio and homepage CTAs

## Tokens

### Color (OKLCH)

```css
:root {
  /* Core surfaces — deeper matte black base */
  --bg: oklch(8% 0 0);                    /* near-void matte black */
  --bg-raised: oklch(12% 0.004 90);       /* cards, surfaces — faint warm tint */
  --bg-sunk: oklch(5% 0 0);              /* hero wells, press-kit spreads — pure void */

  /* Ink */
  --text: oklch(94% 0.01 90);             /* warm paper-white */
  --text-muted: oklch(65% 0.01 90);       /* meta, secondary */
  --text-faint: oklch(45% 0.01 90);       /* timestamps, captions */

  /* Signature gold — metallic gradient range */
  --gold: oklch(76% 0.16 82);             /* gold highlight — bright metallic peak */
  --gold-mid: oklch(64% 0.13 78);         /* gold midtone — gradient middle */
  --gold-shadow: oklch(48% 0.09 75);      /* gold shadow — gradient base / hairlines */
  --gold-dim: oklch(38% 0.07 75);         /* near-dark gold — subtle dividers */

  /* Burgundy — cinematic glow ONLY, never flat fill */
  --burgundy-glow: oklch(38% 0.14 15);    /* deep burgundy — box-shadow / glow source */
  --burgundy-hot: oklch(52% 0.18 18);     /* marquee strip, SOLD OUT tag only */

  /* Turquoise — secondary accent, links + focus ONLY */
  --accent: oklch(68% 0.14 200);          /* veracruz turquoise — links, focus, NOT buttons */

  /* Semantic */
  --border: oklch(20% 0.005 90);
  --focus-ring: oklch(76% 0.16 82 / 0.65); /* gold-highlight @ 65% */
  --color-success: oklch(62% 0.16 145);   /* inline form confirmation */
  --color-error: oklch(52% 0.18 18);      /* form errors — same hue as --burgundy-hot */
}
```

**CTA gradient pattern** (primary buttons, booking CTAs):

```css
background: linear-gradient(135deg, var(--gold-shadow), var(--gold), var(--gold-mid));
```

**Color rules:**

- Gold: metallic gradient (`--gold-shadow → --gold → --gold-mid`) on primary CTA backgrounds, buttons, logo treatment. Flat `--gold` only for eyebrow labels. `--gold-dim` for hairline dividers. NEVER body text.
- Burgundy: `--burgundy-glow` ONLY as `box-shadow` / `filter: drop-shadow()` for cinematic atmosphere on hero, cards, photo overlays. `--burgundy-hot` for marquee strip and "SOLD OUT" tag ONLY. Never as flat fill, background, or text color.
- Turquoise (`--accent`): text link hover, `::after` underline reveals, focus outlines ONLY. NOT used on button backgrounds or CTAs.
- `--color-success` / `--color-error`: booking form inline status only (not body copy)
- All text tokens must hold WCAG AA against `--bg`

### Typography

```css
:root {
  /* Display — headline only */
  --ff-display: 'Cormorant Garamond', 'Playfair Display', Georgia, serif;

  /* Body */
  --ff-body: 'Inter', system-ui, -apple-system, sans-serif;

  /* Mono — tabular data */
  --ff-mono: 'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace;

  /* Fluid scale */
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
}
```

**Typography rules:**

- Cormorant: `h1`, `h2` only. Italic allowed on ONE word per hero max
- Inter: body, UI labels, eyebrows (ALL CAPS tracked `0.18em`, gold color)
- JetBrains Mono: tour-date columns, venue codes, timestamps, `tabular-nums`
- `text-wrap: balance` on headings, `text-wrap: pretty` on body paragraphs
- Jost (legacy) removed — do not add back

### Spacing

```css
:root {
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: clamp(1.5rem, 1rem + 1vw, 2rem);
  --space-lg: clamp(3rem, 2rem + 3vw, 5rem);
  --space-section: clamp(4rem, 3rem + 4vw, 8rem);
  --space-hero: clamp(6rem, 4rem + 6vw, 12rem);

  --container: min(1280px, 92vw);
  --container-narrow: min(720px, 92vw);
}
```

**Spacing rules:**

- No uniform padding. Major sections: `--space-section`. Editorial blocks: `--space-lg`. Trust/stats strips: `--space-md`
- `--radius-card: 0` (sharp, editorial)
- `--radius-pill: 999px` (chips, buttons only)

## Layout

- 12-col grid desktop, 4-col tablet, flow mobile
- `gap: clamp(1rem, 2vw, 2rem)`
- **Asymmetric hero:** full-bleed background video with scrims + film grain; copy left-aligned in container, layered above video. No centered stock-hero
- **Bento grid:** Repertorio, Integrantes, Discografía use 1-large-plus-2-small breakup
- **Tour table:** 4 columns desktop (date / city / venue / CTA), stacked mobile. Date column mono + `tabular-nums`
- **Artwork shelf:** horizontal scroll-snap, 4 visible desktop, full-bleed covers; optional per-item `cover` URL (lazy `<img>`, 80×80) or initials fallback
- **BTS strip:** 3-photo horizontal film reel with edge bleed
- **Press-kit spread (`/contratacion`):** full-bleed cover + 2-col body (bio left, form right)

## Components

Each lives in `web/src/components/` and must respect the tokens above.

1. `**<Hero>`** — full-bleed video background; copy + eyebrow + meta chips left (layered on top)
2. `**<TourTable>`** — 4-col tabular, mono dates, per-row ticket CTA, blood-red `**SOLD OUT`** tag (English label on purpose: ticketing/promo convention; body copy stays Spanish-first)
3. `**<ArtworkShelf>`** — horizontal scroll-snap, hover reveals title + stream links
4. `**<Marquee>`** — single-use per page, CSS `@keyframes` translate, pausable on hover
5. `**<FilmStrip>`** — 3-photo BTS row, bleed to page edges
6. `**<PressKitSpread>`** — 2-col editorial for `/contratacion`, feels InDesign
7. `**<Eyebrow>`** — ALL CAPS Inter, gold, tracked `0.18em`
8. `**<SignatureCTA>**` — mono-italic "Contrátanos." placeholder; upgrade to handwritten SVG later

## Decoration

- **Film grain:** SVG noise overlay, 6% opacity, photo sections only
- **Gold hairline dividers:** `1px`, 40% opacity, section breaks only
- **Marquee strip:** `CORRIDOS TUMBADOS · XALAPA · DESDE 2021 ·` repeating, 1 per page max
- **Ticket-stub clip:** `clip-path` motif on tour cards, 1–2 uses
- **Paper-grain background:** `/contratacion` and `/prensa` only
- **No drop shadows on UI.** Drop shadows only on photos (atmospheric, blurred, low-opacity)

## Motion

- `**prefers-reduced-motion`** honored: disables marquee + scroll-triggered
- **AOS:** restricted to `fade` and `fade-up` only. `zoom-in`, `flip`, `slide-`* forbidden
- **Marquee:** 60s linear infinite, pause on hover
- **Hero video:** autoplay muted, `object-fit: cover`, poster fallback for reduced-motion
- **Hover state:** `transform: translateY(-2px)` + accent underline, 200ms `cubic-bezier(0.16, 1, 0.3, 1)`
- **Focus ring:** 2px gold, 4px offset, never hidden

## Accessibility

- All text tokens meet WCAG AA against `--bg`
- Focus visible on every interactive element
- Reduced-motion honored on all scroll + autoplay animation
- Spanish-first content. `aria-label` values in Spanish
- Touch targets ≥ 44px
- `<h1>` → `<h2>` → `<h3>` hierarchy preserved, no skipping
- Video hero includes `<track kind="captions">` when lyrics are visible
- Keyboard-only navigation works end-to-end

## Information architecture

### Homepage (fan-first)

1. Hero (video + asymmetric logo + eyebrow + meta chips)
2. Marquee strip
3. Próximas fechas (`<TourTable>`, next 5 shows + "Ver todas" link)
4. Artwork shelf (Repertorio top streams + Discografía)
5. BTS film strip (3 recent photos)
6. Integrantes (bento grid)
7. Redes sociales (large icons + latest-post previews)
8. Trust strip (testimonials, venues played)
9. Footer (press link, booking deep-link, socials, legal)

### `/contratacion` (promoter-first)

1. Full-bleed cover + band name + "Press Kit" eyebrow
2. 2-col spread — bio left, form right
3. Tech rider bullets + downloadable PDF
4. Photo reel
5. Contact footer

### `/prensa` (press kit standalone)

- Photo downloads, logo bundle, tech rider PDF, short + long bio, high-res album art

## Don't

- Gradient blobs or glow decorations
- Centered stock-hero + CTA template
- Default Tailwind/shadcn card grids
- Gold-dominant palette (wedding-invite feel)
- Uniform padding across all sections
- More than 1 marquee per page
- AOS `zoom`, `flip`, `slide-`* — `fade` only
- Cormorant for body text
- Drop shadows on UI elements
- English-first copy
- Stock imagery — real band photos only

## Verification

Before any design-adjacent PR ships:

1. `cd web && bun dev` — visual check at 320 / 768 / 1280 / 1920
2. Lighthouse on `/` and `/contratacion` — LCP < 2.5s, CLS < 0.1, TBT < 200ms
3. Playwright + axe-core — zero serious violations
4. Keyboard tab-through — every CTA reachable, focus visible
5. `prefers-reduced-motion` toggle — no autoplay, no marquee, no scroll-trigger
6. Contrast audit — every new token pair against `--bg`
7. `/design-review` skill — final gate

## History

- 2026-04-26 — `/contratacion` bio section restructured: wall-of-text split into lede (Cormorant italic, `--gold-shadow` left hairline), body paragraph, and styled `<ul>` with em-dash gold markers. Confirms token roles: `--accent` (turquoise) = links/focus only; gold gradient = CTAs/labels; `--gold-shadow` = decorative hairlines.
- 2026-04-22 — Palette elevated to premium: `--bg` deepened to `oklch(8%)`, `--bg-sunk` to `oklch(5%)`. Gold expanded to 4-stop metallic gradient range (`--gold`, `--gold-mid`, `--gold-shadow`, `--gold-dim`). `--accent-hot` replaced by `--burgundy-glow` (glow-only) + `--burgundy-hot` (marquee/SOLD OUT). Turquoise demoted from CTA primary to link/focus only.
- 2026-04-21 — Semantic `--color-success` / `--color-error`; tour sold-out tag copy locked to English `SOLD OUT` (see `<TourTable>`).
- 2026-04-18 — Initial DESIGN.md written via `/design-consultation`. Audience locked: fans lead, promoters deep-link. Accent locked: Veracruz turquoise. Type system locked: Cormorant demoted, Inter + JetBrains Mono added.


# Mafia Tumbada — Design System

> Source of truth for visual direction, design tokens, components, and motion rules.
> Any PR that touches the marketing site must reconcile with this file.
> If this file and the code disagree, update one, do not drift.

## Direction

**Gótico Tumbado** — black canvas, gold gothic lettering, red neon accent.

Near-black surfaces, gold gradient on display type, red-orange reserved for
rules, marquee and glow. Grenze Gotisch as the signature blackletter display
face; Archivo for body and UI; JetBrains Mono for tabular data.

Why this direction: the band already has one. Their billing wordmark on event
flyers is a **gold gradient gothic "M⚡T MAFIA TUMBADA"** with a lightning bolt
through the monogram, and their stage backdrop is a **red-orange neon MT**. The
site's previous direction (Cormorant Garamond, coastal turquoise) matched
nothing the band actually uses. Gold carries identity; red carries live energy
and keeps us off the black-and-gold-only template that Peso Pluma, Fuerza
Regida and Carín León all converge on.

## Audience

- **Primary: fans** — music, videos, socials land above the fold
- **Secondary: promoters** — `#contratacion` deep-linked from the Instagram bio

## Tokens

### Color (OKLCH)

```css
:root {
  /* Surfaces */
  --bg: oklch(7% 0 0);                    /* near-void black */
  --bg-raised: oklch(11% 0.006 60);       /* cards — faint warm tint */
  --bg-sunk: oklch(5% 0 0);               /* hero wells */

  /* Ink */
  --text: oklch(95% 0.008 85);            /* warm paper-white */
  --text-muted: oklch(82% 0.008 85);      /* body on photo scrims */
  --text-faint: oklch(58% 0.01 85);       /* mono meta, captions */

  /* Gold — identity. Gradient range, mirrors the flyer wordmark. */
  --gold-peak: oklch(88% 0.14 88);        /* gradient highlight */
  --gold: oklch(78% 0.15 85);             /* flat gold, eyebrow use */
  --gold-mid: oklch(66% 0.13 80);         /* gradient midtone */
  --gold-shadow: oklch(50% 0.10 78);      /* gradient base, hairlines */
  --gold-dim: oklch(38% 0.07 75);         /* hairline dividers only */
  --gold-gradient: linear-gradient(135deg, var(--gold-shadow), oklch(82% 0.15 86), var(--gold-mid));
  --gold-text-gradient: linear-gradient(168deg, var(--gold-shadow) 0%, var(--gold-peak) 38%, oklch(72% 0.15 82) 62%, oklch(48% 0.09 76) 100%);

  /* Red neon — live energy, from the stage backdrop */
  --red: oklch(62% 0.22 30);              /* rules, marquee, bolt */
  --red-link: oklch(72% 0.19 32);         /* links, inline accents */
  --red-glow: oklch(52% 0.20 28);         /* box-shadow / drop-shadow only */

  --border: oklch(19% 0.006 85);
  --focus-ring: oklch(78% 0.15 85 / 0.7);

  --surface: var(--bg-raised);
  --surface2: oklch(14% 0.005 90);
  --muted: var(--text-muted);
  --color-brand: var(--gold);
  --color-border: var(--border);
}
```

**Gold text gradient** (display type, wordmark, section headings):

```css
color: var(--gold);
background-image: var(--gold-text-gradient);
-webkit-background-clip: text; background-clip: text;
-webkit-text-fill-color: transparent;
@supports not ((background-clip: text) or (-webkit-background-clip: text)) {
  -webkit-text-fill-color: currentColor;
}
```

Always pair with a plain `color` fallback declared *before* the clip, so the
text is never invisible where `background-clip: text` fails.

**CTA gradient** (primary buttons):

```css
background: linear-gradient(135deg, var(--gold-shadow), oklch(82% 0.15 86), var(--gold-mid));
color: oklch(10% 0 0);
box-shadow: 0 0 34px var(--red-glow) / 0.35;
```

**Color rules:**

- Gold: display type, section headings, the MTO monogram, primary CTA
  backgrounds. Never body text.
- Red: 28px rules before eyebrows, the marquee strip, the hero lightning bolt,
  link text, and glow via `box-shadow` / `drop-shadow`. **Never a background
  behind body text**, never a flat fill on a large surface.
- `--gold-shadow` measures **3.42:1** against `--bg` and therefore may only
  appear as a gradient stop or a hairline divider — never as standalone text.

### Measured contrast against `--bg`

| Token | Ratio | Verdict |
|---|---|---|
| `--text` | 18.02:1 | AAA |
| `--text-muted` | 11.95:1 | AAA |
| `--text-faint` | 4.87:1 | AA |
| `--gold` | 10.32:1 | AAA |
| `--gold-peak` | 14.47:1 | AAA |
| `--red-link` | 7.52:1 | AAA |
| `--red` | 5.16:1 | AA |
| `--gold-shadow` | 3.42:1 | **decorative only** |

Ink on gold CTA: 11.7:1. Ink on red marquee: 5.03:1. Recompute this table
whenever a token moves — do not assume.

### Typography

```css
:root {
  --ff-display: 'Grenze Gotisch', Georgia, serif;
  --ff-body: 'Archivo', system-ui, -apple-system, sans-serif;
  --ff-mono: 'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace;

  --fs-eyebrow: 0.75rem;
  --fs-body: clamp(1rem, 0.95rem + 0.2vw, 1.125rem);
  --fs-lede: clamp(1.25rem, 1rem + 0.8vw, 1.5rem);
  --fs-h3: clamp(1.5rem, 1.2rem + 1vw, 2rem);
  --fs-h2: clamp(2.5rem, 1.8rem + 3vw, 4rem);
  --fs-h1: clamp(3.5rem, 2rem + 8vw, 9rem);
  --fs-monogram: clamp(2rem, 1.6rem + 1.4vw, 2.5rem);

  --lh-tight: 0.95;
  --lh-body: 1.55;
  --tracking-eyebrow: 0.18em;
  --tracking-display: -0.02em;
}
```

**Typography rules:**

- Grenze Gotisch: `h2`, `h3`, release titles, the MTO monogram. Weight 600–700.
  Never body, never below 24px — blackletter loses legibility fast.
- Grenze Gotisch carries full Spanish diacritics (á é í ó ú ñ ü ¿ ¡). Verify any
  replacement face does too before swapping — most free blackletter does not.
- Archivo: body, UI labels, buttons.
- JetBrains Mono: eyebrows (ALL CAPS, `--tracking-eyebrow`, `--red-link`),
  meta chips, phone numbers, `tabular-nums`.
- `text-wrap: balance` on headings, `text-wrap: pretty` on body paragraphs.
- Cormorant Garamond and Inter are removed — do not add back.

### Spacing

Unchanged from the previous system; the scale still holds.

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
  --radius-card: 0;
  --radius-pill: 999px;
}
```

**Spacing rules:**

- No uniform padding. Major sections `--space-section`; editorial blocks
  `--space-lg`; strips `--space-md`.
- `--radius-card: 0` — sharp, poster-like. `--radius-pill` for chips only.

## Layout

- 12-col grid desktop, 4-col tablet, flow mobile. `gap: clamp(1rem, 2vw, 2rem)`
- **Header:** fixed, 76px desktop / 60px mobile, `oklch(7% 0 0 / 0.55)` with
  `backdrop-filter: blur(12px)` and a `--border` hairline. Left: the **MTO**
  monogram in gold gothic. Right: three mono nav links desktop, a 44px hamburger
  mobile. **No logo image in the header** — the monogram replaces it.
- **Hero:** full-bleed looping video with scrims + film grain; copy left-aligned
  in the container, layered above. The `<h1>` is the existing
  `/icon/mafiatumbada.webp` logo, not type. No centered stock-hero.
- **Artwork grid:** 3-col cards desktop, single-column rows on mobile.
- **Integrantes grid:** `auto-fit` / `minmax(200px, 1fr)`.
- **BTS strip:** 3-photo horizontal film reel bleeding to page edges.

### Hero anatomy

Order, top to bottom, left-aligned:

1. Red 28×2px rule + mono eyebrow `SITIO OFICIAL · XALAPA, VER.`
2. `<h1>` — the logo image, 400px desktop / 215px mobile
3. Lede paragraph, `max-width: 30rem`
4. Meta chips (desktop only): CORRIDOS TUMBADOS · NORTEÑO · REGIONAL MX · DESDE 2021
5. Primary WhatsApp CTA, 52px tall, full-width on mobile

**Hero video** — `public/video/hero.mp4`, mounted by `src/lib/heroVideo.ts`:

```html
<video class="hero-video" muted playsinline loop aria-hidden="true" preload="none">
  <source data-src="/video/hero.mp4" type="video/mp4" />
</video>
```

- `data-src`, not `src` — `mountHeroVideo()` promotes it after first paint so
  the video never competes with LCP.
- `object-fit: cover`, `muted playsinline loop`, `aria-hidden="true"`.
- A poster still must render behind it so the hero is never empty on slow
  connections or when autoplay is refused.
- Under `prefers-reduced-motion: reduce` the video does not autoplay; the poster
  stands in.

**Hero scrim stack** — three layers over the video, in order:

```css
linear-gradient(90deg, oklch(6% 0 0) 4%, oklch(6% 0 0 / 0.82) 34%,
                oklch(6% 0 0 / 0.25) 72%, transparent 100%);  /* copy legibility */
linear-gradient(0deg, oklch(7% 0 0) 0%, transparent 42%);      /* base blend */
box-shadow: inset 0 0 180px 40px oklch(52% 0.20 28 / 0.22);    /* red glow */
```

The logo carries `mix-blend-mode: screen` plus layered gold and red
`drop-shadow()`; it needs dark pixels beneath it, which is what the first scrim
guarantees. Never place it over a bright frame without one.

## Components

Each lives in `src/components/` and must respect the tokens above.

1. `<ArtworkShelf>` — release cards, cover art or initials fallback, stream link
2. `<Marquee>` — single-use per page, red strip, CSS translate, pausable on hover
3. `<FilmStrip>` — 3-photo BTS row, bleeds to page edges
4. `<MemberCard>` — circular grayscale portrait, role eyebrow, name, IG link
5. `<Eyebrow>` — red rule + ALL CAPS mono, `--red-link`, tracked `0.24em`
6. `<Seo>` — meta, canonical, structured data

The header and hero are inline in `src/pages/index.astro`, not components.

## Decoration

- **Film grain:** SVG `feTurbulence` overlay, `opacity: 0.16`,
  `mix-blend-mode: overlay`, hero and photo sections only
- **Red rules:** 28×2px, immediately before every eyebrow
- **Lightning bolt:** inline SVG, `--red`, with a red `drop-shadow` glow. It
  echoes the band's own M⚡T monogram — draw it, never a glyph or emoji
- **Marquee:** `CORRIDOS TUMBADOS · XALAPA · DESDE 2021 ·` repeating on `--red`,
  1 per page max
- **No drop shadows on UI.** Shadows are for photos, the logo, and CTA glow only

## Motion

- `prefers-reduced-motion` honored: disables marquee, hero autoplay, scroll reveal
- **AOS:** `fade` and `fade-up` only. `zoom-in`, `flip`, `slide-*` forbidden
- **Marquee:** 60s linear infinite, pause on hover
- **Hover:** `translateY(-2px)` + accent underline, 200ms `cubic-bezier(0.16, 1, 0.3, 1)`
- **Focus ring:** 2px `--focus-ring`, 4px offset, never hidden

## Accessibility

- Every text token meets WCAG AA against `--bg` — see the measured table above
- `--gold-shadow` is decorative only; it fails AA as text
- Gold gradient text needs a solid `color` fallback declared before the clip
- Focus visible on every interactive element
- Reduced-motion honored on all scroll + autoplay animation
- Spanish-first content; `aria-label` values in Spanish
- Touch targets ≥ 44px, including the mobile hamburger
- `<h1>` → `<h2>` → `<h3>` preserved, no skipping
- The hero `<h1>` is an image: its `alt` must read `Mafia Tumbada`
- Blackletter is decorative by nature — never set body copy or form labels in it

## Information architecture

Single static page. `/contratacion` and `/prensa` were removed in the static
rebuild; booking converts through WhatsApp.

1. Header (MTO monogram + nav)
2. Hero (video + logo + eyebrow + lede + chips + WhatsApp CTA)
3. Marquee strip
4. Música — release cards, Apple Music link, video row (`#musica`)
5. BTS film strip
6. Bio — "El sonido de Xalapa"
7. El grupo — integrantes grid (`#grupo`)
8. Contratación — copy, urgency, WhatsApp CTA, phone (`#contratacion`)
9. Footer (socials, legal)

No tour or fechas section: deliberately excluded, 2026-09-09. The band does play
dated shows, but a hand-maintained list goes stale and an empty one reads worse
than none.

**Booking phone:** `+52 228 353 8827` (`wa.me/5212283538827`). The older
`+52 1 228 835 1464` is wrong and appears on no band-controlled surface.

## Don't

- Gradient blobs or glow decorations beyond the specified red glow
- Centered stock-hero + CTA template
- Default Tailwind/shadcn card grids
- Red or gold as a background behind body text
- `--gold-shadow` as text
- Blackletter below 24px, or in body copy, labels, or form fields
- A logo image in the header — the MTO monogram is the header mark
- More than 1 marquee per page
- AOS `zoom`, `flip`, `slide-*` — `fade` only
- Emoji or dingbats as icons — inline SVG only
- English-first copy
- Stock imagery — real band photos only

## Verification

Before any design-adjacent PR ships:

1. `bun dev` — visual check at 320 / 768 / 1280 / 1920
2. Lighthouse on `/` — LCP < 2.5s, CLS < 0.1, TBT < 200ms
3. Playwright + axe-core — deferred: `e2e/` is empty and neither dependency is
   installed. Accessibility verified manually against contrast, name, keyboard,
   touch-target and reduced-motion criteria below.
4. Keyboard tab-through — every CTA reachable, focus visible
5. `prefers-reduced-motion` toggle — no autoplay, no marquee, no scroll-trigger
6. Recompute the contrast table for any token that moved
7. Confirm gold gradient text still renders with `background-clip` disabled
8. Confirm Spanish diacritics render in Grenze Gotisch at every display size

## History

- 2026-09-09 (pm) — **Direction replaced.** Veracruz Noir retired in favour of
  Gótico Tumbado after scoping pesopluma.com, fuerzaregida.com and
  carinleon.com, then harvesting the band's own socials: their flyer billing
  wordmark is gold gothic with a lightning bolt and their stage backdrop is red
  neon, neither of which the old system reflected. Cormorant Garamond → Grenze
  Gotisch, Inter → Archivo, turquoise links and burgundy retired in favour
  of `--red`. Header mark changed from the logo image to an MTO monogram; the
  logo moves to the hero `<h1>` over the full-bleed video. Fechas section
  considered and declined. Booking phone corrected to `+52 228 353 8827`.
- 2026-09-09 (am) — Reconciled with the static single-page rebuild: IA rewritten
  to the eight sections that ship, `/contratacion` and `/prensa` removed,
  `<TourTable>`, `<PressKitSpread>` and `<SignatureCTA>` dropped, bento member
  grid replaced by an `auto-fit` grid.
- 2026-04-26 — `/contratacion` bio section restructured into lede, body and
  styled list.
- 2026-04-22 — Palette elevated to premium: `--bg` deepened, gold expanded to a
  4-stop metallic range, turquoise demoted from CTA to link/focus.
- 2026-04-21 — Semantic success/error tokens added.
- 2026-04-18 — Initial DESIGN.md written via `/design-consultation`.

# Mafia Tumbada, A Carretera — Design System

> Source of truth for the site's look (owner's pick A, 2026-11-12 21:56; tweak bar settings: A's defaults).
> Build: `src/pages/index.astro`, `src/components/Boton.astro`, `src/components/Icono.astro`.
> References: `docs/design/references.md` (rows tagged **A:**). Direction notes: `docs/design/directions.md` › A.
> The 2026-11-09 truck prototype (tabs over a live three.js scene) is history: `docs/prototipo-camion.md`.

## Overview
- **One line:** the band's black pickup on a night highway, rendered in Cycles, under a black-and-gold one-page site.
- **Audience and actions** (`brief.md`): fans → **Escuchar** (latest release on Spotify); bookers → **Contratar**
  (WhatsApp with date and city prefilled). Escuchar sits in the hero; Contratar in the header, the hero and the close.
- **Untouchable:** band name, logo, WhatsApp only, no tour dates, every line from `research/contenido/` or SPEC §8.

## Colors
```css
:root {
  --bg: #000;                       /* the logo's black faces (public/icon/mafiatumbada.webp) */
  --ink: oklch(95% 0.008 85);       /* warm white, directions.md › A */
  --muted: oklch(80% 0.01 85);      /* secondary text; 4.5:1 on --veil (revisar.sh contrast) */
  --gold: oklch(80% 0.13 82);       /* the logo's bronze-gold bevel, lifted for 11.1:1 on #000 (tweak bar) */
  --gold-deep: oklch(62% 0.11 70);  /* scrollbar only */
  --veil: rgb(0 0 0 / 0.62);        /* references.md › contacto: veil under text over the rendered scene */
  --line: oklch(100% 0 0 / 0.14);   /* section rules, cover borders, thumbnail placeholder */
}
```
- One accent: gold. Filled gold = the two primary actions (Escuchar, Escribir por WhatsApp). Gold text = member
  Instagram links, hover on release titles and video titles. Body links stay ink.

## Typography
- Display: **Saira Condensed 800**, uppercase, slanted (directions.md › A: the lean echoes the logo's slant). The package
  has no italic file, so the slant is the browser's synthetic oblique, exactly as in the picked prototype.
  Alternative offered on the tweak bar and not picked: Reddit Sans Condensed 900 (references.md › hero, urielurbina).
- Text: **Saira** 400/600. Self-hosted with `@fontsource` (latin subsets only).
- Sizes: name `clamp(64px, 13vw, 200px)`, section heads `clamp(44px, 7vw, 96px)`, body 17px/1.55.

## Layout
Fixed header (logo, three section links from 900 px, Contratar). Hero 100svh, name bottom-left over a veil gradient.
Sections: Música (one horizontal strip + platform buttons), Videos (1 col; at ≥900 px 2fr/1fr/1fr with the live video
spanning two rows), La banda (1 col; 3 cols at ≥900), Contratación (panel on veil over the scene), footer socials.
Gutter `clamp(16px, 4vw, 64px)`. Touch targets ≥ 44 px.

## Elevation & Depth
Depth comes from the rendered scene only. No shadows, no cards. Text over images always sits on `--veil`.

## Shapes
Square everywhere: buttons, covers, panel. No pill (owner: only if picked over 2–3 alternatives).

## Components
| Component | Source |
|---|---|
| Hero poster + loop (poster = loop frame 0, portrait/landscape by `media`) | references.md › hero (arraisballet) |
| Loop plays only while visible, never under reduced motion | references.md › hero (landonorris render-while-visible) |
| Pause/play toggle for the loop | references.md › contacto (teamusa motion toggle), placed on the hero it controls (WCAG 2.2.2) |
| Release strip (scroll-snap, passes like road signs) | references.md › musica (landonorris horizontal gallery) |
| Video thumbnails at hqdefault 480 px, link out, no embedded player | references.md › video (dfm rendition sizing; SPEC §3) |
| Member cards (photo, name, role, Instagram) | content: `research/contenido/members.ts`. The cab camera stops (kage row) are not built yet |
| Contact panel on veil over the scene | references.md › contacto (MTO veil note) |
| `Boton.astro`: square, gold edge, fill wipes up 500 ms cubic-bezier(.65,0,.35,1), press dips 2 px in 90 ms | references.md › botones (rafadesign wipe, boleto press). Working version: the buttons-icons pair chain replaces this file |
| `Icono.astro`: static play glyph | working version; morphing icons come from the pair chain (botones Rive row, unproven) |

## States matrix
| Component | default | hover | focus-visible | pressed / selected | disabled | loading | empty | error | **domain** | a11y |
|---|---|---|---|---|---|---|---|---|---|---|
| Boton (line) | gold edge, ink text | gold wipes up, black text | same wipe + 3px gold ring | dips 2 px | n/a: links only | n/a: static link | n/a: always has a label | n/a: static link | n/a | link text names the action |
| Boton (filled) | gold fill, black text | n/a: already filled, cursor only | 3px gold ring | dips 2 px | n/a | n/a | n/a | n/a | n/a | link text names the action |
| Release card | cover + title + type | title turns gold | 3px gold ring + gold title | n/a: link | n/a | lazy image, `--line` border holds the box | n/a: 9 fixed releases | n/a: static | n/a | cover `alt=""`, title is the name |
| Video card | thumb + play + title | title turns gold | 3px gold ring | n/a: link | n/a | lazy, `--line` fill holds 16:9 | n/a | n/a | live video first | thumb `alt=""`, icon hidden |
| Loop toggle | "Pausar video" | ink text | 3px gold ring | `aria-pressed=true`, "Reproducir video" | n/a | n/a | n/a | play() rejected: poster stays | reduced motion: starts paused | real `<button>`, hidden until JS runs |
| Hero media | poster | n/a | n/a: `aria-hidden` | n/a | n/a | poster until the loop plays, 0.4 s fade | n/a | no video: poster | reduced motion: poster | `aria-hidden`, `alt=""` |

## Do's and Don'ts
- Do: plain section names, real content only, poster = loop frame 0, square controls.
- Don't: eyebrows, kickers or numbering on headings; an accent word in gold inside the name; pills; glow blobs; fade-in on
  every section; embedded YouTube players.

## Open (the owner's; placeholders in use)
- WhatsApp number: `socials.ts` (228 353 8827) is used; SPEC §4 says 228 835 1464.
- Lead release: Putifresa (catalog order); "POR EL BLOC" is not in the catalog.
- Covers are 160 px (soft in the strip at 1440); logo is a 794 px webp.
- Tripo figures in the cab (members stop) are not on the page; ToS §5.2.1 is unresolved.
- Known scene flaws: low-poly CC0 pickup, dark-lens bug in the 16:9 loop, no dusk loop
  (the truck model `blender/assets/camion/pickup-quaternius.glb` is missing from disk, so Cycles can't re-render).

## Verification
Report: `docs/design/build-report.md` (revisar.sh web 390/1440, slop-check, refs-check).

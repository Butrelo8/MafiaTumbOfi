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
  --ink: oklch(95% 0.008 85);       /* #f1eee9, warm white, directions.md › A */
  --muted: oklch(80% 0.01 85);      /* #c1bdb7, secondary text; over the scene it sits on --veil: not verified (no tool measures text over images) */
  --gold: oklch(80% 0.13 82);       /* #e7b551, the logo's bronze-gold bevel, lifted for 11.1:1 on #000 (tweak bar) */
  --cap: oklch(17% 0.01 85);        /* #110f0a, the cap of a plain Tecla (Boton.astro) */
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

| Role | Face | Size / leading | Where |
|---|---|---|---|
| Name | Saira Condensed 800 caps | clamp(64px, 13vw, 200px) · 64 · 187 / 0.9 | hero name |
| Section head | Saira Condensed 800 caps | clamp(44px, 7vw, 96px) · 44 · 96 / 0.9 | Música, Videos, La banda, Contratación |
| Card head | Saira Condensed 800 caps | 32 · 26 / 0.9 and 1 | member names, small display |
| Lead | Saira 400 | 18 · 20 · 22 / 1.55 | hero line, contact line |
| Body | Saira 400 | 17 / 1.55 | paragraphs |
| Small | Saira 400 | 15 / 1.55 | release subtitles, roles |
| Title | Saira 600 | 17 / 1.55 | release titles, header links |
| Control | Saira 600 | 16 / 1 · 14 / 1 for the quiet toggle | Tecla labels |

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
| `Boton.astro` (Tecla): a square cap on a 4 px dark-gold lip; press sinks the cap 3 px onto the lip in 80 ms; trailing chevron nudges 4 px on hover and focus (hover only under `(hover: hover)`) | references.md › botones (todoist two-layer lip, nothing.tech chevron). Authored, not from a ficha: the 4 px nudge, the translateY press, the 250 ms icon reaction. Owner's pick from stills, 2026-11-12 |
| `Boton.astro` as the loop toggle (a `<button>`, no `href`): icon + label, ring while buffering | references.md › iconos (rafadesign sound toggle; its `aria-pressed` half is not borrowed: the label swap names the state) |
| `Boton.astro` `discreto` (the loop toggle): a quiet Tecla for utility controls: 2 px lip, veil cap, 14 px label, 46 px tall | references.md › botones (same Tecla source); authored: the quieter hierarchy, so the toggle does not read as a second CTA under the header's Contratar |
| `Icono.astro`: play and pause paths with the same eight points, so MorphSVG mixes them | references.md › iconos (GSAP row). Crafted morph inside 250 ms: 60 ms shrink to .88, 90 ms closing the two bars into one block (the designed middle shape), 100 ms from the block into the other glyph while the scale overshoots with `back.out(2.4)`, settle. Library gap: no measured icon morph exists, unproven |
| Scene prop, pantalla móvil (owner's pick C, 2026-11-13): a box truck with the side LED screen framed by a marquee of warm bulbs, the rear screen the same; LED look = pixelated image under a round-dot mask, emissive; the rear screen shows the empty state ("Próximas fechas · Muy pronto"), never invented dates | references.md › Scene props, phase 1 › pantalla (peru-retail LED box trucks); `blender/utileria.py` `pantalla-c` |
| Scene prop, green signs (owner's pick B, 2026-11-13): a bandera cantilever from the right shoulder, the sign over the band's lane; SCT green field, white retroreflective legend and border, clearance over 5.5 m; shipped lettering in "tipografía México" (stills use Bahnschrift) | references.md › Scene props, phase 1 › portico (NOM-034-SCT2/SEDATU-2022; the El Puertecito cantilever photo); `blender/utileria.py` `portico-b` |
| Scene prop, licence plate (owner approved 2026-11-13 03:36): after the current Veracruz private-car plate: white field, VERACRUZ heading, olive stepped fret in the top corners, faint crest watermark, QR top right (the counted `/wa/` route), slogan logo, TRANSPORTE PRIVADO AUTOMOVIL, 30, red T; ours: MT-420-VER, the MT monogram in the national-seal spot, a simplified crest lookalike. Seen from the scene-6 camera | references.md › Scene props, round 2 › placa (the owner's reference image; NOM-001-SCT-2-2016 for size and slots); `blender/placa_veracruz.py`, `blender/utileria.py` `placa3` |
| Motion tokens: `--dur-press` 80 ms, `--dur-state` 250 ms, `--dur-fill` 500 ms, `--ease-out` | references.md › estados (boleto-perforado timing family; bands 40-80, 150-250, 350-500) |

## Motion
One language for every button and icon: 80 ms press, 250 ms state change and icon morph, one easing `--ease-out`. Only `transform`
and `opacity` animate, with one exception: MorphSVG animates the path's `d` from JS on a 24 px SVG (cheap to paint; `revisar`
cannot see it, so it is judged from a frame strip). Under `prefers-reduced-motion` nothing loops (the loading ring is a
static glyph, "Cargando video" is a visible label), the icon swaps in one frame, and the first frame after a click equals the settled one.

## Scene version needs
The final MTO is a scroll-driven 3D scene with band models in the truck and social buttons on the render. Every button here has a
scene twin (Tecla: a key on the cab dash; the cap and lip are an extrusion, the press is a translation).
- The DOM twin stays a focusable `a` or `button` with the same accessible name, kept in sync with the prop.
- DOM focus is mirrored onto the prop as a visible ring or glow.
- The projected hit area is at least 44 px at 390.
- Each state maps to an animation clip or a material parameter (rest, hover, press, loading, done).
- Reduced-motion parity: the prop swaps state with no loop and no intermediate pose.
Open lab question for that phase, unproven: Rive for detailed icon morphs or as a texture on a prop (its web runtime is a 199 KB
transfer, over the 150 KB cap, `web/site-reading-fichas/landonorris-com/speed-390-throttled.json`).

## States matrix
| Component | default | hover | focus-visible | pressed / selected | disabled | loading | empty | error | **domain** | a11y |
|---|---|---|---|---|---|---|---|---|---|---|
| Boton (plain) | dark cap, ink text, gold-deep edge and lip | cap lightens (an overlay fading in, opacity only), chevron nudges 4 px (hover devices only) | 3px gold ring, chevron nudged | cap sinks 3 px onto the lip | n/a: links only | n/a: off-site links open another app and this page stays alive, so a busy state would stick | n/a: always has a label | n/a: static link | n/a: not date-bound | link text names the action |
| Boton (filled) | gold cap, black text, gold-deep lip | cap lightens, chevron nudges | 3px gold ring | cap sinks 3 px | n/a: links only | n/a: as above | n/a: always has a label | n/a: static link | n/a: not date-bound | link text names the action; Escuchar names its destination |
| Release card | cover + title + type | title turns gold | 3px gold ring + gold title | n/a: link | n/a: links only | lazy image, `--line` border holds the box | n/a: 9 fixed releases | n/a: no remote data | n/a: no dates shown (no tour dates) | cover `alt=""`, title is the name |
| Video card | thumb + play + title | title turns gold | 3px gold ring | n/a: link | n/a: links only | lazy, `--line` fill holds 16:9 | n/a: 5 fixed videos | a missing YouTube thumb leaves the `--line` box and the title | live video first | thumb `alt=""`, icon hidden |
| Loop toggle | pause icon, "Pausar video" | cap lightens | 3px gold ring | cap sinks 3 px; the label and icon swap to "Reproducir video" (no `aria-pressed`) | n/a: always usable | ring and "Cargando video" while the video is buffering; ring static under reduced motion | n/a: one fixed loop | `play()` refused: back to "Reproducir video"; source fails: toggle hidden, poster stays | after a tap starts the video the cap taps once (done); reduced motion: starts paused | real `<button>`, hidden until JS runs; the label carries the state |
| Hero media | poster | n/a: not interactive | n/a: `aria-hidden` | n/a: not interactive | n/a: not interactive | poster until the loop plays, 0.4 s fade | n/a: poster always ships | no video: poster | reduced motion: poster | `aria-hidden`, `alt=""` |

## Do's and Don'ts
- Do: plain section names, real content only, poster = loop frame 0, square controls.
- Don't: eyebrows, kickers or numbering on headings; an accent word in gold inside the name; pills; glow blobs; fade-in on
  every section; embedded YouTube players.

## Open (the owner's; placeholders in use)
- WhatsApp number: `socials.ts` (228 353 8827) is used; SPEC §4 says 228 835 1464.
  The scene plate's QR (`blender/placa_veracruz.py`, `WA`) points at the counted route `https://mafiatumbada.com/wa/5212283538827`,
  pending the band's confirmation. To swap it: edit `WA`, run `uv run -q --with pillow --with qrcode python -I blender/placa_veracruz.py`,
  then re-render `placa3` with `blender/utileria.py`. The site's live WhatsApp buttons need the same swap.
- Scene props (radio + cassette + dash key, glovebox junk, stickers, pantalla móvil, sign gantries, plate, bed props): three
  options each, waiting on the owner's pick (`docs/design/escenas/utileria/index.html`; sources in `references.md` › Scene props,
  phase 1). Each picked element joins Components with its source row; none is a rule yet.
- Lead release: Putifresa (catalog order); "POR EL BLOC" is not in the catalog.
- Covers are 160 px (soft in the strip at 1440); logo is a 794 px webp.
- Tripo figures in the cab (members stop) are not on the page; ToS §5.2.1 is unresolved.
- Known scene flaws: low-poly CC0 pickup, dark-lens bug in the 16:9 loop, no dusk loop
  (the truck model `blender/assets/camion/pickup-quaternius.glb` is missing from disk, so Cycles can't re-render).

## Verification
Report: `docs/design/build-report.md` (revisar.sh web 390/1440, slop-check, refs-check).

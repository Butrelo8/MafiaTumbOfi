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
| Scene camera 3 (owner's pick B, 2026-11-14): the hold at the driver's rear door, looking forward-left at the side screen, the manager's window on the right of frame | references.md › escenas; `blender/utileria.py` `esc3-hombro` |
| Scene light 4 (owner's pick B, 2026-11-14): the cab lit from inside (a warm 6 W point over each seat), the side left to the road lamps; `ESC4_LUZ = "cabina"` | references.md › escenas; `blender/utileria.py` `luz_costado`, `esc4-cabina` / `esc4-fin` |
| Prototype `/prototipo` (2026-11-16, not linked, `noindex`): the whole site over one fixed stage the scroll drives. Stage: `.escena`, the run preview (`public/prototipo/ruta.mp4`, Cycles 16 spp, 640×360) scrubbed by `currentTime`, and the band loop (`bucle.mp4`, Workbench) for the integrantes frames 647–743 and the loop; first paint is run frame 0 as a still | references.md › Prototype (teamusa video-que-avanza; kage anchors; arraisballet poster = first frame). Authored: the 0.25 vh / 0.5 vh anchors that map a section to its frame range, the 4 px per frame of travel, the 250 ms hold before the loop starts, the 4× scroll gain in the loop, the 3× catch-up after leaving it |
| Prototype scroll → loop: holding still in the station plays the loop; scrolling in moves 2–3 drives the loop clock until move 1, then the run takes over (`paso()` in `ruta.ts`); `?gain=N`, `?hud` for tuning | movimiento-plan.md › Band loop › Scroll exit; the gain and the catch-up are the plan's open "speed factor" question |
| Prototype veil bands (`.velo`): Música, Videos, La banda, Gira are full-width `--veil` bands with the scene bare between them (`.viaje`); La banda is a 520 px column so the cab stays visible | references.md › Prototype (contacto veil note; integrantes kage). Contrast over the moving image: not verified |
| Prototype placeholder (`.pendiente`): removed 2026-11-16, nothing on the page waits on text now; the rule stays here for the next gap | references.md › Prototype (ai-slop-tells, tell 6: labelled clay placeholder) |
| Prototype filled slots (2026-11-16): Videos › "Más en YouTube" (the catalog's other 9 titles, text rows); Gira (the plan's empty-state line + Instagram and Plaza Lerdo links, no dates); Contratación (the WhatsApp number as text). The 4th member (the manager, `elmanco420`, owner 2026-11-16) is a photoless row in La banda; no `.pendiente` box is left. Unrendered scenes are named in the footer note. The muted line under the Gira heading (slop-check tell 17, REVIEW) is the plan's empty-state fact (escenas-plan.md §5), not an aphorism: it says where the dates will appear | references.md › Prototype (video, gira, contacto rows; escenas-plan.md §5). The number is unconfirmed, see Open |
| Site `/` (2026-11-18, owner 11:37 "put it as if it were the whole page"): the prototype is `/` (indexable only when CI sets `PUBLIC_ALLOW_INDEXING=true`, else `noindex`); main's live Gótico home (not this look) is kept at `/anterior` (`noindex,nofollow`, not linked); A Carretera is in the history. The footer's scaffold note is a plain place line. Stage stills: `public/prototipo/parada-1..6.webp` (montaje-esc1..6, Tripo v5), one per stop, shown only while the run cannot show a frame (`.sin-video` hides the videos so a poster never covers them); the live run and loop remain the scene wherever they play | references.md › Site `/` (arraisballet poster = first frame). Authored: the 60 % viewport line that picks the stop in view |
| Site `/` merged from main (2026-11-18): Spotify and Instagram Teclas on the first screen (Spotify filled, the one primary); `data-placement` on header, hero, musica, video, grupo, gira, contratacion, footer and one delegated click listener to `POST /e`; the WhatsApp link is the `/wa/` counter; Plausible page views gated on `PUBLIC_PLAUSIBLE_DOMAIN`; the fan list stays parked (`docs/lista-de-fans.md`) | references.md › Site `/` (research/DESIGN.md › Conversion additions; docs/analytics.md). No new visual element: the Instagram button is a plain `Boton` |
| Live scene `/escena` (2026-11-19, owner 01:32 "put that scene in the home", moved off `/` 2026-11-23 when the owner made the video home production again; hidden preview): `/escena` is the live three.js scene with the six stop buttons (Cabina, Caja, Pantalla, Banda, Gira, Placa; Banda opens a second row Manager, Héctor, Alejandro, Diego); camera moves on click and keys, scroll does not; `noindex`, not linked, not in a sitemap. The video home is `/` again (indexable; `/anterior-home` redirects 301 to `/`), the Gótico one `/anterior`, `/vivo-secciones` redirects to `/`. Music, Videos, Gira dates and Contratación sections are not on it yet | references.md › Live home `/` (landonorris live scene; arraisballet poster = first frame). Authored: the six stops and nav row (the live-sections spike) |
| Video home back at `/` (2026-11-23, owner via the mothership: production shows the old design, the 3D scene is a preview): `src/pages/index.astro` is the former `anterior-home.astro` unchanged in layout and copy; added from the Gótico home / scene era: the full `Seo` component (OG, Twitter, canonical, no `noindex`; `PUBLIC_ALLOW_INDEXING=false` still adds it), `MusicGroup` JSON-LD, and Sentry gated on `PUBLIC_SENTRY_DSN`. It never imports three.js or `/vivo/*.glb` | references.md › Prototype (unchanged). Authored: nothing new; no sitemap exists in the repo to add `/` to or keep `/escena` out of |
| Opening (owner 2026-11-18 12:32; `Apertura.astro`, `apertura.ts`, ported to the live home): "MTO" is drawn (3 strokes, 0.7 s each, 0.45 s apart, then a 500 ms gold fill) over `--bg` from the first paint; `public/prototipo/apertura.mp4` starts downloading only after it (`trasPintar`), as do three.js and the GLBs; at least 2.4 s, at most 7 s; then the clip plays once (muted, a camera descent from above the truck into the cab, 6.5 s) and the layer fades out 500 ms once the live canvas has drawn its first frame (a fade, not a cut: the clip is a grey Workbench previz until the Cycles render lands). Page-first rule (owner 2026-11-23 06:16): the layer is a background (z 2, `pointer-events: none`) under the h1 and the nav, which are readable and usable from the first paint; nothing is `inert`; a click on the nav, Saltar (a 44 px pill, above the nav row) or Escape ends it. Skipped before the first paint for reduced motion, a `#anchor`, `?f`/`?parada`/`?toma`, and a return visit in the tab (`sessionStorage` `mto-apertura`); with JavaScript off it is hidden. Autoplay refused (Low Power Mode): straight to the scene | references.md › Live home `/` (realfood drawn lines; arraisballet poster = first frame; teamusa skip), › Page-first opening (cuberto h1 first, no video bytes in the first paint's queue; henriheymans gate = the trap). Authored: the 2.4 s / 7 s bounds, the stagger, the 10° skew |
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
- Scene props (radio + cassette + dash key, glovebox junk, stickers, pantalla móvil, sign gantries, plate, bed props; the bed is `caja4` B, picked 2026-11-14, dressed in `caja5` with the speaker, the beer crate and the
  inflatable alien; drinks in the cab still open, console or hand): three
  options each, waiting on the owner's pick (`docs/design/escenas/utileria/index.html`; sources in `references.md` › Scene props,
  phase 1). Each picked element joins Components with its source row; none is a rule yet.
- Lead release: Putifresa (catalog order); "POR EL BLOC" is not in the catalog.
- Covers are 160 px (soft in the strip at 1440); logo is a 794 px webp.
- Tripo figures in the cab (members stop) are not on the page; ToS §5.2.1 is unresolved.
- Known scene flaws: low-poly CC0 pickup, dark-lens bug in the 16:9 loop, no dusk loop
  (the truck model `blender/assets/camion/pickup-quaternius.glb` is missing from disk, so Cycles can't re-render).

## Verification
Report: `docs/design/build-report.md` (revisar.sh web 390/1440, slop-check, refs-check).

# Mafia Tumbada, truck prototype — Design System

> Source of truth for this prototype's look (branch `cc/goblindrone`, 2026-11-09). References: `docs/design/references.md`.
> Scene values (stops, presets, world): `src/lib/escena.json`, read by Blender and by the page. Last checked: 2026-11-09.

## Overview
- **One line:** the band's black pickup rolls down an endless highway at night (or dusk); each section is a camera stop around it.
- **Audience:** fans first (music, links); promoters second (`#contratacion`, deep-linkable).
- **The one action:** "Escribir por WhatsApp" (the only filled gold button). WhatsApp is the only contact path (`research/wayfinder/SPEC.md`).
- **Untouchable:** band name, WhatsApp link and socials from `research/contenido/`; no tour dates.
- **Direction:** Gótico Tumbado carried over from `research/DESIGN.md` (history, not rules) as the night preset's palette; owner asked for night **and** dusk (11-09), so both are presets of one scene. Not signed off.
- **Voice:** Spanish, plain section names; no invented copy (every line on the page comes from `research/contenido/`).

## Colors
```css
:root {
  --bg: #000;                         /* page ground behind the scene; source: research/DESIGN.md (bg) */
  --text: oklch(95% 0.008 85);        /* research/DESIGN.md --text */
  --text-muted: oklch(82% 0.008 85);  /* research/DESIGN.md --text-muted */
  --gold: oklch(78% 0.15 85);         /* identity: band's flyer wordmark (research/DESIGN.md) */
  --red: oklch(62% 0.22 30);          /* stage neon; panel rule only */
  --veil: rgb(0 0 0 / 0.62);          /* references.md › labels: lowest veil that keeps 4.5:1 on the brightest frame */
}
```
- Accent rule: filled gold goes on the WhatsApp button and the pressed time-of-day button; gold text on headings and the wordmark. **Banned for:** body links.
- **Current/selected:** tab = white text + 2px gold underline + `aria-selected`; time of day = filled gold + `aria-pressed`.
- Contrast: measured by `revisar.sh web` (see Verification).

## Typography
Pirata One (wordmark, panel headings; traced to the band's blackletter flyer wordmark), Archivo 400/600 (body, UI). No mono.

## Layout
Full-bleed scene (canvas, poster or loop behind). Header: wordmark left, time-of-day switch right. Panel bottom-left above the tab bar. Tab bar bottom, scrolls horizontally if it overflows at 390. Touch targets ≥ 44px.

## Elevation & Depth
Depth comes from the 3D scene only. Text sits on `--veil`; the wordmark has a 2px drop-shadow for legibility over the sky.

## Shapes
Panel: square, 3px red left rule. Tabs: square. Time switch and WhatsApp button: pill / 4px radius.

## Components
| Component | Source |
|---|---|
| Scene (canvas) + poster + loop fallback | references.md › hero (arraisballet poster = first frame; landonorris render-while-visible) |
| Tabs (4 stops) | references.md › camera-nav (kage anchors + damped move; rafadesign labelled stops); WAI-ARIA tabs pattern |
| Panel over scene | references.md › labels (veil) |
| Time-of-day switch | user: owner 11-09 (night + dusk presets) |
| Reduced motion / no WebGL | references.md › fallback (teamusa, landonorris) |

## States matrix
| Component | default | hover | focus-visible | pressed / selected | disabled | loading | empty | error | **domain** | a11y |
|---|---|---|---|---|---|---|---|---|---|---|
| Tab | muted text on veil | n/a: no hover style, cursor only | 3px gold ring | white text + gold underline | n/a: never disabled | n/a: tabs work before the scene loads | n/a: fixed 4 tabs | n/a: no remote data | current stop: selected | `role=tab`, arrows/Home/End |
| Time switch | muted text | n/a: cursor only | 3px gold ring | filled gold | n/a: never disabled | HDR loads, old preset stays until ready | n/a: two fixed presets | n/a: load failure keeps the old preset | night / dusk | `aria-pressed` |
| Scene | poster (Cycles frame 0) | n/a: not interactive | n/a: `aria-hidden` | n/a: not selectable | n/a: no disabled state | poster until first frame, 0.8s fade | n/a: always has content | no WebGL → loop video, or poster under reduced motion | moving / reduced motion: still road, camera cuts | `aria-hidden` |
| WhatsApp button | filled gold | n/a: cursor only | 3px gold ring | n/a: link | n/a: never disabled | n/a: static link | n/a: always present | n/a: static link | n/a: not date-bound | link text names the action |

## Do's and Don'ts
- Do: plain nav words; real content only; poster = loop frame 0.
- Don't: eyebrow lines, kickers or numbering on panels, glow blobs, invented stats or copy, fade-in on every panel.

## Verification
See the report in `docs/prototipo-camion.md` (weights, frame times, revisar, slop-check).

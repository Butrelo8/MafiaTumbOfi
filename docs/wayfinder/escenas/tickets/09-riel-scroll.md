---
title: Scroll drives the ride, the camera rail between the six stops
type: build
status: open
assignee:
gate:
blocked_by: [01]
closed_as:
gist:
---

## Question

Today, section buttons move the camera between the six stops, and scroll does nothing (`src/scripts/vivoSecciones.ts`,
header).

Plan v2 §1 asks for one camera rail driven by native scroll: section anchors, then progress, then damping, then the
position and look-at curves, with a field of view per segment. The world keeps streaming whether or not the visitor
scrolls.
- The scene-to-scene moves are the "Move to the next scene" column of plan v2 §1.
- The v3 move (`blender/transicion.py` `CAMINO`) is the first segment.
- The highway-sign gantries carry the section titles, and each one is also the section's DOM `h2`.

Page-first rule: the rail starts after first paint, and the page scrolls normally before it starts. Under
`prefers-reduced-motion` there is no rail: each scene shows its still over normal sections.

## Done-check

- A screen recording at 1440 of a scroll from scene 1 to scene 6, plus stills at each anchor.
- Keyboard (Tab and the arrow keys), a "saltar escena" link at each section start, and history and anchors all work.
- Reduced motion is checked.
- LCP and TTFF are no worse than ticket 01's "after" numbers, with the same script.

```sh
bun test && bun run build
```

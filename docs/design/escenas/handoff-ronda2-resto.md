# Handoff: what round 2 left open (2026-11-13, circudrone on `cc/nerddrone`)

Round 2 of the prop stills is done for the four props the mothership asked to re-render (1 radio → screen, 2 glovebox C cut,
6 plate A, 7 bed A). Picks 4 and 5 are recorded in `DESIGN.md` › Components. The contact page is
`docs/design/escenas/utileria/index.html` (round 1 moved to `ronda1.html`). The full brief for the open items is still
`handoff-fase1-ronda2.md`. Its run commands hold; the round-2 option names are `radio2-a,radio2-b,placa2-a,placa2-b,caja2-a,
caja2-a-esc2,caja2-b,caja2-b-esc2,guantera2-borde,guantera2-c`. Run `blender/pantalla_tablero.py` first; it writes the
screen faces into `tmp/utileria/`.

## Not started
- **Stickers mixed (pick 3).** These are not on the re-render list. The work is a `calcas2` builder with A/B/C styles across
  the four stickers and one faded or scuffed. The §2 rules still apply.
- **Live port fixes.** None of them is started: glass, pole lights and puddles, the RectAreaLight energy match, the re-capture
  with SSIM, the real-GPU fps and the heads retopo. Each is listed in `handoff-fase1-ronda2.md` › Live port fixes.

## Known limits of round 2
- **Glovebox junk: fixed (03:18).** The cause was the pivot. It was taken from the lowest verts, which are the back of the
  0.2 m-deep cut (y 1.3465). It now sits on the front skin at `GUANTERA.y` (1.234). One side wall of the shell sticks up beside the
  door; it is kept, because bin-style gloveboxes have walls.
- **Glovebox.** The faces in the handoff box run 0.2 m deep, so the door carries side walls, not a flat skin. The junk sits on
  a liner on the door's inside. The door turns about world X around a pivot that is not parented to the truck, so this works
  for stills only. The build needs the door parented to the truck.
- **Glovebox cut is destructive.** The `guantera2-*` options must stay last in `utileria.py`, because the dash keeps its hole
  for every later still in the same run.
- **Plate colours.** No source shows the 2026 Veracruz issue. Its colours are not verified, and the white field with black
  characters is kept from round 1 (see the references.md rows).
- **Screen face.** It is one static frame (PUTIFRESA, 1 of 9). Pass the release index to `pantalla_tablero.py` for another
  release. The stepping itself belongs to the build.

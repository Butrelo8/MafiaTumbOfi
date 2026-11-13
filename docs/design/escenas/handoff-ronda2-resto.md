# Handoff: what round 2 left open (2026-11-13, circudrone on `cc/nerddrone`)

Round 2 of the prop stills is done for the four props the mothership asked to re-render (1 radio → screen, 2 glovebox C cut,
6 plate A, 7 bed A). Picks 4 and 5 are recorded in `DESIGN.md` › Components. The contact page is
`docs/design/escenas/utileria/index.html` (round 1 moved to `ronda1.html`). The full brief for the open items is still
`handoff-fase1-ronda2.md`. Its run commands hold; the round-2 option names are `radio2-a,radio2-b,placa2-a,placa2-b,caja2-a,
caja2-a-esc2,caja2-b,caja2-b-esc2,guantera2-borde,guantera2-c`. Run `blender/pantalla_tablero.py` first; it writes the
screen faces into `tmp/utileria/`.

## Next: stickers, a real design pass (mothership brief, verbatim, 03:40)
`calcas2` exists: four styles, IG faded, YouTube scuffed, each sticker on the tailgate surface ray-cast at its own spot. The owner
judged it not real enough. The brief:

> The owner, 03:40, on the stickers: "we might need to dig more design on the stickers so they stand out as real stickies". Do a real design pass on them, references first, before more renders.
> - Reference what makes a real sticker read as one: die-cut white vinyl border, a gloss or satin sheen that catches the light, slightly lifted or curled corners, overlap when several are stacked, wear (scuffs, sun fade, a torn edge), and the slight raised edge on the surface. Look at real band and merch stickers, skate/streetwear sticker bombs, and Mexican troca culture: calcomanías on pickups and tailgates ("Puro Veracruz", ranch and sierreño stickers, holographic and chrome vinyl). Use our library first, then real photos, traced in references.md.
> - Design: each sticker is its own piece of illustration and lettering with a different shape and finish (die-cut, vinyl, holo, matte paper, a classic oval bumper sticker), with the §2 brand rules kept (official glyph unaltered and upright, away from the peel).
> - Material: a separate shader layer per sticker (white border, clearcoat, a normal map for the edge, a curl on one corner), so they stand off the paint in the scene-2 camera.
> Show 2 directions as stills (close-up plus the scene-2 camera), then stop for the owner. If you reach 30% context first, put this brief verbatim in your handoff.

Starting points: the library row `blender/lab/kiln-utility-box/NOTES.md` (decal quads ~0.6 mm off the paint, an atlas) and
`web/designer-fichas/ayzz.md` (placement at angles). The scene-2 camera is `VISTA_ESC2` in `utileria.py`. Draw the sticker art
as images with alpha die-cut shapes, the way `blender/placa_veracruz.py` draws the plate, not with Blender text.

## Live port: started, not matched yet
Done in `lab/vivo/index.html`: the glass override, the tramo cloned with pole SpotLights and additive puddles (from
`src/scripts/escena.ts`), and the cab and bed RectAreaLights (`?ka=` scales them, `?kc=` the bed light only, `?kp=` the poles).
SSIM against Cycles (gray, 1280×720), round 1 → round 2 at ka 0.02 with the poles at 90: f0 0.252 → 0.425, f96 0.857 → 0.799,
f191 0.670 → 0.625: the poles over-lit the road and the bed light washed the bed. Tuned (now the defaults: ka 0.02, kp 30,
kc 0.4): **f0 0.441, f96 0.858, f191 0.745**, all three above round 1; side-by-side in `docs/design/escenas/vivo/lado-a-lado.jpg`
(live left, Cycles right). revisar `--ref` also flags a 1–2 % scale mismatch (lens/fov) and dE 2.4–3.6. Still open: the real-GPU fps
and the heads retopo.

## Known limits of round 2
- **Glovebox triangle: fixed (04:20, nerddrone).** The owner's "weird triangle" (03:30) was the bin's sloped floor riding up on
  the door copy: it runs from the front skin's top edge to the back-bottom corner (y 1.3465), with |n.y| ≈ 0.60, so it passed
  the `piel` normal test. A ray-cast from the `guantera2-borde` camera found it. The `roza` dash hypothesis was wrong and is
  reverted. `piel` now also needs every vertex within 4 cm of the dash face. Regression probe: `blender/probe_guantera.py`
  (a38984e: 0.112 m, FAIL; now: 0.0007 m, PASS). Side effect: the door is now only the front skin, 11.6 cm tall, and the inner
  box spans z 1.279–1.395, while the dash hole still reaches down to z 1.194. In `guantera2-borde.png` this shows as a
  dark band between the shelf lip and the door. It is not fixed (fix: size the inner box from the removed dash faces, not
  from the door).
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

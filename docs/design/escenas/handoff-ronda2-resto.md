# Handoff: what round 2 left open (2026-11-13, circudrone on `cc/nerddrone`)

Round 2 of the prop stills is done for the four props the mothership asked to re-render (1 radio → screen, 2 glovebox C cut,
6 plate A, 7 bed A). Picks 4 and 5 are recorded in `DESIGN.md` › Components. The contact page is
`docs/design/escenas/utileria/index.html` (round 1 moved to `ronda1.html`). The full brief for the open items is still
`handoff-fase1-ronda2.md`. Its run commands hold; the round-2 option names are `radio2-a,radio2-b,placa2-a,placa2-b,caja2-a,
caja2-a-esc2,caja2-b,caja2-b-esc2,guantera2-borde,guantera2-c`. Run `blender/pantalla_tablero.py` first; it writes the
screen faces into `tmp/utileria/`.

## What's left (05:35, yappingdrone, at the mothership's stop)
- **Stickers: the owner's set as of 05:30**, rendered as `calcas3-mix` and `calcas3-mix-esc2`. From A: a-instagram (strawberry),
  a-spotify (holo badge) and a-estrella, whose MT star now reads MÍRANOS / EN YOUTUBE instead of TUMBADO. From B: b-youtube (gold
  strawberry), b-tiktok (black round), b-loteria (EL SOMBRERO card) and b-pura, the gold chrome lettering PURA MT. The owner has
  not said this set is final, and may still swap pieces from `calcas3-arte.jpg` / `calcas3-arte-2.jpg`. Once it is final, record it in
  `DESIGN.md` › Components. The IG/YT/TT glyph slots stay grey until the owner downloads the official files. The build packs the art
  in one atlas (references.md row, kiln-utility-box).
- **Glovebox liner sliver: fixed (05:37, npcdrone).** The skin bulges up to 2.1 cm off its mid plane; the liner sat 2-10 mm off it,
  so a door vertex stood 1.08 cm above the liner (`probe_guantera.py` check 4 "asoma": 0.0108 FAIL before, -0.002 PASS after). The
  liner now runs from 2 mm off the plane to 2 mm above the door's highest vertex (2.1 cm thick) and the junk sits on its top.
- **Live vs clips: the fps question is open.** `lab/vivo` has not been measured on a real GPU. Whether the site runs the scene live
  or ships Cycles clips depends on that number (see "Live port" below).

## Next: stickers, a real design pass (mothership brief, verbatim, 03:40)
`calcas2` exists: four styles, IG faded, YouTube scuffed, each sticker on the tailgate surface ray-cast at its own spot. The owner
judged it not real enough. The brief:

> The owner, 03:40, on the stickers: "we might need to dig more design on the stickers so they stand out as real stickies". Do a real design pass on them, references first, before more renders.
> - Reference what makes a real sticker read as one: die-cut white vinyl border, a gloss or satin sheen that catches the light, slightly lifted or curled corners, overlap when several are stacked, wear (scuffs, sun fade, a torn edge), and the slight raised edge on the surface. Look at real band and merch stickers, skate/streetwear sticker bombs, and Mexican troca culture: calcomanías on pickups and tailgates ("Puro Veracruz", ranch and sierreño stickers, holographic and chrome vinyl). Use our library first, then real photos, traced in references.md.
> - Design: each sticker is its own piece of illustration and lettering with a different shape and finish (die-cut, vinyl, holo, matte paper, a classic oval bumper sticker), with the §2 brand rules kept (official glyph unaltered and upright, away from the peel).
> - Material: a separate shader layer per sticker (white border, clearcoat, a normal map for the edge, a curl on one corner), so they stand off the paint in the scene-2 camera.
> Show 2 directions as stills (close-up plus the scene-2 camera), then stop for the owner. If you reach 30% context first, put this brief verbatim in your handoff.

### Sticker pass: state at 04:32 (nerddrone)
Done: references first, now `references.md` › "Stickers, design pass" (`refs-check` PASS on that section, id `calcas3`). Art
for both directions: `blender/calcas_arte.py` (run: `uv run -q --with numpy --with pillow python -I blender/calcas_arte.py`).
It writes `tmp/utileria/calcas3/<id>.png` (RGBA, the die-cut is the alpha, white border included), `<id>-n.png` (normal map of the
raised edge) and `calcas3.json` (w/h in m, finish, glyph slot as UV + mm). Contact sheet: `docs/design/escenas/utileria/calcas3-arte.jpg`.
Spotify's official icon (from developer.spotify.com/documentation/design, `2024-spotify-logo-icon.zip`):
`tmp/utileria/calcas3/spotify-icon.png`. Glyph ruling (mothership 04:25): IG, YouTube and TikTok get a **neutral grey upright slot,
labelled as a slot**. The owner must download the Meta Instagram glyph, the brand.youtube icon and TikTok's logo pack by hand.

| id | finish | art |
|---|---|---|
| a-instagram | gloss die-cut vinyl | pink strawberry with sunglasses, SÍGUENOS / EN INSTAGRAM |
| a-spotify | holo round badge | cassette on an orange sun disc, ESCÚCHANOS |
| a-youtube | matte paper oval bumper, sun-faded, scuffed | MT, MÍRANOS / EN YOUTUBE on turquoise |
| a-tiktok | gold chrome letter-cut, no background | sombrero, ANDAMOS / EN TIKTOK |
| b-instagram | gloss bumper strip, the oldest (heavy fade, scuffs, chips) | SÍGUENOS EN INSTAGRAM, gold on --cap |
| b-spotify | holo oval | black cassette on a gold disc, ESCÚCHANOS |
| b-youtube | gloss die-cut | gold strawberry, MÍRANOS / EN YOUTUBE |
| b-tiktok | matte paper round, the newest | gold sombrero on black, ANDAMOS |

### Sticker pass: state at 05:25 (yappingdrone): owner picked a mix
Owner 05:15: a mix of A and B; PURA MT or PURA MAFIA TUMBADA instead of PURO VERACRUZ (the band is from Xalapa); fix the T.
Done: `calcas3-mix` / `calcas3-mix-esc2` (A: a-instagram, a-spotify, a-estrella; B: b-youtube, b-tiktok, b-loteria, b-pura =
PURA MT, owner 05:30; the star a-estrella now says MÍRANOS / EN YOUTUBE under the MT instead of TUMBADO, owner 05:30). The T: `letras()` drew the text already shifted by alto·incl, then the slant moved the top row right by
incl·h, so the last letter's top (the T's bar) ran past the mask and was clipped flat; all 16 pieces re-rendered. The star moved off
the red lamp glow at the gate's centre. Open: the owner may swap pieces from the two sheets.

Done, steps 1-5 below, with these departures from the brief (each one seen in a still first):
- **Art: 16 pieces.** Owner 04:38 on `calcas3-arte.jpg`: "those are good, use more variations like that". `calcas_arte.py` adds 8
  band stickers with no platform glyph (`glifo: null`). A: PUTIFRESA lettering, MT holo starburst, lotería card EL CASETE, MAFIA
  TUMBADA ribbon. B: PURO VERACRUZ gold chrome letter-cut, MT shield, card EL SOMBRERO, VER oval. The first eight are byte-identical
  (md5 checked). Sheets: `calcas3-arte.jpg` (first eight) and `calcas3-arte-2.jpg` (new); references.md has a `user:` row for them.
- **Drape.** The gate is not flat: 8-9 mm steps at z 1.22 and 1.05. Each sticker's grid is ray-cast per vertex onto the paint. Rays
  that slip through seams and hit the cab 1.1 m behind are floored 12 mm under the median. A max filter plus a blur over 1.5 cm
  makes the sticker tent over a step (at most 12-19 mm off) instead of diving into it. Before this, stickers looked sliced and a dark square sat on b-instagram.
- **Curl.** The brief's 5 cm fold rolled ~190° and hid lettering. Now 2.5 cm by default and 3.5 cm on the oldest. The corner is the
  one farthest from the slot, and a check raises if the slot falls inside the curl. Grid cells ≤ 4 mm, not 24×24.
- **Lights** (`luces3`): a camera-side fill, plus a 25 W, 0.5 m light at the camera's mirror point across the gate normal, only where that point is
  above the road (close-up yes, ESC2 no). At 120 W and 1.2 m the mirror light washed every sticker. Chrome roughness is 0.25: at 0.12 the letters mirrored the night and read black.
- **Not verified:** how the stickers look is judged from the stills only; revisar measured the contact page, not the renders.
- **Slots.** `ranuras_libres()` samples each slot (clear space, 2× the glyph) against the alpha of every later sticker and raises
  on overlap. It passes for A (6 stickers) and B (8). Grey slots carry an IG/YT/TT label; Spotify uses its official icon.
- Stills: `calcas3-a`, `-a-esc2`, `-b`, `-b-esc2` on the contact page, with both art sheets. slop-check exit 0; revisar web exit 0 at 390 and 1440.
Run: `uv run -q --with numpy --with pillow python -I blender/calcas_arte.py`, then `utileria.py` with
`calcas3-a,calcas3-a-esc2,calcas3-b,calcas3-b-esc2` (about 20 s each after the 30 s scene build).

**The Blender half (done 05:08, see the state above; the brief as it was):** Add it to `utileria.py` **above** the glovebox block, which is destructive and must stay last:
1. `calca3(id, x, z, rot, orden=0)`: a grid of 24×24 in XY, sized from `calcas3.json`, `rot=(pi/2, rot, 0)` like `plano`, sitting
   0.6 mm + `orden`×0.3 mm off the surface hit by `rayo` (as `en()` in `calcas2`). Curl one corner (bottom-left, away from the glyph):
   for a vertex whose distance past a fold line 5 cm from the corner is d > 0, lift it along local +Z by R(1 − cos(d/R)) and pull it
   back by d − R·sin(d/R), with R = 1.5 cm. At ESC2 (about 2.2 px/cm on the tailgate) only a curl of centimetres reads.
2. Material per sticker: the image gives Base Color and its alpha gives Alpha. A Normal Map node (tangent space, image set to
   Non-Color) feeds the normal. The finish: `brillo` → coat 1, coat roughness 0.05, roughness 0.35; `mate` → roughness 0.85, no coat;
   `holo` → metallic 0.6, roughness 0.2, thin film thickness from a noise texture mapped to 250–750 nm, film IOR 1.33; `cromo`
   → metallic 1, roughness 0.12. Mix by Backfacing into a white backing BSDF (roughness 0.6) with the same alpha, so the curl shows
   the backing.
3. Glyph: its own upright quad (no `rot`), at the slot's UV mapped through the sticker's rotation, 1 mm in front. Grey (0.5) for
   IG, YT and TikTok; `spotify-icon.png` with alpha for Spotify. B's overlaps must never cover a slot.
4. Options `calcas3-a`, `calcas3-a-esc2`, `calcas3-b`, `calcas3-b-esc2` (close-up = `VISTA_CALCAS`, scene 2 = `VISTA_ESC2`). A: the
   four spread out like `calcas2`. B: the stack in the upper-left of the tailgate around (CX − 0.4, 1.2): b-instagram under
   b-youtube, which overlaps its torn end; b-spotify and b-tiktok partly over the strip. Add a `relleno` light near each camera
   aimed at the tailgate so the gloss and holo catch a highlight toward the lens. Without it, the gloss doesn't read at night.
5. Add the four stills to `docs/design/escenas/utileria/index.html`. Before the report: read visual-lab `web/ai-slop-tells.md`, run
   `slop-check.py` and `revisar.sh web` at 390 and 1440 on that page, then stop for the owner's pick between A and B.

Starting points: the library row `blender/lab/kiln-utility-box/NOTES.md` (decal quads ~0.6 mm off the paint, an atlas) and
`web/designer-fichas/ayzz.md` (placement at angles). The scene-2 camera is `VISTA_ESC2` in `utileria.py`. Draw the sticker art
as images with alpha die-cut shapes, the way `blender/placa_veracruz.py` draws the plate, not with Blender text.

## Bed props, design pass (06:10, saltydrone): waiting on the owner's pick
Owner 05:36: "might need to work on those bed truck props as well, like the stickers one". Bed B (picked 03:22) stays the frame:
piñata hanging from the roll bar, balloons, a low pile. Done: `references.md` › "Bed props, design pass" (`refs-check` PASS on that
section, id `caja3`); 12 props at real size in `blender/caja3.py` (tololoche and bajo sexto fundas, requinto hard case, ATA road
case, cooler with the strawberry, party speaker, hat box with PURA MT, tejana, generic beer crate, MT flag, duffel, XLR coil, plus
papel picado and ratchet straps); worn edges by a Bevel-node mask (kiln-prop `edges="bevel"`); decals are the band stickers from
`calcas_arte.py` without platform glyphs. Stills on the contact page, section 6: `caja3-hoja` (model sheet), `caja3-a` /
`-a-esc2` (tidy), `caja3-b` / `-b-esc2` (lived-in). The close-up uses a new, higher camera `VISTA_CAJA3` that sees into the bed;
`VISTA_CAJA` sees only what clears the bed walls.
- **Run:** `blender/caja3.py` execs `utileria.py` up to its render loop, adds the `caja3-*` options, then runs that loop (so
  `utileria.py` itself is untouched). Same arguments as `utileria.py`; about 25-45 s a still at 48 samples after the 30 s build.
- **Measured:** bed walls at CX ± 0.565 (ray probes, `CAJA3 pared`), roll bar top z 2.27 (`CAJA3 arco z`). `vaciar_caja()` hides
  Alexandro, Diego, their guitars (child meshes too: hiding the parent left them in round 2's `caja2-*` stills) and the three seat
  cases from `transicion.py`.
- **Open:** the owner's pick or mix; the piñata hangs in front of the road case in the close-up (bed B's own layout). Not verified:
  the look is judged from the stills only.

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
  box spanned z 1.279–1.395 while the dash hole reached down to z 1.194. **Fixed 05:05 (yappingdrone).** The inner box is
  sized from every vertex of the removed faces (`CORTE["hueco_*"]`, box extents in `CORTE["caja_*"]`; `lo`/`hi` stay the door).
  `probe_guantera.py` now also checks the cover in x and z: falta 0.082 m FAIL before, -0.003 m PASS after. That uncovered a second fault.
  The door liner was a vertical box on a skin that leans ~37°, so once the door opened it stood off the door at an angle, and the two
  door meshes showed through the gap (found by ray-casting the `guantera2-borde` camera). The liner now lies on the skin's plane,
  and the junk anchor (`centro`, `n`) follows it. Third fault, same fix: the lowered box started at the top of the leaning skin
  (y 1.147), so below the hinge it stood 9 cm into the cabin (a second ledge under the open door). Below the hinge it now starts at
  the dash face (`hi.y`), and its side walls follow the skin's lean. Probe `sale`: 0.088 m FAIL with the old box, 0.0 PASS now.
  Left: a thin dark sliver where a door-mesh edge pokes through the liner on the
  left, in the empty-door still. The contact page jpgs `guantera2-*.jpg` are these renders.
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

# Yellow seeds on the friend's strawberry (2026-11-14, run `uncdrone`)

Brief: mothership `docs/queue/2026-11-14-mto-strawberry-seeds.md`. The friend's Tripo model (`C:\Users\black\Downloads\strawberry.glb`,
untouched) is copied to `blender/props/strawberry.glb`. It replaces the strawberry options of props pass 2 (board #36).
Sheet for the owner's pick: `E:\Cursor Projects\MTO-uncdrone\docs\design\props-placement\lado-a-lado\fresa-semillas.jpg`.

## What was made
- **One seed list, 336 seeds**: 242 in the model's own pits plus 94 fill seeds where the gap is over 4.5 % of the model height.
  The spacing grows ×1.8 toward the calyx, and there are no seeds within 2–3 % of a green texel. Pits are geometry: they
  survive with the normal map off. To find them, `semillas.py` welds the vertices, smooths a copy (150 Laplacian passes),
  takes h = offset along the normal, and puts one seed per connected patch with h < −0.0025, at the depth-weighted centre.
- **(a) painted**, `blender/props/strawberry-a-pintada.glb`: yellow ellipses in the base colour plus a dome bump in the
  normal map, painted by 3D distance to each seed so a dot that crosses a UV seam stays whole. 3.35 % of the colour texels
  change, all of them inside seeds. The mesh and rm map are byte-identical. The colour map is pixel-identical outside the seeds,
  but it is now stored as a PNG instead of the friend's JPEG (both changed maps are PNG), so the GLB grows from 19.8 to 28 MB. Bump sign +1 = raised, checked under a top light (`estudio.py … rasante`).
- **(b) geometry**, `blender/props/strawberry-b-semillas.glb`: one extra mesh of 336 ellipsoids (about 1 mm at scene scale).
  Each is sunk about a third into its pit and tilted up to 12° at random. Every original bufferView is byte-identical.
- Checks: `semillas_verif.py` (bytes and texels); `revisar.sh` on `pp-fresa` and `pp1-b` against the original, full frame and a
  200 px crop of `pp1-b`: 0 FAIL, colour dE ≤ 0.03 outside the berry.

## What the owner should know
- **At scene scale the seeds are sub-pixel.** In `pp1-b` (scene 1 camera) the berry is about 25 px tall. Measured on a
  200 px box around it against the original: 45 px (a) and 77 px (b) change by dE76 > 10 (max 27 and 31). That is a
  speckle or warm tint over the berry, not separate dots (whether dots read there is not verified). Full-frame revisar
  hides it, because its 0.01 % region floor (207 px) is about the berry's whole size. In the `pp-fresa` close-up: 2791 px (a)
  and 7363 px (b) change by dE > 10.
- The friend's colour map already has faint orange specks in some pits; (a) paints over them only where a seed lands.
- Scale: `_fresa_mallas` fits ring top to tip to 4.1 cm. This model has no ring and a long stem, so its body comes out about
  2.6 cm tall, smaller than the procedural charm's. It was not rescaled, because that is outside this brief.
- In the cab light the lower half of the berry washes pink-white in all three versions (scene lighting, not the seeds).

## Re-run
```sh
cd blender/tripo
R="uv run -q --with numpy --with scipy --with pillow --with opencv-python-headless python -I"
$R semillas.py ../props/strawberry.glb ../../tmp/fresa-semillas 400 0.045           # -> semillas.npz (336)
$R semillas_glb.py ../props/strawberry.glb ../../tmp/fresa-semillas/semillas.npz \
   ../props/strawberry-a-pintada.glb ../props/strawberry-b-semillas.glb
$R semillas_verif.py ../props/strawberry.glb ../props/strawberry-a-pintada.glb ../props/strawberry-b-semillas.glb
/mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w estudio.py)" -- <glb (Windows)> <out prefix> 1000 128
# in scene (the .exe needs WSLENV to see PP_FRESA):
WSLENV=PP_FRESA/p PP_FRESA="$PWD/../props/<glb>" /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 \
  --python "$(wslpath -w ../props_placement.py)" -- "$(wslpath -w "/mnt/e/Cursor Projects/MTO/blender/escena.py")" <out dir> 64 pp-fresa,pp1-b 1920x1080
$R semillas_hoja.py ../../tmp/fresa-semillas/escena ../../tmp/fresa-semillas/hoja-semillas.png 336
```

# Pass 2 (2026-11-14, run `uncdrone`): rescale, bigger gold seeds, emblem sheet

Brief: mothership `docs/queue/2026-11-14-mto-strawberry-seeds-pass2-emblem-sheet.md`. Sheets: `docs/design/props-placement/lado-a-lado/fresa-semillas-2.jpg`
and `emblema-2.jpg`, both on `docs/design/props-placement/index.html` (#fresa-semillas-2, #emblema-2).

## Strawberry
- **Rescale.** The model's body (tip to calyx base, y 0 to about 0.64 of the mesh height) is now 4.1 cm: `PP_FRESA_ALTO=0.0647`
  sets the whole mesh height (stem included) in `props_placement.py` and `tripo/estudio.py` (default stays 0.041). The GLB is not
  touched. Measured: the charm's share of scene 1's frame 0.010 % to 0.025 %, of the close-up 1.68 % to 3.97 %.
- **Seeds.** `tripo/semillas2_glb.py` writes a seed mesh from pass 1's seed list: size, sink and colour are arguments, and seeds
  closer than `min_gap` to a kept one are dropped so the bigger ones do not fuse. Every original bufferView is byte-identical
  (`semillas_verif.py`, run on all four variants); `blender/props/strawberry.glb` is still byte-equal to the friend's `Downloads\strawberry.glb` (cmp).
- Variants (all in `blender/props/`): A `s2-amarilla` (yellow x2, 278 seeds), **B `s2-oro` (satin gold x2, 278, a third buried: kept)**,
  E `s2-oro-hundida` (B half buried), F `s2-oro-alta` (B sitting proud on the pit), C `s3-oro` (gold x3, 161), D `s4-oro` (gold x4, 97).
  Sink is the seed centre's height above the pit floor: 0.003 for A and B, 0.0045 for C, 0.006 for D (proportional to size, as pass 1's
  0.0015), 0 for E and 0.006 for F. Gold = metallic 0.55, roughness 0.32, centre (236,178,38) sRGB.
- **Why B:** the seeds in the studio and in the close-up look like achenes, and the gold has a sheen; C and D look armoured, and at
  x3-x4 the berry reads as a different fruit. At scene 1 the variants are within a few pixels of each other (below), so size
  buys nothing there that justifies the cartoon. Sink moves the gold pixel mass at scene 1 (E 134, B 176, F 235): F is the swap if
  the owner wants more gold at the scene camera.
- **Measured** (`tripo/semillas2_medir.py`, 200 px box around the berry at scene 1, 560 px at the close-up; a seed blob is
  gold-hued, dE76 > 10 against the unseeded berry, >= 3 px; readable = dE >= 15 against its own ring; "reads" = >= 25 readable):

  | variant | scene 1: gold px / blobs / readable | close-up: blobs / readable (lower half) |
  |---|---|---|
  | pass 1 (x1 yellow) | 19 / 2 / 0 | 164 / 134 (81) |
  | A yellow x2 | 216 / 5 / 3 | 156 / 125 (73) |
  | B gold x2 | 176 / 7 / 6 | 169 / 121 (75) |
  | E = B half buried | 134 / 9 / 2 | 166 / 129 (77) |
  | F = B proud | 235 / 7 / 3 | 170 / 121 (70) |
  | C gold x3 | 252 / 7 / 5 | 124 / 78 (39) |
  | D gold x4 | 224 / 9 / 5 | 97 / 57 (25) |

  At scene 1 the berry is about 38 x 46 px (revisar's changed region), 1.1 px/mm: a 3.6 x 2.3 mm seed is 4 x 2.5 px and the
  neighbours are 5 px away, so seeds merge. No variant reads as separate seeds there; what reads is a gold freckling (10x more gold
  pixels than pass 1). Closer cameras read separate seeds for every variant, including the washed lower half (for B, 75 of the 121
  readable blobs sit in the lower half: gold keeps its contrast against the pink-white).
- **The cab light** still washes the lower half pink-white. Left open: fixing it needs the shared cab light or a berry material
  override, which this brief rules out. Gold seeds still read there (75 of B's 121 readable close-up blobs are in the lower half).
- **Rule 1** (road through the windshield, <= 2 % covered by new props): scene 1 with the rescaled berry covers 1.19 % of it (30 of 2531
  probe pixels) with or without seeds: PASS. Pass 1 had 0.67 %. The bigger berry plus its stem hangs lower; the cord was not shortened.
- `revisar.sh` (B against pass 1 and against the unseeded berry, full frame and 200 px / 560 px crops; `tmp/fresa-semillas2/revisar/`):
  0 FAIL at scene 1 (full frame and crop, both refs); color dE <= 0.10; changed region 0.02 % of the frame vs the unseeded berry
  (38 x 46 px). The close-up crop FAILs sharpness (2.1-2.2 x) and halo (8-27 %): the seeds add edges and the berry is larger,
  expected, not a defect.

## Emblem
- `props_placement.py`: `emblema(modo, fuente)` with modos `parado` (14.6 cm cap, as pass 1), `grande` (18.8 cm cap), `plano` (19.9 cm cap),
  fuentes `grenze` and `pirata`, matched on the M's CAP height (Pirata One is much narrower: 14 cm tall letters are 19 cm wide
  vs 33 cm in Grenze). Letters now sit on their baseline, plinth width follows the font. Pass 1's look is kept: `em6-parado-grenze`
  = 0.088 % of scene 6's frame, the same as pass 1's `pp6-b`.
- Options: `em-<modo>-<fuente>` (3/4 camera above the hood) and `em6-<modo>-<fuente>` (scene 6's low camera).
  Pirata One: `blender/fuentes/PirataOne-400.ttf` (OFL, from @fontsource, woff2 to ttf with fontTools; licence beside it).
- Scene 6's share of the frame: Grenze 14 cm 0.088 %, 18 cm 0.151 %, flat 0.008 %; Pirata 14 cm 0.060 %, 18 cm 0.087 %,
  flat 0.010 %. Only 18 cm Grenze clears rule 2's 0.1 %; Pirata would need about 20 cm letters (area scaling, not rendered: not verified).

## Re-run
```sh
cd blender/tripo
R="uv run -q --with numpy --with scipy --with pillow --with opencv-python-headless python -I"
$R semillas2_glb.py ../props/strawberry.glb ../../tmp/fresa-semillas/semillas.npz ../props/strawberry-s2-oro.glb 2.0 0.003 oro 0.040
# scene renders: the rescale only happens with PP_FRESA_ALTO=0.0647 (default stays 0.041, so a plain re-render gives the 2.6 cm body); it needs WSLENV (see the pass-1 commands above), options pp-fresa,pp1-b
$R semillas2_medir.py ../../tmp/fresa-semillas2/escena strawberry strawberry-b-semillas,strawberry-s2-amarilla,strawberry-s2-oro,strawberry-s3-oro,strawberry-s4-oro out.tsv
$R semillas2_hoja.py <est dir> <escena dir> out.tsv fresa-semillas-2.jpg
$R emblema_hoja.py <render dir with em-*, em6-*> emblema-2.jpg
# scene 6 needs tmp/utileria/placa-veracruz.png first: uv run -q --with pillow --with qrcode python -I blender/placa_veracruz.py
```

## Owner's picks (2026-11-14) and the new defaults
The owner picked seeds B and Pirata One for the emblem. A plain `props_placement.py` run now gives them: `FRESA_GLB` defaults to
`blender/props/strawberry-s2-oro.glb` and `FRESA_ALTO` to 0.0647 (body 4.1 cm); `VAR` defaults to the standing Pirata One emblem
(`CAP_MT["elegido"]`). Only `strawberry-s2-oro.glb` is tracked; the other variant GLBs and the friend's original stay untracked.
`pv-fresa-resina` / `pv-fresa-peluche` still point at `tmp/fresa/*.glb` (4.1 cm total height) and would now come out 1.6x too large;
they are dropped from the page.
Rule 1 vs rule 2: no standing Pirata size passes both. Scene 6 needs >= 21.5 cm (0.100 %), and from 21.5 cm up the emblem covers
25-33 px of scene 1's road zone, so the road coverage is 2.17-2.49 % against the 2 % limit (the rest of scene 1 covers 30 px = 1.19 %).
A shorter cord (0.045 to 0 m: 63 px at 23 cm) or fringe (largo 0.025 to 0: 54 px = 2.13 %) does not fix it. The owner chose 21.5 cm on
2026-11-14 ("A, go with 21.5 cm"): rule 2 passes at 0.100 %, rule 1 misses by 5 px (2.17 %), accepted as a judged exception.

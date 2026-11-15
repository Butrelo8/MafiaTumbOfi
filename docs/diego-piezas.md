# Diego as a part-built toy figure (test, 2026-11-14)

The owner's question was whether Diego reads better as a vinyl action figure built from rigid parts than as the skinned
Tripo mesh, whose weights tear and whose projection smears. Brief: `mothership/docs/queue/2026-11-14-mto-diego-parts-figure.md`,
plus the owner's later addition: a TRELLIS.2 regeneration as a fourth entrant.

**Sheet:** `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\piezas-comparacion.png`.
Rows are f22, f70 and f110 of the idle; the front views are on the left, the side views on the right.
Columns: Tripo v2 skinned | Tripo parts (texture) | Tripo parts (flat vinyl) | TRELLIS.2 parts.

## Reference

- **Matched:** the skinned v2 sheet, `MTO-firedrone/blender/render/reparto/repaint/diego/antes-despues-posado.png`. Same
  blend (`idle_v2.blend`), same idle (MediaPipe `idle_floorfull`, retargeted with `rigify_mto.json` plus the +80° hand
  roll), same frames, same Workbench settings and framing as `tex_probe.py`.
  - The skinned column was re-rendered with `render_parts.py` and checked against firedrone's `posed_v2` stills:
    revisar reads 0 changed regions and dE 0.00.
  - Every entrant uses the skinned body's bounding box at that frame for its camera, so all four share one framing.
- **Changed on purpose:** the parts are rigid and hang from toy joints. The cuts follow the 11-09 StableGen + teardown
  proof (weld, plane cuts, capped loops).

## Method (`blender/partes/`)

- **`split.py`**
  - Welds the mesh: 1e-6 for Tripo, 1e-5 for TRELLIS.
  - Cuts 21 planes, each bounded to its joint, and runs a leak test per cut on the vertex graph.
  - Floods faces from one seed per part, without crossing a cut edge.
  - Caps each part's cut loops with `triangle_fill`, plus `holes_fill` for loops a TRELLIS shell leaves open. Cap UVs
    are copied from the rim, so a cut face takes the rim's colour.
  - Parents every part rigidly to one rig bone, with no weights.
  - Result: 15 parts, with 0 open edges on Tripo except 1 each on the head and torso.
- **Garment lines** were measured on the texture and the mesh with `landmarks.py`:
  - collar: a tilted plane at z 0.56;
  - shirt hem: 0.280, just under the hem lip at 0.283;
  - trouser cuff: 0.068;
  - crotch: 0.235, with the hip cuts rising to 0.27 at the outer hip.
- **`joints.py`**, the equivalent of kiln's attachment check, run every 3rd frame from 1 to 118, plus f22, f70 and f110:
  - **gap:** the child's cut-loop vertices left out in the open, as distance to the parent part;
  - **interpenetration:** child vertices inside the parent's capped volume (ray parity in 3 directions).
  - The rest pose reads 0 / 0 on every joint, which is the metric's own check.
  - It also runs kiln's `floating()` at f70: nothing floats.

## Decisions (variants compared; renders in `test/`)

- **Torso: one piece on the chest bone, with a waist swivel under the shirt hem.**
  - `rel.py` shows that chest against hips is a 15° twist about the vertical axis, not a lean. A horizontal cut
    therefore works as a swivel.
- **Shoulder: cut through the armhole, so the sleeve rides with the arm.** Compared with a cut at the sleeve hem on f70
  (`test/shoulders_zoom_f70.png`):

  | shoulder cut | gap max | interpenetration max | how it reads |
  |---|---|---|---|
  | sleeve hem | 15–20 mm | 5–10 mm | the A-pose sleeve stays on the torso as a wing, and the arm's cut face shows through the sleeve opening with smeared rim texture |
  | armhole (kept) | 30–34 mm | 26–30 mm | the opening sits on top of the shoulder, mostly turned away from the camera |

  The numbers favour the hem cut; the look favours the armhole. The armhole was kept for the look, and the owner can
  overrule.
- **Arms pinned to a socket on the torso (no clavicle).**
  - The rig's shoulder bone sits at a constant 22° and moves the arm pivot 45–47 mm relative to the chest.
  - Parented straight to the bones, the shoulder opens 37–43 mm, with up to 41 mm of interpenetration.
  - The arm parts therefore hang from empties fixed on the torso, copying each arm bone's world rotation.
  - Cost: the hands sit 10–20 mm (median) from where the skinned hands are. This is part-to-skinned distance, in
    `joints.json`.
- **Wrist swivel centred on the wrist ring.**
  - The +80° hand roll from `pose_fix.py` turns about the bone, which runs along the top edge of the arm.
  - Recentring the swivel cut the wrist overhang from 46–50 mm to 27–28 mm.
  - What remains is an oval wrist section turned 80°.
- **Limb cuts snap to the narrowest closed ring within −35 to +10 mm of the pivot.**
  - The rig's wrist pivot lies inside the palm. The plane through it cut a 10 cm ring and leaked.

## Numbers (max over the clip, mm)

| joint | Tripo gap max | Tripo interpen. max | TRELLIS.2 gap max | TRELLIS.2 interpen. max |
|---|---|---|---|---|
| collar | 7.2 (f34) | 4.3 | 6.5 | 3.9 |
| hem | 15.2 (f118) | 0.0 | 9.6 | 0.0 |
| wrist.L | 27.0 (f58) | 2.5 | 24.1 | 1.3 |
| elbow.L | 3.2 (f49) | 0.6 | 5.5 | 2.0 |
| shoulder.L | 29.5 (f1) | 29.6 | 43.2 | 4.9 |
| hip.L | 14.0 (f55) | 0.6 | 11.5 | 3.9 |
| knee.L | 18.3 (f55) | 3.6 | 38.0 | 3.8 |
| cuff.L | 9.8 (f118) | 2.2 | 12.7 | 3.2 |
| wrist.R | 28.4 (f70) | 2.6 | 27.6 | 1.9 |
| elbow.R | 5.9 (f34) | 4.8 | 9.4 | 1.2 |
| shoulder.R | 33.7 (f22) | 26.1 | 36.8 | 4.8 |
| hip.R | 9.1 (f55) | 2.1 | 16.1 | 3.8 |
| knee.R | 15.0 (f52) | 3.2 | 28.9 | 3.2 |
| cuff.R | 14.7 (f91) | 5.7 | 6.6 | 5.6 |

- **Knees:** the knee bends 25–33°, and a flat cut opens 15–18 mm on Tripo.
- **TRELLIS knees:** they open 29–38 mm.
  - The likely reason is that the rig's knee pivot (z 0.165) was fitted to Tripo, not to TRELLIS.
  - This is not verified: TRELLIS's trouser legs are straight cylinders, so its knee height can't be read from the
    mesh.
- **TRELLIS garment lines** were measured on its own texture and mesh (`data_trellis/`):
  - hem: 0.275 (lip at 0.280);
  - cuff: 0.078. Tripo's 0.068 falls inside TRELLIS's larger shoe and left 31 mm of interpenetration at rest.
  - collar: Tripo's line is kept. TRELLIS's own collar at 0.575 put its head 36 mm inside the torso at rest.
  - Every TRELLIS joint reads 0 / 0 at rest.

**Clip** (flat vinyl, side, 120 frames at 30 fps, `clip/diego_partes_flat_idle.mp4`): `eagle.sh` reads crawl 0.19
(pass), flicker 0.01 and strobe 0. For comparison, the skinned clip read 0.20 and the rigid control 0.16
(`docs/reparto-rig.md` on firedrone).

**revisar foto at f70** (front / side):

| comparison | changed regions | dE elsewhere |
|---|---|---|
| Tripo parts against skinned v2 | 3.6 % / 4.3 % of the frame, on the arms, knees and feet | 0.15 / 0.12 |
| flat vinyl against textured parts | 0.01 % | 0.31 |
| TRELLIS.2 against skinned | different asset: 16 % changed, sharpness 2.8–3.0× (faceted mesh, crisper texture) | not applicable |

## What the sheet can and cannot show

- **The flat-vinyl column looks the same as the textured one in Workbench.**
  - The repainted v2 texture is already close to flat colour. Posterizing it with `flat_tex.py` (k-means on the texels
    the mesh uses, merging near-identical colours) leaves four colours: black 53,50,49; skin 195,157,139; white
    189,188,186; and a mid tone 137,118,109.
  - The satin finish (MTO `mat()`: roughness 0.42, coat 0.2) is set on `diego_partes_flat.blend`, with no normal
    map. Only a lit engine shows it.
- **Lit strip at f70** (EEVEE, `tex_probe.py`'s one sun and grey world):
  `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\piezas-iluminado-f70.png`.
  - In it, flat against textured reads 0.26–0.27 % changed, dE 0.49–0.54 and sharpness 0.88–0.90×: glossier
    highlights and slightly smoother surfaces.
  - Posterizing Tripo v2 changes little. The difference is mostly the finish.
  - The lit strip also shows skin-coloured rims on TRELLIS.2's knee and hip caps: the cap UVs are copied from a rim
    whose texels border skin islands in its atlas. This was seen in the image, not measured.
- **The TRELLIS.2 entrant** is StableGen 0.5.0's own TRELLIS.2 graph, the API prompt from the 11-09 proof
  (`trellis2_stablegen.json`), run on `comfy-out/para-subir/diego.png`.
  - Seed 7 was kept over seed 33: seed 33 has dot pupils and no mouth line (`trellis/cmp_heads.jpg`).
  - Run times: 79–86 s per run, local.
  - It is aligned to Tripo's bounding box (scale 0.996) and posed on the same rig with the same cut planes.

## Files

- Blends, git-ignored, in `blender/assets/reparto/`:
  - `diego_partes.blend` (kept variant), `diego_partes_flat.blend`, `diego_trellis_partes.blend`;
  - the rejected variants `diego_partes_hem.blend`, `diego_partes_nopin.blend`, `diego_partes_armhole.blend`
    (armhole before the wrist recentring);
  - the GLBs `diego-trellis2-s{7,33}.glb`.
- Evidence in `blender/render/reparto/partes/diego/`: `split*.json`, `joints*.json`, `sheet/`, `rv/`, `clip/`,
  `test/`, `trellis/`.

## Rerun

```bash
F="/mnt/e/Cursor Projects/MTO-firedrone/blender/render/reparto/repaint/diego"; B=/mnt/e/Blender/blender.exe
SHOULDER=armhole PIN=1 WSLENV=SHOULDER:PIN $B -b "$(wslpath -w "$F/idle_v2.blend")" --python split.py -- <out.blend> <split.json> [glb]
$B -b <parts.blend> --python joints.py -- <split.json> <joints.json> 1-120:3
$B -b <blend> --python render_parts.py -- <out.png> <frame> front|side skinned|parts [flat png]
blender/partes/trellis2.sh <image> <seed> <prefix>          # needs ComfyUI and the whole 12 GB card
```

# Diego TRELLIS.2: closing the joints (2026-11-14)

Brief: `mothership/docs/queue/2026-11-14-mto-diego-trellis-joints.md`. It follows `docs/diego-piezas.md`, colddrone's
part-built test.

**Sheet (before | after, lit EEVEE, f22 / f70 / f110):**
`E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\juntas-antes-despues.jpg`.
- Columns: full body front, then the left shoulder (3/4 and side), left knee (3/4 and side), elbow and wrist.
- The full body, shoulder and knee cameras are aimed from the cut, carried by its child part, so before and after
  match.
- The elbow and wrist cuts snap to different rings in the two blends, so those cameras aim at each rig's own
  `ORG-forearm` and `ORG-hand` heads.
- Those tiles still differ: retargeting the same BVH onto the refit rig hangs the hands differently, and the knees now
  bend up to 42.8° (the Tripo rig: up to 40°).

**Variants (shoulder and knee, f70):**
`E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\juntas\cmp_abd.jpg`.
- Rows: before | A ball/drum | B peg | C+D wedge.

**Blend:** `blender/assets/reparto/diego_trellis_juntas.blend` (git-ignored).

## Reference

- **Matched:** colddrone's TRELLIS.2 parts (`diego_trellis_partes.blend`). It has the same seed 7 GLB, the same idle
  (`idle_floorfull`, `rigify_mto.json`, `pose_fix.py 80`), the same 21 cuts and garment lines, and the same pinned
  arms.
- **Changed on purpose:**
  - the rig is refitted on TRELLIS.2's own mesh;
  - every joint gets a cover;
  - cut faces get a flat garment colour.
- **Joint references:**
  - **(A)** ball-jointed doll and figma ball shoulders, and the action-figure hinge drum knee;
  - **(B)** the vinyl peg-in-socket, a telescoping sleeve;
  - **(C)** the rounded hinge end of an action-figure thigh: a filler shaped like the wedge the joint opens.

## Method (`blender/partes/`)

1. **`rig_trellis.sh`** calls firedrone's `rig_fit.py`, `rig_full.py`, `pose_fix.py` and `deform.py`, and visual-lab's
   `retarget.py`, by path. Every output goes to this worktree.
   - TRELLIS landmarks: knee 0.18, ankle 0.10, hip 0.26 and leg_x 0.060.
   - Tripo's were 0.165, 0.07, 0.26 and 0.065.
   - `knee_z` is the midpoint of hip and ankle, not a mesh landmark: the trouser legs are straight cylinders, so
     nothing else on the mesh marks the knee.
2. **`split.py`** runs unchanged on the refit idle, with `GARMENT={"hem":0.275,"cuff":0.078}` and `WELD=1e-5`. The
   result is `diego_trellis_refit.blend`.
3. **`covers.py`** builds the covers. For each joint:
   - it takes the relative motion parent⁻¹·child over the idle (frames 1–120 step 3);
   - it builds the cover from the cap loops, as one closed object hung on the parent;
   - each cut face takes a flat material in its side's garment class, coloured from all of the part's texels of that
     class. The rim texels carry baked shade, which made a wrist band look orange.
4. **`joints.py`** gains `seam`, a two-sided measure that counts the covers:
   - each child ring vertex is paired with the parent ring vertex it sat on at rest;
   - a pair is closed when either vertex is inside or on the other side's part plus its covers;
   - the old one-sided `gap` is kept;
   - `rigid_dev` (the largest deviation of |MᵀM − I| over the clip) shows that the parts never stretch.
5. **Other scripts:**
   - `closeups.py` renders lit close-ups with fixed cameras.
   - `grid.py` and `tabla.py` build the sheets and tables.
   - `piel_check.py` fails if a clothing cut has a skin cap.

**Finding that set the design:** the idle moves each joint only 1.5–8° about its mean (`rot_spread_deg` in
`covers_final.json`). The opening is mostly a fixed offset from the A-pose rest:

| joint | offset from rest |
|---|---|
| shoulder | 57° |
| knee | 24–34° |
| hand roll | 80° |

So the wedge the joint opens over the clip (C) is a small, steady shape, and it stays inside the silhouette.

## Variants (shoulder and knee) and the pick

A and B were measured every 3rd frame; C on all 120 frames (next section).

| variant | shoulder L/R seam max (mm) | knee L/R seam max (mm) | how it reads at f70 |
|---|---|---|---|
| A ball (shoulder R 54–60) / drum (knee R 59) | 0 / 0 | 0 / 0 | pauldron-like ball on the shoulder, a kneepad that is wider than the leg; collar ball 102 mm, hip balls 68–70 mm bulge out |
| B peg 35 mm | 6.7 / 8.1 | 8.5 / 4.0 | a visible step on top of the shoulder; still open past 5 mm |
| **C wedge (kept)** | 0 / 0 | 0 / 0 | the shoulder becomes one solid mass continuing the sleeve, and the knee a continuous trouser leg |

**Kept: C.** It is the only construction that closes the gaps without adding a shape that isn't in the design. Its
cost:
- it is sized to this clip's range;
- a motion that bends further needs `covers.py` rerun on that motion;
- `rot_spread` says how far it can stretch.

**Wrist.** The constant +80° hand roll turns an oval section against itself. That makes a step, not a hole.
- A ball reads as a 48 mm skin ball, and a peg leaves the step: 22–23 mm.
- Kept: `band`, the hull of both rings pushed 6 mm into their own parts. It is a narrow skin-coloured round, read as a
  slight ridge at the wrist.
- The other option: split the roll between elbow and wrist in `pose_fix`. Not done; it changes the rig.

**Collar.** The plane cuts the neck, the chain and the shirt collar. The colour is set by hand (`FORCE` in
`covers.py`): neck skin on the head side, shirt black on the torso side. Without it, the silver chain would win.

## Numbers

All over the idle, every frame 1–120; the 80 frames between the build samples are held out. The cell is "seam max
(old one-sided gap)", in mm.

| joint | before (colddrone) | refit only | after |
|---|---|---|---|
| collar | 5.2 (6.9) | 5.5 (7.0) | 0.8 |
| hem | 2.6 (9.6) | 2.6 (9.6) | 0.0 |
| shoulder.L / .R | 43.4 / 36.2 | 43.9 / 45.2 | 0.2 / 0.2 |
| elbow.L / .R | 1.7 / 9.4 | 5.7 / 4.8 | 0.3 / 0.2 |
| wrist.L / .R | 20.0 / 22.5 (24.1 / 27.6) | 22.3 / 23.2 | 0.0 / 0.0: a band, not a closure (the step is now a 6 mm skin ridge) |
| hip.L / .R | 9.4 / 16.8 | 17.8 / 12.5 | 0.2 / 0.5 |
| knee.L / .R | 38.0 / 28.9 | 23.7 / 16.9 | 0.0 / 0.0 |
| cuff.L / .R | 13.4 / 6.4 | 9.3 / 12.8 | 0.8 / 0.5 |

The done-check uses the two-sided seam: the old one-sided gap can't see covers. The before was rerun on the same
measure.

**Checks:**
- Rest: seam 0 on every joint. `rigid_dev` is 1.7e-5, and kiln `floating()` finds nothing.
- Refit alone takes the knees from 38 / 29 mm to 24 / 17 mm. That confirms colddrone's pivot hypothesis; the covers
  close the rest.
- `piel_check.py`: no skin cap on a clothing cut. Shoulders, hem, hips and knees have rims that are 100 % dark; cuffs
  are 71–82 % dark.

**`deform.py`** (run on `rig_trellis/idle_trellis.blend`, the same rig and action as the final blend;
`rig_trellis/deform_idle.json`):
- No angle outliers: knee ≤ 42.8°, elbow ≤ 15.6°, twist ≤ 83.7° (the deliberate 80° roll; limit 90°), wrist 2.7°,
  neck 4.9°, head 5.6°.
- Its stretch rows measure the skinned TRELLIS Body, which the parts do not use. They fail: breast p99 1146 %, pelvis
  911 %. TRELLIS's separate shells under heat weights are firedrone's cause 1. The thresholds were not loosened.
- The parts are rigid: `rigid_dev` 1.7e-5, so no stretch is possible.

**Clip** (`clip_juntas/diego_juntas_idle.mp4`: side view, Workbench, 120 frames at 30 fps, colddrone's `render.py`):

| check | value |
|---|---|
| crawl | 0.20, FAIL at ≤ 0.2 |
| flicker | 0.01 |
| strobe | 0 |

- **Control:** colddrone's uncovered TRELLIS.2 parts, rendered the same way, read crawl 0.21 (`clip_antes_trellis/`).
  Tripo parts read 0.19.
- The crawl belongs to the TRELLIS.2 asset (faceted mesh, crisp texture). The covers do not cause it.
- **Done-check: miss.** `revisar.sh` and `eagle.sh` exit 1 on crawl.
- **eagle-eye run `9bf69c4a8631`: 3 findings.**
  - **One major:** the crawl claim, filed as "boiling". `check.py` promoted it because my refutation cited no event
    image. My reading: a full-rate strip of both claim tiles shows rigid translation and no redraw.
  - **Two minor:** the wrist band's lip, and a faint line where the flat-black knee wedge meets the textured trouser
    under Workbench cavity.
  - Report: `clip_juntas/revisar_clip/eagle/report.md`.
  - The owner's verdict: `~/projects/visual-lab/scripts/eagle.sh view <clip>`.

## Open

- The wrist band is a design call for the owner. The alternative is to split the 80° roll between elbow and wrist.
- The covers are flat colour. Baking the trouser and shirt texels onto them would remove the faint knee line.
- The crawl FAIL on the TRELLIS.2 asset needs a texture or mesh smoothing decision, not a joint fix.
- Diego only; Manager, Héctor and Alejandro were not touched.

## Files changed from colddrone's uncommitted work

- `joints.py`: adds `seam`, cover support and `rigid_dev`. `rest_gap_pen_mm` now has a third value: rest seam.
- `dump_t.py`: an optional object-name argument.

## Rerun

```bash
cd blender/partes; B=/mnt/e/Blender/blender.exe; R=../render/reparto/partes/diego; A=../assets/reparto
./rig_trellis.sh                                           # fit full clip deform
SHOULDER=armhole PIN=1 WELD=1e-5 GARMENT='{"hem":0.275,"cuff":0.078}' WSLENV=SHOULDER:PIN:WELD:GARMENT \
  $B -b <rig_trellis/idle_trellis.blend> --python split.py -- <A/diego_trellis_refit.blend> <R/split_refit.json>
COVERS='{"collar":"hull","hem":"hull","shoulder":"hull","elbow":"hull","wrist":"band","hip":"hull","knee":"hull","cuff":"hull"}' WSLENV=COVERS \
  $B -b <A/diego_trellis_refit.blend> --python covers.py -- <R/split_refit.json> <A/diego_trellis_juntas.blend> <R/covers_final.json>
$B -b <A/diego_trellis_juntas.blend> --python joints.py -- <R/split_refit.json> <R/joints_final.json> 1-120:1
uv run -q python -I piel_check.py $R/covers_final.json
$B -b <blend> --python closeups.py -- <split.json> <out dir> <frame> [joints]
```

All paths are absolute Windows paths (`wslpath -w`).

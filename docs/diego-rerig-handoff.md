# Diego re-rig: one file for Mixamo and AccuRIG, and how the rigs get compared (2026-11-14)

The owner says the body is good but the bones look wrong when posed. Two external auto-riggers will rig the pass-2
smooth-3 mesh. This step prepares the file and the comparison.

## Upload files

One FBX serves both riggers:

- FBX: `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_rerig.fbx` (18 MB, texture embedded).
- Texture beside it (AccuRIG looks for textures in the model's folder):
  `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_rerig_basecolor.png`.
- Marker guide for Mixamo: `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_rerig_markers.png`.
- Plain front view: `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_rerig_front.png`.

**What the file is.** `blender/partes/export_rerig.py` writes it from the current rig blend's `Body`
(`diego_trellis_rig_full_p3.blend`).
- It is the smooth-3 TRELLIS.2 mesh (`diego-trellis2-s7-r2-f300s3.glb`) with its rig data removed: no modifiers,
  vertex groups or armature.
- One mesh named `Diego`: 198,989 vertices and 299,396 faces, the GLB's counts.
- Transforms are applied. The mesh is 1.0 m tall, centred in XY, with its feet on z = 0, facing −Y in Blender, which
  becomes +Z in the Y-up FBX.
  - "Centred at the origin" here means between the feet, the riggers' convention.
  - It is also the current rig's exact frame, so the returned rigs compare with no offset.
- The FBX is Y-up with −Z forward, and the scale is baked in (`FBX_SCALE_ALL`).
- It carries one material: the base colour texture, roughness 0.6.

**No re-pose was needed.** The mesh is already in an A-pose, arms about 25° below horizontal. The vertices are the
GLB's, scaled uniformly by 1/1.004 and moved onto the floor, so the face does not change.

**Checked by re-importing the FBX into an empty Blender:**
- one mesh object, 198,989 vertices and 299,396 faces;
- bounds x ±0.3993, y ±0.1879, z 0.0–1.0, with object scale 1;
- toes at y −0.142 (it faces front);
- texture 4096² packed, named `diego_rerig_basecolor.png`.

**Why FBX for AccuRIG too.**
- Users report that OBJ comes out 100× off in scale in AccuRIG, while FBX keeps the scale.
- 299k faces is under AccuRIG's reported 600k limit.
- 18 MB is under the roughly 20 MB at which forum users report Mixamo uploads failing.
- None of these limits is official; they come from forum reports.
- If Mixamo stalls on the upload, the fallback is a 100k-face decimation in the same frame. It has not been built.

## Mixamo: where the markers go (front view)

Mixamo shows Diego from the front, so **Diego's left is on the screen's right**. The guide image marks every spot:
green = on a visible feature, amber = estimate.

Heights are fractions of Diego's height from the soles. Side offsets are fractions of his height from the centre
line.

| marker | where, on screen | height | side offset | evidence |
|---|---|---|---|---|
| chin | centre line, at the bottom of the face, where the head meets the neck | 61 % | 0 | measured: the head narrows to the neck's width here |
| groin | centre line, at the top of the gap between the legs | 24 % | 0 | measured: the first row where the legs separate |
| wrists | where the forearm ends and the hand starts to widen, below the shirt line | 41 % | ±27 % | measured: the arm is narrowest at 21–26 % and widens from 27 % on |
| elbows | at the end of each sleeve, on the arm's centre line | 45 % | ±20.5 % | **estimate:** halfway between shoulder and wrist; the elbow isn't visible |
| knees | middle of each trouser leg, a little below halfway from groin to shoe | 16 % | ±6 % | **estimate:** halfway between hip and ankle; the trousers are straight tubes |

In the guide image's pixels (1024 × 1280, soles at y = 1221, head top at y = 58):
- chin (512, 509);
- groin (512, 945);
- elbows (273, 696) and (751, 696);
- wrists (198, 745) and (826, 745);
- knees (442, 1036) and (582, 1036).

The right/left pairs are symmetric: arm thickness at mirrored columns matches within 1 px.

**Mixamo settings:**
- Upload Character, then drop the FBX.
- Leave Skeleton LOD at its default.
- Place the markers as above.
- Download as FBX Binary, With Skin, Pose **Original Pose** (not T-pose), so the bones' rest matches the A-pose mesh.

## AccuRIG

- **Not installed on this PC.** There is no Reallusion folder under Program Files, and nothing was installed. The
  owner installs it; it may need a Reallusion account sign-in (not verified).
- Open the same `diego_rerig.fbx`, with the PNG beside it.
- Place the body markers the same way as in the Mixamo table.
- Export FBX in the rest pose (A-pose), with skin.

## What the silhouette already shows about the current rig (red × in the guide)

The current rig was built by firedrone's `rig_fit.py`. It places joints by ratio: elbow at 45 % and wrist at 75 % of
the shoulder→fingertip line; hip = crotch + 3 cm; knee = the hip–ankle midpoint.

- **Clear:**
  - **The wrist** (hand bone head, X 0.334, z 0.403) sits about 6 cm into the palm. The hand starts at X 0.27. On a
    big-handed chibi the 75 % ratio lands mid-palm, so the palm bends like a forearm.
  - **The elbow** (X 0.255) sits halfway down the bare forearm, about 5 cm past the sleeve end (X 0.205).
- **Uncertain:**
  - **The knee** (z 0.18 against the estimated 0.16).
  - **The ankle** (z 0.10, above the rolled cuff at 0.07–0.10). The shoe top is at z ≈ 0.066, so the real ankle is
    probably lower.
  - Only the riggers' output can settle these two, so they are open.
- **Not an error:** the red hip × above the green groin dot. The hip joint sits above the crotch; z 0.26 against the
  groin at 0.238 is plausible.

## When the FBX files come back

**What gets compared:** joint placement, with our own heat weights.
- Each returned skeleton's joint heads replace `rig_fit`'s landmarks. Our pipeline (`rig_full`, retarget, `pose_fix`,
  `deform.py`) then runs unchanged.
- `deform.py` needs Rigify `DEF-` bones, so the riggers' own skin weights are **not** compared.

1. Save the returned files as:
   - `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_mixamo.fbx`
   - `E:\Cursor Projects\MTO-colddrone\blender\assets\reparto\rerig\diego_accurig.fbx`

2. **Bridge:** `blender/partes/rig_from_fbx.py` (written; identity test passes).
   - It is `rig_fit.py` with the limb joints (shoulder, elbow, wrist, hip, knee, ankle) and the neck taken from the
     FBX. The spine split, breast, pelvis and foot bones still come from rig_fit's mesh landmarks.
   - It writes the same objects as `rig_fit` (`Body`, `rig`), so `rig_trellis.sh full clip deform` runs unchanged.
   - Names: Mixamo `mixamorig:*` / `mixamorig1_*`, or CC/ActorCore `CC_Base_*` (twist bones are included in their
     segment). Both conventions are recognised from the bone list.
   - **Any pose, unit or offset.** For each joint, a similarity transform (rotation, translation, uniform scale) is
     fitted on the vertices one adjacent segment dominates. FBX vertices are matched to ours by UV. The transform
     carries the joint onto our A-pose mesh.
     - Each joint is fitted on both adjacent segments and the more rigid fit (lower rms) is kept.
     - In a T-pose the upper arm's vertices near the shoulder are skin-blended (rms 1.2 mm, elbow 1.8 mm off), while
       the forearm moves rigidly.
     - Per joint the log prints `@@JOINT@@` with scale, rms, vertex count and `disagree` (the gap to the other
       segment's estimate). A large rms or disagreement flags a joint to check by eye.
   - **Identity test** (`blender/partes/rig_from_fbx_test.sh`). Fixtures built from the current rig's own joints
     (`rig_from_fbx_fixture.py`) must give back `diego_trellis_rig_p3.blend`'s 35 DEF bones within 1 mm:

     ```
     mixamo names, T-pose, scaled 1.7x and moved:  worst 0.16 mm (upper_arm); scale recovered 0.588 = 1/1.7
     CC names with twist bones, A-pose:            worst 0.00 mm
     UV matching: 198,825 of 198,989 vertices
     ```

   - The fixtures use our own weights. The real riggers' weights are smoother, so expect a larger rms; the log shows
     it per joint.

3. Command (from `blender/partes`). The baseline dance retarget was run with
   `BVH=<wham10> CLIP=dance RANGE=1-299:3 SUF=_p3 ./rig_trellis.sh clip deform`.

```bash
./rerig_run.sh _p3 _mx:diego_mixamo _ar:diego_accurig       # bridge, full/clip/deform, stills, 299-frame clip, eagle.sh
R=../render/reparto/partes/diego
python3 rerig_compare.py current=$R/rig_trellis_p3/deform_dance.json mixamo=$R/rig_trellis_mx/deform_dance.json \
  accurig=$R/rig_trellis_ar/deform_dance.json
```

4. **Ranking.** Flex angles on a retargeted clip come mostly from the mocap, so they won't separate the rigs.
   - Rank on:
     - region stretch (`dmm` p99 / max for hip, thigh, knee, shoulder, upper arm, elbow);
     - wrong-way frames and deform.py fails;
     - same-frame lit stills (`rerig_stills.py`, f60 / f153 / f240) side by side;
     - `eagle.sh` on each rig's 299-frame Workbench side clip (`rig_trellis<SUF>/clip/dance<SUF>.mp4`).
   - `rig_full` hides `Body_proxy` from renders, so the clip shows only the full mesh.

**Scripts written for this step** (in `blender/partes/`):
- `export_rerig.py` (the upload file and front view);
- `rerig_markers.py` (the guide image);
- `rig_from_fbx.py`, `rig_from_fbx_fixture.py`, `rig_heads.py`, `rig_from_fbx_test.sh` (the bridge and its test);
- `rerig_run.sh`, `rerig_stills.py`, `rerig_compare.py` (the comparison).

## Result: current rig vs Mixamo on wham10 (2026-11-14)

AccuRIG was dropped by the owner (GPU contention), so this compares two rigs.

**Sheet:** `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\rerig-actual-vs-mixamo.jpg`.
- Columns: current rig | Mixamo joints.
- Rows: rest skeleton, lit front f60 / f153 / f240, three-quarter f153 / f240, and Workbench side f153 from the revisar
  clip.

**Mixamo file:** 33 bones. The owner chose Std 65, but Mixamo found one finger chain per hand; the fingers aren't
used. It came back in the Original Pose with all 198,989 vertices. UV matching found 198,825 vertices; every joint
carried with rms 0.00 mm at scale 1.000.

**Where the joints moved** (left side; right is symmetric):

| joint | current (rig_fit) | Mixamo | moved |
|---|---|---|---|
| shoulder (upper_arm head) | 0.137, −0.012, 0.495 | 0.105, 0.004, 0.530 | 50 mm (up and inward) |
| elbow | 0.255, 0.003, 0.440 | 0.208, 0.010, 0.456 | 50 mm (back to the sleeve end) |
| wrist | 0.334, 0.003, 0.403 | 0.269, 0.004, 0.411 | 65 mm (out of the palm, to where the hand starts) |
| hip (thigh head) | 0.060, 0.005, 0.260 | 0.051, 0.004, 0.270 | 13 mm |
| knee | 0.060, −0.001, 0.180 | 0.058, −0.003, 0.162 | 18 mm (down) |
| ankle | 0.060, 0.005, 0.100 | 0.063, 0.002, 0.079 | 22 mm (down to the shoe top) |
| neck (spine.004 head) | z 0.605 | z 0.572 | 33 mm (down, to the neck) |

Mixamo agrees with the silhouette measurements in the marker table (wrist 0.27 / 0.41, elbow 0.205 / 0.45,
knee 0.16).

**Bends on the dance** (`rerig_compare.py`, `deform.py` on frames 1–299, every third frame; dmm = largest edge-length
change at a vertex in mm, p99 / max):

```
row                          current          mixamo
hip.L dmm p99/max          22.1 / 46.0     3.7 / 48.6
hip.R dmm p99/max          14.6 / 50.9     6.6 / 43.5
thigh.L dmm p99/max        10.8 / 18.3    13.6 / 22.1
thigh.R dmm p99/max        15.3 / 25.6    14.5 / 25.3
knee/shin.L dmm p99/max     4.8 /  6.6     6.5 / 12.4
knee/shin.R dmm p99/max     6.5 /  7.2     5.6 /  8.5
shoulder.L dmm p99/max     13.2 / 19.7    10.9 / 12.6
shoulder.R dmm p99/max      4.8 /  6.7     6.2 /  8.4
upper arm.L dmm p99/max    10.3 / 17.7     9.1 / 15.4
upper arm.R dmm p99/max     8.6 / 16.5    11.7 / 18.5
elbow/forearm.L p99/max     6.2 /  9.2     7.5 /  9.5
elbow/forearm.R p99/max     6.5 / 10.1     6.6 /  8.3
knee / elbow flex peaks    69 116 / 128 136   70 116 / 128 136   (mocap-driven, the same)
elbow.L wrong-way frames       25              24   (same frames, f133-166: a retarget issue, not the rig)
deform.py fails                50              48
```

**revisar** (`eagle.sh` on each 299-frame Workbench side clip): both exit 0, with crawl 0.08, flicker 0.00 and
strobe 0.

**Reading:**
- The stretch numbers are mixed. Hip p99 drops sharply (L 22.1 → 3.7, R 14.6 → 6.6), shoulder.L improves, and the
  left knee and right upper arm get a little worse.
- The clear difference is structural. The wrist leaves the palm (65 mm), the elbow moves to the sleeve end and the
  shoulder rises.
- In the stills, Mixamo's hands bend at the wrist where the current rig's palm folds. Judged by eye, not verified by
  a tool.

**Bridge fix made on the real file:**
- Mixamo's elbow sat 7 mm below the shoulder–wrist line (the A-pose droop). That made the rest bend plane point down.
- The first run flagged a wrong-way elbow on 94 of 100 frames (L 51, R 69), including frame 1.
- The bridge now keeps each joint's place along the limb and puts the rest bend only behind the elbow and in front of
  the knee, at least 6 mm. The elbow moves about 7 mm; the identity test still passes (worst 0.16 mm).
- A Mixamo Neck group with no dominated vertex is skipped; the Head segment carries the neck.

**Files:**
- `blender/assets/reparto/diego_trellis_rig_mx.blend` (the rig);
- `render/reparto/partes/diego/rig_trellis_mx/` (deform JSON, stills, clip, eagle log).

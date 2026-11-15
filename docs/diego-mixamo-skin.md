# Diego: Mixamo's skin weights against our stiff pieces, then four clips (2026-11-14)

Brief: `mothership/docs/queue/2026-11-14-diego-mixamo-skin-clips.md`. It follows `docs/diego-rerig-handoff.md`
(§ Result) and `docs/diego-trellis-pase2.md`.

**Verdict:** keep **Mixamo's own rig and skin weights** (column c). The cut rings, the elbow ball and the knee crease
come from the stiff-piece binding: they are gone on the same mesh with Mixamo's weights. The mitten hands, the fused
sleeve hems and the missing eyelids stay, because they are in the mesh. The wrong-way elbows and the dance's wrist
twist come from our retarget (`retarget.py` + `pose_fix` 80).

## Sheets (Windows paths)

- Step 1, three columns: `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\binding-3col.jpg`.
  - Columns: (a) rig_fit joints + parts/covers | (b) Mixamo joints + parts/covers | (c) Mixamo joints + Mixamo skin.
  - Rows: full front at rest / f60 / f153 / f240, three-quarter f153 / f240, elbow / wrist / knee at rest, then
    shoulder, elbow, wrist, hip and knee close-ups at f153 and f240.
- The heat-weight skin against Mixamo's skin, same joints:
  `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\binding\preview_bc.jpg`.
- Clip contact sheets (6 frames, front + three-quarter, Mixamo rig + skin):
  - `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\clips\dance-contact.jpg`
  - `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\clips\sitting_drinking-contact.jpg`
  - `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\clips\driving-contact.jpg`
  - `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\clips\guitar_playing-contact.jpg`

## Reference

- **Matched:** the `rerig-actual-vs-mixamo.jpg` run. Same mesh (TRELLIS.2 r2 300k / smooth 3), same wham10 retarget,
  `pose_fix` 80 and the same frames f60 / f153 / f240. The lighting is the same as `closeups.py` (sun and grey world).
- **Changed on purpose:**
  - all three columns run the dance, not the idle;
  - the covers are swept over the dance (`FRAMES=1-299:3`) for both parts columns, so neither column carries idle
    covers that open 7–38 mm;
  - the joint close-ups aim at each rig's own bone heads (`crops.py`), not at the cuts, so the smooth-skin column can
    be framed the same way.

## The check the mothership asked for first

`diego_trellis_rig_mx` uses **our** weights: its Body has 35 `DEF-*` groups and no `mixamorig:*` group. Its armature
modifier points at `rig`. Those are the heat weights rig_fit computes on the decimated proxy, carried to the full mesh
by `rig_full.py`.

It is also a smooth skin, not stiff pieces. So the earlier current-vs-Mixamo sheet compared two heat skins. The
parts-and-covers binding, where the rings and the ball come from, was not in it.

## Step 1: the three rigs

How each column was built (scripts in `blender/partes/mixskin/`):
- **(a)** `parts_dance.sh _p3`. It runs `split.py`, then the `covers.py` hull covers (wrist band) swept over the dance,
  `cover_normals.py` and `joints.py` seam on all 299 frames. Its source is `rig_trellis_p3/dance_trellis.blend`, the
  rig_fit joints.
- **(b)** the same chain on `rig_trellis_mx/dance_trellis.blend`, the Mixamo joints from `rig_from_fbx.py`.
- **(c)** `mixskin_build.py`. It imports `diego_mixamo.fbx` (Mixamo's 33 bones and its 28 weight groups, up to 6
  influences per vertex) into the (b) dance blend. It then bakes every Mixamo bone, per frame, from its `DEF-`
  counterpart: `W_mx = W_def · W_def_rest⁻¹ · W_mx_rest`.
  - (b) and (c) get the identical pose, so they differ only in the binding.
  - Same vertex order as our Body (0.000 mm correspondence).
  - Bone residual 0.005 mm. The connected Mixamo bones had to be disconnected first; before that the residual was
    10–14 mm.

**Seams of the parts columns** (`joints.py`, two-sided, every frame 1–299, mm; `out/joints_{p3d,mxd}.json`):

| joint | (a) seam max | (b) seam max |
|---|---|---|
| collar | 1.8 | 1.5 |
| shoulder L / R | 4.1 / 2.1 | 1.5 / 2.6 |
| elbow L / R | 3.5 / **9.2 (f239)** | 2.2 / **6.7 (f239)** |
| wrist L / R | 0 / 0 (band) | 0 / 0 (band) |
| hip L / R | 1.6 / 2.3 | 1.6 / 1.1 |
| knee L / R | 1.6 / 1.2 | 2.0 / 1.2 |
| cuff L / R | 0.4 / 5.7 | 1.0 / 1.6 |

`rigid_dev` is 2.2e-5: the parts never stretch.

**Cover sizes** (largest rest extent, mm; `cover_dims.py`). This is the "elbow ball":

| cover | idle covers (`_p3n`) | (a) dance covers | (b) dance covers |
|---|---|---|---|
| elbow L / R | 70 / 68 | **98 / 92** | 80 / 73 |
| wrist L / R (band) | 80 / 85 | 90 / 90 | 67 / 69 |
| shoulder L / R | 88 / 88 | 108 / 88 | 110 / 110 |
| knee L / R | 100 / 98 | 100 / 101 | 97 / 98 |

**Smooth-skin stretch** on the dance (`deform.py`, frames 1–299 step 3; dmm = the largest edge-length change at a
vertex, mm, p99 / max; `rerig_compare.py`):

```
row                     heat, rig_fit joints   heat, Mixamo joints   Mixamo skin (c)
hip.L                   22.1 / 46.0            3.7 / 48.6            2.6 / 18.4
hip.R                   14.6 / 50.9            6.6 / 43.5            2.7 / 18.4
thigh.L                 10.8 / 18.3           13.6 / 22.1            7.6 / 20.3
thigh.R                 15.3 / 25.6           14.5 / 25.3           12.1 / 20.5
knee/shin.L              4.8 /  6.6            6.5 / 12.4            5.0 /  8.9
knee/shin.R              6.5 /  7.2            5.6 /  8.5            5.6 / 10.7
shoulder.L              13.2 / 19.7           10.9 / 12.6            2.8 /  8.9
shoulder.R               4.8 /  6.7            6.2 /  8.4           11.3 / 17.7
upper arm.L             10.3 / 17.7            9.1 / 15.4           10.3 / 23.9
upper arm.R              8.6 / 16.5           11.7 / 18.5            9.4 / 22.4
elbow/forearm.L          6.2 /  9.2            7.5 /  9.5           12.2 / 14.8
elbow/forearm.R          6.5 / 10.1            6.6 /  8.3           18.9 / 20.4
seam gap (split verts)   0                     0                     0 (52,852 pairs)
elbow.L wrong-way frames 25                    24                    24
```

- **Where (c)'s forearm stretch sits** (`where_dmm.py`: the top 200 stretched forearm vertices, t = 0 at the elbow,
  t = 1 at the wrist):
  - It sits in the wrist half, median t 0.65–0.77.
  - It is the same at f60, f153 and f240 (L 12.5 mm each).
  - On the heat skin it sits at the elbow (t 0.03–0.19).
  - A stretch that does not change with the pose is the constant +80° `pose_fix` hand roll. Mixamo has no forearm
    twist bone to spread it, so the roll lands on the wrist.
  - Mixamo's own clips have no `pose_fix` roll, so it does not apply to them.
- **Wrong-way elbows:** the same 24 frames for (b) and (c). It is a bone measure, identical by construction.

**Reading the sheet** (by eye on `binding-3col.jpg`; the numbers above back it):
- **(a)** at rest already shows the elbow skin ball (98 mm dance cover) and the wrist band. In motion it shows the
  ring where the forearm part meets the cover.
- **(b)** moves the cuts to the sleeve end and the wrist, so the ball shrinks to 80 mm. The cut rims still show as
  ragged skin edges at the elbow, and as a dark ring at the knee in the f153 tiles.
- **(c)** bends the elbow, wrist and knee as one surface: no ring, ball or crease at rest or at f153 / f240. Its
  wrist reads a little pinched, which is the roll above.
- **Our heat weights** on the same Mixamo joints (`preview_bc.jpg`) crumple the trousers at the knee and hip at f153.
  That is hip max 43–49 mm against Mixamo's 18 mm: the TRELLIS shells under heat weights, firedrone's cause 1.

## Step 2: the clips on the Mixamo rig

- The three Mixamo clips play on their own rig and skin (`clip_build.py`: the clip FBX, the heat body's material,
  stand-ins placed from the clip's joint paths).
- The dance is column (c).
- Per clip:
  - six lit stills, front and three-quarter, aimed by the figure's own facing (`clip_stills.py`, `contact.py`);
  - a Workbench side clip with render.py's settings, following `mixamorig:Hips` (`clip_wb.py`);
  - `eagle.sh`;
  - `pen.py`.

**Stand-ins:**

| clip | stand-in | how it is placed |
|---|---|---|
| sitting_drinking | box seat, top at z 0.086 | at the lowest vertex the Hips / UpLeg bones dominate, seated frame 289 |
| driving | box seat (top 0.100) and torus wheel, r 124 mm, rim 12 mm, tilted 25° | the wheel is fitted through the mean of both hands |
| guitar_playing | 160 × 50 × 130 mm body and a 22 × 28 mm neck, carried by `mixamorig:Spine` | the body sits at the strumming hand, off the belly; the neck runs to the fretting hand at f1 |

**revisar** (`eagle.sh` on each Workbench side clip, all exit 0):

| clip | frames | crawl | flicker | strobe |
|---|---|---|---|---|
| dance (column c) | 299 | 0.08 | 0.00 | 0 |
| sitting_drinking | 457 | 0.05 | 0.00 | 0 |
| driving | 151 | 0.02 | 0.01 | 0 |
| guitar_playing | 188 | 0.12 | 0.00 | 0 |

**eagle-eye** on guitar_playing (the highest crawl, and a prop that touches the body): run `3281c5c0185f`.
- 0 findings, at medium confidence for the motion categories and low for the frame categories.
- It looked at 4 of 6 events and none of the 6 spread frames.
- Report: `clips/guitar_playing/revisar/guitar_playing_wb/eagle/report.md`.
- The other three clips were not reviewed. They pass revisar with lower crawl.

**Hands through the body or a prop** (`pen.py`, every 2nd frame):
- A hand or forearm vertex counts as inside when it is behind the nearest surface **and** 6 axis rays agree it is
  enclosed.
- The ray vote was added after the face-normal test alone gave 60 mm false hits on TRELLIS's inner shells (dance f115,
  checked with `pen_diag.py` and a close-up).
- Close-ups at the worst frames: `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\clips\pen-closeups.jpg`.

| clip | where | max depth | frames over 3 mm |
|---|---|---|---|
| dance | hands into hip / belly / thigh | L 6.9 mm (f101), R 7.5 mm (f223); forearms ≤ 5.9 | L f1–107, f245–299; R f1–109, f117–233 |
| sitting_drinking | hands into the hips while standing and while getting up | 7.4 mm (f35, f3); forearms ≤ 5.8 | f1–67, f77–145, f413–457; none into the seat, none into the head while drinking |
| driving | both hands through the wheel rim | 11.6 mm (the rim is 12 mm: the closed mitten passes through it) | every frame, 1–151 |
| guitar_playing | fretting hand through the neck; strumming hand into the hip and into the body block | neck 11.0 mm (f21), body block 14.3 mm (f179), hip 5.9 mm | neck and hip on every frame; the block at f49–59 and f135–161 |

**Reading:**
- On every clip, a resting hand sinks 6–7.5 mm into the hip. Mixamo's poses are made for human hips and hands; Diego's
  hands are thick mittens and his hips are wide.
- Both grips go through the stand-in: the mitten hand has no curled fingers to wrap a rim or a neck.
- The guitar block's thickness was a guess, so the 14 mm into the body block is partly placement.
- Seated, Diego sits on an 8.6 cm box with his knees up. Mixamo's chair height scales to the chibi's short legs.

## Step 3: what a paid mesh (Tripo) would remove

**Read by eye, not verified.** It is based on `pass2/probe/tripo/full_lit.png`; the face facet number comes from
pass 2.

| artifact | cause | would a Tripo mesh remove it? |
|---|---|---|
| elbow / wrist cut rings, elbow skin ball, knee crease | binding (parts + covers) | **no need**: Mixamo's skin already removes them on this mesh |
| trouser crumple at knee and hip (heat weights only) | binding (our heat weights on TRELLIS's shells) | no need: Mixamo's weights take the hip to 18 mm max |
| mitten hands, grips through the wheel and neck | mesh | **yes, in part**: Tripo's hands show a separate thumb and finger lines; fingers that curl need finger bones, which Mixamo did not find on this mesh (one chain per hand) |
| fused sleeve hems | mesh | **yes**: Tripo's sleeve hem stands off the arm |
| missing eyelids, flat brows | mesh | **yes**: Tripo models eyelids and brow relief (pass 2) |
| facets on the cheeks (shading) | mesh | yes: cheek facet energy about 1.21 against TRELLIS's 2.12 (approximate, pass 2) |
| wrong-way elbow.L, 24 frames f133–166 | retarget (wham10 → Rigify) | **no** |
| wrist twist on the dance (12.5–21.6 mm) | `pose_fix` +80° roll, no twist bone | **no**: drop the roll for the Mixamo rig, or add a forearm twist bone |
| hands 6–7.5 mm into the hips | retarget plus mesh proportions | no (slimmer hands help a little) |

**Is a paid mesh worth it?**
- For joints, no: the binding change fixes them for free.
- For the close-up face (eyelids, brows, facets) and for hands that hold props (guitar, wheel, cup), yes.
- So pay only if the hero shots show the face or the hands holding props.

## Open (the owner's)

- Keep Mixamo's rig and skin for every clip. The dance would then need wham10 retargeted onto the Mixamo skeleton (or
  the bake in `mixskin_build.py`), without `pose_fix`'s +80° roll.
- Stand-ins were placed from data; the prop builds are not done.
- Nothing was committed.

## Files (`blender/partes/mixskin/`, all new)

- `parts_dance.sh`: the stiff-piece chain on a dance blend.
- `mixskin_build.py`: column (c).
- `weights_of.py`: which groups drive a Body.
- `crops.py`: step-1 tiles.
- `sheet.py`: labelled grid.
- `cover_dims.py`: cover sizes.
- `where_dmm.py`: where the forearm stretches.
- `fbx_info.py`, `clip_probe.py`: what an FBX holds, and the joint paths.
- `clip_build.py`: clip blend and stand-ins.
- `clip_stills.py`, `contact.py`: contact sheets.
- `clip_wb.py`: Workbench clip.
- `clips_run.sh`: pen, clip and eagle per clip.
- `pen.py`, `pen_diag.py`: hands through the body or a prop.
- `closeup_at.py`: worst-frame close-ups.

**Blends** (git-ignored, `blender/assets/reparto/`):
- `diego_trellis_{refit,juntas,juntasn}_{p3d,mxd}.blend`;
- `diego_clip_{sitting_drinking,driving,guitar_playing}.blend`;
- column (c) is `render/reparto/partes/diego/rig_trellis_mxs/dance_trellis.blend`.

## Rerun

```bash
cd blender/partes/mixskin; B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
A=../../assets/reparto; D=../../render/reparto/partes/diego
./parts_dance.sh _p3 _mx                                                      # columns (a), (b)
$B -b "$(w $D/rig_trellis_mx/dance_trellis.blend)" --python mixskin_build.py -- "$(w $A/rerig/diego_mixamo.fbx)" "$(w $D/rig_trellis_mxs/dance_trellis.blend)"
$B -b <blend> --python crops.py -- <out dir> rest,60,153,240 parts|skin       # step-1 tiles; sheet.py builds the grid
$B -b --factory-startup --python clip_build.py -- <clip.fbx> "$(w $A/diego_trellis_rig_full_mx.blend)" <out.blend> sit|drive|guitar
$B -b <clip blend> --python clip_stills.py -- <stills dir> 6; uv run -q --with pillow python -I contact.py <out.jpg> <stills dir> <title>
./clips_run.sh name:<blend>:f0-f1 ...                                         # pen.py, Workbench clip, eagle.sh
```

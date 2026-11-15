# Diego TRELLIS.2 pass 2: denser mesh, lit judging, dance stress, knee line (2026-11-14)

Brief: `mothership/docs/queue/2026-11-14-mto-diego-trellis-pass2.md`, plus mothership's step 5 (wrist re-pose).
It follows `docs/diego-juntas.md` (rizzdrone's joints).

**Sheets:**
- Before/after, lit: `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\pase2-antes-despues.jpg`.
  - Columns: before (seed 7, 100k, idle covers) | pass 2 (300k, smooth 3, cover normals) | re-pose (a miss).
  - Rows: face, full body f70, shoulder, knee, wrist, dance f120 full and shoulder.
  - The two dance rows still show the smooth 2 mesh with union covers. Same shape and rig, so they were not
    re-rendered.
- Covers per clip: `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\pase2-covers-por-clip.jpg`.
  - Columns: covers swept over the idle | over the dance | over the union.
  - Built on the smooth 2 blends.

**Blends** (git-ignored, `blender/assets/reparto/`):
- `diego_trellis_juntas_p3n.blend` (the pass-2 pick: 300k / smooth 3, cover normals), from
  `diego-trellis2-s7-r2-f300s3.glb`;
- `_p3` (smooth 3 without cover normals);
- `_p2n`, `_p2` (the smooth 2 versions), `_p2_dancecov`, `_p2_union{,_idle,_dance}`, `_juntas_dance` (the before on
  the dance);
- GLBs `diego-trellis2-s7-*.glb`, `diego-trellis2-rp-*.glb`.

## Reference

- **Matched:** rizzdrone's `diego_trellis_juntas.blend`: same idle, cuts, garment lines, hull covers and band wrist.
  - Its Workbench clip, re-rendered with the same visual-lab `wham-video-mocap/render.py side`, gives revisar 0
    changed regions and dE 0.00 at f70.
- **Changed on purpose:**
  - TRELLIS.2 decimation and smoothing;
  - cover normals;
  - a lit EEVEE twin of the clip (`blender/partes/clip_lit.py`: closeups.py's sun and grey world, MTO satin
    roughness 0.42 / coat 0.2 on every material).

## 1. Denser, smoothed mesh

`trellis2.sh` takes `FACES` and `SMOOTH` from the environment (DecimateMesh / RemeshMesh); the JSON is unchanged.
Real face counts hit the targets: 99.3k, 249.3k, 298.8k–299.2k. At 300k, VRAM peaked at 11.8 GB while Blender
shared the GPU, with no OOM.

**TRELLIS.2 is not deterministic at a fixed seed.**
- Two fresh seed-7 runs, same input and settings, differ: r1 has barcode-striped pupils and a modelled mouth groove;
  r2 has clean pupils and the red mouth line like this morning's seed 7.
- Settings that only change decimation and smoothing reuse ComfyUI's cached sample, so variants of one run share
  one face.
- So the face is a lottery per fresh run. Compare mesh settings on one cached sample (r2 here).

**Facet energy** (`pass2/facets.py`: DoG std on flat-albedo patches of the lit head; lower = fewer facets) and **face
sharpness** (`probe.py flat`: albedo only, vs seed 7; the tight crop is `pass2/face_align.py`, box
`200 250 824 900`, flat albedo, aligned to seed 7):

| variant | cheek L | cheek R | chin | hair | sharpness × seed 7 | tight face crop × seed 7 |
|---|---|---|---|---|---|---|
| seed 7 (100k, s0) | 2.52 | 1.24 | 1.21 | 0.44 | 1.00 | 1.00 |
| r2 300k s0 | 2.16 | 1.27 | 1.08 | 0.39 | 1.03 | 0.95 |
| r2 250k s1 | 2.28 | 1.18 | 1.12 | 0.39 | 1.00 | 0.88 |
| r2 300k s2 | 1.83 | 1.14 | 1.04 | 0.37 | 1.02 | 0.93 |
| **r2 300k s3 (kept)** | **2.12** | **1.22** | **1.04** | **0.36** | **1.05** | **1.00** |

- **Kept 300k / smooth 3** (re-picked from smooth 2). The brief says a smoother mesh that blurs the face loses, and
  smooth 3 is the only variant that keeps the face on the tight crop (1.00×). Smooth 2 had the lowest cheek facet
  energy but lost 7 % on the face.
- Cost of smooth 3: cheek L facet energy 2.12 against smooth 2's 1.83 (seed 7: 2.52), and a small specular glint on
  one eyebrow (sheet, face row).
- Measured on the smooth 3 chain (`pass2/chain_s3.sh`, suffix `_p3`):
  - rig refit landmarks: knee 0.18, hip 0.26, leg_x 0.06 (smooth 2: 0.059);
  - all 14 seams stay ≤ 0.9 mm over idle frames 1–120, joint for joint the same as smooth 2
    (`pass2/seams.py joints_p2.json joints_p3.json`);
  - `piel_check` finds no skin cap; `rigid_dev` is 1.7e-5.

## 2. Lit clip vs Workbench (120 frames, side view)

Bracketed with `REVISAR_CRAWL` (revisar prints two decimals; the gate is ≤ 0.2):

| clip | Workbench crawl | lit EEVEE crawl |
|---|---|---|
| before (rizzdrone) | 0.200–0.201 FAIL | 0.14 pass |
| pass 2, flat covers (`_p2`) | 0.195–0.1975 pass | not rendered |
| pass 2 smooth 2 + cover normals (`_p2n`) | 0.199–0.200 pass | 0.14 pass |
| **pass 2 smooth 3 + cover normals (`_p3n`, kept)** | **0.197–0.198 pass** | **0.15 pass** |
| uncovered control (rizzdrone) | 0.21 | not rendered |

- Flicker 0.01 and strobe 0 on all of them. `eagle.sh` exits 0 on the `_p2n` and `_p3n` clips (Workbench at
  `REVISAR_CRAWL` 0.199, 0.200 and 0.201; lit at the default).
- `_p3n` clips: `pass2/clip_p3n_wb/p3n_wb.mp4`, `pass2/clip_p3n_lit/p3n_lit.mp4`.
- The slow-orbit crawl proxy on raw GLBs read 0.02–0.04 for every variant, so it can't rank them; judge on the idle
  clip.

## 3. Dance stress (WHAM `wham10.bvh`, 299 frames, `joints.py` on every frame)

Measured on the smooth 2 mesh before the re-pick. Smooth 3 has the same rig and idle seams (section 1), so these
numbers were not rerun.

Seam max in mm, with the frame in brackets:

| joint | idle covers on dance | dance-only covers | union covers on dance | union covers on idle |
|---|---|---|---|---|
| collar | 22.6 (f153) | 1.8 | 1.3 | 0.0 |
| hem | 6.7 | 0.1 | 0.2 | 0.0 |
| shoulder L / R | 36.7 / 24.5 | 3.4 / 2.1 | 3.3 / 0.5 | 0.1 / 0.0 |
| elbow L / R | 35.0 / 36.8 | 3.6 / **10.5 (f239)** | 5.0 / **7.9 (f240)** | 0.2 / 0.0 |
| hip L / R | 28.8 / 37.5 | 1.5 / 2.3 | 1.1 / 1.1 | 0.0 / 0.3 |
| knee L / R | 21.7 / 32.6 | 2.1 / 1.2 | 1.1 / 1.6 | 0.0 / 0.0 |
| cuff L / R | 14.6 / 20.6 | 0.4 / **5.6** | 1.2 / 0.7 | 0.7 / 0.1 |
| wrist L / R | 0 / 0 (band) | 0 / 0 | 0 / 0 | 0 / 0 |

- **Idle covers open 7–38 mm on the dance**, worst at the elbows, shoulders and hips. The dance turns the elbows
  133–138° about their mean (the idle: 2.5–3.9°).
- **The union covers** (one cover set swept over idle 1–359 plus the dance, via NLA, `partes/act.py union`):
  - every joint closes to ≤ 5 mm on both clips except elbow.R, which reaches 7.9 mm at f240 on a held-out frame
    between the step-3 samples;
  - **cost:** the covers grow to the dance's size: elbow 70 → 102 mm, shoulder.L 88 → 106 mm, collar 112 → 125 mm.
    Knees, hips and hem don't change.
  - On the idle the elbow cover reads as a skin ball, the rejected variant A (covers sheet, row 3).
- **Answer:** use the union for knees, hips, hem and cuffs. Build elbow and shoulder covers per clip (swap the cover
  set with the action), or accept the elbow ball.
- **`deform.py` on the dance** (`rig_trellis_p2/deform_dance.json`):
  - fails twist: 177.5° and 179.7° against a 90° limit (the +80° roll plus the dance's forearm turn);
  - fails elbow.L bending the wrong way in 26 frames (a retarget issue);
  - passes knee 69 / 116°, elbow 128 / 136° (limit 150), head 34°, neck 18°.
  - The idle passes every angle.

## 4. The knee line

- **Not texels.** TRELLIS.2's trouser and shirt albedo is (0, 0, 0), and the "flat" cover colour was that median
  already. A garment-texel bake changes nothing, so it was dropped.
- **The line was shading.** The flat-shaded hull wedge caught the studio light as a lighter band.
- **The fix tried:** `partes/cover_normals.py` gives every cover corner the smooth normal of the nearest
  parent/child surface, sampled at f60.
- **Result:** the band is gone. A thin dark crease stays where the cover's edge meets the trouser, a geometric lip.
  In the lit clip a small specular dash at the knee shows before and after.
- **eagle-eye run `aad5bb633b6d`** on `clip_p2n_wb` (smooth 2; not rerun on `_p3n`, which passed revisar): 3 minor
  findings:
  - the knee crease;
  - the wrist step and band;
  - the elbow seam line.
  - The knee finding changed form but is **not gone**. Next lever: round the cut rims, or pull the cover edge
    0.5 mm under the surface.

**Regression from pass 2 (verified, not fixed):**
- the elbow.L cut moved 41 mm down the forearm (`split.py` shift −35 → +10 mm);
- the forearm's rings are all 35–36 mm, so "narrowest ring" is noise there;
- on smooth 3 it stays at +10 mm (`pass2/split_p3.log`), and elbow.R moves too (+7.5 → +10 mm);
- it shows as a thin orange line above the wrist: `pass2/sheet/p2_nonorm/elbow.L_q_f70.png` (smooth 2) and
  `pass2/sheet/p3/elbow.L_q_f70.png` (smooth 3), also in the wrist row of the main sheet;
- fix: break ties within 1 mm toward the pivot, then rerun split, covers and clips.

## Tripo anchor (`pass2/probe/tripo`)

- Tripo's cheek L facet energy is about 1.21. The head framing differs between the models, so the number is
  approximate.
- Tripo also has modelled eyelids and brow relief; TRELLIS.2 has neither at any setting tried.
- So the pick is closer, not Tripo-level: cheek facets 2.52 → 2.12 against Tripo's ≈ 1.21.

## 5. Wrist re-pose: a miss (face gate)

- **The input works.** Klein `preset_edit`, seed 11, with the source head pasted back (`pass2/headpaste.py`):
  `blender/render/reparto/partes/diego/pass2/repose/diego_repose_k11_head.png`.
  - Face sharpness 0.99× the source.
  - Arm-to-torso gap 1.2–1.4 cm just under the armpit.
  - Klein seeds 22 and 33 had 0.1–0.8 cm there, too close for TRELLIS.
- **TRELLIS.2 changes the face.** Five runs: seed 7 ×3, seed 33, seed 101 (300k / smooth 2).
  - Face albedo sharpness 0.46–0.84× seed 7, dE 3.5–4.9.
  - Smaller round or slit pupils, and the red mouth line is lost.
  - Not shipped.
- **Mechanics blocked:** firedrone's `rig_fit.py` looks for an arms-out "arm band" row and finds none on the arms-down
  mesh (max() of an empty list). Left untouched.

## Open questions (the owner's)

- Elbow and shoulder covers: build them per clip, or accept the union's elbow ball on the idle?
- The wrist re-pose needs a face-preserving generator or a face texture transfer.

## Files changed (in `blender/partes/`, against rizzdrone's versions)

- `trellis2.sh`: `FACES` and `SMOOTH` env (DecimateMesh target, RemeshMesh smooth_iters).
- `rig_trellis.sh`: `GLB`, `SUF`, `BVH`, `CLIP`, `ROLL` and `RANGE` env; `retarget.log` is now
  `retarget_<clip>.log`; `--contacts` is passed only if the contacts file exists.
- `covers.py`: `FRAMES` env (the frames the swept covers are built over).
- New: `clip_lit.py` (lit EEVEE twin of the clip), `cover_normals.py` (surface normals onto the covers), `act.py`
  (one action or an NLA union drives the rig).

## Rerun

```bash
cd blender/partes; P=../render/reparto/partes/diego/pass2
FACES=300000 SMOOTH=3 ./trellis2.sh <png> 7 <prefix>            # TRELLIS.2 at pass-2 density (face lottery: probe it)
GLB=<glb> SUF=_p3 ./rig_trellis.sh                                # fit full clip deform -> rig_trellis_p3/
$P/pipe.sh _p3                                                    # split covers joints piel
B -b <juntas_p3.blend> --python cover_normals.py -- <split_p3.json> <out.blend>
$P/clips.sh <name>:<blend>                                        # Workbench + lit EEVEE clips, 120 frames
# all of the above for the smooth 3 pick, plus close-ups: $P/chain_s3.sh
$P/dance.sh a|b|c                                                 # dance: idle covers / dance covers / union
BVH=<bvh> CLIP=dance RANGE=1-299:3 SUF=_p2 ./rig_trellis.sh clip deform
```

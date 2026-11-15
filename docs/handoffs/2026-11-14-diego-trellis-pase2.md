# Handoff: Diego TRELLIS.2 pass 2 (grindsetdrone, 2026-11-14 18:00)

**Spec:** `/home/black/projects/mothership/docs/queue/2026-11-14-mto-diego-trellis-pass2.md`, plus mothership-10's
step 5 (wrist re-pose).
**Worktree:** `/mnt/e/Cursor Projects/MTO-colddrone`, branch `cc/colddrone`. Commit nothing.

**Notes so far:** `docs/diego-trellis-pase2.md`. It is complete for the 300k / smooth 2 pick; the "Update after the
re-pick" section below lists what to change in it.

**Scripts and evidence:** `blender/render/reparto/partes/diego/pass2/` (called `P2` below).

## Decisions

- **Mesh pick: 300k faces, smooth_iters 3, sample r2.** GLB: `blender/assets/reparto/diego-trellis2-s7-r2-f300s3.glb`.
  - Face sharpness on the tight face crop (`face_align.py`, box `200 250 824 900`, flat albedo, against seed 7):
    smooth 0 → 0.95×, smooth 1 → 0.88×, smooth 2 → 0.93×, **smooth 3 → 1.00×**.
  - The brief says a smoother mesh that blurs the face loses, so smooth 3 replaced smooth 2. It is the only variant
    that keeps the face.
  - Facet energy (cheek L / cheek R / chin / hair): smooth 3 → 2.12 / 1.22 / 1.04 / 0.36; smooth 2 → 1.83 / 1.14 /
    1.04 / 0.37; seed 7 → 2.52 / 1.24 / 1.21 / 0.44.
  - Smooth 3 puts a small specular glint on one eyebrow.
- **Step 5 (wrist re-pose) is a miss.** Mothership agreed: report it, leave firedrone's `rig_fit.py` untouched.
  - Face numbers: sharpness 0.46–0.84× seed 7, dE 3.5–4.9, smaller round or slit pupils, the red mouth line lost.
  - rig_fit blocker: it needs the arms-out "arm band" row and finds none on the arms-down mesh.
  - Klein seed-11 input, source head pasted back:
    `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\pass2\repose\diego_repose_k11_head.png`.
- **Step 4:** the colour bake was dropped. TRELLIS's trouser albedo is (0, 0, 0); the knee line was shading.
  `partes/cover_normals.py` (surface normals onto the covers) is the fix kept.

## Done (numbers are in `docs/diego-trellis-pase2.md`)

**Step 1, mesh variants:** done (see Decisions).

**Step 2, Workbench and lit clips at 300k / smooth 2** (crawl bracketed with `REVISAR_CRAWL`):

| clip | Workbench crawl | lit crawl |
|---|---|---|
| before | 0.200–0.201 FAIL | 0.14 |
| `_p2` (flat covers) | 0.195–0.1975 | not rendered |
| `_p2n` (cover normals) | 0.199–0.200 | 0.14 |

**Step 3, dance (WHAM `wham10.bvh`)**, measured on the smooth 2 mesh:
- Idle covers open 7–38 mm on the dance.
- Dance-only covers close to ≤ 5 mm except elbow.R 10.5 mm and cuff.R 5.6 mm.
- Union covers (idle + dance): idle ≤ 0.7 mm; dance ≤ 5 mm except elbow.R 7.9 mm at f240.
  - Elbow covers grow 70 → 102 mm, shoulder.L 88 → 106 mm, collar 112 → 125 mm: the elbow reads as a ball on the idle.
  - Conclusion: union for knees, hips, hem and cuffs; per-clip covers for elbows and shoulders.
- `deform.py` on the dance fails twist (177.5° / 179.7°, limit 90°) and elbow.L wrong-way (26 frames).

**Step 4, eagle-eye run `aad5bb633b6d`** on `P2/clip_p2n_wb`: 3 minor findings (knee crease, wrist band, elbow line).
The knee finding is **not gone**: it changed from a lighter band to a thin dark crease, a geometric lip.

**Sheets:**
- `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\pase2-antes-despues.jpg`
- `E:\Cursor Projects\MTO-colddrone\blender\render\reparto\partes\diego\pase2-covers-por-clip.jpg`
- Both currently use the smooth 2 blends.

**Tripo anchor** (`P2/probe/tripo`): Tripo's cheek L facet energy is 1.21. The head framing differs between the
models, so the number is approximate. Tripo also has modelled eyelids and brow relief that TRELLIS lacks.

**Regression found:**
- On the 300k mesh, the elbow.L cut snapped from −35 mm to +10 mm; the forearm's rings are all 35–36 mm, so the snap
  is noise.
- It shows as a thin orange line at the elbow, which the wrist tile also shows.
- Verified in `P2/sheet/p2_nonorm/elbow.L_q_f70.png`.
- Fix (not done): in `split.py`, break ring-radius ties within 1 mm toward the pivot.

## Running when this was written

`P2/chain_s3.sh` writes to `P2/chain_s3.log` and ends with `CHAINDONE`. It runs:
1. `rig_trellis.sh` with `SUF=_p3`;
2. `pipe.sh _p3` (split, covers, joints, piel);
3. `cover_normals` → `diego_trellis_juntas_p3n.blend`;
4. `clips.sh p3n` → `P2/clip_p3n_{wb,lit}`;
5. close-ups → `P2/sheet/p3`.

## Exact next steps

1. Wait for `CHAINDONE` in `P2/chain_s3.log` (`scripts/esperar.sh log <file> CHAINDONE`, in the background).
   Then check:
   - `python3 P2/seams.py P2/joints_p2.json P2/joints_p3.json`: seams ≤ 0.9 mm;
   - `piel_check` OK;
   - `grep "CUT@@ elbow" P2/split_p3.log`: whether the elbow snap moved again.
2. Run revisar crawl on `P2/clip_p3n_wb/p3n_wb.mp4` and `P2/clip_p3n_lit/p3n_lit.mp4`. Bracket Workbench with
   `REVISAR_CRAWL=0.199 / 0.200 / 0.201`. Then run `eagle.sh` on both (no `--review` unless one FAILs).
3. Rebuild the main sheet with the smooth 3 tiles:
   - in `P2/sheet_main.json`, swap `sheet/p2/` → `sheet/p3/` and the face tile `probe/s7-r2-f300s2` →
     `probe/s7-r2-f300s3`;
   - `uv run -q --with pillow python -I P2/sheet_p2.py P2/sheet_main.json blender/render/reparto/partes/diego/pase2-antes-despues.jpg`;
   - the dance row may stay on the smooth 2 union covers: same shape and rig. Say so in the notes.
4. Update `docs/diego-trellis-pase2.md`:
   - the pick becomes 300k / smooth 3, with the face-crop table above;
   - the p3n crawl numbers;
   - VRAM: up to 11.8 GB while Blender shared the GPU, no OOM (the doc wrongly says "below 11 GB");
   - the elbow regression is verified;
   - the Tripo anchor;
   - a "Files changed" section: `trellis2.sh` (FACES, SMOOTH); `rig_trellis.sh` (GLB, SUF, BVH, CLIP, ROLL and RANGE
     env; `retarget.log` is now `retarget_<clip>.log`; `--contacts` only if the file exists); `covers.py` (FRAMES);
     new `clip_lit.py`, `cover_normals.py`, `act.py`.
5. Write the report to `/home/black/.cache/cc-deck/reports/all/grindsetdrone-1794696466.md`:
   - the sheet's Windows path and a one-line verdict ("closer, not Tripo-level: cheek facets 2.52 → 2.12, Tripo
     ≈ 1.21; no eyelid or brow relief");
   - at most 3 summary lines;
   - the step-5 items mothership asked for;
   - a `paths:` line, the `gotchas:` lines below, `model: opus effort: high`, then `verdict: fine` (or `redo`: the pick
     changed late).
6. SendMessage `mothership-10` one line pointing at the report. If the name doesn't resolve, check ListAgents; never
   send to a suggested name.
7. Tell the user that ComfyUI is still up and the local LLM servers are down (`oc-up` brings them back).

## Open questions (the owner's)

- Elbow and shoulder covers: per clip, or accept the union's elbow ball?
- The wrist re-pose needs a face-preserving generator or a face texture transfer; both are the owner's call.

## gotchas (for the report; general method → visual-lab via `gotchas:` lines)

- TRELLIS.2 isn't deterministic at a fixed seed: fresh runs differ (barcode vs clean pupils) → probe every fresh run's face; compare mesh settings on one cached sample (changing only DecimateMesh/RemeshMesh reuses ComfyUI's cache, about 27 s each)
- A slow-orbit crawl proxy on a static GLB read 0.02–0.04 for every variant while the idle parts clip reads 0.20 → it can't rank mesh variants; judge on the real clip
- revisar prints crawl with two decimals, so 0.20 can be pass or FAIL → bracket it with `REVISAR_CRAWL=0.199/0.200/0.201`
- TRELLIS.2 black cloth has albedo (0, 0, 0), so a texel bake onto covers is a no-op → the knee line was shading; transfer the surface normals instead
- firedrone's `rig_fit.py` needs arms-out rows wider than 2× the pelvis → it can't rig an arms-down re-pose
- On a cylindrical forearm, the "narrowest ring" snap is noise (35–36 mm everywhere), so denser meshes move the cut 4 cm → tie-break toward the pivot
- The rizzdrone idle action is 359 frames, not 120 → NLA unions and clip renders need an explicit range (`frame_end=120`)
- Blender on Windows given `--python /mnt/...` (a WSL path) resolves it under the cwd → wrap every script path in `wslpath -w`
- Klein edits drift the face (sharpness 0.77–0.80×) → paste the source head back with a feathered mask: 0.99×
- A PreToolUse hook denies any Bash call with system python3 plus the word numpy, even inside a heredoc → use Edit or `uv run`

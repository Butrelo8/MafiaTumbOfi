# Diego rebuilt from parts (2026-11-14, skibididrone; in progress)

Brief: `mothership/docs/queue/2026-11-14-diego-parts-pipeline.md`. Research: `visual-lab/docs/research/2026-11-14-blender-parts-motion.md`.
Scripts: `blender/partes2/` (commit `136b11a`). Assets (git-ignored): `blender/assets/reparto/partes2/`. Renders:
`blender/render/reparto/partes2/diego/` (times in `tiempos.log`).

**Status at 22:55:** steps 1–3 done, step 4 half done (rig back from Mixamo, not bound yet), steps 5–6 not started.

## Reference

- **Matched:** `comfy-out/para-subir/diego.png` (the source image), and today's fused Diego
  (`diego-trellis2-s7-r2-f300s3.glb`, colddrone) as the frame and the alignment target: 1.0 m tall, feet on z = 0,
  facing −Y. These are the Mixamo upload's bounds (±0.3993 × ±0.1879 × 1.0, checked).
- **Changed on purpose:** Diego is now separate parts: a body in briefs, a head with sculpted lids, hands with spread
  fingers, a shirt, pants, shoes and hair.

## 1. Part images (Klein `preset_edit`, Lanczos input, 2 seeds each, ~20 s per image)

Sheet: `E:\Cursor Projects\MTO-skibididrone\blender\render\reparto\partes2\diego\partes-klein.jpg`. Picks, with the reason:

| part | pick | why |
|---|---|---|
| body in briefs | s22 | boxer briefs keep a smooth hip-to-thigh line; s11's high-cut briefs leave a groin crease |
| head (bald, "sculpted 3D lids") | s11 | holds the source's scale; s22 grew the skull ~8 % |
| hand (spread fingers, back view, wrist stub) | s22 | widest finger gaps (both are good) |
| shirt / pants / shoes | s22 / s11 / s11 | Klein gave ghost-mannequin garments; shoes s11 keep place and openings |
| hair | both tried | both failed in TRELLIS (below) |

- Masks: Grounded-SAM and Florence-2 are not installed. TRELLIS's own BiRefNet cutout and the fused mesh's colour and
  height labels (`target.py`) did that job, so no SAM pass was needed.

## 2. TRELLIS.2 (StableGen graph via colddrone's `trellis2.sh`, local)

- Times: 97–197 s per part. The body is 200k faces, the head 200k, the hands 60k, the clothes 100k (all smooth 3).
- One hand job hung 15 min in the shape-VAE decode. `/interrupt` did not free it, so ComfyUI was restarted, and
  `parts_trellis.sh` now has a 600 s per-job timeout.
- **The head s7 has real lid relief** (sculpted upper lids, visible in the three-quarter view). This differs from pass 2
  ([C197]: no lids at any setting). The difference is the Klein prompt, "sculpted 3D lids that stick out over the
  eyeballs". Seed 33 has bar-shaped pupils, so s7 was kept.
- **Hair failed.** Both hair images came back ~2× deeper than the head: a front view of a thin shape gives TRELLIS no
  depth. **The hair is cut from today's fused mesh** instead (`hair_fused.py`). It is TRELLIS.2 output, already in this
  frame, grown ×1.086 so it clears the new scalp by 2 mm.
- The garments are good open shells, with the neck, sleeves, hem, waist and cuffs open and the seat modelled. Their
  depth is guessed, so they get a per-axis fit (below).

## 3. Assembly

- **Body:** `fit.py body`, ICP with scale onto the fused Diego's bare skin above the waist: p50 3.3 mm, p90 8.5 mm,
  scale 0.976.
- **Head:** `fit.py head`, ICP onto the placed body's head: p50 2.6 mm.
- **Hands:** `hand_fit.py`, landmark Procrustes, no ICP.
  - The landmarks are the wrist-stub centre, the middle fingertip and the thumb tip on the hand, against the wrist ring
    and forearm axis on the body. Wrists are at x ±0.256, the forearm axis ~30° down, the ring radius 28 mm.
  - Fingers point along the forearm, the palm faces down and the thumb faces forward. TRELLIS gave a right hand; the
    left is mirrored.
- **Seams** (`assemble.py joint()`, the same method at the neck and both wrists):
  - the part is bisected on the cut plane;
  - its lowest 10 mm is snapped, angle by angle, onto the body's ring + 0.5 mm, fading to none within 10–12 mm of the
    ring;
  - the body keeps a column clamped inside the ring that runs 14–22 mm into the part;
  - the hands slide back 19–20 mm so the palm base meets the forearm.
- Ring radii: neck body median 43.1 mm, head rim 46.0 mm; wrists body 28.0 / 27.2 mm, hand rims 26.5 / 26.1 mm.
- Left by eye at a 7 cm frame, not measured: a thin crease and two 5 mm sliver triangles at each palm edge, and a soft
  fringe at the back of the neck.
- **Garments onto the new body** (`fit_body.py`; fitting to the fused clothes left the new body's chest and legs
  through them):
  - ICP onto body + ease (shirt 6, pants 5, shoes 3 mm), per-axis scale for shirt and pants;
  - smoothed push-out to 2 mm clearance;
  - pants clipped at z 0.29, under the shirt hem;
  - nothing dropped.
- Rest clearance: shirt min −5.6 mm (241 vertices inside, at the hem's inner side), pants 1 vertex at −1.4 mm, shoes
  min +1.9 mm.
- Dressed sheet (rest): `E:\Cursor Projects\MTO-skibididrone\blender\render\reparto\partes2\diego\fit\dress_sheet.png`.
  The toes out of the shoes and the crotch patch go under the body mask.

## 4. Mixamo

- The full skin (274k faces, four overlapping shells joined, 14 MB) **bounced twice** in the Auto-Rigger, with no error.
- The **rig proxy** passed in ~1.5 min: a 3 mm voxel remesh, filled, decimated to 90k faces, 1.9 MB
  (`make_proxy.py`). The owner placed the markers (guide: `mixamo/diego_partes2_markers.png`).
- **65 bones, with all 5 fingers × 4 bones on both hands** (today's Diego: one chain per hand).
- Files are in `blender/assets/reparto/partes2/mixamo/dl/`: `diego_partes2_proxy3_mixamo.fbx`, `p2_{sitting_drinking,
  driving,guitar_playing,idle}.fbx`, `old_Idle.fbx` ("Standing Idle" on old Diego).
- The owner may have misplaced a wrist marker: **flag any wrist twist** and he will re-place it.

## Next (not done)

1. Bind: import the proxy rig. Data Transfer (nearest face interpolated) the proxy's `mixamorig:*` weights onto the full
   skin (`diego_partes2_skin.blend`, same frame), then the clothes from the skin.
   - Bone-parent the hair to Head and the shoes to the feet.
   - Mask modifier on the body (body vertices covered by a garment, plus the briefs zone 0.20–0.33 and the feet below
     the shoe tops); Corrective Smooth after the Armature.
2. Eyelids: the head already has lid relief. Separate lid meshes (an extrusion of the socket) with open, half and closed
   keys; a blink test.
3. Clips: the four `p2_*.fbx` onto the bound rig; old Diego's clip blends in colddrone (`diego_clip_*.blend`) plus
   `old_Idle.fbx`.
4. Measure:
   - poke-through per frame: clothes→body (penlib `inside_outer` on the visible body), body→clothes (anchored cloth
     triangle), hands (colddrone `pen.py`);
   - sheets beside today's Diego;
   - `eagle.sh` per clip;
   - a finger close-up.

## Rerun

```bash
cd blender/partes2; B=/mnt/e/Blender/blender.exe; w(){ wslpath -w "$1"; }; F=../render/reparto/partes2/diego/fit; A=../assets/reparto/partes2
./parts_klein.sh "$PWD/../render/reparto/partes2/diego/klein" [part ...]          # ComfyUI up
./parts_trellis.sh name:/abs/image.png:seed:faces:smooth ...
uv run -q --with trimesh --with numpy --with scipy --with pillow python -I target.py <fused.glb> $F/target.npz
uv run ... python -I fit.py body|head|shirt|pants|shoes|hair <part.glb> $F/target.npz $F/<part>.json [body.glb body.json]
uv run ... python -I hand_fit.py $A/hand_s22.glb $A/body.glb $F/body.json $F/hand.json
$B -b --factory-startup --python assemble.py -- "$(w $F)" "$(w $A)" head_s7 hand_s22 "$(w $A)\\diego_partes2_skin.blend"
$B -b "$(w $A/diego_partes2_skin.blend)" --python export_mx.py -- <out.blend> <dir> diego_partes2 $F/hand.json   # markers + full FBX
$B -b "$(w $A/diego_partes2_skin.blend)" --python make_proxy.py -- "$(w $A/mixamo)" diego_partes2_proxy3 0.003 90000
uv run ... --with networkx python -I fit_body.py shirt|pants <garment.glb> $F/<g>.json $A/body.glb $F/body.json $A/head_s7.glb $F/head_s7.json $F/<g>_body.npz
uv run ... python -I hair_fused.py $F/target.npz $A/head_s7.glb $F/head_s7.json $F/fused_body.npz
uv run ... python -I shoes_box.py $A/shoes.glb $F/shoes.json $F/target.npz $F/pants_body.npz $F/shoes_body.npz   # after pants; no zscale
$B -b "$(w $A/diego_partes2_skin.blend)" --python dress.py -- "$(w $F)" "$(w $A)" "$(w $A/diego_partes2_dressed.blend)" shirt=shirt_s22 pants=pants shoes=shoes hair=fused
./rebuild_tail.sh                                    # bind, look.py, 4 clips, lids (~2 min)
```

gotchas:
- TRELLIS.2 hair from a front-view part image → came back 2× deeper than the head (no depth cue); cut the hair from the full-figure mesh instead
- TRELLIS.2 garments from Klein ghost-mannequin images → good open shells, but depth guessed: fit with per-axis scale; never drop "inside" vertices as caps (they were real panels)
- TRELLIS.2 head without lids → asking Klein for "sculpted 3D lids that stick out over the eyeballs" in the part image gave real lid relief
- TRELLIS.2 job hung 15 min in shape-VAE decode, /interrupt did nothing → restart ComfyUI; per-job timeout in the batch script
- Mixamo Auto-Rigger bounced a 274k-face skin of four overlapping joined shells (no error) → voxel-remesh proxy (3 mm, filled, 90k) rigged in 1.5 min with all finger bones; transfer weights back
- joining parts by deleting vertices → sawtooth rims; bisect on the cut plane, snap the band to the body ring with a fade, keep the body column clamped inside
- a garment push-out with a hard clamp on ~12k vertices crumpled the shirt → harmonic (smoothed) push-out only, report the residue
- signed distance from surface samples on a TRELLIS mesh flipped on its ~500 small inner pieces → sample only the largest component with fixed normals

## 2026-11-15 00:15 — model pass (successor session)

- **The 11-14 23:37 poke-through table is void.** `pokethrough.py` measured against the skin's "largest connected
  piece", which was 1,303 of 206,161 vertices: TRELLIS splits the skin at UV seams into 3,439 pieces. Welded by
  position, it is 36 pieces: a double body wall (two full-height pieces), four overlapping open shells per hand, the
  head open at the neck. The script now uses the rigged Mixamo proxy (one watertight piece, same weights) as the body
  volume. Positive control: a point 5 mm inside the hip reads 4.15 mm. `hands_cloth` is not validated yet.
- The owner paused clip fixes (23:56). The work is model quality: seams, lids, hands, shoes, skin, hair, chain.
- Owner's picks (00:13): pale peach skin, soft dark-brown matte hair without the fringe notches, and the silver
  chain, all as in `diego.png`.
- **Shoes (owner: "not lined up with the pants").** Cause: TRELLIS made the shoes 1.45× too long (28 cm against an
  18.5 cm foot; it guessed the depth axis from a front-view image, like the hair). `fit_body.py` fits shoes with
  uniform scale only, so the toe lined up and the heel hung 8.6 cm behind the leg. Its push-out against the bare toes
  also crumpled the toe box. Not the shoe_L/R split, not the hem length.
  - Fix: `shoes_box.py`, a per-axis box fit of each shoe onto the fused Diego's shoe region (the rerig Diego's shoes,
    19.4 cm), no push-out. (Superseded at 00:41: the reference height is right, and each shoe also slides under the leg.)
  - Variant a (height scaled ×0.78) was dropped here at first, wrongly: see 00:41.
  - Sheet: `render/.../model/feet/shoes_ab.jpg`.
- **`bind.py` shoe split:** the vertex selection was not flushed to the faces, so with the new shoes all faces went to
  shoe_L and shoe_R was empty. Fixed (world x, edges and faces selected from their vertices).
- **Look (`look.py`, after bind):**
  - Skin texture: the skin cluster's median goes to the source's peach, sRGB (226, 192, 170).
  - Hair: flat dark brown (64, 55, 51) and matte (the texture was near black).
  - A silver chain: a 1.1 mm curve 1.5 mm off the shirt, dipping 4.5 cm in front, on Spine2.
  - Rendered hue matches the source: cheek R/G 1.16 against 1.18, G/B 1.14 against 1.13. Workbench studio light
    renders every albedo at ~0.64 brightness, so it reads darker than `diego.png`.
- **Lids:**
  - Smooth shading and a level-2 subdivision; depth smoothing up from 6 to 20 passes.
  - Column banding, as the RMS of the second difference of the closed lid's column-mean luminance (8-bit levels):
    1.75 / 2.43 before, 1.23 / 1.62 now.
  - Lid colour against the skin around it: within (3, 6, 7) levels.
  - Open: a white crescent at the outer side of the left eye when closed (1,389 white pixels at a 500 px face, as
    before). A full-width grid reduced it to 984 but put a winged flap on the half key. A real fix wants the eye's own
    surface offset outward as the lid.
- **Open (tried, not fixed):**
  - **Fringe notches** are sculpted steps at the edges of the raised fringe block in the TRELLIS hair. These all left
    them: Laplacian smoothing (the shell collapses into the scalp), voxel remesh (the open sheet vanishes), pushing
    groove vertices out to a smoothed envelope, and zipping boundary vertices within 2–4.5 mm. A fix needs new hair
    (a Klein 3/4-view hair image to TRELLIS, or a modelled bowl cut).
  - **Wrist seams:** two tries, both worse, reverted. Decimating before the joints didn't help. Clamping the body
    column inside the hand's per-angle radius made spikes. The teeth's owner shell is not found yet (next: a
    piece-coloured render).
  - **Thin pale lines over the brows** (texture or brow geometry, not checked).
  - **Pants crotch patch.**
  - The idle pose sinks the hands into the shirt hem at the hip (a pose issue; clips are parked).
- Rebuild from the dressed blend: `rebuild_tail.sh` (bind, look, 4 clips, lids; ~2 min). The clip blends changed, so
  their 11-14 eagle results are stale.
- Stills: `render/.../model/v2/model_v2.jpg` (rest, beside the source).

### 00:41–01:00: shoes lined up, body single wall
- **The body had two complete walls** (TRELLIS; welded pieces of 39k and 24k vertices, both full height). The inner
  one's sawtooth made the wrist teeth (a piece-coloured render shows them green) and the band at the back of the neck.
  `assemble.py drop_inner_wall()` keeps the outer wall (larger median radius at z 0.35–0.55: 169.4 against 167.0 mm).
  The wrist teeth are mostly gone. Left: a faint ring line and small flaps under the right wrist.
  Seams sheet: `render/.../model/seams/cmp.jpg`.
- **Shoes, line-up (owner 00:39).**
  - The box fit put the shoes where the fused Diego's shoes were, but the new legs stand elsewhere: the pant leg met
    the shoe 57 % back from the toe, where the reference has 74 %.
  - `shoes_box.py` now slides each shoe so the pant leg at the shoe top sits at the reference's fractions of the shoe
    box: 0.74 back, 0.30 from the inner edge. `diego.png` agrees: cuff centre ~0.32 from the inner edge.
  - Height: the reference (top 0.09, source ~0.083) is right. Keeping TRELLIS's height put the cuff inside the shoe.
  - Sheet: `render/.../model/v3/feet_v3.jpg`.
- **Hair:** flat brown. Recolouring only its dark texels had left skin-coloured stripes on the nape edge.
- **Open:**
  - the ragged nape edge of the hair (geometry, cut from the fused mesh; it was there on 11-14 too);
  - a ragged patch on the shirt's lower back at the hem (on 11-14 too).

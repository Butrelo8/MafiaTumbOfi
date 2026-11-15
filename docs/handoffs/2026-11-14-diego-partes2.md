# Handoff: Diego rebuilt from parts, steps 5–6 to finish (2026-11-14 23:16, skibididrone)

Spec (re-read first): `/home/black/projects/mothership/docs/queue/2026-11-14-diego-parts-pipeline.md`.
Running doc with every decision, number and the rerun block: `docs/diego-partes2.md` (it stops at 22:55, before bind/lids/clips:
update it). Scripts: `blender/partes2/` (each has a usage header). Commits: `136b11a`, `d79eff1` + the commit with this file.
Times: `blender/render/reparto/partes2/diego/tiempos.log` (append the remaining steps).

## Done since the running doc

- **Rig bound** (`bind.py` → `blender/assets/reparto/partes2/diego_partes2_rig.blend`).
  - Mixamo proxy rig (`mixamo/dl/diego_partes2_proxy3_mixamo.fbx`, 65 bones, 5 fingers × 4 per hand), same frame
    within 0.5 mm.
  - Weights: Data Transfer (nearest face, interpolated) proxy → skin "Diego" → shirt, pants; Armature, then Corrective
    Smooth.
  - Hair bone-parented to Head; shoes split to `shoe_L` / `shoe_R` on the Foot bones.
  - Mask "hidden" (33 % of skin vertices): skin covered by a garment (normal ray within 4 cm), below the shoe tops
    (z 0.121) and the briefs zone z 0.20–0.33.
- **Clips** (`clip.py`): `diego_p2_{idle,sitting_drinking,driving,guitar_playing}.blend` (251/457/151/188 frames).
  - Blender 5.2 layered actions: the action slot must be set explicitly, already in `clip.py`.
  - `_v.blend` versions also carry the lids.
- **Eyelids** (`lids_fit.py` → `render/.../fit/lids.json`, `lids_build.py`).
  - A 24 × 12 lid grid over each eye's white outline, 4 mm proud of every head vertex there, depth smoothed.
  - Keys open/half/closed, bone-parented to Head, skin colour.
  - Blink keyed at f100–109 in `diego_p2_idle_blink.blend` (= `diego_p2_idle_v.blend`).
  - Strip: `render/reparto/partes2/diego/blink_strip.png`. It reads as a blink; faint column banding remains, plus a
    sliver of white at the outer lower corner when closed (not measured).
- **Poke-through** (`pokethrough.py`, every frame, mm):
  - cloth→body uses the nearest skin face plus penlib's 6-ray `enclosed`, read-only from colddrone
    (`penlib.py` mtime 1794710302);
  - body→cloth is a ray back into the body that crosses cloth within 1.5 cm;
  - hands→trunk is a nearest-face sign test with no ray vote.
  - Positive control (shirt shrunk ×0.9): raw 7.5, body→cloth 1.9 → the test fires.
  - **driving: all 0.0** over 151 frames and at rest. The other three were still running in background task
    `bg1cd8roz`, writing `render/reparto/partes2/diego/clips/poke_<clip>.json`. If those files are missing, rerun:
    `cd blender/partes2; $B -b "$(w $A/diego_p2_<clip>.blend)" --python pokethrough.py -- "$(w $R/poke_<clip>.json)" 1`
    (~1.7 s per frame).
- **Workbench clips + eagle.sh: done, all four pass, exit 0** (`clips_wb.sh` →
  `render/reparto/partes2/diego/clips/<clip>/<clip>_wb.mp4`, `eagle.log`). Today's Diego, for comparison: 0.02 / 0.12 /
  0.05.

  | clip | frames | crawl | flicker | strobe |
  |---|---|---|---|---|
  | driving | 151 | 0.03 | 0.01 | 0 |
  | guitar_playing | 188 | 0.10 | 0.00 | 0 |
  | idle | 251 | 0.03 | 0.01 | 0 |
  | sitting_drinking | 457 | 0.04 | 0.00 | 0 |
- Sent to the user: the part sheet `partes-klein.jpg`, `fit/dress_sheet.png`, `blink_strip.png`,
  `clips/idle_st.png`.

## Poke-through results (finished 23:37; `render/reparto/partes2/diego/clips/poke_<clip>.json`, per-frame rows inside)

| clip | cloth→body visible max (frame, frames > 1 mm) | cloth→body raw | body→cloth | hands→trunk |
|---|---|---|---|---|
| driving | 0.0 | 0.0 | 0.0 | 0.0 |
| guitar_playing | **18.8 (f122, 111 frames)** | 18.8 (127) | 15.0 (188 frames) | 0.0 |
| idle | 2.4 (f190, 8 frames) | 2.4 | 15.0 (251 frames) | 0.0 |
| sitting_drinking | **16.2 (f82, 10 frames)** | 18.4 | 15.0 (58 frames) | 0.0 |

- **The done-check (≤ 1 mm) is not met yet on 3 of 4 clips.** Every rest value is 0.0.
- **body→cloth = 15.0 is the ray's 1.5 cm limit** on every frame, so it is almost surely a false hit of the metric.
  The likely case: arms down beside the shirt, where a visible arm vertex's inward ray reaches cloth across the arm.
  Find the vertex (add its position to the rows) and render it before believing it.
- **cloth→body 16–19 mm on guitar f122 and sitting f82 is a real candidate.**
  - Likely sleeve or hem cloth inside the arm or thigh at a strong bend (Data Transfer weights from the skin, but the
    cloth sits 2–6 mm off it).
  - Next: close-ups at those frames, then fixes. Candidates: a Shrinkwrap "outside surface" modifier on the clothes
    after the Armature (target the skin, offset 1 mm), or more Corrective Smooth.
- **hands→trunk 0.0 everywhere** disagrees with today's Diego (hands 6–7.5 mm into the hips), and the test has no
  positive control. Before reporting it, check that a hand vertex placed inside the hip reads > 0.

## Exact next step

1. When `clips_wb.sh` is done (one GPU job at a time), make the side-by-side sheets with `stills.py`.
   - **New:** `$B -b <diego_p2_<clip>_v.blend> --python stills.py -- <dir> <frames> - <Left|Right>`.
   - **Today's Diego:** `$B -b --python stills.py -- <dir> <frames> <fbx> <side>`. Its FBX files (With Skin =
     today's mesh + Mixamo skin) are `/mnt/e/Cursor Projects/MTO-colddrone/blender/assets/reparto/rerig/clips/{sitting_drinking,driving,guitar_playing}.fbx`
     and the idle `blender/assets/reparto/partes2/mixamo/dl/old_Idle.fbx`.
   - Frames: idle 1,50,100,150,200,250 (blink at 104); sitting 1,90,180,270,360,450; driving 1,30,60,90,120,150;
     guitar 1,37,74,111,148,185.
   - Compose with `sheet.py` (labelled grid): columns today front | parts front | today ¾ | parts ¾ | today hand |
     parts hand. The hand column is the done-check's finger close-up. `stills.py` is untested: test it on one frame.
2. **Check for wrist twist** on the clips. The owner may have misplaced a wrist marker. If the forearm twists, message
   mothership-10 and he re-places it.
3. Update `docs/diego-partes2.md` with:
   - bind, lids and clips;
   - per-clip poke-through and eagle numbers next to today's (colddrone `docs/diego-mixamo-skin.md` § pen.py table:
     hands into hips 6–7.5 mm, wheel 11.6, guitar neck 11.0);
   - time per step;
   - whether the recipe is ready for the manager;
   - the gotchas below.
4. Run eagle-eye only if a clip FAILs (`~/projects/visual-lab/cross-tool/skills/eagle-eye/SKILL.md`). Then commit,
   write the report `/home/black/.cache/cc-deck/reports/all/skibididrone-1794712782.md` (≤ 3 lines + paths, `paths:`
   line with image/clip paths, then `model: opus effort: high`, `verdict: ...`), and SendMessage mothership-10 one
   line.

## Open / decisions to report

- **Hair** is cut from today's fused TRELLIS mesh (`hair_fused.py`). Both part-image TRELLIS hairs came back 2× too
  deep. Say so in the report.
- **Hands:** no props in these clips. hands→trunk is measured only against the body (driving 0.0). Props stand-ins
  are colddrone's; if needed, the owner places props with a locked placement .blend (mothership rule, 22:36).
- **Seams:** neck and wrists are ring-snapped. At a close-up the wrist shows a thin crease and two 5 mm slivers;
  not measured.
- **Rest clearance:** shirt has 241 vertices up to 5.6 mm inside the body at the hem's inner side, but the 0.0 driving
  result is measured with the enclosed-vote test.
- **Recipe for the manager:** looks ready except hair, which wants a 3/4 view image or a cut from a full-figure mesh.
  Mixamo needs the proxy route.

## Suggested skills

`eagle-eye` (read its SKILL.md by path) only on a FAIL; `director` not needed; `comfy-local` not needed (ComfyUI is
stopped and the GPU is free for Blender).

## gotchas (also for visual-lab via the report)

- TRELLIS.2 hair from a front-view part image → came back 2× deeper than the head; cut the hair from the full-figure mesh
- TRELLIS.2 garments from Klein ghost-mannequin images → good open shells, depth guessed: per-axis-scale fit; never drop "inside" vertices as caps
- TRELLIS.2 head without lids → Klein prompt "sculpted 3D lids that stick out over the eyeballs" gave lid relief
- TRELLIS.2 job hung 15 min in shape-VAE decode, /interrupt did nothing → restart ComfyUI; 600 s per-job timeout
- Mixamo bounced a 274k-face skin of 4 overlapping joined shells (no error) → 3 mm voxel-remesh proxy, 90k, rigged in 1.5 min with all finger bones; Data Transfer back
- Blender 5.2: an action assigned to another armature does nothing until `animation_data.action_slot = act.slots[0]`
- eyelid shape keys on TRELLIS eyes: a sphere fit is unstable (flat disc eyes) and sampling depth on the whites puts the lid behind the sculpted lid relief → grid over the white outline, depth from all head vertices there, smoothed, 4 mm proud
- poke-through on TRELLIS meshes: a nearest-face sign test alone read 30 mm false hits → add penlib's 6-ray enclosed vote, and a positive control (shrunk shirt)

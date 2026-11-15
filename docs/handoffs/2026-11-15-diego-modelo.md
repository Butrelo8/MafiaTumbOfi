# Handoff: Diego from parts, model pass (2026-11-15 00:58, successor of skibididrone)

Branch `cc/skibididrone`, commits `9596cfa`, `01b673d`, `487ef99`. Running doc: `docs/diego-partes2.md` § "2026-11-15".
Previous handoff: `2026-11-14-diego-partes2.md`.

## State

- **On hold.** The owner is comparing this route with a Tripo-generated rigged Diego (saltydrone). Resume only if the
  owner keeps the parts route (ask mothership-10). Clip fixes are parked (owner, 23:56).
- **Rebuild:**
  1. `assemble.py` → `diego_partes2_skin.blend` (it now drops the body's duplicate inner wall).
  2. `dress.py` with `shoes_box.py`'s `shoes_body.npz` → `diego_partes2_dressed.blend`.
  3. `blender/partes2/rebuild_tail.sh` (~2 min): bind, `look.py` (skin, hair, chain), the 4 clips, lids.
- **Stills:** `stills.py` with a rest pre-script (`arm.data.pose_position = "REST"`), `feet_view.py`, `seam_view.py`.
  Latest sheets:
  - `render/reparto/partes2/diego/model/v2/model_v2.jpg` (whole model; hair and shoes changed since)
  - `.../model/v3/feet_v3.jpg`
  - `.../model/v3/hands_neck.jpg`
  - `.../model/v3/back.jpg`
- **Poke-through numbers:** the 11-14 table is void, because it tested 1,303 of 206,161 skin vertices.
  `pokethrough.py` now measures against the watertight proxy (control: 5 mm reads 4.15). `hands_cloth` is not
  validated. No clip has been re-measured.
- **Clip eagle results** (11-14) are stale: the meshes changed (shoes, lids, single-wall body).

## Open list (if the parts route is kept)

1. **Hair fringe notches.** Sculpted steps at the edges of the raised fringe block in the TRELLIS hair. These all
   left them: smoothing, voxel remesh, pushing groove vertices out to an envelope, and zipping boundary vertices.
   Needs new hair: a Klein 3/4-view hair image → TRELLIS, or a modelled bowl cut. **Owner's call; hold.**
2. **Hair nape:** a ragged comb-like lower edge (the cut from the fused mesh; it was there on 11-14 too). Same fix as 1.
3. **Lid crescent:** with the lid closed, eye white still shows at the outer side of the left eye (1,389 white pixels in
   a 500 px face). A full-width grid made it 984 but put a winged flap on the half key. The real fix: build the lid
   from the eye's own surface, offset outward. **Owner's call; hold.**
4. **Wrist ring:** after dropping the inner body wall, a faint ring line and small flaps under the right wrist remain.
   - Clamping the body column inside the hand's per-angle radius makes spikes, on both the double and the single wall.
     Don't retry it.
   - Untried: snap the hand rim 1 mm inside the ring instead of 0.5 mm outside. Or delete the body column entirely
     and let the hand rim close onto the forearm.
5. **Shirt back hem:** a ragged dark patch on the lower back at the hem (it was there on 11-14 too). Not diagnosed.
   Likely the pants waistband or the hem's inner side (241 vertices up to 5.6 mm inside the body at rest).
6. **Brows:** thin pale lines over both brows (texture or brow geometry, not checked).
7. **Pants crotch patch** (front view).
8. **Clips:** the idle pose sinks the hands into the shirt hem at the hip. Hand placement goes through the owner's
   locked placement .blend rule. Re-run `clips_wb.sh` + eagle and `pokethrough.py` before any clip claim.

## gotchas

- TRELLIS.2 body came back with two complete walls (welded pieces 39k + 24k verts, both full height) → keep the outer one (larger median radius); the inner wall's sawtooth made the seam teeth
- TRELLIS skin "largest connected piece" was 1303 of 206161 verts (split at UV seams) → weld by position first; for inside tests use the watertight rig proxy, not the skin
- TRELLIS.2 shoes from a front-view part image came back 1.45× too long → per-axis box fit onto a reference shoe, then slide so the leg sits at the reference's fraction of the shoe; no push-out (the foot is masked)
- bmesh vertex select without flushing to faces → mesh.separate took every face; set edge/face select from their verts
- Workbench studio light renders albedo at ~0.64 brightness → compare hue ratios (R/G, G/B) with the source, not raw RGB
- open-shell TRELLIS hair: smoothing collapses it, voxel remesh deletes it, boundary zips do nothing for sculpted fringe steps → regenerate the part instead

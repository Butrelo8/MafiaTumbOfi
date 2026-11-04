# Flow job4 (sacristía → camarín), fixed: verdict

**Master:** `job4_fix.mkv` (FFV1 bgr0, 1920×1080, 24 fps, 204 frames = 8.5 s, no audio); h264 preview `job4_fix_h264.mp4`
(crf 18). Built from `va/` (aligned tail, chosen); `vp.mkv` = plain tail (job3's), **not chosen**.
At speed: `lado_flow_fix.mp4` (Flow as delivered | fix, 204 frames, Flow holds its f191 for the last 12),
`pintura_al_paso.mp4` (fix f28–165, left 1100 px at 100 %: the invented painting from its entrance to its exit).
No LOOK/halación (seethingdrone's pass in `tmp/07/look` applies later). Nothing written to `entrega/`.
User's decision on the invented painting: **keep as provisional, exit smear included (2026-10-14)**. Name and `entrega/`: vibeship's call.

## Reference
Matched: job3's montage (`../../job3/fix/montar_fix.py`): f0 = the plate exactly, 10-frame head dissolve from the plate
warped by the per-frame SIFT homography, tail dissolve into the loop's own wrap (228–239) and loop frames 0–19 raw.
Changed on purpose: no paste (no object of the plates goes wrong here), and the tail dissolves geometry as well as
colour, because job4's camera is still pushing at the cut (job3's stood still from ~f150).

## What Flow did against the prompt
The prompt asked to push into the dark painting over the turntable and have **its** canvas swing open. Flow kept that
painting in place and invented a **second** framed painting (a woman in a red dress and green mantle holding a candle,
a jug below) that swings in from the left edge (f30–43, motion-blurred), comes at the lens, darkens and becomes the
black (f67–86), and on the camarín side hangs at the left of the room, then swings out of frame (f118–~158).
It reads as plan 1's idea (a portrait that opens like a door), not as the painting that was asked for.

## Measured (Flow 1280, then the RTX ×1.5 frames)
- **Head.** f0 vs start.png: diff 2.22, scale 1.0001, 0.0 px (`extremos.py`); start.png = sacristía loop f0
  (`cmp` byte-identical). The push is slow from the start: scale 1.0029 at f10, 1.0198 at f30, 1.0729 at f66.
- **Tail.** Best cut **f184** (scale 0.9999, 0.0 px, diff 2.79); but the camera keeps pushing: 0.9869 at f172,
  1.0068 at f191 (~1.2e-3 scale per frame, not easing). revisar on Flow: end 1.1 at f184, drift 1.5.
- **Black.** `../cobertura.py`: **20 frames ≥ 90 % under luma 20, f67–86, 100 % at f67** (column max 1). revisar:
  hidden-cut 20 frames f67–86, morph 0 frames in both scenes, swap f67.
- **Neon (the likely invented light).** `neon.py` (the tube's signature: a pale strip with deep red on both sides): in
  every sacristía frame f0–66 (it drifts x1230 → x1274 of 1280 with the push), **in no frame f67–191**. Deep-red
  share 8 % → 0.00 % in the black → 2.3 % in the camarín (end.png 2.25 %: the candles).
- **Other invented lights.** `camarin.py`, f87–191 every frame: **0 px** with luma > 200 that have no bright plate
  pixel within 15 px (end.png brought onto each frame by a SIFT homography).
- **Novel colours.** revisar flags 2.5–3.2 % f94–126; `novel_mapa.py` at f99 puts it on the grey stone jamb at the
  right edge (the doorway Flow drew between the rooms), not a light. Like job3's stairs: Flow's own, no plate.
- **Painting gone before the tail.** Left 15 % columns vs the warped end plate (`camarin.txt`, `izq` vs `der`): 18–21 at
  f135–143, 7.9 at f155, **3.4 at f159 (middle of the frame 4.2)**, 1.4–1.9 from f163. Gone 13 frames before the
  tail dissolve starts (f172).

### The invented painting: stable or morphing (`pintura.py`, `pintura_pasos.py`)
Tracked per side from one Flow frame (ECC homography of the canvas box, 1920), stabilised crops in `pint_sac/`,
`pint_cam/` (strips `pint_{sac,cam}_tira.jpg`). Step ncc = high-pass detail correlation of consecutive stabilised
frames (a morph dips; a slow light change does not).

| stretch | what it does | face step ncc | reading |
|---|---|---|---|
| f30–43 | swings in from the left | ~0 (0.0–0.5) | motion blur of the swing, not measurable |
| f44–62 | hangs, darkens (face luma 27 → 8) | 0.52–0.86, two dips 0.29/0.08 at luma 8 | **holds** (dips at the noise floor) |
| f63–66 | near black | 0.60–0.68 | holds |
| f87–117 | camarín, lit up (face luma 9 → 29) | 0.57–0.88 | **holds**: same face, candle, jug |
| f118–~135 | swings out at the left edge | track lost (0.11–0.29) | **morphs**: the face loses its features and the candle smears into a glow over ~8 frames (`pint_cara_salida.jpg`, full rate f115–126) |

Across the black, the painting is the same subject and palette but **redrawn**: the face is about 14 % of the canvas
width at f44 and about 19 % at f100 (read off the grids, `grid44.jpg`/`grid100.jpg`); ECC between the two canvases does
not lock (detail ncc 0.00). The redraw happens inside the 20 black frames, so it is never on screen as a change.

## Fix (`montar4.py`, TAIL=alineado)
1. 1920 via the RTX pass (`scripts/loop-vivo.sh rtx`, ×1.5, `rtx/job4_rtx_00001_.mp4`).
2. Head: f0 = start.png exactly; 10-frame cosine dissolve into Flow from the plate warped by the per-frame SIFT
   homography (gap 2.77–3.04 warped vs 2.78–3.22 plain: the push is only 0.3 % by f9, so both are fine).
3. Tail: Flow f172–183 into vestidor loop f228–239. Per frame A_k = SIFT similarity of loop f0 → Flow frame; both
   layers are warped to a shared geometry that goes from Flow's to the plate's with the dissolve weight, so the push
   eases to a stop on the plate. Blend gap **aligned 3.40–3.80 vs plain 3.75–7.79** (f177: 3.51 vs 6.49). Then loop
   frames 0–19 raw.
4. Not fixed: the painting's exit morph (f118–~135, see below).

Variants: `vp` (plain dissolve, job3's): ghosts the 1.3 % scale gap at mid-dissolve. **`va` kept** for the halved
blend gap. Cost: the camera's per-frame scale change rises from 1.14e-3 to a peak of 1.83e-3 at f175 before easing to
0 at f184 (`costura_va.txt`; plain measures 1.70e-3 from the blend itself). Arriving at rest on the plate means
covering the same 1.3 % in the same frames, so a short surge is unavoidable with any ease-out.

## Numbers
`revisar.sh job4_fix.mkv --inicio ../start.png --fin ../end.png` (`revisar_job4_fix/`):

| check | value | threshold | result | where |
|---|---|---|---|---|
| start | 0.0 | <= 4 | pass | f0 vs --inicio |
| sharpness-start | 1.00 x start | 0.5-2 | pass | |
| end | 0.0 | <= 4 | pass | best cut f201 |
| sharpness-end | 1.00 x end | 0.5-2 | pass | |
| drift | 0.0 | | info | |
| dark | 100 % < 20 | | info | f67 |
| hidden-cut | 20 frames >= 90 % | >= 5 | pass | f67–86 |
| morph | 0 frames both scenes | <= 12 | pass | swap f67 |
| novel | 2.5 % at f99 | >= 0.5 % flagged | info | f94–126 (the stone jamb; Flow original 3.2 % f101) |
| events | 2 | | info | f67 swap, f94 novel |

Seams (`costura.py`): master f184–203 = vestidor loop f0–19, **max diff 0**; step master f203 → loop f20 = 0.0001
against the loop's median step 0.0000 (the vestidor loop is near-static). Tail steps f172–183: 0.0077–0.0093 falling to
0.0008, within the range of Flow's own steps before the cut (0.0063–0.0096 at f160–171). Master frames are bit-exact to `va/` (f100,
f183 checked).

## Not fixed
- **The painting's exit (f118–~135):** as it swings out at the left edge the face washes out and the candle smears
  into a glow (the track loses it: step ncc 0.11–0.29). A local fix would mean pasting f100–110's canvas on a track of
  the frame's moulding while it goes edge-on and leaves the top of the frame; not attempted before the user decides
  whether the painting stays at all.
- The painting itself is Flow's invention, not the sacristía's painting over the turntable that the prompt named.
- The stone jamb at the right of the camarín (f87–~150) is Flow's doorway; no plate covers it.

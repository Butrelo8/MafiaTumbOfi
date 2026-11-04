# Flow job3 (cripta → atrio), fixed: verdict

**Master:** `job3_fix.mkv` (FFV1, 1920×1080, 24 fps, 204 frames = 8.5 s, no audio); h264 preview `job3_fix_h264.mp4`.
`job3_fix_master.mkv` / `v8.mkv` = variant v8 (phone brightened ×1.16), **not chosen**; `v9.mkv` = same bytes as the master.
At speed: `lado_antes_despues.mp4` (Flow as delivered | fix; the side-by-side stops at 192 frames, the shorter clip),
`lado_telefono3.mp4` (100 % crop f0–80: Flow | fix | v8). User's OK: **given 2026-10-13 (~20:00), plate's phone (v9)**. Nothing written to `entrega/` yet (name and encodes: vibeship's call).

## Reference
Matched: the SUV paste in the atrio (`e5/charcos/pegar_charco.py`): the plate's object goes back in through a mask; the
rest stays as it is. Changed on purpose: the object moves, so it rides a per-frame track with motion blur and
matched sharpening instead of a fixed paste.

## Measured first (Flow, 1280 → RTX ×1.5)
- **Ends.** f0 = start.png (diff 2.8, 0.0 px, scale 1.0000). The tail does **not** drag, unlike job1/job2: f184–191 is
  within 0.1 px, scale ≤ 1.0006 (`extremos.py`). The camera stands still from ~f150; the atrio fades up from black.
- **Black.** It does reach black: 28 frames ≥ 90 % dark (f116–143), 100 % at f122 (job2 never did).
- **Phone (the user's "looks off").** Planar track + stabilised crops (`estab_tel_tira.jpg`): Flow loses the dial from
  ~f24, washes the body to cream and smears it from ~f48. Detail correlation with the plate's phone: 0.73 (f0) → 0.55
  (f24) → 0.22 (f48) → −0.01 (f68) (`medir_tel.txt`).
- **Other objects.** Candles keep their shape (`estab_vela{I,D}_tira.jpg`). Their correlation drop comes from motion
  blur, not deformation, so they were left alone. Altar face: res 2–4 on a luma-7 surface, nothing to paste.
  Atrio (SUV, gate): 0.1 px/frame, detail correlation 0.89–0.95 through the fade-up, no deformation. The stair passage
  and the arches in the move are Flow's own, with no plate to paste from (see "Not fixed").
- **Tracks.** The phone's gray ECC track shears once the phone deforms (jump at f53: 10 → 21 px against the candles).
  An altar-band homography is ill-conditioned (the band is thin; 22 px off by f48). Used instead: an **affine ECC on
  Lab b* (yellowness), blurred**, which places the phone by its gold silhouette (`seguir_oro.py`): smooth (frame-to-frame
  acceleration 0.5–3 px through f64), sits on Flow's phone through f68 (`overlay` check), extrapolated f69–80 as it leaves.

## Fix (`montar_fix.py`, SHUT=0.2 GAIN=0 SHARP=1)
1. Phone + coiled cord from start.png (mask `mascara_telcable_1920.png`: two hulls, handset and body, plus the cord;
   the window under the handset stays Flow's), on the smoothed track; motion blur = 9 sub-frame warps over 0.2 of a
   frame; per-frame unsharp to Flow's own phone sharpness (k 0.25–1.5). f0–79.
2. Head: f0 = start.png exactly; 10-frame cosine dissolve into Flow from the plate warped by the per-frame SIFT
   homography. Warped vs plain: the gap the dissolve blends at f9 is 4.2 vs 9.3, so no ghosting.
3. Tail: Flow f172–183 dissolve into atrio loop frames 228–239 (the loop's own wrap); then loop frames 0–19 **raw**,
   so the player's `COSTURA` (loop resumes at f20) is exact.
4. 1920 via our RTX pass (`loop-vivo.sh rtx`, ×1.5, 36 s); geometry identical to bicubic (< 0.02 px).

Variants: v1–v3 (shutter 0.5/1.0) over-blurred the phone against Flow's crisp edges; v4 (0.2, no sharpening) soft;
v5/v8 (sharpening + gain ×1.16 from the altar band) and v9 (sharpening, no gain). **v9 kept:** against v8 it has fewer
novel colours (0.6 % at f70–74 vs 0.8 % at f56–75), less highlight clipping (hi 0.05 % vs 0.21 %), and a paste fringe
at or under the untouched frame's (below), with phone correlation equal or higher.

## Numbers
`revisar.sh job3_fix.mkv --inicio ../start.png --fin ../end.png` (`revisar_job3_fix/`):

| check | value | threshold | result | where |
|---|---|---|---|---|
| start | 0.0 | <= 4 | pass | f0 vs --inicio |
| sharpness-start | 1.00 x start | 0.5-2 | pass | |
| end | 0.4 | <= 4 | pass | best cut f202 |
| sharpness-end | 0.98 x end | 0.5-2 | pass | |
| drift | 0.0 | | info | |
| hidden-cut | 28 frames >= 90% | >= 5 | pass | f116-143 |
| novel | 0.6% at f71 | >= 0.5% flagged | info | f70-74 box x0.00-0.30 (Flow original: 0.6 % f69–71) |
| events | 4 | | info | f68 jump+novel, f84, f97 jump, f122 darkest |

The f84/f97 "jumps" are Flow's own camera motion, identical to RTX alone (7.53 vs 7.53). They are flagged only
because the 20 near-static loop frames lower the median (1.88 vs 2.10). The paste adds ≤ 0.24.

Seams: master f184–203 = atrio loop f0–19, max diff **0**; step master f203 → loop f20 = 0.0002 = the loop's median
step; dissolve steps f173–183 0.0006–0.0029, under Flow's own fade-up steps (0.002–0.007).

Phone (plate's phone placed by the track, mask core; `medir_tel.py`):

| frame | Flow ncc | Flow dif | fix ncc | fix dif |
|---|---|---|---|---|
| 0 | 0.73 | 18.9 | 0.91 | 8.8 |
| 24 | 0.55 | 24.5 | 0.97 | 7.7 |
| 48 | 0.22 | 34.5 | 0.93 | 8.7 |
| 56 | 0.13 | 38.8 | 0.88 | 11.5 |
| 64 | 0.04 | 44.8 | 0.82 | 13.5 |
| 68 | −0.01 | 49.3 | 0.84 | 12.3 |

Paste edge, `revisar.sh <frame> --ref <RTX frame> --mask <warped paste mask>` at f30/50/60/68 (`foto/`): align 0 px,
colour dE 0.00 outside the phone, sharpness 0.95–1.00×, halo 0 %; mask-fringe dE 13.3/12.4/5.5/6.5 against the
untouched RTX frame's 14.3/13.5/6.7/6.8 with the same mask. **mask-notch FAIL 11 %**: the "bite" is the triangle
between the rising cord and the body, which the mask leaves concave on purpose (the check's own comment: a concave
subject bites too). `revisar.sh` video mode has no `--mask`, so the phone zone was checked with foto mode per frame.

## Not fixed
- The stair passage, the arch stone and the wall texture in the move (f60–120) are Flow's invention; no plate covers
  them, so they can't be pasted. Fixing them would mean regenerating (H3), which was not started.
- The phone is a 2D paste (affine): as the camera trucks past, the plate's phone keeps its frontal view instead of
  turning (angle not measured). Flow's phone is also drawn wider than the plate's from ~f56.
- The fixed phone keeps the plate's light: darker gold than Flow's beam-lit cream (v8 brightens it, at the cost above).
- Candles: left as Flow drew them (shape held in the stabilised crops).

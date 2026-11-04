# 07 pair A2 (closed wardrobe door → crypt altar): Seedance 1.5 pro vs the approved local take (2026-10-16)

**Verdict: worse for MTO, mixed on motion.** Seedance makes a real camera move with no cut or dissolve: it passes the
door, goes through a stone arch and pushes in to the altar. The baseline is mostly a door wipe over a crypt that is
already almost in its final framing. revisar finds no FAIL rows on either clip. Seedance loses on the measures that
matter for the splice and for the user's complaint, which is wobble:

- **It lands off the plate.** The last frame is stretched 2.1 % horizontally about the centre. The altar and phone stay
  in place (+0.7 px), but the frame edges move up to ±13 px at 720 (about ±20 px at 1080). It is also 2.6 levels
  darker, and its content still differs by 4.67 after registration. Its end difference is 5.33 against the baseline's
  2.49, so the cut into the crypt loop would show a step at the edges and in brightness.
- **The objects boil more**, even when the camera has slowed to the baseline's speed: candles 0.300 vs 0.139, door
  0.577 vs 0.396.
- **It invents a foreground arch** (novel colours 4.6 % vs 1.5 %).
- **It is 720p and carries the "AI generated" watermark.**

The altar body ties at rest (0.446 vs 0.448). Every full-frame and whole-range number is confounded by speed:
Seedance moves 3× faster overall and 4–7× faster on the objects.

## Inputs and setup
- Seedance: `A2_s15pro_720.mp4`, 1280×720, 24 fps, 123 f (5.1 s), h264 yuv420p, BytePlus playground, prompt = `partido/prompts/A2.txt` adapted to 5 s.
- Baseline: `fasth3/partido/clips/partido_A_s2s3_rife_telk0f.mkv` (approved by the user 17:22). The A2 span is RIFE
  f108–212, 105 f (4.4 s). f108 is byte-identical to native A2 f3 (diff 0.00), because the join kept A2 f3–55. So the
  baseline starts three native frames after keyA, while Seedance starts on keyA itself.
- Anchors: `fasth3/partido/keys/keyA.png` (first), `fasth3/in/end_nuevo.png` (last).
- **Same scale:** everything runs at Seedance's native 1280×720. The baseline was downscaled with area resampling, so
  neither clip is upscaled (`prep.py`).
- **Watermark:** the box covers pixels with luma > 150 in > 95 % of Seedance frames, plus 10 px: x1022–1241,
  y631–685 at 720 (`med/caja.txt`). For revisar, the box is filled with one constant colour in **both** clips and
  both anchors (`med/*_m.*`), so it reads the same in all of them. warp, hervor and the end match exclude it from
  their masks. None of the objects overlap it.
- Tools: `scripts/revisar.sh` (visual-lab); `scripts/experiments/warp.py`, imported with its valid mask ANDed with
  "outside the box", as `tel/warp_tel.py` does; the `fasth3/hervor.py` formula plus the box exclusion;
  `partido/tel/warp_tel.py` unchanged for the phone; ffmpeg scene score. Object tracking and boil follow
  `telefono_pega.py`'s plate-coordinates boil: `medir.py`. Raw output is in `med/medir.txt`; per frame in
  `med/cuadros.tsv` and `med/objetos.tsv`.

## Numbers
Pass/fail uses revisar's thresholds where one exists. "≤ baseline" means the approved take is the bar. Rows marked
*n.v.* are **not verified against the user's eye**: the full-frame warp_hf median already disagreed with the user on
the walls (partido.md).

| # | criterion | Seedance | baseline (telk0f A2) | threshold | Seedance | baseline |
|---|---|---|---|---|---|---|
| 1 | revisar FAIL rows | 0 | 0 | 0 | pass | pass |
| 2 | start, revisar (f0 vs keyA) | 1.8 | 1.4 | ≤ 4 | pass | pass |
| 3 | end, revisar (best cut) | 3.1 at f118, last f122 = 3.8 | 1.6 at f104 = last | ≤ 4 | pass (narrow) | pass |
| 4 | first vs keyA, mean 8-bit / % px > 8 | 2.52 / 7.3 % | 1.66 / 0.6 % (A2 f3) | ≤ baseline | **fail** | — |
| 5 | last vs end_nuevo, mean 8-bit / % px > 8 (box masked) | 5.33 / 19.0 % (unmasked 5.71) | 2.49 / 4.8 % | ≤ baseline | **fail** | — |
| 6 | last frame registered on the plate (ECC affine vs end_nuevo) | x-scale 1.021 about the centre (displacement +0.4 px at the centre, +0.7 at the phone, −13 / +14 px at the left / right edges), cc 0.978; diff after registration still 4.67 | scale 1.000, shift −0.2 px, cc 0.998 | scale ±0.5 %, centre displacement < 2 px (my threshold, not the eye's) | **fail** | pass |
| 7 | landing luma (last / end_nuevo 16.9) | 14.3 | 15.9 | ≤ baseline gap | **fail** | — |
| 8 | hard cut: ffmpeg scene score max | 0.024 (f68) | 0.009 (f55) | < 0.3 | pass | pass |
| 9 | dissolve (still-but-changing frames: speed < 0.5 and warp_lf > 2× median) | f117–120, in the settle, not a scene change | f46 | no run across the transition | pass | pass |
| 10 | camera moves through space (warp speed median, px/f at 960) | 1.47 (103/123 frames moving) | 0.47 (48/105) | info | real move | wipe over a near-still crypt |
| 11 | strobe (revisar) | 0 runs | 0 runs | 0 | pass | pass |
| 12 | novel colours, revisar | 4.6 % at f71 (f31–84: the foreground arch) | 1.5 % at f46 | info | invents more | — |
| 13 | sharpness at the ends, revisar (× anchor at 1280) | 0.77 / 0.91 | 1.07 / 1.07 | 0.5–2 | pass | pass |
| 14 | full-frame warp_hf, moving frames, med / p90 *n.v.* | 0.496 / 0.592 | 0.413 / 0.573 (native frames only 0.355 / 0.593) | ≤ baseline | worse | — |
| 15 | full-frame hervor, mean / p90 *n.v.* | 0.367 / 0.490 | 0.253 / 0.372 (native frames only 0.321 / 0.490) | ≤ baseline | worse | — |
| 16 | door, nboil at rest (speed < 2 px/f) *n.v.* | 0.577 (n 7, f1–7) | 0.396 (n 10, f1–10) | ≤ baseline | **fail** | — |
| 17 | altar body, nboil at rest *n.v.* | 0.446 (n 12, f108–122) | 0.448 (n 61) | ≤ baseline | tie | — |
| 18 | candles (red bodies), nboil at rest *n.v.* | 0.300 (n 20) | 0.139 (n 53) | ≤ baseline | **fail** | — |
| 19 | flames, nboil at rest *n.v.* | 0.213 | 0.193 | ≤ baseline | ≈ (flames flicker legitimately) | — |
| 20 | phone, nboil at rest / warp_tel warp_hf med/p90 *n.v.* | 0.172 / 0.276 / 0.332 | 0.162 / 0.270 / 0.294 | ≤ baseline | ≈ slightly worse | (pasted plate phone) |
| 21 | object fidelity at rest, NCC with the anchor's object (altar / candles / phone) | 0.981 / 0.885 / 0.943 | 0.984 / 0.972 / 0.961 | ≤ baseline | worse on candles | — |
| 22 | deliverable as is | 720p (1.5× upscale to 1080), watermark | 1920×1080 ffv1 | 1080, clean | **fail** | pass |

### Objects across the whole tracked range (speed not matched; for reference)
| object | clip | tracked | object speed med (px/f at 720) | boil med / p90 | nboil med / p90 | fid med / min | end diff (object, last vs anchor) |
|---|---|---|---|---|---|---|---|
| door | Seedance | f0–18 | 3.02 | 1.10 / 1.66 | 0.574 / 0.784 | 0.750 / 0.639 | 3.50 (f0 vs keyA) |
| door | baseline | f0–18 | 1.41 | 0.60 / 0.79 | 0.497 / 0.771 | 0.864 / 0.737 | 2.02 |
| altar | Seedance | f34–122 | 3.98 | 0.76 / 0.90 | 0.548 / 1.135 | 0.879 / 0.764 | 5.71 |
| altar | baseline | f19–104 | 0.76 | 0.55 / 0.61 | 0.460 / 1.120 | 0.981 / 0.636 | 2.24 |
| candles | Seedance | f37–122 | 6.86 | 2.36 / 5.12 | 0.314 / 1.069 | 0.536 / −0.21 | 14.99 |
| candles | baseline | f33–104 | 1.16 | 0.86 / 3.35 | 0.144 / 0.662 | — | 4.74 |
| flames | Seedance | f41–122 | 4.02 | 3.61 / 6.96 | 0.209 / 0.577 | 0.473 / 0.09 | 19.29 |
| flames | baseline | f32–104 | 0.86 | 3.92 / 6.62 | 0.208 / 0.458 | 0.718 / −0.01 | 12.09 |
| phone | Seedance | f39–122 | 5.77 | 4.16 / 11.49 | 0.222 / 0.918 | 0.397 / 0.09 | 17.08 |
| phone | baseline | f26–104 | 0.90 | 2.63 / 3.72 | 0.164 / 0.673 | 0.952 / 0.16 | 4.47 |

The object masks come from the anchors: the door is keyA x167–900, y33–667; the altar is end_nuevo x461–851,
y413–667, minus the phone, candles and flames; candles are red pixels on the altar top; flames are luma > 200 there;
the phone is `in/mascara_tel_cripta.png`. Sheet: `med/objetos_mascaras.jpg`. Tracking uses ECC affine on a
gamma-lifted gray image, cc ≥ 0.8. The door runs forward from f0, and the crypt objects run backward from the last
frame. In both clips the door track holds f0–18, until the door leaves or darkens.

## How to read it
- **No cut, no dissolve, on either clip** (rows 8–10). Seedance's biggest frame-to-frame step is a scene score of
  0.024, more than ten times below ffmpeg's cut range. Its frames keep moving (speed median 1.47), so it is not a
  dissolve. This is the one thing Seedance does that the local take does not: it shows the space between the door and
  the altar. It does so by **inventing geometry**: a near stone arch the camera passes through (f41–84, revisar's
  novel 4.6 %), which is not part of the crypt plate.
- **The landing is the main loss** (rows 5–7). revisar's `end` passes because it takes the best of the last frames,
  and 3.1 sits close to the 4.0 threshold. The registration shows why the number is high. The last frame is stretched
  2.1 % in x about the centre, so the edges move ±13 px while the phone stays in place (warp_tel's phone centre at f122:
  x 985.7 at 1920, against 983.6 for the baseline). Once the stretch is removed, the frame still differs by 4.67: the
  content itself differs, mostly in the centre third (6.71), and it is 2.6 levels darker. In `fin_altar_1a1.png` the
  right candle stands about 5 px further right, which fits the stretch. A splice into the crypt loop would need a warp
  plus a crossfade. The baseline does not need either (scale 1.000, shift 0.2 px).
- **Wobble.** Over the full frame Seedance scores higher on both warp and hervor (rows 14–15). This comes with two
  caveats that work in opposite directions. First, Seedance moves about 3× faster, and these residuals grow with
  speed. Second, Seedance is h264 at 720 while the baseline is ffv1 downscaled from 1080. Compression smooths fine
  detail, so it likely flatters Seedance (not measured). When the motion is matched
  (objects below 2 px/f, rows 16–20), Seedance is still worse on the door and the candles, ties on the altar body and
  is roughly level on the flames and the phone. The baseline's phone is the plate's phone pasted in (`_telk0f`), so
  row 20 compares a model-drawn phone with a pasted still. The object "at rest" samples for Seedance are short
  (n 7–20, its settle f92–122), while the baseline's are long (n 53–65).
- The baseline's RIFE in-betweens halve its motion per frame. Its native-frames-only rows (14–15) are closer to
  Seedance on p90 and still lower on the median.

## For the user's eye
- A/B at the same scale (1280×720 each, 2560×720, 123 f): `/mnt/e/Cursor Projects/MTO/tmp/07/seedance/ab_seedance_vs_baseline.mp4`.
  Seedance is on the left and the baseline on the right. The baseline's last frame is held for 18 frames, so Seedance's
  landing is not cut off: from f105 on, the right side is a frozen frame.
- Side-by-side contact strip: `/mnt/e/Cursor Projects/MTO/tmp/07/seedance/tira_seedance_vs_baseline.jpg`. Each column
  shows the same fraction of each clip, with keyA and end_nuevo at the edges. It is gamma 1/1.8 for visibility, so it
  is an overview, not evidence.
- Landing at 1:1 (altar region): `/mnt/e/Cursor Projects/MTO/tmp/07/seedance/fin_altar_1a1.png`, with Seedance's
  last frame, the baseline's last frame and end_nuevo.
- Frame-by-frame viewer with revisar's strip:
  `~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med/seedance_A2.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med/baseline_telk0f_A2.mkv"`

## Not done
- No eagle-eye pass, because revisar found no FAIL rows and this is a measurement, not a handoff.
- The object-boil and full-frame numbers are not calibrated against the user's eye.
- No splice test into the crypt loop.
- No paid API was called, and no generation was run.

## Files
`prep.py` (720 copies, watermark box), `medir.py` (warp, hervor, cut, objects, ends), `med/medir.txt` (raw output),
`med/cuadros.tsv` (per frame), `med/objetos.tsv` (per object per frame), `med/tel_{sd720,bl720}.tsv` (warp_tel),
`med/revisar/{sd_m,bl_m}/` (revisar tables and evidence).

---

# Round 2: rerun with a "no arch" prompt (2026-10-16)

**Verdict: the invented arch is gone and the object boil is lower, but the landing is unchanged, so the splice problem is not fixed.**
`A2_s15pro_noarch_1.mp4` (Seedance 1.5 pro, same anchors keyA → end_nuevo, audio off, 1280×720, 24 fps, 123 f, same h264 and
the same watermark) was measured with round 1's scripts and the same watermark box (`med/caja.txt`; the rerun's own
watermark sits inside it, x1032–1230, y641–674). Three columns: take 1 (`A2_s15pro_720.mp4`), the rerun, the approved
baseline (`telk0f` A2 span). Take 1 and baseline numbers were recomputed in the same run and match round 1 exactly.

| # | criterion | take 1 | rerun | baseline | threshold | rerun result |
|---|---|---|---|---|---|---|
| 1 | revisar FAIL rows | 0 | 0 | 0 | 0 | pass |
| 2 | start, revisar (f0 vs keyA) | 1.8 | 2.0 | 1.4 | ≤ 4 | pass |
| 3 | end, revisar (best cut) | 3.1 (f118) | 3.0 (f118) | 1.6 | ≤ 4 | pass (narrow, same as take 1) |
| 4 | first vs keyA, mean 8-bit / % px > 8 | 2.52 / 7.3 % | 2.60 / 8.2 % | 1.66 / 0.6 % | ≤ baseline | fail (as take 1) |
| 5 | last vs end_nuevo, mean / % px > 8 (box masked) | 5.33 / 19.0 % | **5.33 / 18.7 %** | 2.49 / 4.8 % | ≤ baseline | **fail, not improved** |
| 5b | same, by column third L / C / R | 3.22 / 6.71 / 6.07 | 3.25 / 6.65 / 6.10 | 1.81 / 3.16 / 2.52 | | no change |
| 6 | last-frame x-scale (ECC affine vs end_nuevo, `landing.py`) | 1.0209 | **1.0207** | 1.0002 | ±0.5 % | **fail, no change** |
| 6b | displacement at left edge / centre / phone / right edge, px at 720 | −13.0 / +0.4 / +0.7 / +13.7 | −12.8 / +0.4 / +0.8 / +13.6 | −0.2 / −0.1 / −0.1 / 0.0 | centre < 2 | same stretch |
| 6c | diff after registration (`landing.py`) | 4.22 | 4.31 | 2.48 | | same |
| 7 | landing luma, gap to end_nuevo 17.09 (`landing.py`) | 14.02 (−3.08) | **13.83 (−3.26)** | 16.07 (−1.02) | ≤ baseline gap | **fail, slightly worse** |
| 8 | hard cut: scene score max | 0.024 | 0.010 (f83) | 0.009 | < 0.3 | pass |
| 9 | dissolve (still-but-changing run) | f117–120 | f117–120 | f46 | none across the transition | pass (settle only) |
| 10 | camera moves: warp speed median px/f at 960 / frames > 0.5 | 1.47 / 103 | **1.15 / 91** | 0.47 / 48 | info | real move, a bit gentler |
| 11 | strobe (revisar) | 0 runs | 0 runs | 0 runs | 0 | pass |
| 12 | **novel colours, revisar** | **4.6 %** at f71 (f31–84) | **0.9 %** at f55 (f50–67, f108–109) | 1.5 % | info, flagged ≥ 0.5 % | **arch gone** |
| 13 | sharpness at the ends (× anchor) | 0.77 / 0.91 | 0.75 / 0.87 | 1.07 / 1.07 | 0.5–2 | pass |
| 14 | full-frame warp_hf, moving frames, med / p90 *n.v.* | 0.496 / 0.592 | 0.485 / 0.560 | 0.413 / 0.573 | ≤ baseline | slightly better, still worse than baseline |
| 15 | full-frame hervor, mean / p90 *n.v.* | 0.367 / 0.490 | 0.324 / 0.458 | 0.253 / 0.372 | ≤ baseline | better than take 1, still worse than baseline |
| 16 | door, nboil at rest (speed < 2 px/f) *n.v.* | 0.577 (n 7) | 0.535 (n 3) | 0.396 (n 10) | ≤ baseline | not comparable (n 3) |
| 17 | altar body, nboil at rest *n.v.* | 0.446 (n 12) | 0.486 (n 54, f66–122) | 0.448 (n 61) | ≤ baseline | ≈ (slightly worse) |
| 18 | candles, nboil at rest *n.v.* | 0.300 (n 20) | 0.209 (n 28) | 0.139 (n 53) | ≤ baseline | better than take 1, still worse than baseline |
| 19 | flames, nboil at rest *n.v.* | 0.213 | 0.116 | 0.193 | ≤ baseline | ok |
| 20 | phone, nboil at rest / warp_tel warp_hf med / p90 *n.v.* | 0.172 / 0.276 / 0.332 | 0.095 / 0.119 / 0.173 | 0.162 / 0.270 / 0.294 | ≤ baseline | ok (the phone barely moves, 0.11 px/f) |
| 21 | NCC with the anchor's object at rest (altar / candles / phone) | 0.981 / 0.885 / 0.943 | 0.922 / 0.875 / 0.935 | 0.984 / 0.972 / 0.961 | ≤ baseline | worse on altar and candles |
| 22 | deliverable as is | 720p, watermark | 720p, watermark | 1080 clean | 1080, clean | fail |

Brightness over the clip (mean luma at 0 / 25 / 50 / 75 / 100 % of the frames, watermark box masked): take 1 3.1 / 8.7 / 20.2 / 21.0 / 13.9;
rerun 2.9 / 9.0 / **25.6** / 21.8 / 13.7; baseline 3.4 / 3.1 / 17.1 / 16.4 / 15.9. The rerun does brighten out of the door's
darkness, as asked, but it overshoots the plate (25.6 against 17.1) and then settles about 3 levels below it.
Camera speed by tenth of the clip (px/f at 960): take 1 0.7 1.5 3.8 5.9 6.7 6.3 1.5 1.0 0.6 0.3; rerun 1.1 1.6 2.6 5.4 7.7 3.1 0.8 0.5 0.4 0.3; baseline 0.6 1.8 3.0 1.1 0.5 0.4 0.4 0.4 0.4 0.4.

### Objects across the whole tracked range, rerun (speed not matched; for reference)
| object | tracked | object speed med (px/f at 720) | boil med / p90 | nboil med / p90 | fid med / min | end diff (object, last vs anchor) |
|---|---|---|---|---|---|---|
| door | f0–25 | 3.33 | 0.97 / 2.28 | 0.573 / 1.125 | 0.800 / 0.636 | 3.65 |
| altar | f43–122 | 1.73 | 0.85 / 1.36 | 0.529 / 1.265 | 0.899 / 0.774 | 5.72 |
| candles | f59–122 | 2.16 | 1.40 / 1.88 | 0.222 / 0.299 | 0.868 / −0.146 | 14.45 |
| flames | f53–122 | 1.64 | 2.70 / 4.89 | 0.125 / 0.818 | 0.873 / −0.083 | 19.63 |
| phone | f52–122 | 1.28 | 2.26 / 4.51 | 0.111 / 0.282 | 0.892 / 0.098 | 15.55 |

Take 1 and baseline rows of this table are unchanged from round 1 (above).

## How to read round 2
- **The arch is gone.** Novel colours fall from 4.6 % to 0.9 %, and a gamma-lifted sheet of f30–110 (`med2/arco_hoja.jpg`, an
  overview, not evidence) shows take 1's heavy foreground arch at f45–90 replaced by the door leaf swinging open at the left,
  with the crypt's own niches behind it. The remaining 0.9 % at f50–67 is wide (x0.00–0.89), which fits the door leaf and the
  brightness overshoot rather than new geometry; not inspected further.
- **The landing did not move.** The last frame is stretched 2.07 % in x, the same as take 1 (2.09 %), the end diff is 5.33 in
  both, and it is 0.18 level darker than take 1 (3.26 below the plate; the baseline is 1.02 below). The prompt's "end must match
  the last image in framing and brightness" had no measurable effect: the model seems to finish on a fixed composition regardless
  of this wording, so the edge shift of ±13 px would still show in a splice into the crypt loop.
- **Boil at rest is lower**, and the rest window is much longer (rerun settles by f66, take 1 only by f88–108), so the samples are
  more meaningful: candles 0.209 vs 0.300, flames 0.116 vs 0.213, phone 0.095 vs 0.172. Against the baseline, candles are still worse (0.209
  vs 0.139) and the altar body is level to slightly worse (0.486 vs 0.448). A lower boil can also come from a smoother or darker
  image; sharpness at the ends is 0.75 / 0.87, which does not suggest blur. Door: only 3 frames at rest, so no verdict.
- **Cut vs move: a move, no cut.** Scene score max 0.010, no frames above 0.1, the same short settle run f117–120 as take 1. The
  camera moves more gently than take 1 (median 1.15 vs 1.47 px/f, peak tenth 7.7 vs 6.7) and then rests for the last 40 %.

## Not done (round 2)
- No eagle-eye pass (revisar has no FAIL rows; this is a measurement, not a handoff). Boil and hervor numbers are still not
  calibrated against the user's eye. No splice test. No paid API call and no generation.
- `landing.py` is new in round 2 (round 1's registration was ad hoc). On take 1 it reproduces round 1's scale, shifts and mean
  diff (1.021; −13 / +14 px; 5.33 / 2.49), but differs on two derived numbers: diff after registration 4.22 (round 1: 4.67) and luma
  gap −3.08 (round 1: −2.6), a different registration crop and luma definition. Compare only within one script's columns.
- Pitfall met: launching `medir2.py` with `&` inside a `run_in_background` call left a second process writing the same
  `med2/medir.txt`; the first numbers read were garbled (baseline 99 frames). The table above comes from a clean single rerun,
  and its take 1 and baseline columns equal round 1 line for line.

## Files (round 2)
- A/B, 3 columns (take 1 | rerun | baseline, 960×540 each, 2880×540, 123 f, baseline's last frame held 18 f):
  `/mnt/e/Cursor Projects/MTO/tmp/07/seedance/ab3_take1_rerun_baseline.mp4`
- `prep2.py` (rerun decode + masked copy → `med2/rr720.mkv`, `med2/rr_m.mkv`), `medir2.py` (round 1's medir.py with the rerun as a third clip →
  `med2/medir.txt`, `med2/objetos.tsv`, `med2/cuadros.tsv`), `landing.py` (→ `med2/landing.txt`), `resto.py` (at-rest table from objetos.tsv),
  `med2/tel_rr720.tsv` (warp_tel on the rerun), `med2/revisar/rr_m/` + `med2/revisar_rr_m.log` (revisar:
  `REVISAR_OUT=med2/revisar/rr_m scripts/revisar.sh med2/rr_m.mkv --inicio med/keyA_m.png --fin med/end_m.png`), `med2/arco_hoja.jpg`.
- Frame-by-frame viewer: `~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med2/rr_m.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med/baseline_telk0f_A2.mkv"`

---

# Round 3: Veo 3.1 Fast (Google Flow), same anchors and move (2026-10-16)

**Verdict: Veo is the best AI take so far and the first one that can land on the plate, but only if it is trimmed at f184 of 192.**
It makes a real camera move with no cut, no dissolve and no invented arch: the door leaf slides out of frame, the crypt's own
lighting ramps up out of near-black, and a continuous push-in reaches end_nuevo at f184 (x/y scale 0.9999, centre shift 0.0 px, mean
diff 1.94 against the baseline's 2.49). It does not stop there: it keeps pushing and its last frame is 1.3 % too large, which
gives the headline "last vs end" 3.44 (still better than both Seedance takes, 5.33, and worse than the baseline's 2.49). Luma lands
on the plate (+0.01; the baseline is 1.02 below and Seedance about 3 below). Object boil at rest is level with or below the
baseline on the altar, phone and flames and 11 % above it on the candles (0.155 vs 0.139). The costs: it is 8 s instead of 5 s, about 4 s of it near-dark
(mean luma stays under 10 until about f96), and its h264 is 1.6 Mbps against Seedance's 6.6, so the boil numbers may be flattered by
smoothing (altar sharpness 0.87 of the anchor against 1.15 / 1.27 for Seedance; not isolated).

## Inputs and setup
- Veo: `../veo_a2/A2_veo31fast.mp4`, 1280×720, 24 fps, 192 f (8.0 s), h264 yuv420p, 1.56 Mbps, with an AAC track (not used). Prompt:
  `../veo_a2/prompt.txt` (the Seedance no-arch move, 8 s: 1 s of near-black door, then a slow forward move to rest on the end frame).
  Anchors `veo_a2/A2_start_door.png` and `A2_end_altar.png` are byte-identical to `keyA.png` and `end_nuevo.png`.
- **Watermark: none.** No pixel has luma > 150 (or > 60) in > 95 % of the frames, the last frame's diff against end_nuevo shows no
  localized excess in any corner (bottom-right block 2.0, the frame's blocks otherwise range 0.4–17.8 where the content differs), and
  the bottom-right corner crops show only compression texture. Nothing needed masking. So that all four columns are judged on the same
  pixels, the **same box as round 1** (`med/caja.txt`, x1022–1241 y631–685) is still filled with the same constant in the Veo masked
  copy and excluded from warp, hervor and the end match. Veo's frame content under it is not lost information anywhere that matters
  (no object overlaps it).
- Scripts are round 2's with one more clip, nothing else changed: `prep3.py` (decode + masked copy → `med3/vo720.mkv`, `med3/vo_m.mkv`),
  `medir3.py` (= `medir2.py` + "veo" → `med3/medir.txt`, `objetos.tsv`, `cuadros.tsv`), `landing3.py`, `resto3.py`. The take 1, no-arch
  and baseline columns were recomputed in the same run and equal rounds 1–2 line for line, apart from the revisar rows, which are
  copied from them. Run singly in the foreground of a background job (round 2's double-process pitfall avoided).
- **Matched speed (as in round 1):** Veo moves much more slowly overall (speed median 0.38 px/f against 1.47 / 1.15 / 0.47), so the
  boil rows use only frames where the object itself moves < 2 px/f (`resto3.py`), with n and the frame range stated. Caveat: Veo's
  late move is a radial push-in, and the speed metric (median flow magnitude) under-reads it, which is why 115 of 192 frames count as
  "not moving" while the scale still grows 9 % between f140 and f191.

## Numbers (four columns)
Thresholds are those of rounds 1–2. *n.v.* = not verified against the user's eye.

| # | criterion | Veo | take 1 | no-arch | baseline | threshold | Veo result |
|---|---|---|---|---|---|---|---|
| 1 | revisar FAIL rows | 0 | 0 | 0 | 0 | 0 | pass |
| 2 | start, revisar (f0 vs keyA) | 0.8 | 1.8 | 2.0 | 1.4 | ≤ 4 | pass, best |
| 3 | end, revisar (best cut) | 0.8 at **f184** (last f191: drift 0.9 over the 7 frames after the cut) | 3.1 | 3.0 | 1.6 | ≤ 4 | pass, best if cut at f184 |
| 4 | first vs keyA, mean 8-bit / % px > 8 | 1.25 / 0.2 % | 2.52 / 7.3 % | 2.60 / 8.2 % | 1.66 / 0.6 % | ≤ baseline | pass |
| 5 | last vs end_nuevo, mean / % px > 8 (box masked) | **3.44 / 11.4 %** | 5.33 / 19.0 % | 5.33 / 18.7 % | 2.49 / 4.8 % | ≤ baseline | **fail, but 35 % better than Seedance** |
| 5a | same, best of the last 10 frames | **1.94 at f184** | 4.88 (f118) | 4.71 (f118) | 2.49 (f104) | ≤ baseline | **pass at f184** |
| 5b | last frame by column third L / C / R | 1.31 / 4.74 / 4.30 | 3.22 / 6.71 / 6.07 | 3.25 / 6.65 / 6.10 | 1.81 / 3.16 / 2.52 | | centre and right off |
| 6 | last-frame ECC affine vs end_nuevo (`landing3.py`): x-scale / y-scale | **1.0129 / 1.0123** (uniform) | 1.0209 / 0.9997 (x only) | 1.0207 / 0.9996 | 1.0002 / 0.9997 | ±0.5 % | **fail (overshoot)** |
| 6b | displacement at left / centre / phone / right, px at 720 | −8.4 / −0.2 / +0.1 / +8.1 | −13.0 / +0.4 / +0.7 / +13.7 | −12.8 / +0.4 / +0.8 / +13.6 | −0.2 / −0.1 / −0.1 / 0.0 | centre < 2 | edges ±8 |
| 6c | diff after registration | 2.06 | 4.22 | 4.31 | 2.48 | | content matches best of all |
| 6d | **same registration at f184** (`landing_traj.py`; same frame as row 5a's 1.94, a different script's crop gives 1.91) | scale 0.9999 / 0.9999, shift −0.0 / −0.0 px, cc 0.998, diff 1.91 | | | | ±0.5 % | **pass** |
| 7 | landing luma, gap to end_nuevo 17.09 | 17.10 (+0.01) | 14.02 (−3.08) | 13.83 (−3.26) | 16.07 (−1.02) | ≤ baseline gap | **pass, best** |
| 8 | hard cut: scene score max | 0.007 (f1); no frame > 0.1 | 0.024 | 0.010 | 0.009 | < 0.3 | pass |
| 9 | dissolve rule (speed < 0.5 and warp_lf > 2× median) | 20 flagged frames, f87–113 | f117–120 | f117–120 | f46 | none across the transition | **rule trips, inspected: not a dissolve** (see below) |
| 10 | camera speed median px/f at 960 / frames > 0.5 | 0.38 / 76 | 1.47 / 103 | 1.15 / 91 | 0.47 / 48 | info | slow radial push; under-read |
| 11 | strobe (revisar) | 0 runs | 0 | 0 | 0 | 0 | pass |
| 12 | novel colours, revisar | 2.2 % at f93 (f79–105, box x0.43–0.60) | 4.6 % (f31–84) | 0.9 % | 1.5 % | info, flagged ≥ 0.5 % | flagged, not new objects (see below) |
| 13 | sharpness at the ends (× anchor) | 1.03 / 1.40 | 0.77 / 0.91 | 0.75 / 0.87 | 1.07 / 1.07 | 0.5–2 | pass (1.40 at the end is the highest; compression texture can inflate a Laplacian) |
| 14 | full-frame warp_hf, moving frames, med / p90 *n.v.* | 0.516 / 0.608 | 0.496 / 0.592 | 0.485 / 0.560 | 0.413 / 0.573 | ≤ baseline | worst of the four (76 moving frames, mostly the dark door-opening phase) |
| 15 | full-frame hervor, mean / p90 *n.v.* | 0.283 / 0.417 | 0.367 / 0.490 | 0.324 / 0.458 | 0.253 / 0.372 | ≤ baseline | between no-arch and baseline |
| 16 | door, nboil at rest (object speed < 2 px/f) *n.v.* | no frame at rest (object speed med 3.89) | 0.577 (n 7) | 0.535 (n 3) | 0.396 (n 10) | ≤ baseline | not comparable; whole range f0–28: 0.418 vs 0.574 / 0.573 / 0.497 at unmatched speeds |
| 17 | altar body, nboil at rest *n.v.* | **0.393 (n 98, f76–191)** | 0.446 (n 12) | 0.486 (n 54) | 0.448 (n 61) | ≤ baseline | **pass** |
| 18 | candles, nboil at rest *n.v.* | 0.155 (n 36, f95–189) | 0.300 (n 20) | 0.209 (n 28) | 0.139 (n 53) | ≤ baseline | slightly worse (+11 %), the closest AI take |
| 19 | flames, nboil at rest *n.v.* | 0.085 (n 51, f131–191) | 0.213 | 0.116 | 0.193 | ≤ baseline | lower than all (flames flicker legitimately; low could also mean calm) |
| 20 | phone, nboil at rest *n.v.* (warp_tel not run for Veo) | 0.056 (n 73, f115–191) | 0.172 | 0.095 | 0.162 | ≤ baseline | pass |
| 21 | NCC with the anchor's object at rest (altar / candles / phone) | **0.981 / 0.974 / 0.961** | 0.981 / 0.885 / 0.943 | 0.922 / 0.875 / 0.935 | 0.984 / 0.972 / 0.961 | ≤ baseline | ties the baseline |
| 22 | deliverable as is | 720p, no watermark, 1.6 Mbps h264; Flow's 1080 upscale exists | 720p, watermark | 720p, watermark | 1080 clean | 1080, clean | native 720 fails the size; the upscale is the row below |

Extra row (teammate's request): **Flow upscale** (`../veo_a2/A2_veo31fast_1080up.mp4`, 1920×1080, 192 f, 3.5 Mbps), last frame
against `end_nuevo.png` at full 1920×1080 (`landing_up.py`), with the 720 native measured by the same script:

| clip | last vs end, mean / % px > 8 | best of the last 12 | luma gap | ECC x / y scale | diff after registration | sharpness × end |
|---|---|---|---|---|---|---|
| Veo 720 native (vs 720 end) | 3.42 / 11.3 % | 1.93 at f184 | +0.01 | 1.0129 / 1.0124 | 2.05 | 1.18 |
| Flow upscale 1080 (vs 1080 end) | 4.36 / 15.0 % | 3.05 at f184 | −0.23 | 1.0123 / 1.0118 | 3.19 | 2.04 |

The upscale keeps the same geometry (same overshoot, same f184 minimum). Its diffs are higher only because they are taken at 1080,
where the anchor's fine detail is compared against a 2× upscale with 2.04× the anchor's Laplacian variance (visibly over-sharpened or
noisy), so do not compare the 1080 diffs with the 720 columns. A baseline at 1080 was not measured in this form.

### Objects across the whole tracked range, Veo (speed not matched; for reference)
| object | tracked | object speed med (px/f at 720) | boil med / p90 | nboil med / p90 | fid med / min | end diff (object, last vs anchor) |
|---|---|---|---|---|---|---|
| door | f0–28 | 3.89 | 0.61 / 0.93 | 0.418 / 0.653 | 0.879 / 0.649 | 1.45 (f0 vs keyA) |
| altar | f58–191 | 1.37 | 0.45 / 0.56 | 0.416 / 1.335 | 0.976 / 0.710 | 2.60 |
| candles | f65–191 | 3.24 | 0.95 / 1.74 | 0.176 / 0.781 | 0.960 / −0.132 | 10.04 |
| flames | f87–191 | 2.02 | 2.31 / 5.35 | 0.097 / 0.361 | 0.883 / 0.187 | 26.23 |
| phone | f90–191 | 1.49 | 1.10 / 1.99 | 0.061 / 0.089 | 0.954 / 0.351 | 13.42 |

The candle / flame / phone end diffs (10–26) are large for Veo, as for everyone else, because the last frame is the overshoot, not the
plate; they come from the 1.3 % scale (a 5–10 px shift at the candles) and from the candle flames, which the plate has lit and Veo
lights late (f120 and after).

Brightness (mean luma at 0 / 25 / 50 / 75 / 100 % of the frames, box masked): Veo 5.4 / 6.0 / 9.5 / 17.3 / 17.1 (max 17.5 at f129);
take 1 3.1 / 8.7 / 20.2 / 21.0 / 13.9; no-arch 2.9 / 9.0 / 25.6 / 21.8 / 13.7; baseline 3.4 / 3.1 / 17.1 / 16.4 / 15.9; the plate is 17.09.
Veo is the only take that does not overshoot the plate's brightness and then fall below it; it rises to the plate and stays.
Camera speed by tenth of the clip (px/f at 960): Veo 0.6 1.3 1.9 1.9 0.8 0.4 0.3 0.3 0.3 0.3.

## How to read round 3
- **Cut vs move: a move, and the transition is a reveal.** Scene score max 0.007. The rule in row 9 trips on 20 frames in f87–113
  because Veo's warp_lf median is small, and the crypt brightens quickly from luma 3 (f72) to 15 (f108), which raises the
  low-band residual with little motion. I looked at f54–87 every three frames (gamma-lifted sheet, an overview and not evidence): the
  door leaf keeps a sharp edge and slides out of the frame to the right as a rigid object while the altar's top line stays at the same
  y from f60 to f87 and the beam stays put, so it is not a crossfade between two images. The moonbeam and the dim crypt appear
  from f63 (a small patch first, no soft overlay of the door) and the camera starts to push in around f78 (a speed spike of 5.0 px/f at f80). This is a judgement from frames, not a number; the rule's
  threshold is relative to the clip's own median and does not suit a clip that is slow and brightening.
- **No invented geometry.** revisar's novel 2.2 % at f79–105 is where the beam and the crypt's lit surfaces first appear against a
  plate that is brighter. A look at f93 and f105 beside end_nuevo shows the plate's own arch, niche, altar, beam and dust, with the
  candles unlit; nothing like take 1's foreground arch. The only difference in content is that the candle flames are off until about
  f120–130 and the plate's are on. (Judgement from a gamma-lifted sheet.)
- **Landing: it passes through the plate but does not come to rest on it.** The push-in is almost linear in scale
  (0.9224 at f140, 0.9573 at f160, 0.9926 at f180, 0.9999 at f184, 1.0129 at f191, about 0.18 %/f at the end), with the centre fixed
  (shift under 0.3 px from f170). So the plate is a cut point, not a settle: trim at f184 (7.67 s) and the cut into the crypt loop
  has scale 0.9999 and mean diff 1.94 against the baseline's 2.49, with luma on target. Left untrimmed, the last frame has a ±8 px edge
  shift and a 3.44 diff. The prompt asked to "come to rest exactly on the end frame"; the model did hit the frame, not the rest.
  The camera is still pushing at 0.2 %/f when the clip ends, so any splice at f184 needs a short hold or a deceleration (not tested).
- **Boil at rest** (rows 16–21): with long windows (n 36–98, against 12–20 for take 1), Veo is better than the baseline on the
  altar (0.393 vs 0.448), better on the phone and flames, 11 % worse on the candles (0.155 vs 0.139), and ties it on fidelity to the anchor (0.981 / 0.974 / 0.961
  vs 0.984 / 0.972 / 0.961). Compared with the Seedance takes it is lower on every object. Two caveats: (1) the full-frame warp_hf
  median is the worst of the four (0.516) even though Veo is the slowest clip, so speed does not explain it; I suspect the dark
  door-opening phase and the brightening ramp, which make up most of its 76 moving frames, but I did not split them (not verified); (2) Veo's bitrate is a quarter of Seedance's, so
  encoder smoothing could lower these numbers (the end-frame sharpness reads 1.40 × anchor, which argues against blur, but compression
  noise inflates a Laplacian). The door has no at-rest frames, so it has no verdict.
- **Time.** The part with the crypt visible (mean luma above 10) runs from about f96 to f184, 3.7 s. The first 4 s (door, dark,
  reveal) alone are about as long as the baseline's whole A2 span (4.4 s); trimmed at f184, the clip is 7.7 s against that 4.4 s slot.

## Not done (round 3)
- No eagle-eye pass (revisar has no FAIL rows; this is a measurement, not a handoff). Boil and hervor numbers are still not
  calibrated against the user's eye. warp_tel (row 20's second half) was not run for Veo. No splice test and no f184-trim render. The
  1080 upscale was measured only at its last frames, with no boil or warp rows. No paid API call and no generation; the Flow take was
  generated by the user.

## Files (round 3)
- A/B, 2×2 at 960×540 per tile (Veo | Seedance take 1 / no-arch | baseline; 1920×1080, 192 f; the shorter clips' last frames held; originals with the "AI generated" watermarks visible, no gamma):
  `/mnt/e/Cursor Projects/MTO/tmp/07/seedance/ab4_veo_take1_rerun_baseline.mp4`
- `prep3.py`, `medir3.py`, `landing3.py`, `landing_traj.py` (Veo's approach to the plate), `landing_up.py` (the Flow upscale row), `resto3.py`;
  output in `med3/` (`medir.txt`, `landing.txt`, `objetos.tsv`, `cuadros.tsv`, `objetos_mascaras.jpg`, `revisar/vo_m/` + `revisar_vo_m.log`):
  `REVISAR_OUT=med3/revisar/vo_m scripts/revisar.sh med3/vo_m.mkv --inicio med/keyA_m.png --fin med/end_m.png`.
- Frame-by-frame viewer: `~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med3/vo_m.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/seedance/med/baseline_telk0f_A2.mkv"`

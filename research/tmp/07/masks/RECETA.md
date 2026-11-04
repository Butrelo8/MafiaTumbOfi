# Precise masks: guitar f0–61 results + reusable recipe (2026-10-14)

Spec: `~/projects/mothership/docs/queue/2026-10-14-precise-masks.md`. Nothing under `tmp/07/fasth3/` was touched and the
clip was not re-composited.

## What was tested (local GPU, native ComfyUI nodes, no custom nodes installed)

- **SAM 3.1** (`sam3.1_multiplex_fp16.safetensors`, 1.7 GB, core nodes `SAM3_Detect` / `SAM3_VideoTrack` /
  `SAM3_TrackToMask`). It replaced SAM 2.1 from the brief: it is already in core v0.37.4, so there was no third-party code to
  install, and the spec lists both. Licence: SAM License (royalty-free, commercial use not excluded; military/ITAR end uses
  barred; ship the licence text if the weights are ever redistributed).
- **BiRefNet** (core `RemoveBackground`, `birefnet.safetensors`, already installed; MIT).
- **Refinement**: Gaussian feather sized from a measurement, guided filter (`cv2.ximgproc`), closed-form matting
  (`pymatting`, MIT) on a ±2 px trimap.
- **MatAnyone: skipped.** Licence NTU S-Lab 1.0 = non-commercial only, and the mask the paste uses is a warped still, which has no
  shimmer by construction.

## Reference ("hand-checked frame")

I did not draw a reference by eye: the plate's headstock is too soft for that (its edges go from 10 % to 90 % over 2.25 px).
The reference is the plate's own edge. For every point of a mask's 0.5 contour, `medir_borde.py` finds the sub-pixel maximum of
the luminance gradient along the normal (±3 px). The error is the distance to that maximum. A point with less than 6 levels of
contrast counts as "unsupported" (the contour crosses flat wall or flat wood). The check overlay for the user is
`pix/borde_<candidate>.png` (×12: green = vector to the plate's edge, red = no edge found). Bright-feature coverage counts the 8
bright blobs in the headstock box (pegs, nut, slots) and reports the mask's mean alpha over each.

## Results: plate guitar mask (what `guitarra.py` pastes)

Headstock + pegs box (x1020–1078, y606–650), plate f0. Edge error is mean / p95 in px.

| candidate | edge err | unsupported | bright features covered | alpha 10–90 % width |
|---|---|---|---|---|
| A GrabCut, binary (apedrone's polygon + GrabCut) | 0.60 / 2.16 | 28 % | 8/8 (1.00) | 1.0 (before blur) |
| A as used today (σ 1.2 blur) | 0.61 / 2.05 | 29 % | 8/8 (0.92) | 3.25 |
| **A, measured feather σ 0.88** | **0.59 / 1.98** | 28 % | 8/8 (0.95) | **2.50** (plate 2.25) |
| A, closed-form matting, ±2 px trimap | 0.76 / 1.84 | 23 % | 8/8 (0.97) | 2.75 |
| A, guided filter r2 ε1e-2 | 0.53 / 2.06 | 28 % | 8/8 (0.98) | 4.50 (too soft) |
| B SAM 3.1, 3 points | 0.95 / 2.54 | 23 % | **4 of 8 < 0.5** | 1.5 |
| B2 SAM 3.1, + 6 points on the pegs | 0.71 / 2.47 | 25 % | 8/8 (0.93) | 1.5 |
| C BiRefNet on the 384² crop | 1.04 / 2.62 | 34 % | 8/8 (0.99) | 1.5 |
| C2 BiRefNet, headstock at ×8 | 1.12 / 2.64 | 51 % | 8/8 (1.00) | 1.5 |

Reading:
- The current GrabCut mask is already the most accurate on the headstock. SAM on its own drops the pegs. BiRefNet makes the
  headstock a blob that bridges the pegs and reaches into the wall above. Running BiRefNet on an 8× crop made this worse, not better.
- The one measurable improvement is the **feather**. Today's σ 1.2 gives a 3.25 px edge on a plate whose edges are 2.25 px.
  σ 0.88 (= 2.25 / 2.563, the 10–90 % width of an erf edge) gives 2.50 px and the best p95 of the simple options. Closed-form
  matting has the best p95 (1.84) but leaves a dark notch on the lowest peg (visible at ×8).
- Temporal: every plate-based candidate travels as a warped still, so its edge moves only by resampling (0.13–0.15 px/frame).
- Overhang: the take's own (bent) headstock sticks out of the plate mask by ≤ 14 px in any frame of f0–56
  (`medir_seguimiento.py`), so the paste already hides it. There is no union or fill to do on the guitar.

Side-by-side (each candidate pasted over the take's f40, stabilised; top row 100 %, bottom ×8 nearest):
`ab/clavijero_f40_lado_a_lado.png`. At 100 % the differences are about one pixel.

## Results: SAM 3.1 video tracking on the raw take (method for phone/door/truck)

Raw take `fasth3/clips/f1080_film2_rampa.mkv` f0–61, 384² crop → 1008² Lanczos, back-warped to plate coordinates with
the body affine. Edge movement = Σ|Δα| / contour length, in px/frame, median / p95, f0–56:

| seed of the track | headstock | neck | whole guitar | pegs |
|---|---|---|---|---|
| SAM's own detection (3 points) | 0.38 / 0.46 | 0.13 / 0.18 | 0.24 / 0.34 | pop in and out (`pix/tira_borde_f20-25.png`) |
| **the planned plate mask** (warped to f0) | **0.21 / 0.32** | 0.13 / 0.25 | 0.25 / 0.64 | held in every frame (`pix/tira_borde_semilla_f20-25.png`) |
| warped still (baseline) | 0.13 / 0.23 | 0.09 / 0.14 | 0.15 / 0.20 | n/a |

Clips at 24 fps (stabilised ×6, red = SAM, yellow = plate): `ab/borde_sam3_vs_placa_f0-61_6x.mp4`,
`ab/borde_sam3semilla_vs_placa_f0-61_6x.mp4`. Time: 18–20 s for 62 frames at 1008², warm. The run is deterministic (a rerun through
`gen.sh` gave identical bits).

## Recipe (reuse for the phone transplant, the door occluder, the truck beads)

1. **Crop square around the object's whole path** (the path bbox from the tracking affine plus a margin) and Lanczos-upscale
   it to 1008² before ComfyUI. SAM 3 squashes any input to 1008² and returns a binary mask that was upsampled from 252² logits.
   On a full 1920×1080 frame a 40 px headstock gets ~20 px. On a 384² crop the mask is 2.6× supersampled, and an
   INTER_AREA downsample gives an anti-aliased edge.
2. **Plan the first-frame mask, don't let SAM guess thin parts.** Use a polygon on a labelled ×2–×16 grid, then GrabCut from
   that polygon (the `guitarra.py` method), or SAM `preset_mask_sam3_still` with one positive point per thin part (pegs,
   antenna, edge of the door) plus negatives on the background. Check it with `medir_borde.py` (edge error to the plate's
   gradient, bright-feature coverage).
3. **Video: seed `SAM3_VideoTrack` with that mask** (`preset_mask_sam3_track`: `2.file` = PNG-codec .mov of the
   1008² crop, `4.image` = seed mask PNG warped to f0, `9.filename_prefix`). Never seed it with SAM's own point detection on a
   thin object.
4. **Feather by measurement**: measure the plate's 10–90 % edge width along the contour normals (`medir_borde.py` prints it)
   and blur the hard mask with σ = width / 2.563. Add motion blur on top as `guitarra.py` does.
5. **Measure before claiming**: edge error at the planned frame (`medir_borde.py`), edge movement per frame against the
   warped-still baseline, and how far the object sticks out of the pasted mask (`medir_seguimiento.py`). Show a 24 fps
   stabilised overlay (`clip_borde.py`), not a sheet.

## Files

- Scripts: `candidatos.py`, `refinar.py`, `medir_borde.py`, `medir_seguimiento.py`, `clip_borde.py`, `lado_a_lado.py`, `wf/`
  (API workflows + `encolar.sh`)
- Alphas (384² crop at x890 y570 of the plate, float32): `out/alfa_*.npy`. Tracked masks: `out/sam3_toma*/`,
  back-warped `out/*_en_placa.npy`
- Presets: `E:\ComfyUI\workflows\preset_mask_sam3_still.json`, `preset_mask_sam3_track.json`

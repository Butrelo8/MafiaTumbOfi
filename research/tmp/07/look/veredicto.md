# 07, LOOK + halación over E5 and the provisional E6 (2026-10-14)

**Masters (FFV1, `maestros/`):** `{vestidor,cripta,atrio}_{esc,movil}.mkv` (240 frames) and the two transitions:
`grupo_ida_job2.mkv` (185 frames, camarín → cripta) and `contratacion_ida_job3.mkv` (204 frames, cripta → atrio).
Chain: `armar.sh`. Seams: `costuras.py`. Determinism: `determinismo/LEEME.md`. revisar: `revisar/{sin,look}_*`.
Side-by-sides at 24 fps: `ver/*_antes_despues.mp4`. Stills: `ver/placas_antes_despues.jpg`.

## Reference
Matched: the approved sacristía master (`tmp/sac10/esc/armar.sh`). It uses the same LOOK (Kodak 2383 at 50 %,
desaturated greens/cyans, curve, PI/5 vignette) and `halacion.sh` at its defaults (HAL 0.8, MIST 0.45). The verticals
are the graded desktop re-cropped, as in `sac10/vert2`.
Changed on purpose: `vignette=PI/5:dither=0` (vibeship, 2026-10-14). The atrio vertical is graded on its own because its
low mist exists only in the vertical (vibeship).
Variants: the parameters are fixed by the brief. The one variant compared was cripta movil, graded directly vs re-cropped
(below).

## Determinism
The approved chain is **not** per-frame deterministic: `vignette` dithers by default, with random state carried across
frames. With `dither=0`, the whole chain (LOOK + halación) gives the same output frame (md5) for the same input frame, at
any position in the stream. Evidence on the masters: job3's tail is the atrio loop's frames 0–19, and after grading the
two streams separately those 20 frames are identical byte for byte.
Cost: about 0.5 luma darker than nave/sacristía (the dither added [0,1)). No banding in the corners.

## Seams (`costuras.py`, mean |dif| in 8 bits)
| transition | check | before the look | after |
|---|---|---|---|
| job3 cripta → atrio | f184–203 vs atrio loop 0–19 | 0.000, 20/20 identical | **0.000, 20/20 identical** |
| | f0 vs cripta plate (graded the same way) | 0.000 | **0.000** |
| | f0 vs cripta loop f0 (live zones) | 0.44 (2.4 % px > 8) | 0.92 (3.8 %) |
| | f203 vs atrio plate | 0.38 | 0.29 |
| job2 camarín → cripta | f165–184 vs cripta loop 0–19 | 8.39 | 6.18 |
| | f0 vs start.png | 4.65 | 3.36 |
| | f184 vs end.png | 3.19 | 1.96 |
job2 never had a seam with the loops: it has no 20 raw frames (COSTURA), and it starts from the camarín plate from
before the production plates (f0 vs the E5 vestidor loop: 29.6 → 27.5). The look does not make it worse. That is for
the E6 final to fix.

## revisar (before → after)
| loop | seam (≤ 1.00) | sharpness | crawl | flicker (static %) |
|---|---|---|---|---|
| vestidor esc | 0.01 → 0.01 | 1.00 → 1.00 | 0.00 → 0.00 | 0.00 → 0.01 (100 %) |
| cripta esc | 0.01 → 0.03 | 1.00 → 1.00 | 0.00 → 0.00 | 0.00 → 0.01 (94 %) |
| atrio esc | 0.03 → 0.03 | 0.98 → 0.95 | 0.01 → 0.02 | 0.00 → 0.01 (96 %) |
| vestidor movil | 0.03 → 0.02 | 0.88 → 1.01* | 0.00 → 0.00 | 0.00 → 0.01 (99 %) |
| cripta movil | 0.06 → 0.11 | 0.86 → 1.00* | 0.00 → 0.01 | 0.02 → 0.33 (7 %) |
| atrio movil | 0.04 → 0.04 | 0.96 → 0.97 | 0.01 → 0.01 | 0.01 → 0.01 (93 %) |
\* The ref is the vertical plate graded directly, not re-cropped, so the sharpness of the re-crops is only indicative.
All pass, well under the approved loops' seams (nave/sacristía 0.75 / 0.51).
Cripta movil: in the `cerrado` crop the halación and mist glow of the candles and the light shaft cover more of the frame
(the dark band is rebuilt each frame from rows that now carry glow). The static area falls to 7 % and flicker rises to
0.33, still under 0.5. Graded directly instead, it gives 0.03 (static 83 %) with a similar moving area (22 % vs 26 % of
pixels with temporal std > 0.5). The re-crop is kept so it stays the same pixels as the desktop (vibeship).

Transitions (revisar `--inicio/--fin` with the plates graded the same way):
- job3: start 0.0, end 0.3, hidden-cut 42 frames ≥ 90 % (f106–147), morph 0.
- job2: start 1.0, end 0.6, morph 0. hidden-cut **14 frames ≥ 90 % (f85–98)**: the look's darkening now gets it to black.
  Without the look it failed (max 86 %).

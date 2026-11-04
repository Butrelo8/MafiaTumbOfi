# Is the LOOK per-frame deterministic? No: `vignette` dithers with state carried across frames (2026-10-14)

Test: the 6-frame clip A B A C A A (A = vestidor_esc f0, B = cripta_esc f100, C = atrio_esc f50), graded with the
approved chain: `format=gbrp,$LOOK,format=bgr0` → ffv1, then `halacion.sh` with `VC=ffv1` and the default HAL 0.8 / MIST 0.45.

| stage | A at f0, f2, f4, f5 (framemd5) |
|---|---|
| input | identical |
| LOOK without `vignette` | identical |
| LOOK with `vignette=PI/5:dither=0`, then halación | identical |
| **LOOK as approved (`vignette=PI/5`, dither on by default)** | **all differ** |
| that look, then halación | all differ |

Size (`diff.py`): after LOOK, max 1 level on about 70 % of pixels (mean 0.34). After halación and yuv420p, max 5 and
mean 0.41 on about 39 %.
Cause: ffmpeg 6.1.1's `vignette` adds dither from a random generator whose state carries over from one frame to the
next. The output depends on where the frame sits in the stream, not only on its pixels.

Cost of `dither=0` (`band2.py`, corners after halación): no banding (the plates' grain hides it: distinct levels and
the residual after a σ12 blur are the same). There is one systematic offset: with dither the frame is +0.42 to +0.51
luma brighter on average, because the dither adds [0,1) before truncating to 8 bits. So E5/E6 with `dither=0` come out
about 0.5 level darker than nave/sacristía.
4× crop of the corner, lifted: `banding_vestidor_esquina_x4.png`.

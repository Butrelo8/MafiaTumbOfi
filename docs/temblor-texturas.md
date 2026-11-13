# Trembling textures in the transition clips: cause, variants, fix (2026-11-12)

Owner on `transicion-v2-*.mp4`: "some trembling going on some textures". Code: `blender/temblor.py` (renders variants of the
render settings on a stretch, same scene/camera/light as `escena.py transicion`). Measures: `scripts/temblor-flujo.py`
(no reference needed), `scripts/temblor-ref.py` (against a 1024-sample reference). Renders and logs: `blender/render/transicion/temblor/`.
The harness reproduces the v2 clip: its frame 170 differs from `v2-1280x720/f_0170.png` in 16 pixels by 1 level.

## Where
revisar's crawl/flicker rows are n/a on this shot (static area 0 %, the camera never stops), so the measure is the
residual of each frame against the mean of its two optical-flow-warped neighbours (8-bit levels, per 160x160 tile; real motion mostly cancels).
Outside the two windshield passes (f41-55, f121-133) the hot tiles are the lit centre of the frame in both clips:
- f2-35: dashboard, centre console and the two front heads (16:9 tiles 1.4-2.6 levels against 0.1-0.8 at the edges; 9:16 the same place, 2.2-2.7).
- f140-190: the two figures on the truck bed and the truck's rear (16:9 2.0-2.2 and 9:16 2.2-2.4 against 0.4-0.6 on the road at the sides).
Crops of the worst stretch (f164-187, figures at x560 y230 260x200): `tira-act-f170-181.png` (the v2 settings, 12 consecutive frames at 200 %, gain 2):
the hair and window behind the figures change blotch pattern every frame, and f180 has an orange firefly on the right figure's nose.

## Why
Sampling noise left over by the denoiser, not texture aliasing, motion blur or encoding.
```
variant (f164-187, 1280x720, figures crop)  hp  tstd  rms  | flow residual: figures road rear | s/frame
act   24 spp OIDN, fixed seed (v2 clips)     5.40 3.96  6.37 |  2.18  0.55  2.07 | 15.8
nodn24 24 spp, no denoiser                   20.01 15.51 23.62|  10.3  4.10  7.02 |  5.5
```
- Raw 24-sample noise is RMS 23.6 levels against the reference; OIDN (already with albedo + normal passes, `ACCURATE` prefilter, `HIGH` quality: those are Blender's defaults, so
  "denoise with albedo+normal" was already the setting) takes it to 6.4, but what it leaves differs from frame to frame.
- Fixed seed is the right choice: an animated seed makes it worse (24 spp: hp 5.40 to 6.50; 128 spp: 3.86 to 4.39).
- Motion blur off: hp 5.44 against 5.40, no effect.
- Encoding: the same flow residual on the decoded MP4 and on the PNGs (f165-186): figures 2.22 vs 2.18, rear 2.11 vs 2.07, road 0.65 vs 0.55. Small.
- Texture shimmer (no mipmaps in Cycles): **not tested**. The `tex1k` variant (4096 textures scaled to 1024, 12 images) rendered identical to `act` in two attempts
  (also with `pack()`): the scaled images never reached the render, so it says nothing. Indirect: more samples (which supersample textures too) fixes most of it.

## Variants (same 24 frames; hp/tstd/rms: vs the reference on the figures crop, 8-bit levels, lower = steadier)
```
variant                  hp    tstd  rms  | flow: figures road rear | s/frame | look
act 24 spp OIDN          5.40  3.96  6.37 |  2.18  0.55  2.07      | 15.8    | firefly on nose f180, blotchy windows
seed 24 spp anim seed    6.50  4.10  6.42 |  2.64  0.55  2.11      | 16.0    | worse
nomb 24, no motion blur  5.44  3.98  6.37 |  2.21  0.69  1.65      | 18.5    | same
s128 OIDN                3.86  2.58  4.00 |  1.67  0.52  1.91      | 17.3    | holds, firefly gone
s128seed                 4.39  2.63  3.98 |  1.92  0.52  1.94      | 16.6    | worse than fixed
s256 OIDN                3.36  2.23  3.39 |  1.52  0.52  1.87      | 20.6    | holds
s128o OptiX              4.03  2.69  4.22 |  1.71  0.50  2.03      |  6.7    | holds
s256o OptiX              3.52  2.33  3.58 |  1.56  0.50  1.95      |  6.9    | holds
s512o OptiX              3.15  2.07  3.11 |  1.43  0.51  1.88      |  9.4    | holds (mean luma 20.53 vs 20.56)
eevee 64 TAA             6.29  10.23 25.33|  1.20  0.46  0.77      |  2.6    | does not hold (see below)
```
EEVEE is the steadiest frame to frame but the look changes: noses and eyes read flat, the taillights bloom, the hair loses its shading
(rms 25 against the Cycles reference). Not an option without re-lighting.
The reference (`ref`: 1024 spp, no adaptive, OIDN HIGH) covers only the figures crop (7.3 s/frame), so it is OIDN-flavoured; the reference-free flow columns agree with the ranking.
Interior stretch (f9-30, flow residual, no reference): act vs s512o: dashboard 2.27 to 1.41, heads 1.07 to 0.78; 17.4 vs 10.8 s/frame.

## Fix
Cycles OptiX, 512 samples, **OptiX denoiser** (`cycles.denoiser = "OPTIX"`), fixed seed, everything else unchanged.
It lowers the figures' frame-to-frame error 5.40 to 3.15 (-42 %) and is also cheaper: the 15.8 s/frame of v2 is mostly the CPU OIDN denoise (nodn24 is 5.5 s/frame; the 128-spp OIDN run is 17.3 s, so samples cost almost nothing here).
Full re-render, 192 frames per format: about 9.4-10.8 s/frame = 30-35 min per format, about 1.1 h for both (v2 took 56 min for 16:9 alone). Same camera, framing, scale, light.
Not done: re-rendering the clips, eagle.sh/revisar on a clip made from these frames (these are variants on a stretch, not a deliverable).

## And if the transitions lived inside a real-time 3D scene (three.js, GLB)?
For the trembling it would remove this cause: a rasterizer has no sampling noise and applies mipmaps and anisotropic filtering, so textures sit still. It would not carry the look:
even Blender's own rasterizer (EEVEE, above) changes faces, taillights and hair, and the Cycles night (headlight pools, glass, haze, soft bounce on the figures) would have to be
rebuilt by hand in three.js lighting and baked maps. On phones it is the weak side: the four Tripo figures are 290k-480k triangles, 13-19 MB each with three 4096-px textures and no skeleton
(`research/2026-11-12-interactividad.md`), so they would need decimating (to a few tens of thousands of triangles), 1k textures and a rig before a phone could run them; the research found skinned figures
dropping from 60 to 10-20 fps on a phone after a re-export, against a 3 MB entry budget. Today each phone downloads one 3.3 MB clip (the 9:16 one); a live scene is three.js (about 0.15-0.25 MB gzipped, not measured here) plus the truck, the road
and four figures, plausibly several MB and certainly above the clip once textures are counted (not measured). The Tripo free-plan licence applies either way, and a GLB on the page redistributes the asset itself, which is the greater exposure of the two.
Recommendation: fix the render (about 1.1 h for both formats) and keep real-time 3D for small interactive layers later.

## v3 clips (2026-11-12): the fix applied to both formats
`blender/temblor.py` variant `s512o` over frames 0-191 (OptiX denoiser, 512 samples, fixed seed; scene, camera, scale, light as v2), encoded with the v2 command (x264 crf 16, yuv420p).
Clips: `blender/render/transicion/transicion-v3-1280x720.mp4` (12.7 s/frame, 41 min), `transicion-v3-720x1280.mp4` (13.6 s/frame, 43 min); frames in `v3-<WxH>/`, logs `v3-<WxH>.log`, `CHOQUES 0` on both. v2 untouched.
eagle.sh/revisar (`revisar-v3-<WxH>/`): exit 0 on both, same table as v2: strobe 0 runs (pass), dark 80 % / 75 %, jump events f41/f54 (16:9) and f48/f119 (9:16), crawl/flicker n/a.
Tremble (`scripts/temblor-flujo.py`, flow residual in 8-bit levels, PNG frames, v2 -> v3):
```
                           16:9 v2->v3     9:16 v2->v3
figures, f165-186          2.18 -> 1.43    2.40 -> 1.51
truck rear, f165-186       2.07 -> 1.88    1.63 -> 1.49
road (16:9 only), f165-186 0.55 -> 0.50
dashboard, f9-30           2.27 -> 1.41    2.51 -> 1.54
front heads, f9-30         1.07 -> 0.78    1.17 -> 0.82
whole frame f2-38          0.82 -> 0.62    0.74 -> 0.52
whole frame f62-115        0.88 -> 0.88    1.01 -> 1.03
whole frame f140-189       0.93 -> 0.83    0.96 -> 0.85
```
Not verified: f62-115 (the road pass) did not change, and the frames around the windshield and disocclusion (f41-55, f121-133) were not isolated; no frame-by-frame look at v3 beyond the stretch strips above.

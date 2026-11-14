# EffectCraft pilot: the cab shot as a 2.5D composite (2026-11-13)

Pilot of EffectCraft 0.24.1 (storytold/effectcraft, Apache-2.0, alpha) as our After Effects for Blender renders,
owner-approved 11-13. Result, numbers and verdict at the end.

## Install
Linux tarball from the v0.24.1 release, no sudo, no system packages, `ldd` clean:
```bash
~/.local/opt/effectcraft-0.24.1/            # bin/effectcraft-cli (headless), bin/effectcraft (UI), share/
~/.local/bin/effectcraft-cli -> ~/.local/opt/effectcraft-0.24.1/bin/effectcraft-cli
```

## Re-run
```bash
# 1. layers from Blender (scene code read from the main checkout, see below), ~30 s/frame/pass at 1080p, 24 spp
effectcraft/render-capas.sh 1920 1080 blender/render/effectcraft/capas-1920x1080 24 bg:0-59 fig:0-59 fg:0-59
effectcraft/render-capas.sh 1080 1920 blender/render/effectcraft/capas-1080x1920 24 bg:0-59 fig:0-59 fg:0-59
# 2. composition (kept variant C by default) and render; --out must not contain spaces (see bugs)
effectcraft/componer.sh 1920 1080 blender/render/effectcraft/capas-1920x1080 <dir>/cabina-16x9.ecproj
effectcraft-cli --project <dir>/cabina-16x9.ecproj render --comp Cabina --format h264 --out <path without spaces>.mp4 --progress
# 3. Lottie
effectcraft-cli --empty script effectcraft/lottie.jsx --save-as <dir>/titulo.ecproj
effectcraft-cli --project <dir>/titulo.ecproj exec file.exportLottie --params '{"comp":"Titulo","path":"<dir>/titulo.json","textAsShapes":true}'
effectcraft/lottie-check.sh <dir>        # lottie-web 5.12.2 in headless Chromium: totalFrames, two frames as PNG
# 4. MCP probe (not registered anywhere): python3 -I effectcraft/mcp_probe.py <root without spaces> [tool json]...
```
Outputs live in `blender/render/effectcraft/` (git-ignored).

## Scene dependency
The cab scene is uncommitted work in the main checkout (`/mnt/e/Cursor Projects/MTO`, branch `cc/goblindrone`):
`blender/escena.py`, `blender/transicion.py`, `src/lib/escena.json`, `blender/assets/reparto/`. `effectcraft/capas.py`
reads them from there without changing them and prints their sha256 (`2b6fdc2b8cbefc0f`, `32e5c8ef15c66351`,
`4284419a3aa23d0f` for this run). `escena.py` ends in an unconditional `main()`, so its source is exec'd minus that line.

## The shot
- Camera frozen at f0 of `transicion.CAMINO` (between the rear headrests, 20 mm; 9:16 keeps the 75 % horizontal-angle rule).
- Reference: the between-the-seats car interior of *Children of Men* (2006). Kept: both front heads framing the
  windshield, focus on the heads, a slow creeping move. Changed on purpose: no handheld float; an eased straight push
  with a small sideways drift, foreground seat backs out of focus.
- 60-frame layers, cycled with `loopOut('cycle')` on time remap: the road tile (8 m), ground (4 m) and tramo (48 m)
  repeat every 60 frames at 0.8 m/frame; nod and bob are 20 f; steering `sin(2πf/120)` is 0 at f0 and f60.

## Layer split (what worked, what did not)
| pass | content | how |
|---|---|---|
| bg | everything but the band and the two front seat backs, opaque | figures `visible_camera=False`; seat-back box transparent on camera rays |
| fig | the band, alpha | non-figure surfaces: seat-back box transparent, anything else holdout, camera rays only |
| fg | the two front seat backs, alpha | outside the box holdout; figures `is_holdout` (heads sit in front of the seat tops) |

The masks are injected into every non-figure material as `Mix(orig, mask, Light Path › Is Camera Ray)`, so shadows
and bounce light are identical in every pass. Stacked at t = 0 against a plain render of f0 (1920×1080):
mean |Δ| 0.0010, p99 0.012, 0.16 % of pixels over 0.05 (denoiser noise and edges).

Tried first and dropped:
1. **Camera clip at 1.10 m** (fg = clip_end, bg = clip_start): Δ 0.0054, and a figure's hand that a cushion hides
   showed on top (the cushion was in bg, behind the figure layer). On the push, the roof — one surface crossing the
   split — opened onto the sky at the top of the frame.
2. **Distance mask on camera rays** (near transparent / far holdout): at 1.10 m the seat backs straddle the split and
   cut the figures' shoulders (holes a push would reveal); at 1.30 m it fixed the bodies but kept the roof tear.
A box around the objects that really are in front is the split that holds under parallax.

## Composition (effectcraft/composicion.jsx)
No depth pass was rendered: three discrete planes with the camera's depth of field covered it.
Three 3D layers at their real distances (seat backs 1.0 m, band 1.25 m = the 100 % plane, bg 2.6 m), each scaled
d / zoom so the frame matches the render at t = 0; a one-node camera pushes 10 % of the band's distance with a
40 px drift (16:9), depth of field focused on the band plane by expression, aperture 20; `wiggle` sway on the band
(2 px, 0.6 Hz); Glow (threshold 78) on bg; layer and comp motion blur.
Variants at t = 0 and 6.9 s, side by side: A push 8 % / aperture 40 (the road through the windshield turns to mush),
B 6 % / 12 (reads as a flat zoom), **C 10 % / 20 / drift 40 px, kept**: most parallax, heads sharp, road still readable.

## Times (RTX 4070 Ti for Cycles; EffectCraft on CPU)
```
Blender, per pass, 1080p, 24 spp, OptiX device, OIDN denoise:  ~27-29 s/frame, ~22 s of it OIDN denoising
  same at 96 spp with denoiser OPTIX: ~6 s/frame (96 spp raw: 5.6 s/frame) -> use DENOISER=OPTIX next time
  16:9 batch bg+fig+fg 0-59: 4940 s (bg 1719, fig 1610, fg 1582), scene build ~30 s
EffectCraft render h264 1920x1080, 168 frames (7 s): 98 s (0.58 s/frame); +Remove Grain x3 layers: 161 s (strength 3: 204 s)
EffectCraft render-frame 1920x1080: 0.6-1.6 s;  --gpu in WSL is llvmpipe (software Vulkan): 0.54x of CPU
Lottie export: instant; 13,843 B JSON (3,147 B gzip)
```

## Done-check: crawl FAIL, and where it comes from
`eagle.sh` on the 16:9 MP4: exit 1, every row passes except `crawl 0.73 (<= 0.2)` (dark 76 %, flicker 0.16, strobe 0,
events 0). Bisect, all with the same EffectCraft composition:
```
noise-free f0 stills + push/DoF/drift                0.13  pass
raw bg layer (Blender PNGs looped, locked)           0.20  pass (edge)
three layers stacked, camera locked, no DoF/wiggle   0.29  FAIL
full, no DoF                                         0.56
full + Remove Grain (temporal)                       0.58  (strength 3, 2 passes: 0.60)
animated bg, frozen fig/fg                           0.55
frozen bg, animated fig/fg                           0.24
full (kept)                                          0.73
```
Render settings on the 24-frame version of the same composite (`effectcraft/prueba-ruido.sh`), wall time for
bg+fig+fg × 24 frames:
```
24 spp OIDN (the clips)          0.55   ~2000 s
48 spp OIDN                      0.51    2056 s
96 spp raw                       0.60     406 s
96 spp OIDN                      0.48    2169 s
96 spp OptiX denoiser            0.48     438 s
96 spp OptiX, world frozen       0.27     471 s   (MUNDO_QUIETO=1: road and lamps stop, figures keep their idle)
```
From 24 to 48 spp the bg layer's frame-to-frame high-frequency change in its dark parts drops 5 % (0.247 → 0.234);
sample noise would drop ~30 %. Freezing the world takes crawl from 0.48 to 0.27. So the crawl is mostly designed motion:
the passing lamp light sweeping the cab and the road, plus the figures' nod, inside revisar's static mask, which the
push shrinks onto the dark interior. Render noise is a minor part, and EffectCraft is not the cause (its output on still
layers: 0.13). With mothership's agreement, the 3 h re-render at 96 spp was not run (its preview reads 0.48).
eagle-eye: 16:9 run 680aed12d648 (claim confirmed as minor `boiling`, written before the frozen-world test);
9:16 run 445871e654c0 (claim refuted with the strips and the numbers above; the checker still lists it as a finding).
No tears, holes or seam problems in either.

## EffectCraft: what failed or deviated (0.24.1)
1. `render --out` and `mcp --automation-read-root/--automation-write-root` cut the path at
   the first space: `render --out "/mnt/e/Cursor Projects/…/x.mp4"` wrote `/mnt/e/Cursor.mp4`; `mcp
   --automation-write-root "/mnt/e/Cursor Projects/…"` exited with `automation root /mnt/e/Cursor: No such file or
   directory`. Paths inside JSON params (`exec file.exportLottie`) and JSX are fine. Workaround: a symlink without spaces.
2. JSX on a shape layer: `layer.property("Position" | "Scale" | "Opacity")` binds the first shape group's transform,
   not the layer's (After Effects binds the layer). Use `layer.property("Transform").property(…)`.
3. Image-sequence import defaults to 30 fps; set `footage.mainSource.conformFrameRate = 24`.
4. MCP with `--automation-*-root`: `run_script` is refused ("not available while file access is confined"), so a
   confined agent only has engine commands (`command_run`, `set_property`, `render_frame`…), no JSX.
5. `--gpu` under WSL2 falls back to llvmpipe (software Vulkan), slower than the CPU path.
6. `get` with an effect path (`effects/1/noiseReductionSettings/noiseReduction`) answered `no property`; `props --flat`
   lists the real paths. Nothing crashed.
Worked as documented: JSX object model (comps, 3D layers, camera + DoF, expressions `wiggle`, `loopOut('cycle')`
on time remap, Glow, Remove Grain, motion blur), headless `render` with `--progress`, `render-frame`, Lottie export
with an empty warning list, MCP over stdio (27 tools; `open_project`, `render_frame`, confinement refusals).

## Lottie
`effectcraft/lottie.jsx`: gold "MAFIA TUMBADA" title (Inter Bold, text exported as shapes) that rises and fades in,
plus a rule that scales out, 800×240, 3 s. 13,843 bytes (3,147 gzip), `warnings: []`. Plays in lottie-web 5.12.2
(headless Chromium): 72 frames at 24 fps, frame 2 faded and 25 px lower than frame 36, which matches EffectCraft's own
render at 1.5 s.

## Result
```
Windows: E:\Cursor Projects\MTO-uncdrone\blender\render\effectcraft\cabina-16x9.mp4 · ...\cabina-9x16.mp4 · ...\lottie\titulo.json
clips: blender/render/effectcraft/cabina-16x9.mp4  1920x1080 24 fps 168 f H.264 15 Mb/s, 13.1 MB, rendered in 98 s
       blender/render/effectcraft/cabina-9x16.mp4  1080x1920 24 fps 168 f H.264, rendered in 94 s
eagle.sh/revisar 16:9: exit 1 — crawl 0.73 FAIL; dark 76 % info, flicker 0.16, strobe 0 runs, events 0 pass
eagle.sh/revisar 9:16: exit 1 — crawl 0.83 FAIL; dark 69 % info, flicker 0.21, strobe 0 runs, events 0 pass
loop seams (wrap / mean step), 16:9 bg 1.35x fig 1.04x fg 0.81x; 9:16 bg 1.30x fig 1.06x fg 1.18x (all inside the step range)
lottie: blender/render/effectcraft/lottie/titulo.json 13,843 B, plays in lottie-web 5.12.2
```

## Verdict
CLI: **usable for drones, yes.** Headless, no display, ~0.6 s per 1080p frame on CPU, and the After Effects JSX object
model (3D layers, camera DoF, expressions, effects, time remap) builds a whole comp from one script. Re-runs are
deterministic and Lottie export is one command. Watch for: paths with spaces in `--out` and the automation roots,
and the shape-layer property binding. It's an alpha: nothing crashed in this pilot, but pin the version.
MCP: works (27 tools, stdio, confinement enforced), but a confined server refuses `run_script`, so a confined drone
can't use JSX. For drones the CLI + JSX path is better; the MCP suits interactive inspection (`render_frame`,
`get_property`).

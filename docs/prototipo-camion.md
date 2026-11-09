# Truck on an endless highway: hybrid prototype (2026-11-09, branch `cc/goblindrone`)

Spec: `~/projects/mothership/docs/queue/2026-11-09-mto-truck-hybrid-prototype.md`. Owner update 11-09: night **and** dusk as
two presets of one scene; the Cycles loop is rendered in **night**.

## What it is
- One scene, built by `blender/escena.py` from `src/lib/escena.json` (stops, presets, world sizes: the one place for values).
  - `-- glb` exports `public/escena/escena.glb` (truck + one 48 m stretch of roadside props + hills) for the page.
  - `-- loop noche alta W H dir` renders the Cycles loop of the same scene from the first stop.
- Page `src/pages/index.astro` + `src/scripts/escena.ts`: the truck is held still, the world scrolls under it at 19.2 m/s
  (the loop's speed). The props stretch is cloned 12 times and wraps every 48 m; the road and ground textures scroll.
  Four tabs (Inicio, Música, El grupo, Contratación) move the camera between the stops alta, cabina, lado and cenit
  (1.6 s ease). Noche/Atardecer switches the preset.
- Poster = frame 0 of the Cycles loop (`poster-720x1280.jpg` portrait, `poster-1600x900.jpg` landscape). The live scene fades in over it.
  - No WebGL2: the loop plays (`loop-*.mp4`); with reduced motion as well, the poster stays.
  - A slow device (median frame > 50 ms after 3 s) swaps the live scene for the loop.
  - Reduced motion: road still, wheels still, camera cuts.
- Truck: Quaternius "Pickup Truck", CC0 (licence and source in `public/escena/LICENSE.md`). Repainted black clearcoat + chrome
  by swatch, narrowed to 2.05 m; its stock proportions read as a lowered truck. HDRIs and road textures: Poly Haven / ambientCG, CC0.
- The seamless loop holds by construction. The world moves 192 m per 10 s loop (= 4 stretches = 24 road tiles = 48 ground tiles),
  the wheels turn exactly 64 times, and frames 0–239 are rendered (frame 240 = frame 0).

## Run
```bash
scripts/prototipo.sh        # one command: ext4 mirror, install, build, preview on http://thiccpc-wsl:3109 (3100 is taken by another project)
# rebuild the scene / loop:
/mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- glb
scripts/render-loop.sh 64 720x1280 && scripts/render-loop.sh 32 1600x900   # ~12 s/frame each (RTX 4070 Ti)
scripts/encode-loop.sh 720x1280 22 && scripts/encode-loop.sh 1600x900 22
```
On `/mnt/e` a cold `bun run build` takes 6.5 min and the dev server takes minutes to answer. A mirror on ext4 builds in 1.6 s.

## Numbers (2026-11-09, production build, `scripts/prototipo.sh`)
```
weight at 390, live path      1.61 MB  sum of every file the page loads (Playwright response bodies)       budget 3 MB
                              (medir-peso 0.85-1.00 MB and revisar 1.05 MB stop at network idle before the HDR/textures finish: undercount)
render cost 390 CPU x4        renderer.render() p50 2.1 ms  p95 4.9 ms   Windows Chrome headless, ANGLE D3D11 RTX 4070 Ti
render cost 1440              p50 0.4 ms  p95 0.7 ms                     same backend
frame interval 390 / 1440     p95 6.2 / 6.1 ms = the display's rAF cadence (~164 Hz), a ceiling, not a cost
                              (an earlier 36.4 ms p95 ran while Cycles was rendering on the same GPU)
Mac WebKit, iPhone size       OK from WebKit's side (mothership pass, results ~/cc-out/mto-camion-webkit/results.json on the Mac):
                              modo=vivo on Apple GPU, 0/6 blank shots, frame p95 36 ms (headless WebKit paces at ~33 ms),
                              keyboard tabs OK, no WebGL -> poster + .mp4 loop; reduced motion cuts (the 100 ms two-shot check
                              could not resolve it: one screenshot takes ~135 ms)
revisar web 390/1440          all pass (overflow 0, tap<44 0, contrast 0, cls 0.000/0.001, reduced-motion 0 animations)
slop-check src                1 FAIL menu-button-not-plain = false positive (role="tab" buttons carry aria-controls; labels are plain words)
refs-check references.md      PASS (6 sections);  check-matrix DESIGN.md 0 errors;  bun test 10/10
revisar --loop 720x1280       seam 1.50 <= 3.05 pass, strobe 0 pass, crawl 0.20 pass, flicker 2.27 FAIL (accepted, see below)  [lens-fix render; eagle.sh]
revisar --loop 1600x900       seam 1.44 <= 2.29 pass, strobe 0 pass, crawl 0.49 FAIL, flicker 1.97 FAIL (static 8 %)
loop files                    loop-720x1280.mp4 980 KB, loop-1600x900.mp4 1.61 MB, posters 32 / 46 KB (fallback only, not on the live path)
```
**Loop crawl/flicker: accepted (mothership decision 11-09, for the owner's look).** The FAILs come from the pole lights sweeping over the
truck every 2.5 s: the sky's per-pixel temporal std is 0.00 (no render noise), the truck region's mean swings 5.3 (mean 15). revisar counts
the stationary truck as "static". The sweep reads as driving at night, so it stays; no light linking.

**Lens bug (fixed 11-09).** `materials.clear()` reset the polygons' material indices, so headlight and brake-light faces lost their
emissive materials. Fixed in `blender/escena.py`; the GLB is re-exported. The vertical loop is re-rendered with the fix.
**The 16:9 loop (`loop-1600x900.mp4`, `poster-1600x900.jpg`) still carries the bug** (dark lenses); it stays until the owner has seen the look.

## Shots
`docs/prototipo-camion/capturas/`: `{390,1440}-{noche,atardecer}-{inicio,musica,grupo,contratacion}.jpg` (16),
`hoja.jpg` (contact sheet), `movimientos-1440.webm` (the moves, night then dusk), `resultados.json`.

## Weakest, next
- Dusk washes the black paint to silver at grazing angles (clearcoat Fresnel against a bright sky). Lower the dusk env or darken the coat.
- The truck is a low-poly CC0 model: the silhouette is fine, but the close stops (lado, cabina) show its flat panels. Next is a better licensed pickup or a `kiln-prop` pass.
- At 390 the side stop crops the truck (the portrait rule keeps the horizontal angle of a square frame).

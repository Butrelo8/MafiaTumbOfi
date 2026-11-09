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
bun install && bun dev --port 3108 --host 0.0.0.0        # http://thiccpc-wsl:3108 on the tailnet (3100 is taken by another project)
# rebuild the scene / loop:
/mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- glb
scripts/render-loop.sh 64 720x1280 && scripts/render-loop.sh 32 1600x900   # ~12 s/frame each (RTX 4070 Ti)
scripts/encode-loop.sh 720x1280 22 && scripts/encode-loop.sh 1600x900 22
```
On `/mnt/e` a cold `bun run build` takes 6.5 min and the dev server takes minutes to answer. A mirror on ext4 builds in 1.6 s.

## Numbers (2026-11-09, production build via `astro preview`)
```
weight at 390 (live path)     1.00 MB  scripts/medir-peso.mjs   | 1.05 MB revisar weight-390   (budget 3 MB)
frame time 390 CPU x4         p50 6.1 ms  p95 6.2 ms   Windows Chrome headless, ANGLE D3D11 RTX 4070 Ti (dev build earlier: p95 36.4)
frame time 1440               p50 6.1 ms  p95 6.2 ms   same backend; slow-device fallback did not fire
revisar web 390/1440          all pass (overflow 0, tap<44 0, contrast 0, cls 0.000/0.001, reduced-motion 0 animations)
slop-check src                1 FAIL menu-button-not-plain = false positive (role="tab" buttons carry aria-controls; labels are plain words)
refs-check references.md      5/5 PASS (6 sections)
revisar --loop 720x1280       seam 1.49 <= 3.04 pass, strobe 0 pass, crawl 0.42 FAIL, flicker 2.30 FAIL (static 7 %)
revisar --loop 1600x900       seam 1.44 <= 2.29 pass, strobe 0 pass, crawl 0.49 FAIL, flicker 1.97 FAIL (static 8 %)
loop files                    loop-720x1280.mp4 975 KB, loop-1600x900.mp4 1.61 MB, posters 32 / 46 KB (fallback only, not on the live path)
```
The loop FAILs are the pole lights sweeping over the truck, not render noise. Per-region temporal std over the 240 frames:
the sky's per-pixel std is 0.00, while the truck body's region mean swings 5.3 (mean 15) every 2.5 s, when a pole passes.
revisar counts the stationary truck as "static", so that designed light sweep reads as flicker and crawl.
Making the loop pass means dimmer poles plus more fill light (a re-render, about 1 h per size). Not done.

A frame time on a desktop RTX with CPU throttling is not a phone. The real-phone number comes from the Mac WebKit pass
(`docs/queue/2026-11-09-mto-camion-mac-webkit.md`, not run: it needs a Mac drone, and this drone may not spawn one).

## Shots
`docs/prototipo-camion/capturas/`: `{390,1440}-{noche,atardecer}-{inicio,musica,grupo,contratacion}.jpg` (16),
`hoja.jpg` (contact sheet), `movimientos-1440.webm` (the moves, night then dusk), `resultados.json`.

## Weakest, next
- Dusk washes the black paint to silver at grazing angles (clearcoat Fresnel against a bright sky). Lower the dusk env or darken the coat.
- The truck is a low-poly CC0 model: the silhouette is fine, but the close stops (lado, cabina) show its flat panels. Next is a better licensed pickup or a `kiln-prop` pass.
- At 390 the side stop crops the truck (the portrait rule keeps the horizontal angle of a square frame).

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

## Numbers
See the table at the end (filled in from the final runs).

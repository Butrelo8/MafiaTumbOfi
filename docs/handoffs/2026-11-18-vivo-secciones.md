# Handoff: live sections spike (sweatingdrone, 2026-11-18)

Spec: `~/projects/mothership/docs/queue/2026-11-18-mto-live-sections-spike.md`. Branch `cc/sweatingdrone`, fast-forwarded to
`cc/sitio-completo` (2842949). No prod, no merge.

## Owner additions after the spec (relayed by buggyship, 12:36 to 12:40)
- The truck keeps driving the whole time. The world, road, wheels, sway and lights move, and nothing freezes at a stop.
  Section clicks move the camera around the moving truck.
- The screen truck's side screen plays a real video as a VideoTexture. Measure the frame time with the video playing and the
  bytes the video adds.
- Traffic in both directions (2+2 lanes). Same-direction cars overtake in the left lane and oncoming cars use the other
  carriageway. Keep the cars low-poly CC0; list the licences of anything new (nothing is new so far). Bring in ickdrone's
  highway signs (gantry B, arch C). Count the cars' draw calls and bytes.
- buggyship OK'd (12:40) the preview serving the Tripo-cast GLB. Keep it out of git, and keep raw FBX and other source files
  out of `public/`.
- buggyship agreed (12:40) to put the done-check items first, bake a lightmap for the world only, light the truck and cars
  live, and re-encode hero.mp4 for the screen.

## Done so far
- `blender/vivo_secciones_montar.py` (step 1): runs montaje's chain with road3 and the screen truck, swaps utileria's render
  loop for a record of each stop's camera and objects, and saves `tmp/vivo/vivo-montado.{blend,json}`. That run took 5 min
  and exited 0. Log: `tmp/vivo/montar.log`. Command: see the script's docstring.
  - Stop cameras (Blender axes; lens in mm on a 36 mm horizontal sensor; the stills are 960×540):
    1 (1.72,-0.75,1.88)→(1.72,6,1.45) 20 · 2 (0.92,-6.8,3.6)→(1.72,-0.6,1.35) 28 · 3 (0.22,-1.9,2.0)→(-1.02,2.4,2.0) 24 ·
    4 (7.92,-0.3,2.6)→(1.72,-0.3,1.45) 24 · 5 (1.42,0.9,2.45)→(1.72,10.94,1.25) 30 · 6 (3.12,9.44,0.95)→(1.82,1.44,1.2) 32
- `blender/vivo_secciones_exportar.py` (step 2, **first run in progress at handoff**, log `tmp/vivo/exportar.log`). It bakes
  one 240-frame idle clip per Tripo rig (nla.bake, visual keying), prints the f0→f240 seam per rig, decimates the figures
  (1.9 M → 40 k tris each) and the truck (8.2 M → 150 k), and writes `public/vivo/{escena,mundo}.glb` (Draco, WebP) plus
  `public/vivo/vivo.json`. Not verified yet: the screen-truck root rename, the wheel names (`ruedas` may come out empty),
  the cab box (an estimate around stop 1), and whether geometry-nodes plant scatter exports.
- `src/pages/vivo-secciones.astro` and `src/scripts/vivoSecciones.ts`: the page. The truck is fixed and the world moves and
  wraps every 192 m. The page has six nav buttons (aria-current, arrow keys, Home and End), a pool of 4 same-direction and 5
  oncoming cars, a car-following rule behind the screen truck, a VideoTexture on the screen, `?f=0` to freeze for the sheet,
  `?parada=N`, and `window.__vivo` (frameMs, renderMs, ttff, calls, tris). It falls back to `bucle.mp4` without WebGL2.
  **Not built or run yet.**
- `src/lib/vivoRuta.ts` and its test: the camera path (an elliptic orbit around the truck, lifted over the roof, with a
  windshield exit for the cab stop). The test reads `public/vivo/vivo.json`, so it runs once step 2 has written that file.
- `public/vivo/pantalla.mp4`: hero.mp4 re-encoded to 640×360, 24 fps, crf 30, no audio. 882 KB for 15.9 s.
- `public/vivo/{coche_*,portico_b,arco_c}.glb`: copied from ickdrone's export in `~/cc-out/mto-signs-traffic/wb/glb/`
  (git-ignored).
- Assets in this worktree: junctions for `blender/assets/{camion,reparto}` (pointing at the main checkout) and
  `reparto-v5` (pointing at MTO-meltingdrone), plus copies of `assets/utileria` and `tmp/{fuentes,utileria}`. They are
  untracked: never `git add` them.

## Measured so far
```
cast clip seam f0 -> f240 (max bone offset)   manager 0.005 m  alejandro 0.017 m  hector 0.193 m  diego 0.874 m
```
Diego's sip clip ping-pongs on a period that isn't 240 frames, and Héctor's caja5 grip search drifts. Give each rig its own
window from its real period (Diego: read the NLA strip of colddrone's clip), or crossfade the last 12 frames into the first.

## Next, in order
1. Read `tmp/vivo/exportar.log` and fix what failed. Check the GLB sizes and the per-rig seam. Set `ruedas` to the real wheel
   names (`escena.py` names them; grep for `rueda`).
2. Build on an ext4 mirror, following the `scripts/prototipo.sh` pattern (`MIRROR=~/.cache/mto-sweatingdrone-site`), on a
   port other than 3100 or 3109. Copy `node_modules/three/examples/jsm/libs/draco/gltf/*` into `public/vivo/draco/` in the
   mirror. Then run `bun test src/lib/vivoRuta.test.ts`.
3. World materials. road3's surfaces are procedural, so glTF exports them as flat colours. Bake one COMBINED atlas for the
   world with the truck lights off and the fog box (`w_niebla`) hidden. Ship it as unlit `MeshBasicMaterial` in the page.
   Headlight pools: either a baked additive plane fixed to the truck, or the live SpotLights onto a lit road material.
4. Sheet: `?f=0&parada=N` at 960×540 next to `~/cc-out/mto-tripo-v5/montaje/montaje-escN.png`, one row per stop, saved to
   `~/cc-out/mto-vivo-secciones/hoja.jpg`.
5. Numbers: render p50 and p95 plus rAF p50 and p95 in Chromium at 1440 and 390, with the video playing and paused. Also
   draw calls, triangles and bytes per file (cars and signs as their own rows), and TTFF with Chromium's network throttled
   to Fast 4G. Take no numbers while any Blender is rendering (`tasklist.exe | grep -i blender`).
6. Mac WebKit pass. Drones can't run `cc-deck spawn`, so write the brief following `~/projects/mothership/.claude/skills/mac-webkit-pass/SKILL.md`
   and ask buggyship to chain it. Serve the page on 127.0.0.1:4411 behind tailscale serve on :4412.
7. Gates: `slop-check.py`, `revisar.sh web` at 390 and 1440, and `refs-check.py` if `references.md` changes. Then the upload
   command for the owner: `! npx wrangler versions upload` from the mirror, run by the owner.

## Decisions taken (assumptions)
- Endless road: the truck stays fixed and the whole road3 world (4 periods, -384..768 m) moves +Y→ and wraps every 192 m.
  This follows `ruta.py`, and the Cycles run does the same. The camera rides with the truck for free.
- One dressing for all stops: the set every stop shares, plus scene 6's truck picks and scene 1's pennant and strawberry.
  The stills differ per stop. The screen truck is placed per stop and eased with the camera: 40 m ahead in the left lane,
  alongside at stop 3, ahead in our lane at stop 5.
- KTX2: downloading toktx was denied (auto mode), so textures ship as WebP and meshes as Draco.

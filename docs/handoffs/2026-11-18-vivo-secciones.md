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

## Part 2 (laggingdrone, 2026-11-18 13:00 to 13:45): the page works, the look does not hold yet
Commits 90aecb3, a51c6df and the one after them. Export fixed (3 runs): objects parented outside the export set are unparented
with their world transform kept (the sampler's `KeyError: None`), one NLA track per rig (4 clips), the screen truck's 21
loose parts hang from a `pantalla_camion` empty, and the truck box uses visible meshes only, with min x mirrored about x 1.72.
Page: one copy of road3 (the GLB already spans y -960..1344 m), signs once per period, wheel pivots, lights in truck-local
coordinates, the `u_led_N` material plays the video, `?sinpantalla`, `?respaldo`, and Diego ping-pongs (seam not verified with a strip).
Bug fixed: the move's u went negative on the first frame after a click and `getPointAt` threw, which stopped the loop.

```
checks (Windows Chrome, RTX 4070 Ti D3D11)  clicks 10/10, keys 6/6, cars both ways (+8..10 m/s overtaking, 46..52 m/s oncoming,
                                             one held behind the screen truck), wheels spin, world wraps, video plays, 0 page errors
frame 1440 video / paused                    rAF p50 6.1 p95 12.2 / 6.1 12.2 ms; render p95 12.5 / 12.3; during a move rAF p95 18.1
frame 390 CPU x4 video / paused              rAF p50 36.3 p95 72.8 / 30.3 78.9 ms; during a move p95 103
draw calls / triangles                       780 / 3.75 M (world 24 objects incl. scatter, truck 145 k, cast 4 x 38.8 k)
draw calls per source (GLB primitives x     escena 335, mundo 9, cars 9 x 7 = 63, signs 6 periods x (portico 35 + arco 9) = 264
instances, upper bound before culling)       -> the signs are a third of the calls: instance or merge them
bytes                                        escena.glb 9.74 MB, mundo.glb 1.89 MB, pantalla.mp4 0.88 MB, portico_b 0.24, arco_c 0.11,
                                             cars 4 x ~0.11 = 0.45, draco wasm 0.19, js 0.17; total 13.74 MB
TTFF Fast 4G (165 ms, 9 Mbps), 390           13.1 s
camera path test                             bun test src/lib/vivoRuta.test.ts 32/32
gates                                        slop-check 27/27 pass; revisar web (?respaldo, 390+1440) all pass except weight-390
                                             11.49 MB FAIL (the page preloads escena.glb even on the fallback)
```
Sheet `~/cc-out/mto-vivo-secciones/hoja.jpg` (stills in `run2/`): every stop's framing matches the Cycles still, but the night
look does not hold. The world is flat grey (road3's procedural materials export as flat colours), there's no fog, no treeline,
no lane paint and no headlight pool, and the cab interior is lit beige where Cycles is dark. The scripts are
`scripts/medir-vivo.mjs` (Windows node.exe + playwright-core in `E:\tmp\pw-vivo`) and `scripts/hoja-vivo.py`.

## Next, in order
1. World bake (old step 3): one COMBINED atlas for road3, with the truck lights off and `w_niebla` hidden. Save it as plain
   sRGB 8-bit with "Save as Render" off, so AgX isn't applied twice. In the page use MeshBasicMaterial with the map in sRGB.
   Add a baked additive headlight-pool plane fixed to the truck. Trim the world to about 250 m ahead (the fog hides the rest),
   and cut the scatter: those are the 780 calls and 3.75 M triangles.
2. Weight: escena.glb is 9.7 MB. Drop the stop-only props nobody sees, cut the truck below 145 k triangles, and set textures to
   512. Don't preload escena.glb on the fallback path.
3. Leak: escena.glb still carries the old stand-ins (`alejandro`, `hector`, `diego`, `manager`, their `_rig`s, `diego_raiz`);
   the small figure on the road at stop 2 is likely one. Exclude them in the exporter (bytes and triangles drop with them).
4. Diego's seam: check the ping-pong with a full-frame-rate strip, or re-bake on his own period.
5. Mac WebKit pass: brief at `docs/queue/2026-11-18-mto-vivo-secciones-mac-webkit.md` (buggyship chains it). The preview dies with
   the session that started it: `cd ~/.cache/mto-sweatingdrone-site && bunx astro preview --port 4411 --host 127.0.0.1`
   (tailscale :4412 -> 4411 already mapped), then re-run the brief's 200/206 curls before spawning.
6. Upload for the owner: `! cd ~/.cache/mto-sweatingdrone-site && npx wrangler versions upload`.

## Decisions taken (assumptions)
- Endless road: the truck stays fixed and the whole road3 world (12 periods in this blend, y -960..1344 m) moves +Y→ and wraps every 192 m.
  This follows `ruta.py`, and the Cycles run does the same. The camera rides with the truck for free.
- One dressing for all stops: the set every stop shares, plus scene 6's truck picks and scene 1's pennant and strawberry.
  The stills differ per stop. The screen truck is placed per stop and eased with the camera: 40 m ahead in the left lane,
  alongside at stop 3, ahead in our lane at stop 5.
- KTX2: downloading toktx was denied (auto mode), so textures ship as WebP and meshes as Draco.

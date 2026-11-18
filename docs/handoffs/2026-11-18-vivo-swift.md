# Handoff: /vivo-secciones "make it swift" (rizzdrone, 2026-11-18)

Spec: `~/projects/mothership/docs/queue/2026-11-18-mto-vivo-swift.md`. Branch `cc/sweatingdrone`. No prod, no merge.

## What changed
- `scripts/vivo-optimizar.mjs` (new pipeline step after the Blender exporter; raw export kept in `tmp/vivo/crudo/`):
  - It drops the four old stand-ins: 1.58 M triangles, undecimated, still in escena.glb.
  - It strips transmission and clearcoat. In three.js, transmission re-rendered every opaque object a second time.
  - It simplifies the screen truck's cab (124 k → 15 k) and the strawberry (50 k → 7 k), and takes textures to 512.
  - It splits the cast into `reparto.glb`.
  - Run: `GT=<dir with @gltf-transform/*, draco3dgltf, meshoptimizer, sharp> bun scripts/vivo-optimizar.mjs tmp/vivo/crudo public/vivo`
    (this session's deps: the scratchpad `gt/` dir; reinstall with `bun add @gltf-transform/cli@4.2.1 … sharp@0.33.5`).
- **Cast placement bug found and worked around.** The exporter leaves each `_v5` rig with a local translation that cancels
  its parent's, so the Tripo cast sat at the world origin. That was the small figure on the road at stop 2. Only the old
  stand-ins filled the seats. The optimizer now zeroes each v5 rig's local translation, which puts it on its old rig's origin:
  the cast is back in the cab, but **stop 1 is worse than run2 and Cycles**: the heads sit low behind the headrests, and the
  close figure at the right edge is missing (`hoja-swift.jpg` row 1). Stops 4 and 6 hold. The real fix belongs in
  `blender/vivo_secciones_exportar.py`, where the rig's object transform is lost.
- **Page** (`src/scripts/vivoSecciones.ts`):
  - Load order: poster, then escena + mundo (first frame), then the cast, then cars + signs, then video. Each part runs
    `compileAsync` first.
  - Static meshes are merged per rigid parent (scene, truck, screen truck, each wheel, world). All untextured materials share
    one mesh per side: colour goes in the vertex colours, roughness/metalness/emissive in lookup textures.
  - Signs: 4 periods merged per material. Cars: one InstancedMesh per model and material, with the tint as instance colour.
  - DPR is capped at 1.5 on desktop and 1.25 on phone. A frame probe drops to DPR 1 and turns the pole lights off when the
    median frame is above 20 ms.
  - No per-frame allocations in the steady loop (camera moves still allocate in getPointAt/b2t). The `<link rel=preload>` is gone. `__vivo.cargado`, `.fases`, `.dpr`, `.sondeo` and `.escena`
    are exposed for measuring.

## Numbers (Windows Chrome, RTX 4070 Ti; `scripts/medir-vivo.mjs`; run2 = before, run6 = after)
```
draw calls                 780 (644 in a move)        -> 44 at stop 1, 71 max (side stop / move)   target <= 120  met
triangles                  3.75 M                     -> 317 k (all in view 327 k)
bytes before first frame   ~13.7 MB (all preloaded)   -> ~2.4 MB (escena 1.55, mundo 0.48, draco 0.19, js 0.17); 5.5 MB total
first frame, fast 4G, 390  13.1 s                     -> 3.1 s (cast 4.6 s, cars 5.5 s, video 5.7 s)  target <= 4 s  met (CPU not throttled in that run)
390 CPU x4 rAF p95         72.8 ms (render 76.5)      -> current build: 6.2-18.2 ms (render 4.9-12.8) at 39-55 % Windows load from other
                                                         jobs; 6.2 ms quiet only on the build before the cast fix (161 k tris). Target NOT proven.
390 CPU x4 in a move       103 ms, hitch at click     -> 24.3 ms p95, max 43 ms (was a 346 ms hitch: fixed by compileAsync(scene) before frame 1)
1440 rAF p95               12.2 ms (render 12.5)      -> 6.2 ms (render 2.7)
revisar web ?respaldo      weight-390 11.49 MB FAIL   -> all pass, weight-390 1.75 MB
```
Bytes per lever: escena 9.74 -> 1.77 MB (stand-ins out, transmission/clearcoat out, textures 512), 1.77 -> 1.55 MB (cab and
strawberry simplified); mundo 1.89 -> 0.48 MB (textures 512); cast 1.39 MB moved off the critical path. Draw-call levers were
measured together. Per lever: merging and the stand-in drop cut calls from 780 to 92 (run3); the lookup-texture merge then cut them to 40–71
(run4). Video off vs on at 390 CPU×4 (quiet): render p95 3.5 vs 4.3 ms. Under CPU throttling, DPR and lights show no delta;
their gain is GPU-side and lands in the WebKit pass.

## Sheet
`~/cc-out/mto-vivo-secciones/hoja-swift.jpg`: before | after | Cycles. Framing holds at every stop. The road no longer shows
the transmission smear, and the cast is in the cab. The night look is still the gap: flat ground, no treeline, no lane
paint, and a beige cab where Cycles is dark.

## Spec levers not done (gaps)
Night bake; phone-tier decimation of the cast and truck; a texture atlas (textures were resized one by one, not atlased).

## Next
1. Night bake of the world tile (spec lever, not done): COMBINED atlas for one road period, MeshBasicMaterial. See the
   2026-11-18-vivo-secciones handoff, Next step 1. It is the look fix and the phone fragment-cost fix.
2. Fix the cast placement in the exporter (rig object transform), then drop the zeroing in vivo-optimizar.
3. Re-measure 390 CPU×4 on a quiet machine, including the camera move.
4. Mac WebKit pass: the brief is updated (`docs/queue/2026-11-18-mto-vivo-secciones-mac-webkit.md`).
5. Upload for the owner: `! cd ~/.cache/mto-sweatingdrone-site && npx wrangler versions upload`.

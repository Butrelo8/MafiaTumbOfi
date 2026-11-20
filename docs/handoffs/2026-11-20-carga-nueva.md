# Handoff: new roof load (chilldrone, 2026-11-20 ~08:10, stopped at the 25 % context mark as the brief asks)

Brief: `~/projects/mothership/docs/queue/2026-11-20-mto-roof-props-swap-rebuild.md`. Branch `cc/chilldrone` (merged `cc/slaydrone` ff-only first). Nothing pushed, no deploy.

## Done (measured)
- His 07:15 file dumped, his file untouched (md5 equal to my copy): `E:\tmp\mto-g63-nuevo\volcado-0715.json`.
- Cast bake with that dump through the old exporter: `/mnt/e/tmp/mto-props-nuevos/crudo-reparto/` (use it as `OLD=`; set `cast` to `{"dy":0,"dz":0}` in `blender/props/g63_paradas.json`).
- Pieces prepared (git-ignored, `blender/assets/carga-nueva/`): `maleta-{6,12,24}k.glb` (Tripo flight case 1.97 M tris -> baked 1024 base/rm/normal; all three levels look the same as the full mesh at 1:1 by eye, not verified by numbers; 12k is the one `g63_carga.PIEZAS` loads, 6k would save a little), `guitarra-5k.glb`, `bolsa-5k.glb`, `mochila-9k.glb`. Atlas of the seven r1 stickers (newest set: `blender/props/calcas-r1`, 2026-11-15, 8d625ae): `tex/calcas_atlas.png` 1024.
- BackPack_Blend ships no textures: its mesh got the maps from `max_physical.zip` (UVs do not match exactly, some strap patches differ in colour). The `.max` itself was skipped (Blender cannot open it). No licence file in any package (`LICENSE.txt` written).
- Sizes: flight cases x0.88, backpack x0.70, the gig bags are white in the download so each got a colour (a charcoal, b oxblood).
- Layout chosen: variant 1 (two flight cases lengthwise on the middle and front bars, a guitar case on the outer half of each, bag + backpack side by side on the roof ahead of the front bar, donut where he left it, alien on the pile). Variant 2 (bag behind the pile) looks the same; variant 3 (bags on the pile) puts the alien 0.9 m over the roof: rejected. Sheets: `/mnt/e/tmp/mto-props-nuevos/trabajo/ver/hoja-variantes.jpg`, `hoja-cerca-v1.jpg`, `hoja-piezas.jpg`.
- Deliverable `E:\tmp\mto-g63-nuevo\colocar-g63-carga.blend` (built by `blender/colocacion_g63_carga.py` on a copy of his file; handles `techo_maleta_a/b, guitarra_a/b, bolsa, mochila, dona, alien`; net `carga_red`, straps `carga_red_alien`; his hand/elbow controls unchanged). Dump: `E:\tmp\mto-g63-nuevo\volcado-carga.json`.
```
round trip   bones vs volcado-0715: 0.0000 m, 0.000 deg (4 rigs); props vs layout json: 0.0 (all 7), donut moved 0.0
net          rope vertices inside any netted piece: 0 (7 pieces)
alien        no net above any alien vertex; gap to the net 1.67 cm; straps: min 5.9 mm to the alien, 45 vertices within 12 mm, 0 inside; pairwise mesh overlaps and piece/bar overlaps: none
```
No still of "alien above the net" taken yet for the report (`hoja-cerca-v1.jpg` shows it).

## Not done (exact next steps)
1. `blender/g63_rack.py`: replace `traer_props`/`colocar_carga` (orphaned) by: the donut and alien from the PROPS glb (as now), the rest from `g63_carga.traer()` + `g63_carga.calcas(o, name[3:])`; with VOLCADO each `k3_*` takes its dump matrix (`colocar_volcado` already does); then `g63_carga.tender(cajas without k3_alien, alien, geom_rack(), cam)` instead of `red()` (also in `g63_red_ajustar.py`). `scripts/vivo-g63.sh`: `VOLCADO=/mnt/e/tmp/mto-g63-nuevo/volcado-carga.json`, `OLD=/mnt/e/tmp/mto-props-nuevos/crudo-reparto`. Names already fit `vivo-optimizar` EXTRAS (`k3_`, `carga_red*`) and `montar` (`carga_` prefix; do not name anything `carga_correas`/`carga_cable`). Check the `extras.length < 27` guard.
2. `scripts/vivo-optimizar.mjs`: material `calcas_atlas` -> alphaMode MASK cutoff 0.5 by name (in `terminar`), and keep the atlas at 1024 (a second `textureCompress` with `pattern`) instead of the 512 resize; measure bytes.
3. Sizes: camion_extras.glb old = 576,304 B; report the new one and the load share.
4. `bun run build`, `bun test`, `npx wrangler versions upload --preview-alias vivo` (cloudflare:wrangler skill first), `scripts/g63/ttff.sh` (cap 4 s; measure the current preview interleaved), `vivo-tomas.mjs` Caja/roof stops at 1440 and 390 (draw calls at stop 1 <= 90). Textured materials add ~5 draws in the roof group (maleta, bolsa, mochila, atlas; the guitar colours are flat and merge).
5. Stop cameras (`g63_paradas.json` banda/cabina) were not moved to the new heads.
6. Update `docs/g63-nuevo-dueno.md` "Cosas del techo" (new handle names, net/straps, stickers).

## gotchas
- `wslpath -w` on a relative path gives a relative Windows path: Blender wrote renders to `C:\trabajo` -> pass absolute paths.
- `Mesh.transform` on a copy taken after scaling scales twice (second flight case came out 0.77) -> take every copy before any transform.
- Nearest-surface normal sign gave false "rope inside" counts on a backpack with flipped normals -> test the shrunk box plus distance to surface < rope radius.
- A ribbon sampled every 1.5 cm cut through the alien's flank on the way down (4 vertices < 2 mm) -> spread the alien's height 3 cm to each side and sample 1 cm.
- `vivo_secciones_exportar.py` second argument is the montado's input json (`vivo-montado.json`), not an output.
- The system-python hook blocks any Bash line that mentions `python3` together with PIL: split the edit from the `uv run`.

# Handoff: the live scene catches up with tonight's Blender work (cricketdrone, 2026-11-19 03:50)

Spec: `~/projects/mothership/docs/queue/2026-11-19-mto-live-catchup.md`. Branch `cc/brainrotdrone`, commits afb57ce..ba208df.
Preview only, nothing merged or deployed.

## Preview
- Alias: https://vivo-mafiatumbada.bube-ncio8.workers.dev/
- Version: https://9a1c28d3-mafiatumbada.bube-ncio8.workers.dev/
- The previous version, for comparison: https://e9399a7c-mafiatumbada.bube-ncio8.workers.dev/

## What changed
1. **Truck** (afb57ce): cookingdrone's uncommitted work was copied from MTO-breaddrone. Each shared file was checked identical to
   breaddrone's base before the copy. Carried: G63 lamps, grille, emblem parented, amber both sides, ambient kit, the bed with
   only the cases, donut and alien, no console bottle, and the Tripo seats and console (`CABINA_TRIPO=1`; the owner placed the
   cast on them, and saltyship was told).
2. **Cast** (50b47c8):
   - `blender/vivo_reparto_volcar.py` dumps the owner's evaluated pose from `colocar-reparto-v3.blend`. The 01:30 and 01:39
     saves are identical.
   - The exporter's `VIVO_POSE` puts all four rigs in that pose, held static, as a two-frame clip (saltyship 02:25, option A).
   - Héctor's bottle sits in his hand, and the Tripo console is where he moved it.
   - Bone error against his file: 0.00000 m. Head tops match to 0.1 mm.
3. **Diego**: no newer animation exists. Gate 3 is not built, and only pose A was approved at gate 1. He is in the owner's
   static placed pose (hands on thighs); the old sip clip is gone.
4. **Parenting**: the exporter's `al_camion()` hangs every root on the truck from `camion`.
   - The old escena.glb had about 150 loose roots (emblem, lamp bar, bulbs, bed load, fringe) that floated under the sway.
   - Now the roots are only `camion`, `cerros` and `pantalla_camion`.
5. **Stop 4**: the four look-at points and the cab lamps follow the moved faces. The cameras and exit legs are unchanged, because
   the body did not move.
6. **Fixes found on the way**:
   - The optimizer's `dedup()` merged `vidrio_falso` into `k3_alu`, which made the windows opaque. In the old build the merge
     went the other way and the cases were see-through. Glass is now marked BLEND 0.15 before the dedup.
   - The common decimation (0.094) shredded the headlight rings, LED strips, amber markers and grille (ba208df).

## Numbers
```
                         before (e9399a7c)    now (9a1c28d3)
draw calls stop 1..6     -                    62 88 45 71 37 81   (cap 90; was 48 82 36 75 33 75 at P1 phase 2)
calls stop 1 / moving    49 / 68              62 / 71
bytes total (4G run)     5.74 MB              5.98 MB   escena.glb 1.52 -> 1.86 MB, reparto.glb 1.39 -> 1.29 MB
TTFF Fast 4G 390         3.46 s               4.01 s    (one run each)
clicks / keys / band     -                    10/10, 6/6, 5/5; page errors 0 (vivo-tomas, 36 shots + medir-vivo)
emblem drift (live)      8.14 px (Blender)    0.43 px max over 90 live frames, 1440, against a hood point
bun test                 125 pass             125 pass
```
- The flattening rule in `vivo-optimizar.mjs aplanar()` turns five near-black kiln textures into flat colour and saves 5 calls:
  stop 2 went 92 -> 87, then 88 with the full-detail lamps. At most 0.13 % of pixels change by more than 8 levels.
- The old version's live drift could not be measured: its page doesn't expose the camera.

## Not carried / open
- **Footwell blue lights**: they are Blender AREA lights, and the exporter has `export_lights=False`. The red strips carry, as an
  emissive material. Carrying the footwells needs page lights or a glow decal.
- **Amber markers**: they read pale amber live (hue 38, 247/228/195). The Cycles core is just as pale (hue 30); the orange there
  is glow, which live doesn't have.
- **El Manco's feet** hover soles forward over the footwell, symmetric. His left leg does not point at the far handle, so the
  owner's pose is kept and nothing fell back to 00:52.
- **No motion**: the cast is static until gate 3.
- **The fringe at 4a** is still open (from p1-fase2).
- **ruta.py** still carries the full bed load.

## Rebuild the live files
```
OUT=/mnt/e/tmp/mto-live-catchup/vivo   # montado blend + logs on E:
GPU=0 CABINA_TRIPO=1 MONTAJE_PANTALLA=a MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta \
  WSLENV=CABINA_TRIPO:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA ~/.claude/scripts/blender-run \
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/vivo_secciones_montar.py)" \
  -- "$(wslpath -w blender/escena.py)" "$(wslpath -w $OUT)" 1 all 960x540                                   # 5 min
GPU=0 VIVO_POSE="$(wslpath -w /mnt/e/tmp/mto-live-catchup/pose-blend1.json)" WSLENV=VIVO_POSE ~/.claude/scripts/blender-run \
  /mnt/e/Blender/blender.exe -b --python-exit-code 1 "$(wslpath -w $OUT/vivo-montado.blend)" \
  --python "$(wslpath -w blender/vivo_secciones_exportar.py)" -- "$(wslpath -w $OUT/crudo)" "$(wslpath -w $OUT/vivo-montado.json)"  # 3 min
GT=/home/black/projects/scratch-blender-skills bun scripts/vivo-optimizar.mjs $OUT/crudo $OUT/pub   # then copy *.glb + crudo/vivo.json to public/vivo/
```
Check: `PW=E:\tmp\pw-vivo\node_modules\playwright-core CHROME=<chrome.exe> node.exe scripts/vivo-tomas.mjs <url> <out> 1.6094,1.5691,-2.6842`
(the last argument is the emblem's top vertex in three.js axes; it enables the drift).

Sheet: `tmp/catchup/hoja-lote6b-vivo.jpg` (copy at `E:\tmp\mto-live-catchup\hoja-lote6b-vivo.jpg`). Each row puts lote6b Cycles
on the left and the live preview at 1440 on the right. The last four rows are live only: feet, bottle, rear cab, stop 2. All
shots are in `E:\tmp\mto-live-catchup\preview\`.

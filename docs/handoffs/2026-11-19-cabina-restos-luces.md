# Handoff: old cab leftovers, lamp objects, roof facets (incognitodrone, 2026-11-19 17:45, stopped at the context cap)

Spec: `~/projects/mothership/docs/queue/2026-11-19-mto-cabina-restos-luces.md` (read it first). Branch `cc/brainrotdrone`.
Nothing is committed, published or deployed yet. The work tree is uncommitted (list below). The `vivo` alias still serves 50042ca0.
Owner's extra request (17:01, mid-task): a pass over the truck's exterior (roof and metal) for triangles that show live.

## Causes found (measured)
- **Floating old-seat bits:** `cabina_tripo.borrar_viejos` deleted a face only if it lay wholly inside a box.
  - The old seats' inboard sides lie exactly on the box edge (x 1.585 = CX − 0.135), so their big soup triangles survived.
  - Workbench renders with the flagged faces in magenta: `/mnt/e/tmp/mto-cabina-restos/ver-antes/` (`cabina_atras.png`, `parada1.png`).
  - The wheel exemption also covered the passenger side, and carbon trim was always kept.
- **Console / dash clipping:**
  - `vivo_secciones_exportar.poner_pose` puts `tripo_consola` at the owner's matrix (`/mnt/e/tmp/mto-live-catchup/pose-blend1.json`): +0.3 m forward and tilted 20° nose-up.
  - Its front ends at y 1.18–1.28, z 1.19–1.41, inside the centre stack (face y ≈ 1.13), right under the dash screen.
  - At that pose: 1,266 old faces lie inside it and 545 cross it.
  - The screen bezel `Cube.081` (u_bisel, `pantalla_consola`) also crosses about 170 old stack faces.
  - The `MONTAJE_PANTALLA` in the spec is the screen truck, not the dash screen. The dash screen is `Plane.016` + `Cube.081`.
- **Roof triangles (owner's 17:01 report):**
  - No holes or interior poking out: a downward probe found 2 headliner hits in 21,600 rays.
  - The G63 is unwelded triangle soup. The common DECIMATE at 0.0985 collapses the roof's ribs and panel lines into big flat triangles.
  - Sheets: `/mnt/e/tmp/mto-cabina-restos/techo/hoja-techo.jpg` (entero | diezmado | normales) and `hoja-techo2.jpg` (entero | diezmado | soldado).

## Done (uncommitted)
- `blender/cabina_tripo.py`, rewritten removal:
  - **Centre rule:** a face goes when its centre is in a box (+2 cm in x). Seat boxes are capped at z 1.88; 2.12 took 315 headliner faces.
  - **Exemptions:** the wheel exemption is driver-only; carbon is no longer kept; the floor (`cab_alfombra`) goes only when enclosed.
  - **Enclosed and crossing faces:** they go when a new part encloses them, or crosses them with the face centre inside its box. `poner()` now imports the parts before the removal.
  - Prototype result on the old montado (console at the build position): crossing 267→74, enclosed 55→0, floating leftovers 0, no holes. Hole check: `ver-borrar2/*-sin.png`.
- `blender/cabina_choques.py`: the clash metric (atraviesan / dentro / flotan / asoman) from the live cameras plus close-ups.
  - Flags: `borrar`, `diezmar=r`, `soldar`, and env `VIVO_POSE`.
  - The exporter runs it with `CABINA_CHOQUES=<prefix>` (writes `-entero.json` / `-diezmado.json`).
- `blender/cabina_choques_ver.py`: Workbench renders of the flagged faces. Env `VER_VISTAS`, `VER_SUFIJO`, `VIVO_POSE`; flag `sin_nuevas` hides the new parts.
- **Lamps:**
  - `luces_g63.separar()`, called from `escena.py` after `malla()`, cuts the model's lamp meshes (Light_Col, Material__544, Material__470) and `luces_g63` into 33 objects `luz_*`, named by role and side (`LUCES` in `luces_g63.py`). Montar log: `LUCES separadas 33`.
  - `blender/luces_leer.py` (read-back → `blender/props/luces.json` `fuera`) and the exporter hides the listed lamps (log: `VIVO luces fuera []`).
  - `blender/luces_blend.py` makes the owner's truck-only file. **Not run yet.**
  - Owner steps: `docs/luces-dueno.md`. No lamp was deleted. `luz_volante_*` are amber Light_Col faces on the wheel spokes, flagged as candidates to delete.
- **Roof:** `blender/vivo_normales.py soldar()` welds at 0.1 mm and marks sharp edges by angle before the decimate. It is wired into the exporter for `Material*` and `rueda*`.
- `blender/vivo.py`: `luz_*` is exempt from its decimate.
- `scripts/vivo-tomas.mjs`: new views `asiento_izq_lado`, `asiento_der_lado`, `tablero`, `techo`.
- **Builds:**
  - New montado: `/mnt/e/tmp/mto-cabina-restos/vivo/vivo-montado.blend` (montar.log there).
  - Export with weld and clash count: `vivo/crudo`, `vivo/pub`, `exportar.log`, `opt.log`. **Not copied to `public/vivo/` yet.**
  - Before live shots of alias 50042ca0, all views at 1440 and 390: `/mnt/e/tmp/mto-cabina-restos/antes-vivo/`.

## Fable (roof), 17:42
- Fable's pick: keep the weld, and give `Material3.004` (roof paint) 3× its share with `MAS = {"Material3.004": 3.0}` in the ratio. Total tris unchanged.
- Its other findings:
  - The mean-|diff| metric ranks as-shipped best, against the eye. Compare Sobel edge maps instead.
  - Mark the sharp edges after applying the decimate, not before. This likely explains the smeared tailgate.
  - Scale the weld distance by object scale, and print `soldar`'s vertex counts.
- None of this is adopted or measured yet.

## Next step (exact)
1. **Console:** read `ver-pose/*.png` and `choques-pose.json`.
   - Both are done (17:44): 6 renders. Totals at the owner's pose on the new montado: crossing 545, enclosed 1,274, floating 0, seen from outside 555.
   - Then pick:
     - (a) In the exporter, after `poner_pose()`, call `cabina_tripo.borrar_viejos(O["camion"], [seats, tripo_consola])` again. This cuts the stack around the owner's console. Recommended: it keeps his placement.
     - (b) Move or un-tilt the console. That changes the owner's placement, so ask cricketship first.
   - Bezel `Cube.081` crossing the stack: likely acceptable (flush mount). Name it as a survivor, or add it to the second removal pass.
2. **Roof:** try Fable's `MAS` weight and the sharp-after-decimate pass as variants, using the same 6-view loop.
   - Loop: `cabina_choques_ver.py ... diezmar=0.0985 soldar`, `VER_SUFIJO`. Diff script: scratchpad `dif.py` (move it to `scripts/` if kept).
   - Judge by eye on `techo` / `parada2` plus edge counts. Keep the variant that loses the facets and keeps the ribs.
3. **Re-export** with `CABINA_CHOQUES`. Target: crossing / enclosed / floating = 0, or each survivor named. The floor carpet the seats sink into (BAJA 8 cm) is the expected survivor.
   - Rebuild commands: scratchpad `montar.sh` / `exportar.sh` (copied below).
   - Then run `vivo-optimizar`, copy `pub/*.glb` + `crudo/vivo.json` to `public/vivo/`, run `bun run build`, then `npx wrangler versions upload --preview-alias vivo` (preview only).
4. Run `luces_blend.py` on the new montado → `E:\tmp\mto-cabina-restos\colocar-luces.blend` (the path the owner doc names).
5. **Checks:**
   - vivo-tomas on the new URL (draw calls ≤ 90).
   - TTFF Fast 4G 390, 3 runs, measured sequentially against 50042ca0 in the same session (`scripts/medir-vivo.mjs`). Must stay under 4 s.
   - `bun test`.
   - Before/after sheet: stops 1–4 plus `cabina_atras`, `hector_botella`, `manco_pies`, the seat-side views, `tablero`, `techo`.
6. Delete `blender/__pycache__/`, which this session created. Commit on `cc/brainrotdrone`, since earlier drones committed there. Do not merge, and do not deploy prod.
7. **Report:** ≤3 lines → `/home/black/.cache/cc-deck/reports/all/incognitodrone-1795129038.md`, then a SendMessage to `cricketship`. Format per the spec.

## Rebuild (as run)
```
OUT=/mnt/e/tmp/mto-cabina-restos/vivo; POD="$(wslpath -w blender/assets/asiento/pod-tripo-v31-c1.glb)"
GPU=0 CABINA_TRIPO=1 CABINA_TRIPO_CONSOLA=consola-tripo-v31-c2.glb PIEZA_CONSOLA_TECHO="$POD" MONTAJE_PANTALLA=a MONTAJE_PANTALLA_LUZ=ancha \
  MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta WSLENV=CABINA_TRIPO:CABINA_TRIPO_CONSOLA:PIEZA_CONSOLA_TECHO:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA \
  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 \
  --python "$(wslpath -w blender/vivo_secciones_montar.py)" -- "$(wslpath -w blender/escena.py)" "$(wslpath -w $OUT)" 1 all 960x540   # ~6 min
GPU=0 VIVO_POSE="$(wslpath -w /mnt/e/tmp/mto-live-catchup/pose-blend1.json)" CABINA_CHOQUES="$(wslpath -w /mnt/e/tmp/mto-cabina-restos/choques-despues)" \
  WSLENV=VIVO_POSE:CABINA_CHOQUES ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b --python-exit-code 1 "$(wslpath -w $OUT/vivo-montado.blend)" \
  --python "$(wslpath -w blender/vivo_secciones_exportar.py)" -- "$(wslpath -w $OUT/crudo)" "$(wslpath -w $OUT/vivo-montado.json)"   # ~8 min
GT=/home/black/projects/scratch-blender-skills bun scripts/vivo-optimizar.mjs $OUT/crudo $OUT/pub
```
Live shots: `PW='E:\tmp\pw-vivo\node_modules\playwright-core' CHROME='C:\Program Files\Google\Chrome\Application\chrome.exe' WSLENV=PW:CHROME node.exe "$(wslpath -w scripts/vivo-tomas.mjs)" <url> "$(wslpath -w <out>)"`.
A Blender job that renders must run without `GPU=0` (a hook enforces this). Waits go through `scripts/esperar.sh ... log <file> <regex>` in the background.

## gotchas (for visual-lab, report as `gotchas:` lines)
- Old soup faces on a removal box's edge survived a "wholly inside" test → test the face centre with a small margin across the edge axis, and cap the box below the headliner.
- The cab clash count read 0 on the montado but 1,266 live → the exporter moves the console to the owner's matrix after the removal; measure inside the exporter, as shipped.
- Decimate on triangle soup flattened the roof's ribs into big triangles → weld first; a DataTransfer of custom normals from the full copy made it worse.
- Pixel mean |diff| against the full mesh ranked the faceted decimate best → compare edge maps (Fable).
- A hook blocks system python3 when the command line contains "numpy" anywhere → split the edit and the uv run into separate calls.

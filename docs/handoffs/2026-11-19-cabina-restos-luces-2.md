# Handoff: cab leftovers + lamps, part 2 (brainrotdrone, 2026-11-19 19:45, stopped at the context cap)

Seed spec: `~/projects/mothership/docs/queue/2026-11-19-mto-cabina-restos-luces-2.md` (read it). Its parent spec and the part-1
handoff `docs/handoffs/2026-11-19-cabina-restos-luces.md` still apply (constraints, done-check, report format).
Branch `cc/brainrotdrone`. **Nothing is committed yet**; everything below is in the work tree. Report file:
`/home/black/.cache/cc-deck/reports/all/brainrotdrone-1795134641.md` (not written yet), then SendMessage `cricketship`.

## Decisions (made, don't reopen)
- Console: option (a). The exporter re-runs `cabina_tripo.borrar_viejos` after `poner_pose()` (seats + console). Bezel `Cube.081`/`Plane.016` left out of the pass on purpose: flush mount, named survivor.
- Roof: weld without pre-marked sharp edges, decimate, then sharp by angle 30° after it (`vivo_normales.afilar`, Smooth by Angle modifier); `MAS = {Material3.004: 3, rueda0-5: 0.6}` at the same total.
  - Sobel edge F1 vs the full mesh, 6 outside views: as shipped 0.928 (15,460 spurious px) → 0.952 (6,043).
  - Variants rejected: MAS only 0.927; sharp-after only 0.934 (both roll-bar tubes flattened); 50° 0.935. Renders + sheets: `/mnt/e/tmp/mto-cabina-restos/techo3/` (hoja*.png).
  - Known cost: the roll-bar tubes shade faceted (30° marks every edge of a low-poly tube). Named survivor.
- Cast (cricketship 18:48 + 18:49, owner "go all out"): `FIG = 150000` per figure, plain decimate (was 40000).
  - A Decimate vertex group does NOT protect: the group marks where to collapse, and with invert, factor 10, the head kept 141 k and the body went to ~50 tris. Removed.
  - In Blender, Diego's face reads clean even at 40 k (textured, flat light: `/mnt/e/tmp/mto-cabina-restos/caras/hoja-*-tex.png`). The live facets were probably silhouette + strong light. Judge on the live close-up.
- Seats: their own decimate, `ASIENTO = 9000` each, on top of the truck budget (were 47,944 → 4,721 at the common ratio). The 4.7 k render shows white torn shards, 9 k doesn't, 14 k adds little (`/mnt/e/tmp/mto-cabina-restos/asientos/`). Their normal map is unlinked before export (baked for 48 k; without tangents, three shades it per triangle).
- Stickers (owner shot 5, white tailgate blobs): calca3 materials mix front art / white backing by Backfacing, and the glTF exporter shipped the backing (white RGB + art alpha). The exporter now links the front shader to the output (84 `c3_*` materials). Verified: the new glb's textures carry the art.
- Tail lamps (shot 5, smeared red): `luz_calavera_*` sat 1.7 mm behind the decimated dark surround (Material3.001). Moved 5 mm out (-y). Lamp-first ray share over the lamp box: 30.9/32.0 % → 48.0/48.0 % (`calaveras_glb.py`).
- Roof pod (cricketship 18:58): `u_consola_techo*` squashed ×0.6 in z, top kept on the roof (z 2.192). It must appear at stop 1 in the before/after sheet.
- Opening clip (cricketship 18:58): `public/prototipo/apertura.mp4` is now 12.0 s, 692 KB: the old 6.54 s previz plus its last frame held (`tpad`, crf 20). `apertura-f0.jpg` was re-extracted from frame 0.
  - All 157 original frames match (PSNR ≥ 44.96 dB). eagle.sh exit 0. Its extra "jump" events (f84/114/134/147) are revisar's baseline shifting over the 5.5 s still tail: the original shows only f17.
- Don't touch hats (cricketship).

## State of the build
- Export 1 (all of the above, **without** the headrest boxes) is published: preview version `f43eb992`, alias https://vivo-mafiatumbada.bube-ncio8.workers.dev. `public/vivo/*` holds it.
  - vivo-tomas on it: `/mnt/e/tmp/mto-cabina-restos/despues-vivo/`. Page errors 0, max draw calls 85 (parada2, caja_arriba).
  - Before shots of 50042ca0: `/mnt/e/tmp/mto-cabina-restos/antes-vivo/`.
- Tris and bytes per glb, before (50042ca0) → after (f43eb992):
  - escena: 149,135 tris / 1,857,004 B → 145,464 / 1,993,100. The extra bytes are mostly the stickers' colour art.
  - reparto: 155,198 / 1,284,492 → 582,000 / 3,338,288.
  - mundo: 18 / 478,504 → same.
- Clash counts as shipped (decimated), before → after export 1:
  - Crossing 120 → 52. Survivors: carpet under the seats 20 (BAJA, expected); console vs stack 14; bezel `Cube.081`/`Plane.016` 12 (flush); pod vs headliner 3; seats vs plastic 4.
  - Enclosed 100 → 0.
  - Floating 21 → 12 (cab_piel / plastico re-cut by the decimate at cabina_atras, manco_pies, parada1).
- **Found after export 1** (live shot `banda-diego`, crop `/mnt/e/tmp/mto-cabina-restos/ab-diego-crop.png`): pale flat planes over the front seats, behind Héctor's cap and at the B-pillar.
  - Raycast through the glass on the shipped glb (`ident.py`): `Material3.001 plastico` at z 1.89–1.99, x 1.24–1.37 and 2.11–2.20, y 0.17–0.28.
  - These are the old headrests and backrest tops above the seat boxes' 1.88 cap: ~270 cab_piel + ~350 plastico faces at z 1.88–2.03 (`tope.py`). This is the owner's "old cab around Diego reads as shredded facets".
  - **Fix written, not yet exported:** `cabina_tripo.CAJAS` gains `cabecera_izq/der` (z 1.88–2.03, y 0.05–0.60, 3 cm off the door side), and `zona_vieja(c, mat)` skips them for the headliner `cab_techo`. The exporter's second pass applies it.
- TTFF loop running (`/mnt/e/tmp/mto-cabina-restos/scripts/ttff.sh` → `/mnt/e/tmp/mto-cabina-restos/ttff/<ver>-<n>/log.txt`). **Done (3 sequential runs each):** 50042ca0 3,943 / 3,914 / 3,921 ms (median 3.92 s); f43eb992 3,985 / 4,002 / 3,963 ms (median 3.99 s, one run over 4 s). Bytes total 5.98 → 8.17 MB (the heavier reparto included). This is a fail-in-waiting: cut the sticker textures (512 → 256 webp, most stickers sit far from the cameras) in the re-export, then remeasure. Step 1 below is done. The limit is 4 s, and escena grew 136 KB, so this may fail. If it does, cut sticker texture size (they're 512 webp; most stickers sit far from the cameras) before anything else.
- Owner lamp file built: `E:\tmp\mto-cabina-restos\colocar-luces.blend` (86 objects, 33 lamps). Owner steps: `docs/luces-dueno.md`.

## Next step (exact)
1. Read the TTFF results in `/mnt/e/tmp/mto-cabina-restos/ttff/*/log.txt` (`"ttff_ms"`), 3 per version. If the loop died with the session, rerun `bash /mnt/e/tmp/mto-cabina-restos/scripts/ttff.sh` after deleting its first line (the wait on a dead task id).
2. Re-export with the headrest boxes:
   - Run `bash /mnt/e/tmp/mto-cabina-restos/scripts/exportar2.sh` (~10 min, background, wait with `scripts/esperar.sh log /mnt/e/tmp/mto-cabina-restos/vivo/exportar.log "VIVO listo"`). It also runs vivo-optimizar.
   - Check `CABINA_TRIPO borradas` for `cabecera_*` counts and the `CHOQUES diezmado totales`.
3. Copy `vivo/pub/*.glb` + `vivo/crudo/vivo.json` to `public/vivo/`, then `bun run build`, `bun test` (125 pass before), then `npx wrangler versions upload --preview-alias vivo` (preview only, never deploy prod).
4. vivo-tomas on the alias into `/mnt/e/tmp/mto-cabina-restos/despues-vivo2/`. Command: the part-1 handoff's "Live shots" line.
   - Look at `banda-diego` (planes gone?), `banda-hector`, `cabina_atras`, `parada1` (pod squash, the two reading lenses), `parada2` (stickers, lamps).
   - If the pale planes persist, raycast again with `scripts/ident.py <glb> x <px,py>...`.
5. TTFF 3 runs on the new version (edit the version ids in `ttff.sh`). Must stay < 4 s.
6. Before/after sheet:
   ```
   uv run -q --with pillow python -I /mnt/e/tmp/mto-cabina-restos/scripts/hoja.py \
     /mnt/e/tmp/mto-cabina-restos/antes-vivo /mnt/e/tmp/mto-cabina-restos/despues-vivo2 /mnt/e/tmp/mto-cabina-restos/hoja-antes-despues.jpg \
     parada1,parada2,parada3,parada4,cabina_atras,hector_botella,manco_pies,asiento_izq_lado,asiento_der_lado,tablero,techo,banda-diego,banda-hector
   ```
7. Delete `blender/__pycache__/` if present. Commit on `cc/brainrotdrone`: all files listed by `git status` except `node_modules` and `blender/assets/*` (untracked, large, licensed). Include `public/prototipo/*` and both handoffs. Don't merge, don't deploy prod.
8. Report (≤3 lines + `paths:` line + tris/bytes line + `model: opus effort: high` + `verdict:`) to the report file above, then SendMessage `cricketship` one line pointing at it.

## Open / survivors to name in the report
- Roll-bar tubes shade faceted (30° sharp-after). Bezel and console crossings are flush mounts. Carpet under the seats.
- Diego's face: confirm on the live close-up after the re-export. If it is still faceted at 150 k, the cause is not the tri count (see Decisions).
- The tripo_material_1f145… (escena; probably the pod) also has a normal map. Not decimated, so left as is.

## Scripts (copied durable: `/mnt/e/tmp/mto-cabina-restos/scripts/`)
- `exportar2.sh` export + optimize.
- `ttff.sh` old/new TTFF.
- `hoja.py` sheet.
- `bordes.py` Sobel edge compare.
- `calaveras_glb.py` lamp-first check.
- `ident.py` raycast pixels on a glb.
- `tris.mjs` / `mats.mjs` / `normales.mjs` / `nm.mjs` / `tex.mjs` glb inspectors (run with `GT=/home/black/projects/scratch-blender-skills bun <script> <glb>`).
- `caras*.py` / `asientos.py` / `tope.py` Blender probes on the montado.
- Repo changes: `blender/vivo_secciones_exportar.py`, `vivo_normales.py` (soldar marcar=, razones, afilar), `cabina_choques.py`/`cabina_choques_ver.py` (diezmar mas=/despues/ambos, pesos), `cabina_tripo.py` (cabecera boxes).

## gotchas (for visual-lab, report as `gotchas:` lines)
- Decimate on one material inside a G63 soup let its triangles poke through an undecimated lamp 1.7 mm in front of it → move the lamp object a few mm out; measure the lamp-first ray share on the shipped glb.
- glTF export of a Mix Shader (front / back by Backfacing) ships the second branch (white backing with the art's alpha) → link the front Principled to the output before export.
- Decimate modifier vertex group: weight marks where to collapse; inverted at factor 10 it froze the head and collapsed the body to ~50 tris → use separate budgets, not a vertex group, to favour a region.
- Smooth by Angle after the decimate (30°) makes low-poly tubes shade faceted, while sharp marks before the decimate kept them round but smeared flat panels → judge both by Sobel edge F1 plus the eye on the tubes.
- Tripo normal maps on a decimated mesh shade per triangle in three.js (no tangents) → drop the normal map when decimating hard.
- revisar.sh "jump" events grow when a held still tail is appended (its baseline shifts) → compare against the source clip's events, plus PSNR per frame.
- A hook denies any Bash line that contains both `python3` and `numpy` (even inside a heredoc writing a script) → write the file and run uv in separate calls.

Read /mnt/e/Cursor Projects/MTO-brainrotdrone/docs/handoffs/2026-11-19-cabina-restos-luces-2.md and continue.

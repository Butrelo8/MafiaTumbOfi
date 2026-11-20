# Handoff: new roof load rebuilt and uploaded (copingdrone, 2026-11-20 ~08:55)

Continues `2026-11-20-carga-nueva.md`. Branch `cc/copingdrone` (ff-merged `cc/chilldrone` first). Nothing pushed, prod untouched.

## Preview
`https://vivo-mafiatumbada.bube-ncio8.workers.dev` = version `ef2e5453` (earlier tries: `e626ec97` and `7598cf53` were missing git-ignored files, see gotchas). Sheet: `E:\tmp\mto-carga-copingdrone\hoja-carga-vivo.jpg`; shots `E:\tmp\mto-carga-copingdrone\tomas2\`.

## Numbers
```
rack checks   rope vertices inside any piece 0 (7 pieces); no net above any alien vertex; gap alien-net 1.67 cm; straps 5.9 mm from the alien, 45 vertices within 12 mm, 0 inside; overlaps none
sizes         escena.glb 1,692,856 B (first-frame file, unchanged)   camion_extras.glb 1,146,816 B (was 576,304); its textures 378 KB (atlas 1024 webp 107 KB)
page          errors 0; draw calls stop 1 (parada1) 78 at 1440 and 390; Caja (parada2) 82 at 1440, 93 at 390
TTFF Fast 4G  abba91a3 (same first-frame file): 4766 4704 4453 and 4364 4545 4784 ms, median ~4.6 s
              baselines the same minutes: 8db7f25c 6029 5659 5601; bf7e4a6c (3.8-4.0 s last night) 4734 4428 4724
```
TTFF is over the 4 s cap on this machine today, as the version that measured under the cap last night is (bf7e4a6c, same escena.glb size within 112 B). The load is in camion_extras.glb, loaded after the first frame, so it does not move TTFF; the cap needs the first-frame file to shrink or a quieter machine.

## What changed
- `blender/g63_rack.py`: donut + alien from the PROPS glb, the rest from `g63_carga.traer()` + `calcas()`; the dump is now required (3rd arg); net and alien straps via `g63_carga.tender`; prints `G.medir`. Old `colocar_carga`, `red`, `hexcuerda` removed.
- `blender/g63_red_ajustar.py` rewritten on `g63_carga.tender`.
- `blender/g63_carga.py`: bug fix, `traer()` tested a stale loop variable so the guitar cases stayed white (stickers' white border vanished); now coloured, and an assert stops the build if not.
- `scripts/vivo-optimizar.mjs`: `calcas_atlas` alphaMode MASK 0.5 (set before `aplanar`, which would otherwise flatten the mostly-transparent atlas), atlas kept at 1024.
- `scripts/vivo-g63.sh`: `OLD` and `VOLCADO` defaults point at the new bake and dump; `SALTAR1=1` reuses `g63-listo.blend` (the source `g63.blend` is git-ignored and absent in this worktree).
- `blender/props/g63_paradas.json`: cast shift 0.
- `docs/g63-nuevo-dueno.md`: "Cosas del techo" and the object table.

## Not done
Stop cameras (`g63_paradas.json` banda/cabina) not moved to the new heads. `colocar-g63-carga.blend` (his file, untouched) was built with the guitar-colour bug, so its guitar cases are white there; rebuild it with `colocacion_g63_carga.py` if he should see the colours.

## gotchas
- Fresh worktree: git-ignored files are absent (prepared load pieces, `public/vivo/draco/`, six static scene glbs, `node_modules`) -> pieces regenerate with `carga_texturas.py`, `carga_atlas.py`, `carga_preparar.py`; draco and the static glbs were taken byte-for-byte from the baseline preview URL; `bun install --frozen-lockfile`. Missing draco files show as a 404 plus a page that never reaches `__vivo.cargado`, not as an obvious error.
- `for ... in pendientes` reading a variable set by an earlier loop ran the guitar colouring never -> carry the key in the tuple.
- TTFF drifts ~0.8 s between sessions on this machine: always interleave with a known version.

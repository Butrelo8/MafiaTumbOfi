# Handoff: Tripo console and roof pod live, mirror rosettes out (uncdrone, 2026-11-19 04:50)

Spec: `~/projects/mothership/docs/queue/2026-11-19-mto-tripo-console-lightbar.md`. Branch `cc/brainrotdrone`, commits d7afb4d
(mirror) and 2f0c202 (Tripo parts). Preview only; nothing merged or deployed to production.

## Preview
- Version: https://50042ca0-mafiatumbada.bube-ncio8.workers.dev/
- Alias: https://vivo-mafiatumbada.bube-ncio8.workers.dev/ (now this version)
- Before: https://9a1c28d3-mafiatumbada.bube-ncio8.workers.dev/

## What the owner's circles were
- **48.png, top circle:** this was not an exterior roof light bar. It was the overhead axle-lock / tyre-pressure pod over the
  windshield (`consola_techo`, kiln-built from ref r04: three gauges, four yellow knobs, two red levers). Under it sat the two
  reading-lamp lenses (`luces_g63`, `g63_cabina`, y 0.78). Projecting the pod's box into the stop-1 camera lands on the circled
  bar.
- **48.png, bottom circle:** the Tripo console (tripo3, 49 k tris). The exporter's common decimate ratio (0.094) cut it to
  4.6 k tris of shreds.
- **49.png, mirror:** `props_placement.monos()` (P7, ref [13]): white satin rosettes, four tori plus two 0.40 m tails, on both
  outside mirrors. It was added 2026-11-13 (d4316ca) and was the owner's pp6-b pick ("two rosettes"). It reached the live scene
  with the spike 8f4b7a0 (2026-11-18), because the exporter takes all of scene 6's dressing. Live, it read as a ridged ball on a
  stick. It is no G63 part, so it is hidden in the exporter by material (`pp_satin`); the Cycles stills keep it. To bring it
  back, delete those 4 lines in `vivo_secciones_exportar.py`.

## Tripo
- Credits: 160 (4 × 40). Balance 605 → 445. Model v3.1-20260211 with texture_quality=detailed. P2, the CLI default, was
  110 per job.
- These jobs ran before saltyship's "do not spend" message (04:14). Nothing was spent after it.
- Inputs: local FLUX 3 Klein edits (`preset_edit_flux3`, seeds 1–2) of r04 and r01 into isolated product shots on white.
  - Pod: seed 2. Its box depth and its rail wrapping the face follow r04.
  - Console: seed 1. One clean part; seed 2 grew hanging cupholders.
- Inputs and raw outputs: `/mnt/e/tmp/mto-tripo-consola/` (`ref/`, `tripo-pod/`, `tripo-consola/`, `vistas/`).
- Picks:
  - **pod c1:** its knobs keep r04's arrows; c2's lost them.
  - **console c2:** c1 has garbled fake lettering on its rear face.
  - The spares are in `blender/assets/asiento/` (untracked; provenance in its LICENSE.txt).

## Verdict per part (sheet: `tmp/tripo-consola/hoja-antes-despues.jpg`; candidates: `tmp/tripo-consola/hoja-candidatos.jpg`, `vistas-candidatos.jpg`)
- **Console: Tripo wins.** At 5.6 k tris and undecimated, it reads as an armrest, an alu deck and a rotary knob, where before
  it was shreds. Its box sits within 1 cm of the old one, under the owner's matrix (`cabina.json` `consola`, applied in the
  exporter).
- **Pod: Tripo wins on likeness, with one trade-off.**
  - It has r04's rail, gauges, yellow knobs and red levers, where the kiln build had a different layout and no rail.
  - It is 0.129 m tall against the kiln's 0.07. From the stop-1 camera it hides the two reading-lamp lenses behind it. Their
    positions are unchanged.
  - The real cab is the same: in r04 the lamp unit sits behind and above the pod.
  - If the owner wants the lenses visible, either squash the pod vertically (about ×0.6, at the cost of oval gauges) or go
    back to the kiln pod (unset `PIEZA_CONSOLA_TECHO`). Either is a 13-minute rebuild.
- I built no separate procedural console: the old procedural G63 console is the one cabina_tripo removes by volume, and the
  Tripo console it was replaced by is what was shredding.

## Numbers
```
                         before 9a1c28d3      after 50042ca0
draw calls max           88                   85      (vivo-tomas, 36 shots, 1440 + 390; every changed shot -3)
stop 1 / 2 / 3 (1440)    62 / 88 / 45         59 / 85 / 45
page errors              0                    0       (vivo-tomas + 3 medir-vivo runs)
TTFF Fast 4G 390         3.75 s median (cricketdrone)   3.92 s median (3906 / 3920 / 3996), bytes 5.98 MB both
escena.glb               1.862 MB             1.857 MB
console tris live        4662 (decimated)     5572 (exempt)     pod 686 (5 materials) -> 1766 (1 material)
bun test                 125 pass             125 pass
```
TTFF moved 170 ms with the same total bytes. My guess is network variance between the two sessions; I did not check it. It is
still under the 4 s target.

## Rebuild
```
OUT=/mnt/e/tmp/mto-tripo-consola/vivo
POD="$(wslpath -w blender/assets/asiento/pod-tripo-v31-c1.glb)"
GPU=0 CABINA_TRIPO=1 CABINA_TRIPO_CONSOLA=consola-tripo-v31-c2.glb PIEZA_CONSOLA_TECHO="$POD" MONTAJE_PANTALLA=a \
  MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta \
  WSLENV=CABINA_TRIPO:CABINA_TRIPO_CONSOLA:PIEZA_CONSOLA_TECHO:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA \
  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 \
  --python "$(wslpath -w blender/vivo_secciones_montar.py)" -- "$(wslpath -w blender/escena.py)" "$(wslpath -w $OUT)" 1 all 960x540
# then export (VIVO_POSE) and vivo-optimizar exactly as in 2026-11-19-vivo-catchup.md › Rebuild; mkdir $OUT/pub first
```
Pod from a raw Tripo file: `blender/tripo/pod_contrato.py -- <raw.glb> <out.glb> 0 0 -90 40`. The raw file's face is +X with
its long side on Y, and it leans about 15° back, so incl 40 nets about 25° down.

## Open
- Reading-lamp lenses hidden by the taller pod at stop 1 (above).
- The kiln cupholder (`portavasos`) is still placed by a ray onto the console as built, before the owner's console matrix. I
  have not checked whether it now floats over the new console's deck. Close-up view: `cabina_atras` in vivo-tomas.

## gotchas (for visual-lab)
- Tripo image_to_model returned its longest side on glTF Z, not X -> read the axes from a four-view render of the raw GLB before scaling; scaling by the x extent made the pod 1.2 m long.
- A Tripo part looked shredded only live -> the exporter's common decimate ratio hit it; ask Tripo for face_limit at the live budget and exempt the part by name with a tri cap, so a heavy fallback can't ship whole.
- The tripo CLI defaults to P2 at 110 credits/job -> `--model tripo-v3.1 -p texture_quality=detailed` costs 40; check with `--dry-run` (free) first.
- A clean image-to-3D input from a cluttered car-interior photo -> FLUX 3 Klein edit ("show only X as a standalone product photo on white", listing exact counts) held r04's counts: three gauges, four knobs, two levers.

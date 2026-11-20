#!/usr/bin/env bash
# Live scene with the owner's new G63 (2026-11-20): the whole chain from the .blend to public/vivo/, run as one.
#   scripts/vivo-g63.sh [out dir = /mnt/e/tmp/mto-g63-nuevo]
# 1 g63_nuevo.py   blender/assets/g63-nuevo/g63.blend -> g63-listo.blend   (scale, wheels, web materials; ~1 min)
# 2 g63_rack.py    + roof rack, the band's load, the net                      (-> g63-rack.blend)
# 3 vivo_g63_montar.py  + cab dressing, headlamps, wheel radius              (-> vivo-g63.blend, -datos.json)
# 4 vivo_g63_exportar.py  -> coche.glb (uncompressed)
# 5 vivo-g63-unir.mjs   swaps it into the exporter's crudo files (cast, screen truck, cerros stay; the cast moves by
#                       blender/props/g63_paradas.json `cast`), writes vivo.json
# 6 vivo-optimizar.mjs  -> pub/*.glb, then copied to public/vivo/ with vivo.json
# The crudo files (OLD=/mnt/e/tmp/mto-cabina-restos/vivo/crudo) come from the old exporter on the old montado; once the owner has placed
# the cast in the new car's file (docs/g63-nuevo-dueno.md): blender/vivo_reparto_volcar.py on his file -> VIVO_POSE -> the old exporter
# (docs/handoffs/2026-11-19-cabina-restos-luces.md "Rebuild") -> a new OLD crudo, set `cast` to 0 in g63_paradas.json, rerun step 5-6.
# Each Blender step is one blender-run job; waits go through scripts/esperar.sh. Run this with run_in_background.
set -euo pipefail
cd "$(dirname "$0")/.."
D=${1:-/mnt/e/tmp/mto-g63-nuevo}
OLD=${OLD:-/mnt/e/tmp/mto-cabina-restos/vivo/crudo}
PROPS=${PROPS:-/mnt/e/tmp/mto-cab-consola-luces/pub0/escena.glb}  # a live escena.glb: the k3_* props and the dressing come from it
export GT=${GT:-/home/black/projects/scratch-blender-skills}
B=/mnt/e/Blender/blender.exe
run() { ~/.claude/scripts/blender-run $B -b "$(wslpath -w "$1")" --python-exit-code 1 --python "$(wslpath -w "blender/$2")" -- "${@:3}"; }
mkdir -p "$D"
run blender/assets/g63-nuevo/g63.blend g63_nuevo.py "$(wslpath -w "$D/g63-listo.blend")" > "$D/1-listo.log" 2>&1
run "$D/g63-listo.blend" g63_rack.py "$(wslpath -w "$D/g63-rack.blend")" "$(wslpath -w "$PROPS")" red > "$D/2-rack.log" 2>&1
run "$D/g63-rack.blend" vivo_g63_montar.py "$(wslpath -w "$D/vivo-g63.blend")" "$(wslpath -w "$PROPS")" > "$D/3-montar.log" 2>&1
run "$D/vivo-g63.blend" vivo_g63_exportar.py "$(wslpath -w "$D/coche.glb")" > "$D/4-exportar.log" 2>&1
bun scripts/vivo-g63-unir.mjs "$OLD" "$D/coche.glb" "$D/vivo-g63-datos.json" "$D/crudo" > "$D/5-unir.log" 2>&1
mkdir -p "$D/pub"
bun scripts/vivo-optimizar.mjs "$D/crudo" "$D/pub" > "$D/6-optimizar.log" 2>&1
cp "$D/crudo/vivo.json" public/vivo/vivo.json
cp "$D/pub/"*.glb public/vivo/
echo "VIVO-G63 listo: $(ls -l public/vivo/escena.glb | awk '{print $5}') bytes escena.glb"

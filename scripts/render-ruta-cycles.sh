#!/usr/bin/env bash
# Cycles night render of the run (frames 0-1103) and the band loop (1127-1607; 1607 = the wrap check, not encoded) for /prototipo,
# 640x360, 64 spp (16/32 smear the faces behind the windshield), then the two mp4s and their first-frame posters in public/prototipo.
# Both clips use the same scene settings (RUTA_PERIODOS=9) so the run -> loop handover frames match.
# Usage: scripts/render-ruta-cycles.sh <out dir (WSL path)>     about 1.5 s/frame to build and 2.0 s/frame to render: ~45 min on the RTX 4070 Ti.
# Run ~/.claude/scripts/gpu-busy --for blender first, in its own command. For a 24-frame sample, edit the two render lines below.
set -eu
cd "$(dirname "$0")/.."
OUT=${1:?uso: render-ruta-cycles.sh <out dir>}; SPP=${SPP:-64}
export MONTAJE_PANTALLA=b MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta RUTA_PERIODOS=9 RUTA_PASO_ASOM=1000
export WSLENV=RUTA_PERIODOS:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA:RUTA_PASO_ASOM:RUTA_DESDE:RUTA_HASTA
render() {  # render <name> <from> <to>
  mkdir -p "$OUT/$1"
  RUTA_DESDE=$2 RUTA_HASTA=$3 /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/ruta.py)" -- \
    "$(wslpath -w blender/escena.py)" "$(wslpath -w "$OUT/$1")" "$SPP" ruta 640x360 > "$OUT/$1/build.log" 2>&1
}
render bucle 1127 1607
render ruta 0 1103
enc() {  # enc <name> <first frame> <frames> <keyframe interval>
  ffmpeg -v error -y -framerate 24 -start_number "$2" -i "$OUT/$1/cuadros/%04d.png" -frames:v "$3" -c:v libx264 -preset slow -crf 26 \
    -pix_fmt yuv420p -g "$4" -keyint_min "$4" -sc_threshold 0 -movflags +faststart -an "public/prototipo/$1.mp4"
}
enc bucle 1127 480 4
enc ruta 0 1104 3
ffmpeg -v error -y -i "$OUT/bucle/cuadros/1127.png" -q:v 4 public/prototipo/bucle-f0.jpg
ffmpeg -v error -y -i "$OUT/ruta/cuadros/0000.png" -q:v 4 public/prototipo/ruta-f0.jpg

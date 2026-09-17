#!/usr/bin/env bash
# PNG de Blender -> AVIF + src/data/scene.json.
#
# Entrada:  tmp/frames/{movil,escritorio}/{tramo-N/NNN.png,estacion-N.png}
# Salida:   public/scene/{mobile,desktop}/... y src/data/scene.json
#
# El CRF viene medido, no estimado: ver "CRF calibrado contra AVIF real" en
# docs/blender-notas.md. 38 para los tramos, 30 para las estaciones, que son
# las que pintan el LCP y tienen presupuesto de sobra.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ORIGEN="$RAIZ/tmp/frames"
DESTINO="$RAIZ/public/scene"
CRF_TRAMO=38
CRF_ESTACION=30

avif() {   # <png> <avif> <crf>
  ffmpeg -y -loglevel error -i "$1" -c:v libaom-av1 -still-picture 1 \
         -crf "$3" -cpu-used 6 "$2"
}

declare -A CARPETA=( [movil]=mobile [escritorio]=desktop )

for formato in movil escritorio; do
  salida="$DESTINO/${CARPETA[$formato]}"
  for tramo in "$ORIGEN/$formato"/tramo-*; do
    [ -d "$tramo" ] || continue
    mkdir -p "$salida/$(basename "$tramo")"
    for png in "$tramo"/*.png; do
      avif "$png" "$salida/$(basename "$tramo")/$(basename "${png%.png}").avif" "$CRF_TRAMO"
    done
  done
  mkdir -p "$salida"
  for png in "$ORIGEN/$formato"/estacion-*.png; do
    [ -f "$png" ] || continue
    avif "$png" "$salida/$(basename "${png%.png}").avif" "$CRF_ESTACION"
  done
done

python3 "$RAIZ/scripts/scene-json.py"

echo "build-scene: listo"
du -sh "$DESTINO"/*

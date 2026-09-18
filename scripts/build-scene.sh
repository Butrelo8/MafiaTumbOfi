#!/usr/bin/env bash
# PNG de Blender -> AVIF + src/data/scene.json.
#
# Entrada:  tmp/frames/{movil,escritorio}/{tramo-N/NNN.png,estacion-N.png,
#           estacion-N-relampago.png,estacion-N-frente.png}
# Salida:   public/scene/{mobile,desktop}/... y src/data/scene.json
#
# El CRF viene medido, no estimado: ver "CRF calibrado contra AVIF real" en
# docs/blender-notas.md. 38 para los tramos, 30 para las estaciones, que son
# las que pintan el LCP y tienen presupuesto de sobra.
#
# Las capas de frente van en WebP y no en AVIF: medido el 2026-09-17, el ffmpeg
# de este equipo descarta el canal alfa con libaom-av1 y devuelve la imagen
# opaca. Con libwebp lo conserva. No hay avifenc ni cwebp instalados.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ORIGEN="$RAIZ/tmp/frames"
DESTINO="$RAIZ/public/scene"
CRF_TRAMO=38
CRF_ESTACION=30
Q_CAPA=72          # la capa de frente es casi toda transparente

avif() {   # <png> <avif> <crf>
  ffmpeg -y -loglevel error -i "$1" -c:v libaom-av1 -still-picture 1 \
         -crf "$3" -cpu-used 6 "$2"
}

# La capa de frente NO se encodea tal cual. Su RGB se descarta y se queda sólo
# su alfa, que se pega sobre los píxeles del frame plano de la misma estación.
#
# El motivo está medido (2026-09-17): la capa se renderiza con la niebla del
# mundo desconectada —si no, el volumen llena el alfa entero— y sin esa niebla
# los mismos objetos salen hasta un 19% más oscuros que en el frame plano. Al
# fundir la capa se veía oscurecer las columnas. Recortando el frame plano con
# el alfa de la capa, componer la capa sobre su estación devuelve la estación
# original por construcción, y no hay nada que compensar a mano.
capa() {   # <png-plano> <png-frente> <webp> <calidad>
  ffmpeg -y -loglevel error -i "$1" -i "$2" \
         -filter_complex "[1:v]format=rgba,alphaextract[a];[0:v]format=rgb24[c];[c][a]alphamerge" \
         -c:v libwebp -q:v "$4" "$3"
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
    base="$(basename "${png%.png}")"
    case "$base" in
      *-frente)
        plano="${png%-frente.png}.png"
        [ -f "$plano" ] || { echo "capa sin su estacion: $png" >&2; exit 1; }
        capa "$plano" "$png" "$salida/$base.webp" "$Q_CAPA" ;;
      *) avif "$png" "$salida/$base.avif" "$CRF_ESTACION" ;;
    esac
  done
done

python3 "$RAIZ/scripts/scene-json.py"

echo "build-scene: listo"
du -sh "$DESTINO"/*

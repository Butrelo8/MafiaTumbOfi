#!/usr/bin/env bash
# Video del hero: tomas de dos videos del canal de la banda, mismo color, sin audio.
#
# Fuentes (no se versionan; se bajan una vez a tmp/hero/src):
#   S  Tal Vez — Good Luck Sessions   https://www.youtube.com/watch?v=7Sx0yDjGoq0  3840x1728
#   L  En vivo Plaza Lerdo, Xalapa    https://www.youtube.com/watch?v=XxhXFo-hm-I  3840x2160,
#      con franjas negras: lo activo es 3840x1904 desde y=128
#   yt-dlp -f "bv*[height<=2160]" -o "tmp/hero/src/%(id)s.%(ext)s" <url>
#
# Salida en public/video/:
#   hero.av1.mp4 (1080p)  hero.mp4 (720p)  horizontal (escritorio)
#   hero-v.av1.mp4        hero-v.mp4       vertical 720x1280 (móvil)
#   hero-poster.jpg
#
# Sólo los tres integrantes del roster actual (src/data/members.ts) salen en
# primer plano: el bajista de la sesión ya no toca con ellos (2026-10-04).
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=tmp/hero/src
OUT=public/video
TMP=tmp/hero/build
S=$SRC/7Sx0yDjGoq0.mkv
L=$SRC/XxhXFo-hm-I.mkv

# fuente inicio duración centro-x (0–1 del cuadro 16:9; lo usa el recorte vertical)
TOMAS=(
  "S 107.6 2.0 0.52"   # dúo en el círculo rojo, todo negro alrededor
  "S 197.2 1.5 0.50"   # Héctor con el micro vintage
  "L 460.9 2.0 0.46"   # Héctor en la plaza, primer plano
  "L 271.5 2.5 0.50"   # la plaza llena con el palacio
  "L 326.0 1.5 0.40"   # Héctor con el brazo arriba
  "S 34.0  2.0 0.50"   # guitarra acústica (suéter verde); corta en ~36.5
  "L 43.0  1.5 0.50"   # plaza llena; corta en ~44.8
  "S 145.8 3.0 0.50"   # Héctor y el de la chamarra en el círculo; se apaga a negro
)

# Look con el kit de LUTs del repo de Resolve (luts/README.md): balance por
# fuente → verdes de las camisetas de la selección apagados → Kodak 2383 (print)
# al 50% → negro levantado al 2% (el negro puro hace bloques al comprimir) →
# viñeta. Sin grano: el códec no lo comprime.
KIT="/mnt/e/Cursor Projects/Davincy Resolve/luts/terceros/film/print/kodak_2383_constlclip.cube"
LOOK="huesaturation=colors=g+c:saturation=-0.8,split[o][l];[l]lut3d=file='$KIT':interp=tetrahedral[l2];\
[o][l2]blend=all_mode=normal:all_opacity=0.5,curves=master='0/0.02 0.5/0.48 1/0.96',vignette=PI/5"
BAL_S="colorbalance=bs=-0.06:gs=-0.03:rs=0.02"   # quita la sombra verde-azulada del set
BAL_L="eq=brightness=-0.06:gamma=0.85"           # la plaza es muy blanca

# recorte <fuente> <centro-x> <horizontal|vertical> → filtro crop
recorte() {
  local alto y x16 w16
  if [[ $1 == S ]]; then alto=1728; y=0; w16=3072; x16=384; else alto=1904; y=128; w16=3385; x16=228; fi
  if [[ $3 == horizontal ]]; then echo "crop=$w16:$alto:$x16:$y"; return; fi
  local w=$(( alto * 9 / 16 / 2 * 2 ))
  local x; x=$(python3 -c "print(max(0, min(3840 - $w, round($x16 + $2 * $w16 - $w / 2))))")
  echo "crop=$w:$alto:$x:$y"
}

corte() {  # <horizontal|vertical> <ancho> <alto> <salida>
  local i=0 lista=$TMP/lista-$1.txt
  mkdir -p "$TMP"; : > "$lista"
  for t in "${TOMAS[@]}"; do
    read -r f ini dur cx <<<"$t"
    local src=$S bal=$BAL_S
    [[ $f == L ]] && { src=$L; bal=$BAL_L; }
    # la última toma se apaga a negro: punto del loop y salida hacia la capilla
    local fin=""
    (( i == ${#TOMAS[@]} - 1 )) && fin=",fade=t=out:st=$(python3 -c "print($dur - 1.5)"):d=1.5"
    ffmpeg -v error -y -ss "$ini" -t "$dur" -i "$src" -an \
      -vf "$(recorte "$f" "$cx" "$1"),$bal,scale=$2:$3:flags=lanczos,fps=24,format=gbrp,$LOOK$fin,format=yuv420p" \
      -c:v libx264 -crf 12 -preset fast "$TMP/$1-$i.mp4"
    echo "file '$1-$i.mp4'" >> "$lista"
    i=$((i + 1))
  done
  ffmpeg -v error -y -f concat -i "$lista" -c copy "$4"
}

web() {  # <maestro> <base de salida> <alto h264> <crf h264>
  ffmpeg -v error -y -i "$1" -c:v libsvtav1 -crf 40 -preset 6 -pix_fmt yuv420p10le \
    -movflags +faststart -an "$2.av1.mp4" 2>/dev/null
  ffmpeg -v error -y -i "$1" -vf "scale=-2:$3" -c:v libx264 -crf "$4" -preset slow -profile:v high \
    -pix_fmt yuv420p -movflags +faststart -an "$2.mp4"
}

corte horizontal 1920 1080 "$TMP/maestro-h.mp4"
corte vertical 720 1280 "$TMP/maestro-v.mp4"
web "$TMP/maestro-h.mp4" "$OUT/hero" 720 26
# El vertical en H.264 es el de los iPhone sin AV1 (anteriores al A17): a CRF 26
# pesaba 3.4 MB; a 28, 2.4 MB.
web "$TMP/maestro-v.mp4" "$OUT/hero-v" 1280 28
# Un solo poster: <video poster> no admite media; en vertical lo recorta object-fit.
ffmpeg -v error -y -i "$TMP/maestro-h.mp4" -frames:v 1 -vf scale=1280:-2 -q:v 4 "$OUT/hero-poster.jpg"
ls -l "$OUT"/hero*

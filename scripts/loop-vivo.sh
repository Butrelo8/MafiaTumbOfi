#!/usr/bin/env bash
# Tubería del loop vivo: placa → H3 → máscara → montaje → foco → halación → escalera de códecs, por pasos.
# Reemplaza las copias por carpeta de tmp/ (h3*.sh, klein*.sh, montar*.sh, cine-look/, ladder.sh). Los prompts son
# datos por ticket: prompts/<ticket>/<nombre>.txt (índice en prompts/README.md).
#
# Orden (docs/handoffs/2026-10-10-micro-colgado.md; lo de en medio, atenuar/micro_viva/velas/polvo, es de cada ticket):
#   klein  <prompt.txt> <maqueta.png> <prefijo> [referencia.png]  barrido de semillas desde UNA placa, nunca en cadena
#   h3     <prompt.txt> <placa.png> <control> <prefijo>            control .png (canny, cámara quieta) o .mp4 (cámara)
#   rtx    <h3.mp4> <prefijo>                                       RTX: ×1.5 si H3 mide 1280 de ancho, si no ×2
#   suave  <entrada> <salida.mkv>                                   tmix 1-2-1 (H3 arranca y para en tomas largas)
#   montar <h3> <placa_viva> <mascara_llamas> <mascara_humo> <salida.mkv>
#   foco   <entrada> <disparidad.png> <salida.mkv> <foco_x> <foco_y> <coc_px>   (dof.py; FOCO_D, FOCO_MASK)
#   halacion <entrada> <salida.mp4> [HAL] [MIST]                     (GOP=N para loops de más de 250 cuadros; VC)
#   escalera <master.mkv> <prefijo>                                 AV1/HEVC/H.264 con peso y SSIM
#
# Variables: FORMATO escritorio|movil (escritorio), DUR 5|10|15 s (5), N cuadros del loop (24·DUR), X fundido (20),
# W/H tamaño de H3, SEMILLA (7), SEMILLAS de Klein ("11 22 33"), MP megapíxeles de Klein (1.56), DEST carpeta (.).
# klein/h3/rtx sólo imprimen la orden de gen.sh; CORRER=1 la lanza (ComfyUI, minutos por trabajo).
# HUMO60=1: el humo como sub-loop propio de 60 cuadros fundido de punta a punta (montar_r7.sh / montar_nave.sh, r3 del
# ticket 13). Por omisión el humo va en el mismo loop de N que las llamas (montar_largo.sh): "va en todas las versiones
# nuevas" (tmp/micro/NOTAS.md, 2026-10-10).
set -euo pipefail
paso=${1:?paso: klein|h3|rtx|suave|montar|foco|halacion|escalera}; shift
AQUI=$(cd "$(dirname "$0")" && pwd)
G=${GEN:-$HOME/.claude/skills/comfy-local/scripts/gen.sh}
PY="uv run -q --with numpy --with opencv-python-headless python -I"
FORMATO=${FORMATO:-escritorio}; DUR=${DUR:-5}; N=${N:-$((24 * DUR))}; X=${X:-20}; DEST=${DEST:-.}
case $FORMATO in escritorio) TAM=1920:1080 ;; movil) TAM=704:1280 ;; *) echo "FORMATO escritorio|movil"; exit 1 ;; esac
KIT="/mnt/e/Cursor Projects/Davincy Resolve/luts/terceros/film/print/kodak_2383_constlclip.cube"
# LOOK= (vacío) monta sin look: E5 del 07 va sin grade hasta el pase único sobre E5+E6 (vibeship, 2026-10-13)
LOOK=${LOOK-"huesaturation=colors=g+c:saturation=-0.8,split[o][l];[l]lut3d=file='$KIT':interp=tetrahedral[g];[o][g]blend=all_mode=normal:all_opacity=0.5,curves=master='0/0.02 0.5/0.48 1/0.96',vignette=PI/5"}

gen() {  # imprime la orden; con CORRER=1 la lanza
  printf '%q ' "$G" "$@"; echo
  [ "${CORRER:-}" = 1 ] && "$G" "$@" 2>&1 | tail -2 || true
}

case $paso in
klein)
  prompt=$1 maqueta=$2 pref=$3 ref=${4:-}; mkdir -p "$DEST"
  # nombre nuevo por prefijo: ComfyUI cachea LoadImage por nombre
  cp "$maqueta" "$DEST/${pref}_maqueta.png"; m=$(realpath "$DEST/${pref}_maqueta.png")
  [ -n "$ref" ] && { cp "$ref" "$DEST/${pref}_ref.png"; r=$(realpath "$DEST/${pref}_ref.png"); }
  for s in ${SEMILLAS:-11 22 33}; do
    if [ -z "$ref" ]; then
      gen preset_edit "$(realpath "$DEST")" "76.image=$m" "75.text=$(cat "$prompt")" 75.noise_seed=$s \
        75/80.upscale_method=lanczos 75/80.megapixels=${MP:-1.56} 9.filename_prefix=mto/${pref}_s$s
    else  # preset_edit_ref = preset_edit con el nodo 92 (2 imágenes): 76 maqueta, 121 referencia
      gen preset_edit_ref "$(realpath "$DEST")" "76.image=$m" "121.image=$r" "92.text=$(cat "$prompt")" 92.noise_seed=$s \
        92/111.megapixels=${MP:-1.56} 92/85.megapixels=${MP:-1.56} 122.filename_prefix=mto/${pref}_s$s
    fi
  done
  # Lienzo alto (vertical sin shift, 704×1920): recortar luego los 2/3 de abajo con
  #   ffmpeg -i <salida> -vf "crop=iw:ih*2/3:0:ih/3" <recorte>   (Klein ignora el shift_y de la lente; ticket 06)
  ;;
h3)
  prompt=$1 placa=$2 ctl=$3 pref=$4; mkdir -p "$DEST"
  if [ -z "${W:-}" ]; then
    case $FORMATO:$DUR in
      escritorio:5) W=1280 H=704 ;; escritorio:10) W=928 H=512 ;;  # ticket 04: 10 s sólo cabe en 12 GB a 928×512
      movil:5) W=704 H=1280 ;; movil:10) W=512 H=928 ;;
      *) echo "$FORMATO a $DUR s: no hay tamaño de H3 probado; pasa W y H (múltiplos de 32)"; exit 1 ;;
    esac
  fi
  L=$((N + X)); L=$(( (L - 5 + 16) / 17 * 17 + 5 ))  # H3 pide 17n+5 cuadros: N del loop + X para fundir la costura
  if [[ $ctl == *.png ]]; then  # cámara quieta: canny de la placa repetido, como el anuncio de E:\ComfyUI (PLAYBOOKS.md)
    ffmpeg -v error -y -loop 1 -framerate 24 -i "$ctl" -vf scale=$W:$H:flags=lanczos -frames:v $L -c:v libx264 -crf 12 -pix_fmt yuv420p "$DEST/ctl_$pref.mp4"
    extra=(15.steps=${PASOS:-40} 10.end_percent=0.5)
  else
    ffmpeg -v error -y -i "$ctl" -vf scale=$W:$H:flags=lanczos -frames:v $L -c:v libx264 -crf 12 -pix_fmt yuv420p "$DEST/ctl_$pref.mp4"
    extra=(15.steps=${PASOS:-20})
  fi
  ffmpeg -v error -y -i "$placa" -vf scale=$W:$H:flags=lanczos "$DEST/first_$pref.png"
  d=$(realpath "$DEST")
  gen preset_posevideo_ff "$d" "8.file=$d/ctl_$pref.mp4" "11.image=$d/first_$pref.png" 12.width=$W 12.height=$H 12.length=$L \
    "12.prompt=$(cat "$prompt")" "${extra[@]}" 13.noise_seed=${SEMILLA:-7} 21.filename_prefix=mto/$pref
  ;;
rtx)
  ancho=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$1")
  esc=(); [ "$ancho" = 1280 ] && esc=(1.resize_type.scale=1.5 8.fps=24)  # como contrabajo-12; el ×2 de 10 s, sin slots
  gen preset_4k "$(realpath "$DEST")" "6.file=$(realpath "$1")" "${esc[@]}" 9.filename_prefix=mto/${2}_rtx
  ;;
suave)
  ffmpeg -v error -y -i "$1" -vf "tmix=frames=3:weights='1 2 1'" -c:v ffv1 -an "$2"
  ;;
montar)
  h3=$1 placa=$2 ml=$3 mh=$4 out=$5
  # H3 trae N+X cuadros: los X del final repiten la pose de los X del principio y se funden sobre ellos.
  CAP="[x]trim=start_frame=$N:end_frame=$((N + X)),setpts=PTS-STARTPTS[t];[y]trim=end_frame=$X,setpts=PTS-STARTPTS[h];\
[z]trim=start_frame=$X:end_frame=$N,setpts=PTS-STARTPTS[c];[t][h]blend=all_expr='A*(1-N/$X)+B*(N/$X)'[s]"
  MASC="[2:v]format=gray,format=gbrp[ml];[3:v]format=gray,format=gbrp[mh];[pl][cap][ml]maskedmerge[m];[m][humo][mh]maskedmerge,${LOOK:+$LOOK,}format=bgr0"
  if [ "${HUMO60:-}" = 1 ]; then
    [ "$N" = 120 ] || { echo "HUMO60 sólo con N=120 (dos vueltas del sub-loop de 60)"; exit 1; }
    HUMO="split[h1][h2];[h1]trim=end_frame=60,setpts=PTS-STARTPTS[ha];[h2]trim=start_frame=60:end_frame=120,setpts=PTS-STARTPTS[hb];\
[ha][hb]blend=all_expr='A*(N/60)+B*(1-N/60)',loop=1:60:0,setpts=N/24/TB[humo]"
    if [ "$FORMATO" = escritorio ]; then  # montar_r7.sh: costura sobre el RTX y luego escala
      F="[0:v]split[a0][b0];[a0]split=3[x][y][z];$CAP;[s][c]concat=n=2:v=1,scale=$TAM:flags=lanczos,format=gbrp[cap];\
[b0]scale=$TAM:flags=lanczos,format=gbrp,$HUMO;[1:v]scale=$TAM:flags=lanczos,format=gbrp[pl];$MASC"
    else  # montar_nave.sh: H3 ya sale a 704×1280, sin escala
      F="[0:v]format=gbrp,split=4[x][y][z][w];$CAP;[s][c]concat=n=2:v=1[cap];[w]$HUMO;[1:v]format=gbrp[pl];$MASC"
    fi
  else  # montar_largo.sh / montar_largo_v.sh: humo y llamas en el mismo loop de N
    F="[0:v]scale=$TAM:flags=lanczos,format=gbrp,split=3[x][y][z];$CAP;[s][c]concat=n=2:v=1,split[cap][humo];\
[1:v]scale=$TAM:flags=lanczos,format=gbrp[pl];$MASC"
  fi
  ffmpeg -v error -y -i "$h3" -i "$placa" -loop 1 -framerate 24 -i "$ml" -loop 1 -framerate 24 -i "$mh" \
    -filter_complex "$F" -frames:v $N -c:v ffv1 -an "$out"
  echo "montado $N cuadros ($FORMATO${HUMO60:+, humo 60}): $(stat -c%s "$out") B"
  ;;
foco) $PY "$AQUI/loop-vivo/dof.py" "$@" ;;
halacion) "$AQUI/loop-vivo/halacion.sh" "$@" ;;
escalera) "$AQUI/loop-vivo/escalera.sh" "$@" ;;
*) echo "paso desconocido: $paso"; exit 1 ;;
esac

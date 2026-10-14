#!/usr/bin/env bash
# Peldaño de escritorio a 2560×1440 (2026-10-14, el usuario eligió la variante A: Lanczos sin enfoque;
# docs/2026-10-14-resolucion-1440.md). Sale de los maestros FFV1 de entrega/maestros con los mismos peldaños que
# tmp/07/look/escalera07.sh (AV1 crf 40 preset 4, HEVC crf 26 slow) y sólo AV1 y HEVC: el H.264 se queda en 1920.
# GOP 240 en los loops, 60 en las transiciones; la vuelta es la ida al revés. Lanczos escala cada cuadro por separado,
# así que las colas que en el maestro son los cuadros 0–19 del loop siguen siéndolo (lo comprueba `costuras`).
#   scripts/escalera-2560.sh [nombre...]     (sin nombres: todo)   salida: entrega/escritorio-2560/
set -euo pipefail
cd "$(dirname "$0")/.."
M=entrega/maestros OUT=entrega/escritorio-2560
mkdir -p "$OUT"
ESC="scale=2560:1440:flags=lanczos"
LOOPS="nave sacristia vestidor cripta atrio"
IDAS="ida musica-ida contratacion-ida"

# Loops en AV1 con enable-tf=0 (vibeship, 2026-10-14): con un solo cuadro clave por loop el cuadro clave filtrado en el
# tiempo devolvía de golpe el grano fino que los P del final ya habían borrado (el polvo del haz de la cripta saltaba hasta
# 5.1 niveles en f239 → f0); sin ese filtro, 3.2, +1.5 % de peso (docs/2026-10-14-07-loops-v5.md). Transiciones igual.
enc() {  # enc <entrada> <salida sin códec> <gop> [filtro previo] [svtav1-params]
  local vf="${4:+$4,}$ESC"
  ffmpeg -nostdin -v error -y -i "$1" -vf "$vf" -c:v libsvtav1 -preset 4 -crf 40 ${5:+-svtav1-params $5} -pix_fmt yuv420p -g "$3" -an \
    -movflags +faststart "$2-av1.mp4" 2>/dev/null
  ffmpeg -nostdin -v error -y -i "$1" -vf "$vf" -c:v libx265 -preset slow -crf 26 -tag:v hvc1 -x265-params log-level=error \
    -pix_fmt yuv420p -g "$3" -an -movflags +faststart "$2-hevc.mp4"
  printf '%-34s %6d KB   %-34s %6d KB\n' "$2-av1.mp4" $(( $(stat -c%s "$2-av1.mp4") / 1024 )) \
    "$2-hevc.mp4" $(( $(stat -c%s "$2-hevc.mp4") / 1024 ))
}

# Colas: los maestros de ida y musica-ida son bgr0 y su cola es igual al loop en RGB, no en el yuv420p que reciben los
# codificadores (media 0.65–0.78, máx. 12, también en el peldaño de 1920). Aquí la cola se toma del maestro del loop:
# idéntica a lo que codifica el loop. <ida>:<loop>:<cuadros de cola>
COLAS="ida:sacristia:1 musica-ida:vestidor:20 contratacion-ida:atrio:20"
empalme() {  # empalme <ida> → ruta del maestro con la cola del loop (FFV1 yuv420p, en tmp/)
  local c; for c in $COLAS; do [ "${c%%:*}" = "$1" ] || continue
    local l=${c#*:}; local n=${l#*:} out=tmp/escalera-2560/$1.mkv; l=${l%%:*}; mkdir -p tmp/escalera-2560
    local k=$(( $(ffprobe -v error -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$M/esc-$1.mkv") - n ))
    ffmpeg -nostdin -v error -y -i "$M/esc-$1.mkv" -i "$M/esc-$l.mkv" -filter_complex \
      "[0]trim=end_frame=$k,setpts=PTS-STARTPTS,format=yuv420p[a];[1]trim=end_frame=$n,setpts=PTS-STARTPTS,format=yuv420p[b];[a][b]concat=n=2:v=1" \
      -c:v ffv1 -an "$out"
    echo "$out"; return; done
  echo "$M/esc-$1.mkv"
}

[ $# -gt 0 ] || set -- $LOOPS $IDAS
for n in "$@"; do
  case " $LOOPS " in
    *" $n "*) enc "$M/esc-$n.mkv" "$OUT/$n" 240 "" enable-tf=0 ;;
    *) m=$(empalme "$n")
       enc "$m" "$OUT/$n" 60
       enc "$m" "$OUT/${n/ida/vuelta}" 60 reverse ;;
  esac
done

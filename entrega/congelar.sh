#!/usr/bin/env bash
# Paso 0 del alcance (docs/scope-terminado-2026-10-12.md): copia lo aprobado de tmp/ a entrega/ con nombres finales
# y escribe MANIFEST.tsv (sha256, cuadros, tamaño, origen). Los maestros sin pérdida (*.mkv) se copian pero no se
# versionan (.gitignore). Volver a correrlo es seguro: sólo sobrescribe con los mismos orígenes.
set -euo pipefail
cd "$(dirname "$0")"
T=../tmp
H=$T/micro/trans_esc/hd_det
V=$T/micro/trans
mkdir -p escritorio vertical placas maestros

# destino  origen  (orden: lo que va a la web, luego placas, luego maestros)
LISTA="
escritorio/nave.mp4            $T/micro/largo/capas240/r7_micro_10s_240.mp4
escritorio/ida-av1.mp4         $H/ida_final_av1.mp4
escritorio/ida-hevc.mp4        $H/ida_final_hevc.mp4
escritorio/ida-h264.mp4        $H/ida_final_h264.mp4
escritorio/vuelta-av1.mp4      $H/vuelta_final_av1.mp4
vertical/nave.mp4              $T/micro/movil/nave_micro_10s.mp4
vertical/ida-av1.mp4           $V/cod/ida_av1_crf40.mp4
vertical/ida-hevc.mp4          $V/cod/ida_hevc_crf26.mp4
vertical/ida-h264.mp4          $V/ida_micro.mp4
vertical/vuelta-h264.mp4       $V/vuelta_micro.mp4
vertical/sacristia-5s.mp4      $T/movil-06/web/sacristia.mp4
placas/sacristia-esc-s11.png   $T/micro/trans_esc/klein/sac17_s11_00001_.png
placas/nave-esc-micro.png      $T/micro/placa_micro_rosa.png
placas/nave-vert-micro-s4.png  $T/micro/movil/placa_micro_vb_s4_suj.png
placas/nave-esc-s44.png        $T/props-06/klein/nave13props_p4_s44_00001_.png
placas/nave-esc-s44-vacia.png  $T/props-06/s44_vacia.png
placas/nave-vert-s33-vacia.png $T/props-06/klein/s33_vacia_s7_00001_.png
maestros/esc-ida.mkv           $H/ida_master_mezcla.mkv
maestros/vert-ida.mkv          $V/cod/ida_master.mkv
"
while read -r dst src; do
  [ -n "$dst" ] || continue
  cp -p "$src" "$dst"
done <<<"$LISTA"

# El maestro del loop vertical no se guardó: es halacion.sh sobre nave_micro240_dof.mkv con VC=ffv1
# (SSIM 0.990 contra nave.mp4, el H.264 crf 23 aprobado). El de escritorio no existe (esc240_dof.mkv se borró).
[ -f maestros/vert-nave.mkv ] || VC="-c:v ffv1" GOP=240 $T/cine-look/halacion.sh \
  $T/micro/movil/nave_micro240_dof.mkv maestros/vert-nave.mkv

{
  printf 'archivo\tcuadros\tKB\tsha256\torigen\n'
  while read -r dst src; do
    [ -n "$dst" ] || continue
    n=$(case $dst in *.png) echo 1 ;; *) ffprobe -v error -select_streams v:0 -count_packets \
      -show_entries stream=nb_read_packets -of csv=p=0 "$dst" ;; esac)
    printf '%s\t%s\t%s\t%s\t%s\n' "$dst" "$n" $(( $(stat -c%s "$dst") / 1024 )) \
      "$(sha256sum "$dst" | cut -c1-16)" "${src#../}"
  done <<<"$LISTA
maestros/vert-nave.mkv tmp/micro/movil/nave_micro240_dof.mkv + halacion.sh VC=ffv1"
} > MANIFEST.tsv
column -t -s$'\t' MANIFEST.tsv

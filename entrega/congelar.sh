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
escritorio/nave.mp4            $T/g6/esc/nave_g6_esc_c.mp4
escritorio/ida-av1.mp4         $H/ida_final_av1.mp4
escritorio/ida-hevc.mp4        $H/ida_final_hevc.mp4
escritorio/ida-h264.mp4        $H/ida_final_h264.mp4
escritorio/vuelta-av1.mp4      $H/vuelta_final_av1.mp4
vertical/nave.mp4              $T/g6/vert/nave_g6_vert.mp4
vertical/ida-av1.mp4           $V/cod/ida_av1_crf40.mp4
vertical/ida-hevc.mp4          $V/cod/ida_hevc_crf26.mp4
vertical/ida-h264.mp4          $V/ida_micro.mp4
vertical/vuelta-h264.mp4       $V/vuelta_micro.mp4
vertical/sacristia-5s.mp4      $T/movil-06/web/sacristia.mp4
escritorio/grupo-ida-provisional-h264.mp4  $T/07/e6prov/grupo-ida-provisional-h264.mp4
placas/sacristia-esc-s11.png   $T/micro/trans_esc/klein/sac17_s11_00001_.png
placas/nave-esc-micro.png      $T/micro/g5/placa_micro_tallo.png
placas/nave-vert-micro-s4.png  $T/micro/movil/placa_micro_vb_s4_suj.png
placas/nave-esc-s44.png        $T/props-06/klein/nave13props_p4_s44_00001_.png
placas/nave-esc-s44-vacia.png  $T/props-06/s44_vacia.png
placas/nave-vert-s33-vacia.png $T/props-06/klein/s33_vacia_s7_00001_.png
placas/nave-esc-g2.png         $T/props-06/nave_g2.png
placas/nave-vert-g3.png        $T/props-06/nave_g3.png
placas/nave-esc-g4-real.png    $T/props-06/nave_g4_esc.png
placas/nave-vert-g4-real.png   $T/props-06/nave_g4_vert.png
placas/nave-esc-g4-disp.png    $T/props-06/nave_g4_esc_disp.png
placas/nave-vert-g4-disp.png   $T/props-06/nave_g4_vert_disp.png
placas/nave-esc-g5-micro.png   $T/micro/g5/esc_g5.png
placas/nave-vert-g5-micro.png  $T/micro/g5/vert_g5_up20.png
placas/micro-vert-g5.png       $T/micro/g5/vert_placa_micro_g5.png
placas/mascara-micro-esc-g5.png  $T/micro/g5/mascara_micro_g5.png
placas/mascara-micro-vert-g5.png $T/micro/g5/vert_mascara_g5.png
placas/mascara-rosa-vert-g5.png  $T/micro/g5/vert_rosa_g5.png
placas/nave-esc-g5-disp.png    $T/micro/g5/esc_disp_g5.png
placas/nave-vert-g5-disp.png   $T/micro/g5/vert_disp_g5.png
placas/mascara-micro-esc-tallo.png  $T/micro/g5/mascara_micro_tallo.png
placas/micro-vert-tallo.png         $T/micro/g5/vert_placa_micro_tallo.png
placas/mascara-micro-vert-tallo.png $T/micro/g5/vert_mascara_tallo.png
placas/mascara-rosa-vert-tallo.png  $T/micro/g5/vert_rosa_tallo.png
placas/nave-esc-tallo-disp.png      $T/micro/g5/esc_disp_tallo.png
placas/nave-vert-tallo-disp.png     $T/micro/g5/vert_disp_tallo.png
placas/nave-esc-g6-copal-real.png  $T/g6/copal/nave_g6_esc_real_copal.png
placas/nave-esc-g6-copal-klein.png $T/g6/copal/nave_g6_esc_klein_copal.png
maestros/esc-ida.mkv           $H/ida_master_mezcla.mkv
maestros/vert-ida.mkv          $V/cod/ida_master.mkv
maestros/esc-nave.mkv          $T/g6/esc/maestro_nave_esc.mkv
maestros/vert-nave.mkv         $T/g6/vert/maestro_nave_vert.mkv
"
while read -r dst src; do
  [ -n "$dst" ] || continue
  cp -p "$src" "$dst"
done <<<"$LISTA"

# G6: los maestros de los loops son halacion.sh VC=ffv1 sobre tmp/g6/<f>/dof240.mkv (tmp/g6/tanda.sh).

{
  printf 'archivo\tcuadros\tKB\tsha256\torigen\n'
  while read -r dst src; do
    [ -n "$dst" ] || continue
    n=$(case $dst in *.png) echo 1 ;; *) ffprobe -v error -select_streams v:0 -count_packets \
      -show_entries stream=nb_read_packets -of csv=p=0 "$dst" ;; esac)
    printf '%s\t%s\t%s\t%s\t%s\n' "$dst" "$n" $(( $(stat -c%s "$dst") / 1024 )) \
      "$(sha256sum "$dst" | cut -c1-16)" "${src#../}"
  done <<<"$LISTA"
} > MANIFEST.tsv
column -t -s$'\t' MANIFEST.tsv

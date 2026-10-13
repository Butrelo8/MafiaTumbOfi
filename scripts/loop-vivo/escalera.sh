#!/usr/bin/env bash
# Escalera de códecs (ticket 05: AV1 → HEVC → H.264) desde el máster sin pérdida; peso + SSIM contra el máster.
# El SSIM sólo ordena peldaños del mismo clip: no mide si se ve bien (la escena es casi toda negra).
# escalera.sh <master.mkv> <prefijo>: escribe <prefijo>_<peldaño>.mp4 (relativo a donde se lance).
# Antes tmp/micro/{trans,trans_esc}/cod/ladder.sh, que hacía cd a su carpeta; lo demás, igual.
set -euo pipefail; M=${1:?master}; P=${2:?prefijo}
enc() { local name=$1; shift; ffmpeg -v error -y -i "$M" "$@" -g 60 -an -movflags +faststart "${P}_$name.mp4"
  local s; s=$(ffmpeg -i "${P}_$name.mp4" -i "$M" -lavfi "[0]format=yuv420p[a];[1]format=yuv420p[b];[a][b]ssim" -f null - 2>&1 | grep -o 'All:[0-9.]*' | cut -d: -f2)
  printf '%-16s %6d KB  SSIM %s\n' "$name" $(( $(stat -c%s "${P}_$name.mp4") / 1024 )) "$s"; }
enc h264_crf23 -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p
enc h264_crf26 -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p
enc hevc_crf26 -c:v libx265 -preset slow -crf 26 -tag:v hvc1 -pix_fmt yuv420p -x265-params log-level=error
enc hevc_crf28 -c:v libx265 -preset slow -crf 28 -tag:v hvc1 -pix_fmt yuv420p -x265-params log-level=error
enc av1_crf40 -c:v libsvtav1 -preset 4 -crf 40 -pix_fmt yuv420p
enc av1_crf40_10b -c:v libsvtav1 -preset 4 -crf 40 -pix_fmt yuv420p10le
enc av1_crf45_10b -c:v libsvtav1 -preset 4 -crf 45 -pix_fmt yuv420p10le

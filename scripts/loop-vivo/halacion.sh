#!/usr/bin/env bash
# halacion.sh <in> <out> [HAL] [MIST] — film halation (red glow round candles/neon) + light diffusion (Pro-Mist)
# on top of the graded loop. Defaults = "stronger" (user, 2026-10-09); tested first: HAL 0.5 MIST 0.3 UMBRAL 0.6 ANCHO 10 GAN 1 (too subtle at 100 %).
# Sizes scale with width (calibrated at 1920). Prototype for the movie-look test.
# GOP: x264 keyframe interval (default 250). Loops longer than 250 frames: pass the frame count, or the keyframe at 250
# pops visibly in the dark (15 s loop, 2026-10-10).
# VC: replaces the x264 encode, e.g. VC="-c:v ffv1" for a lossless master to encode AV1/HEVC from (ticket 17).
set -euo pipefail
IN=$1; OUT=$2; HAL=${3:-0.8}; MIST=${4:-0.45}; UMBRAL=${UMBRAL:-0.5}; ANCHO=${ANCHO:-18}; GAN=${GAN:-2}  # colorchannelmixer caps at 2
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$IN")
ffmpeg -v error -y -i "$IN" -filter_complex "[0]format=gbrp,split=3[g][h][d];
[h]curves=all='0/0 $UMBRAL/0 $(echo "($UMBRAL+1)/2" | bc -l)/1 1/1',gblur=sigma=$((W*ANCHO/1920+1)),colorchannelmixer=rr=$GAN:gg=$(echo "$GAN*0.4" | bc -l):bb=$(echo "$GAN*0.15" | bc -l)[hal];
[d]curves=all='0/0 0.45/0 1/0.8',gblur=sigma=$((W*40/1920+1))[mist];
[g][hal]blend=all_mode=screen:all_opacity=$HAL[gh];[gh][mist]blend=all_mode=screen:all_opacity=$MIST,format=yuv420p" \
  ${VC:--c:v libx264 -preset slow -crf 23 -g ${GOP:-250} -pix_fmt yuv420p -movflags +faststart} -an "$OUT"

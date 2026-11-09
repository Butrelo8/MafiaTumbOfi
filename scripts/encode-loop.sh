#!/usr/bin/env bash
# Encode the rendered loop frames into the page's fallback video and poster (poster = frame 0, so the swap has no jump).
# Usage: scripts/encode-loop.sh <w>x<h> [crf]  -> public/escena/loop-<w>x<h>.mp4, public/escena/poster-<w>x<h>.jpg
set -euo pipefail
cd "$(dirname "$0")/.."
wh=$1 crf=${2:-27}
in="blender/render/loop-noche-alta-$wh"
[ "$(ls "$in"/f_*.png | wc -l)" -eq 240 ] || { echo "need 240 frames in $in" >&2; exit 1; }
ffmpeg -v error -y -framerate 24 -start_number 0 -i "$in/f_%04d.png" -c:v libx264 -preset slow -crf "$crf" \
  -pix_fmt yuv420p -g 48 -keyint_min 48 -sc_threshold 0 -movflags +faststart -an "public/escena/loop-$wh.mp4"
ffmpeg -v error -y -i "$in/f_0000.png" -q:v 4 "public/escena/poster-$wh.jpg"
ls -l "public/escena/loop-$wh.mp4" "public/escena/poster-$wh.jpg" | awk '{print $5, $9}'

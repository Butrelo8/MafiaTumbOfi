#!/usr/bin/env bash
# Render the Cycles hero loop (night, stop "alta") as PNG frames, vertical then 16:9.
# Usage: scripts/render-loop.sh [samples]   -> blender/render/loop-noche-alta-<w>x<h>/f_0000..0239.png
set -euo pipefail
cd "$(dirname "$0")/.."
S=${1:-64}
for wh in "720 1280" "1600 900"; do
  set -- $wh
  out="blender/render/loop-noche-alta-${1}x${2}"
  mkdir -p "$out"
  /mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- \
    loop noche alta "$1" "$2" "$(wslpath -w "$out")" "$S" 2>&1 | grep -E "Traceback|Error|Saved: .*f_0(000|120|239)" || true
  ls "$out"/f_*.png | wc -l
done

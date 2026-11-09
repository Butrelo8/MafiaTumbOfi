#!/usr/bin/env bash
# Render the Cycles hero loop (night, stop "alta") as PNG frames, vertical then 16:9.
# Usage: scripts/render-loop.sh [samples] [sizes]   -> blender/render/loop-noche-alta-<w>x<h>/f_0000..0239.png
#   sizes: comma list, default 720x1280,1600x900. Rendered at 64 (720x1280) and 32 (1600x900) samples, ~12 s/frame each
#   on an RTX 4070 Ti. Then scripts/encode-loop.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
S=${1:-64}
IFS=, read -ra SIZES <<< "${2:-720x1280,1600x900}"
for wh in "${SIZES[@]}"; do
  w=${wh%x*} h=${wh#*x}
  out="blender/render/loop-noche-alta-${w}x${h}"
  mkdir -p "$out"
  /mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- \
    loop noche alta "$w" "$h" "$(wslpath -w "$out")" "$S" 2>&1 | grep -E "Traceback|Error|Saved: .*f_0(000|120|239)" || true
  ls "$out"/f_*.png | wc -l
done

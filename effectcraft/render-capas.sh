#!/usr/bin/env bash
# Render the cab shot's layers for one format: effectcraft/render-capas.sh <w> <h> <out_dir> <samples> <pass:a-b>...
# e.g. effectcraft/render-capas.sh 1920 1080 blender/render/effectcraft/capas-1920x1080 24 bg:0-59 fig:0-59 fg:0-59
set -euo pipefail
cd "$(dirname "$0")/.."
w=$1 h=$2 out=$3 samples=$4; shift 4
mkdir -p "$out"
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w effectcraft/capas.py)" \
  -- "$w" "$h" "$(wslpath -w "$(realpath "$out")")" "$samples" "$@" > "$out.log" 2>&1
grep -E 'SHA256|CAMARA|PASE|TOTAL' "$out.log"

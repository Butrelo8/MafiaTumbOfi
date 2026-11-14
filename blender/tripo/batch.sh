#!/bin/bash
# batch.sh <prefix_out> <mode> <size> glb...
cd "$(dirname "$0")"; pre=$1; mode=$2; size=$3; shift 3
W(){ wslpath -w "$PWD/$1"; }
for g in "$@"; do n=$(basename "$g" .glb)
  timeout 900 /mnt/e/Blender/blender.exe -b --factory-startup --python "$(W vistas.py)" -- "$(W "$g")" "$(W r)\\${pre}${n}_${mode}" $mode $size 2>&1 | grep -E "^INFO" > "r/${pre}${n}_${mode}.info"
  ffmpeg -loglevel error -y -i r/${pre}${n}_${mode}_front.png -i r/${pre}${n}_${mode}_right.png -i r/${pre}${n}_${mode}_back.png -i r/${pre}${n}_${mode}_left.png -filter_complex hstack=4 r/${pre}${n}_${mode}_sheet.png
done

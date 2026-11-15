#!/bin/bash
# clips_wb.sh name ...: per clip, the Workbench side clip (wbclip.py) of diego_p2_<name>_v.blend at 30 fps and eagle.sh
# on it. Outputs: render/reparto/partes2/diego/clips/<name>/{frames,<name>_wb.mp4,eagle.log}.
D=$(cd "$(dirname "$0")" && pwd); B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
A=$D/../assets/reparto/partes2; R=$D/../render/reparto/partes2/diego/clips
for n in "$@"; do O=$R/$n; mkdir -p "$O/frames"; t0=$(date +%s)
  $B -b "$(w "$A/diego_p2_${n}_v.blend")" --python "$(w "$D/wbclip.py")" -- "$(w "$O/frames")" > "$O/render.log" 2>&1
  ffmpeg -v error -y -framerate 30 -start_number 1 -i "$O/frames/%04d.png" -c:v libx264 -crf 12 -pix_fmt yuv420p "$O/${n}_wb.mp4"
  (cd "$O" && ~/projects/visual-lab/scripts/eagle.sh "$O/${n}_wb.mp4" > "$O/eagle.log" 2>&1); e=$?
  echo "@@ $n: $(ls "$O/frames" | wc -l) frames, eagle exit $e, $(( $(date +%s) - t0 ))s"; grep -E "^(crawl|flicker|strobe)" "$O/eagle.log"
done

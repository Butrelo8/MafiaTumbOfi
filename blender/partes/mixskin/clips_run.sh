#!/bin/bash
# clips_run.sh name:blend:range ...: per clip, pen.py (step 2), the Workbench side clip (clip_wb.py) and eagle.sh on it.
# Outputs: render/reparto/partes/diego/clips/<name>/{pen.json,wb/frames,<name>_wb.mp4,eagle.log}
P="/mnt/e/Cursor Projects/MTO-colddrone/blender/partes/mixskin"; B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
R="/mnt/e/Cursor Projects/MTO-colddrone/blender/render/reparto/partes/diego/clips"
cd "$P"
for x in "$@"; do IFS=: read n bl rg <<< "$x"; O=$R/$n; mkdir -p "$O/wb/frames"
  $B -b "$(w "$bl")" --python pen.py -- "$(w "$O/pen.json")" 2 > "$O/pen.log" 2>&1; grep -q @@PEN "$O/pen.log" && echo "pen $n ok" || tail -5 "$O/pen.log"
  $B -b "$(w "$bl")" --python clip_wb.py -- "$(w "$O/wb/frames")" $rg > "$O/wb/render.log" 2>&1; echo "wb $n $(ls "$O/wb/frames" | wc -l) frames"
  ffmpeg -v error -y -framerate 30 -start_number $(ls "$O/wb/frames" | head -1 | sed 's/^0*//; s/\.png//') -i "$O/wb/frames/%04d.png" -c:v libx264 -crf 12 -pix_fmt yuv420p "$O/${n}_wb.mp4"
  (cd "$O" && ~/projects/visual-lab/scripts/eagle.sh "$O/${n}_wb.mp4" > "$O/eagle.log" 2>&1); echo "eagle $n exit $?"; grep -E "^(crawl|flicker|strobe)" "$O/eagle.log"
done; echo CLIPSRUNDONE

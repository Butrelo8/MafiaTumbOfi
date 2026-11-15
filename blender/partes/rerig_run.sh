#!/bin/bash
# rerig_run.sh SUF[:fbx-name] ...: one rig through the WHAM dance, for the current-vs-Mixamo-vs-AccuRIG comparison.
#   SUF alone (e.g. _p3)          the existing rig (its rig_trellis$SUF/dance_trellis.blend must exist: rig_trellis.sh clip)
#   SUF:name (e.g. _mx:diego_mixamo)  rig_from_fbx.py on blender/assets/reparto/rerig/<name>.fbx, then rig_trellis.sh full clip deform
# Then per rig: lit stills (rerig_stills.py) at FRAMES, a 299-frame Workbench side clip (visual-lab render.py) and eagle.sh.
# Outputs: render/reparto/partes/diego/rig_trellis$SUF/{deform_dance.json,stills/,clip/dance$SUF.mp4,eagle.log}
set -e
P="/mnt/e/Cursor Projects/MTO-colddrone/blender/partes"; A="/mnt/e/Cursor Projects/MTO-colddrone/blender/assets/reparto"
R="/mnt/e/Cursor Projects/MTO-colddrone/blender/render/reparto/partes/diego"; B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
GLB=$A/diego-trellis2-s7-r2-f300s3.glb; BVH=/home/black/projects/visual-lab/blender/lab/wham-video-mocap/out/wham10.bvh
RP=/home/black/projects/visual-lab/blender/lab/wham-video-mocap/render.py; FRAMES=${FRAMES:-60,153,240}
cd "$P"
for x in "$@"; do s=${x%%:*}; O=$R/rig_trellis$s; mkdir -p "$O/stills" "$O/clip/frames"
  if [ "$x" != "$s" ]; then
    $B -b --factory-startup --python-exit-code 1 --python "$(w rig_from_fbx.py)" -- "$(w "$GLB")" "$(w "$A/rerig/${x#*:}.fbx")" "$(w "$A/diego_trellis_rig$s.blend")" > "$O/rig_fit.log" 2>&1
    grep -E "@@FBX|@@JOINT" "$O/rig_fit.log" || { tail -5 "$O/rig_fit.log"; exit 1; }
    GLB=$GLB SUF=$s BVH=$BVH CLIP=dance RANGE=1-299:3 ./rig_trellis.sh full clip deform
  fi
  $B -b "$(w "$O/dance_trellis.blend")" --python "$(w rerig_stills.py)" -- "$(w "$O/stills")" $FRAMES 2>&1 | grep -E "@@STILLS|Error"
  $B -b "$(w "$O/dance_trellis.blend")" --python-expr "import bpy; bpy.context.scene.frame_end = 299" --python "$(w $RP)" -- "$(w "$O/clip/frames")" side > "$O/clip/render.log" 2>&1
  ffmpeg -v error -y -framerate 30 -i "$O/clip/frames/%04d.png" -frames:v 299 -c:v libx264 -crf 12 -pix_fmt yuv420p "$O/clip/dance$s.mp4"
  ~/projects/visual-lab/scripts/eagle.sh "$O/clip/dance$s.mp4" > "$O/eagle.log" 2>&1 && echo "eagle $s: exit 0" || echo "eagle $s: exit $?"
  grep -E "^(crawl|flicker|strobe)" "$O/eagle.log" || true
done
echo RERIGDONE

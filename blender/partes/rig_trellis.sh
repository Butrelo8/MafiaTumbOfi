#!/bin/bash
# rig_trellis.sh [stage...]: refit the Rigify rig on TRELLIS.2's own mesh (its own crotch, ankle, knee, shoulders),
# then the same idle as the Tripo rig. Calls firedrone's rig scripts and visual-lab's retarget.py by path (read-only);
# every output lands in this worktree. Stages (default all): fit full clip deform
#   fit    rig_fit.py on the TRELLIS GLB             -> blender/assets/reparto/diego_trellis_rig$S.blend
#   full   rig_full.py (full TRELLIS mesh as Body)    -> blender/assets/reparto/diego_trellis_rig_full$S.blend
#   clip   retarget.py idle_floorfull + rigify_mto.json, pose_fix.py 80 -> $O/${C}_trellis.blend
#   deform deform.py over the idle (joint angles; stretch of the skinned TRELLIS Body as a reference)
# Env: GLB (default diego-trellis2-s7.glb), SUF (suffix on every output name, so a pass never overwrites another),
#      BVH + CLIP (another source clip and its action/blend name; default idle_floorfull / idle).
#      ROLL (pose_fix hand roll, default 80), RANGE (deform frames, default 1-120:3).
set -e
stages=${*:-fit full clip deform}
M=$(cd "$(dirname "$0")/../.." && pwd); FD="/mnt/e/Cursor Projects/MTO-firedrone/blender/rig"
VL=/home/black/projects/visual-lab; LAB=$VL/blender/lab/mediapipe-simple-motion
B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
GLB=${GLB:-$M/blender/assets/reparto/diego-trellis2-s7.glb}; A=$M/blender/assets/reparto; S=${SUF:-}
O=$M/blender/render/reparto/partes/diego/rig_trellis$S; mkdir -p "$O"
BVH=${BVH:-$LAB/out/bvh/idle_floorfull.bvh}; C=${CLIP:-idle}
for s in $stages; do case $s in
  fit)  $B -b --factory-startup --python "$(w "$FD/rig_fit.py")" -- "$(w "$GLB")" "$(w "$A/diego_trellis_rig$S.blend")" \
          > "$O/rig_fit.log" 2>&1; grep @@RIG@@ "$O/rig_fit.log" ;;
  full) $B -b "$(w "$A/diego_trellis_rig$S.blend")" --python "$(w "$FD/rig_full.py")" -- "$(w "$GLB")" \
          "$(w "$A/diego_trellis_rig_full$S.blend")" > "$O/rig_full.log" 2>&1; grep @@FULL@@ "$O/rig_full.log" ;;
  clip)
    $B -b "$(w "$A/diego_trellis_rig_full$S.blend")" --python "$(w $VL/blender/scripts/retarget.py)" -- --src "$(w $BVH)" --map cmu \
      --target "$(w "$FD/rigify_mto.json")" --rig rig --out $C --fps 30 $([ -f "${BVH%.bvh}_contacts.json" ] && echo --contacts "$(w "${BVH%.bvh}_contacts.json")") \
      --save "$(w "$O/${C}_trellis.blend")" --report "$(w "$O/${C}_retarget.json")" --check > "$O/retarget_$C.log" 2>&1
    $B -b "$(w "$O/${C}_trellis.blend")" --python "$(w "$FD/pose_fix.py")" -- "$(w "$O/${C}_trellis.blend")" ${ROLL:-80} 2>&1 | grep @@POSEFIX ;;
  deform)
    $B -b "$(w "$O/${C}_trellis.blend")" --python "$(w "$FD/deform.py")" -- "$(w "$O/deform_$C.json")" ${RANGE:-1-120:3} 2>&1 | grep @@DEFORM ;;
esac; done

#!/bin/bash
# rebuild_tail.sh: from diego_partes2_dressed.blend to the clip blends, in order (one Blender job at a time):
#   bind.py -> diego_partes2_rig.blend; look.py -> diego_partes2_look.blend (skin, hair, chain);
#   clip.py per clip -> diego_p2_<clip>.blend; lids_build.py -> diego_p2_<clip>_v.blend (idle: blink at f100, also
#   copied to diego_p2_idle_blink.blend). Prints each step's @@ lines and its seconds.
set -e
D=$(cd "$(dirname "$0")" && pwd); B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
A=$D/../assets/reparto/partes2; L=$D/../render/reparto/partes2/diego/fit/lids.json
run() { local t0=$(date +%s); "$B" -b "$@" 2>&1 | grep -E "^@@|Traceback|Error:" || true; echo "   ($(( $(date +%s) - t0 )) s)"; }
run "$(w "$A/diego_partes2_dressed.blend")" --python "$(w "$D/bind.py")" -- "$(w "$A/mixamo/dl/diego_partes2_proxy3_mixamo.fbx")" "$(w "$A/diego_partes2_rig.blend")"
run "$(w "$A/diego_partes2_rig.blend")" --python "$(w "$D/look.py")" -- "$(w "$A/diego_partes2_look.blend")"
for c in idle sitting_drinking driving guitar_playing; do
  run "$(w "$A/diego_partes2_look.blend")" --python "$(w "$D/clip.py")" -- "$(w "$A/mixamo/dl/p2_$c.fbx")" "$(w "$A/diego_p2_$c.blend")"
  blink=; [ "$c" = idle ] && blink=100
  run "$(w "$A/diego_p2_$c.blend")" --python "$(w "$D/lids_build.py")" -- "$(w "$L")" "$(w "$A/diego_p2_${c}_v.blend")" $blink
done
cp "$A/diego_p2_idle_v.blend" "$A/diego_p2_idle_blink.blend"

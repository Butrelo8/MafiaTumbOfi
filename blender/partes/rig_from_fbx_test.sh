#!/bin/bash
# rig_from_fbx_test.sh: identity test of rig_from_fbx.py. Fixtures built from the current smooth-3 rig's own joints
# (Mixamo names in a T-pose, scaled 1.7x and moved; CC names with twist bones in the A-pose) must give back
# diego_trellis_rig_p3.blend's DEF bones within 1 mm (heads and tails). Exit 0 = pass.
set -e
P="/mnt/e/Cursor Projects/MTO-colddrone/blender/partes"; A="/mnt/e/Cursor Projects/MTO-colddrone/blender/assets/reparto"
O="/mnt/e/Cursor Projects/MTO-colddrone/blender/render/reparto/partes/diego/rerig_test"; mkdir -p "$O"
B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }; cd "$P"
GLB=$A/diego-trellis2-s7-r2-f300s3.glb
$B -b "$(w "$A/diego_trellis_rig_p3.blend")" --python "$(w rig_heads.py)" -- "$(w "$O/heads_p3.json")" > /dev/null 2>&1
fail=0
for c in mixamo:T cc:A; do n=${c%%:*}; p=${c#*:}
  $B -b "$(w "$A/diego_trellis_rig_full_p3.blend")" --python "$(w rig_from_fbx_fixture.py)" -- "$(w "$O/fix_$n$p.fbx")" $n $p 2>&1 | grep -E "@@FIXTURE|Error"
  $B -b --factory-startup --python-exit-code 1 --python "$(w rig_from_fbx.py)" -- "$(w "$GLB")" "$(w "$O/fix_$n$p.fbx")" "$(w "$O/rig_$n$p.blend")" > "$O/rig_$n$p.log" 2>&1 \
    || { echo "FAIL $n$p: bridge crashed"; grep -E "Error|assert" "$O/rig_$n$p.log" | tail -3; fail=1; continue; }
  grep -E "@@FBX|@@JOINT" "$O/rig_$n$p.log"
  $B -b "$(w "$O/rig_$n$p.blend")" --python "$(w rig_heads.py)" -- "$(w "$O/heads_$n$p.json")" > /dev/null 2>&1
  python3 - "$O/heads_p3.json" "$O/heads_$n$p.json" "$n$p" <<'PY' || fail=1
import json, sys, math
a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
d = sorted(((max(math.dist(a[k][0], b[k][0]), math.dist(a[k][1], b[k][1])) * 1000, k) for k in a), reverse=True)
print(f"{sys.argv[3]}: {len(d)} DEF bones, worst {d[0][0]:.2f} mm ({d[0][1]}), then " + ", ".join(f"{k} {v:.2f}" for v, k in d[1:4]))
sys.exit(0 if d[0][0] <= 1.0 and set(a) == set(b) else 1)
PY
done
[ $fail = 0 ] && echo "IDENTITY PASS" || { echo "IDENTITY FAIL"; exit 1; }

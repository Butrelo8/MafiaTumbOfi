#!/bin/bash
# parts_trellis.sh name:image:seed:faces:smooth ...: each part image -> TRELLIS.2 GLB via colddrone's trellis2.sh (read-only,
# commit ec54929; StableGen 0.5.0 graph), copied to blender/assets/reparto/partes2/<name>.glb. One GPU job at a time.
set -u
R=$(cd "$(dirname "$0")/../.." && pwd); T="/mnt/e/Cursor Projects/MTO-colddrone/blender/partes/trellis2.sh"
for job in "$@"; do
  IFS=: read -r name img seed faces smooth <<<"$job"; t0=$(date +%s)
  stage=$(mktemp -d)/d2_${name}_$t0.png; cp "$img" "$stage"     # no spaces, and a new name per run (LoadImage cache)
  out=$(FACES=$faces SMOOTH=$smooth timeout ${JOB_TIMEOUT:-600} "$T" "$stage" "$seed" "d2_$name" 2>&1) || { echo "@@ $name TIMEOUT/fail after $(( $(date +%s) - t0 ))s: interrupt + restart ComfyUI"; continue; }
  f=$(echo "$out" | awk '/^-> /{print $NF}' | tail -1); sub=$(echo "$out" | awk '/^-> /{print $2}' | tail -1)
  [ "$sub" = "$f" ] && sub=""
  if [ -n "$f" ]; then cp "/mnt/e/ComfyUI/ComfyUI/output/${sub:+$sub/}$f" "$R/blender/assets/reparto/partes2/$name.glb"; fi
  echo "@@ $name seed $seed ${faces}/${smooth}: $(echo "$out" | grep -E '^status|^ERROR' | tr '\n' ' ') $f $(( $(date +%s) - t0 ))s"
done

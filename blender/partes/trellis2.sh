#!/bin/bash
# trellis2.sh <image> <seed> <prefix>: Diego regenerated locally with TRELLIS.2 + native PBR, through StableGen 0.5.0's own
# ComfyUI graph (trellis2_stablegen.json = the API prompt StableGen submitted in the 11-09 teardown proof; only the input
# image, seeds and filename prefix change). Needs ComfyUI up (start-comfy.ps1) and the whole 12 GB card.
# Run with run_in_background; prints the GLB path under E:\ComfyUI\ComfyUI\output.
# FACES / SMOOTH (env) override DecimateMesh target_face_count (100000) and RemeshMesh smooth_iters (0).
set -e
IMG=$1; SEED=${2:-33}; PFX=${3:-mto_diego_trellis2}
API=http://$(ip route | awk '/default/{print $3; exit}'):8188
D=$(cd "$(dirname "$0")" && pwd)
up=$(curl -sm60 -F "image=@$IMG" -F overwrite=true "$API/upload/image")
name=$(echo "$up" | python3 -c 'import sys,json;print(json.load(sys.stdin)["name"])')
body=$(FACES=${FACES:-100000} SMOOTH=${SMOOTH:-0} python3 - "$D/trellis2_stablegen.json" "$name" "$SEED" "$PFX" <<'PY'
import json, sys, os
p = json.load(open(sys.argv[1])); p = p.get("prompt", p)
for n in p.values():
    if n["class_type"] == "LoadImage": n["inputs"]["image"] = sys.argv[2]
    if n["class_type"] == "KSampler": n["inputs"]["seed"] = int(sys.argv[3])
    if n["class_type"] == "SaveGLB": n["inputs"]["filename_prefix"] = sys.argv[4]
    if n["class_type"] == "DecimateMesh": n["inputs"]["target_face_count"] = int(os.environ["FACES"])
    if n["class_type"] == "RemeshMesh": n["inputs"]["smooth_iters"] = int(os.environ["SMOOTH"])
print(json.dumps({"prompt": p}))
PY
)
id=$(curl -sm60 -H 'Content-Type: application/json' -d "$body" "$API/prompt" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("prompt_id") or d)')
echo "queued $id"; t0=$(date +%s); last=0
while :; do
  h=$(curl -sm10 "$API/history/$id" || true)
  echo "$h" | grep -q '"status_str"' && break
  now=$(( $(date +%s) - t0 )); if [ $((now - last)) -ge 60 ]; then echo "esperando $id: ${now}s"; last=$now; fi
  sleep 3
done
echo "$h" | python3 -c '
import sys,json; h=list(json.load(sys.stdin).values())[0]; print("status", h["status"]["status_str"])
for m in h["status"].get("messages", []):
    if m[0] == "execution_error": print("ERROR", m[1].get("exception_message"))
for k,o in h["outputs"].items():
    for v in o.values():
        if isinstance(v,list):
            for f in v:
                if isinstance(f,dict) and "filename" in f: print("->", f.get("subfolder",""), f["filename"])'
echo "secs $(( $(date +%s) - t0 ))"

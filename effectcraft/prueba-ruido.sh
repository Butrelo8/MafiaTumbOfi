#!/usr/bin/env bash
# Crawl test for a render setting on 24 frames: compose the layers in <capas_dir> over 1 s with the kept move's
# per-frame speed (7 s push and drift / 7), render, run revisar, print its crawl/flicker rows.
#   effectcraft/prueba-ruido.sh <capas_dir with bg fig fg (>= 24 frames each)> <name>
# Outputs in blender/render/effectcraft/ruido/<name>.{ecproj,mp4} and revisar-<name>/.
set -euo pipefail
cd "$(dirname "$0")/.."
capas=$1 name=$2
out=blender/render/effectcraft/ruido
mkdir -p "$out"
tmp=$(mktemp -d /tmp/ruido.XXXX)   # EffectCraft's render --out cuts paths at spaces: render to /tmp, then move
trap 'rm -rf "$tmp"' EXIT
effectcraft/componer.sh 1920 1080 "$capas" "$out/$name.ecproj" 0.0142857 20 5.714 1 > /dev/null
effectcraft-cli --project "$out/$name.ecproj" render --comp Cabina --format h264 --out "$tmp/$name.mp4" > /dev/null
mv "$tmp/$name.mp4" "$out/$name.mp4"
REVISAR_OUT="$out/revisar-$name" ~/projects/visual-lab/scripts/revisar.sh "$out/$name.mp4" 2>&1 | grep -E '^(crawl|flicker)' \
  | sed "s/^/$name  /" || true   # revisar exits 1 on a FAIL row: the numbers are the output here

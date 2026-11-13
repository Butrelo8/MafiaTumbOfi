#!/usr/bin/env bash
# Build the cab composition in EffectCraft from rendered layers and render it.
#   effectcraft/componer.sh <W> <H> <capas_dir> <out.ecproj> [PUSH] [APERTURA] [DERIVA] [DUR]
#   then:  effectcraft-cli --project <out.ecproj> render-frame --comp Cabina --time 6.9 --out f.png
#          effectcraft-cli --project <out.ecproj> render --comp Cabina --format h264 --out clip.mp4 --progress
# Defaults are the kept variant (see docs/effectcraft-piloto.md).
set -euo pipefail
here=$(dirname "$(realpath "$0")")
W=$1 H=$2 capas=$(realpath "$3") out=$4
PUSH=${5:-0.10} APERTURA=${6:-20} DERIVA=${7:-$((W / 48))} DUR=${8:-7}   # kept variant C: 10 % push, aperture 20, drift 40 px at 1920
GRANO=${GRANO:-0}   # Remove Grain noise reduction (2 passes + temporal) on the three layers; 0 = off
jsx=$(mktemp --suffix=.jsx)
trap 'rm -f "$jsx"' EXIT
printf 'var W=%s, H=%s, CAPAS="%s", PUSH=%s, APERTURA=%s, DERIVA=%s, DUR=%s, GRANO=%s;\n' "$W" "$H" "$capas" "$PUSH" "$APERTURA" "$DERIVA" "$DUR" "$GRANO" > "$jsx"
cat "$here/composicion.jsx" >> "$jsx"
effectcraft-cli --empty script "$jsx" --save-as "$out"

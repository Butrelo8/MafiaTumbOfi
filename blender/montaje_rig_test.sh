#!/usr/bin/env bash
# Regression test: a rigged clip placed through one root empty keeps its bone-parented parts on the bone (montaje_rig_test.py).
# Exit 0 PASS, 1 FAIL. Default clip: the interim Diego the integration build uses.
set -euo pipefail
cd "$(dirname "$0")/.."
CLIP=${1:-'\\wsl.localhost\Ubuntu\home\black\cc-out\mto-integracion\assets\diego_clip_sitting_drinking_sip.blend'}
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/montaje_rig_test.py)" -- "$CLIP" \
  2>&1 | grep '^RIGTEST\|Traceback\|Error'
exit "${PIPESTATUS[0]}"

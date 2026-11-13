#!/usr/bin/env bash
# Round checks for the buttons-icons pair run: revisar.sh web on a built page, each state, both themes, reduced motion.
# Usage: scripts/revisar-botones.sh <url> <out dir>   (the site has one dark theme; light is shot to prove it renders the same)
set -uo pipefail
url=$1; out=$2
RV=/home/black/projects/visual-lab/scripts/revisar.sh
BANDS=40-80,150-250,350-500
mkdir -p "$out"
run() { # name, extra flags...
  local n=$1; shift
  REVISAR_OUT="$out/$n" "$RV" "$url" --motion "$BANDS" "$@" > "$out/$n.log" 2>&1
  echo "$n exit $? FAIL=$(grep -c $'\tFAIL' "$out/$n/table.tsv" 2>/dev/null)"
}
run base-dark --theme dark
run base-light --theme light
run mid-dark --scroll mid --theme dark
run end-dark --scroll end --theme dark
run toggle-pressed --state '#pausa' --theme dark
run reduce --reduce --theme dark

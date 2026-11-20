#!/bin/bash
# TTFF Fast 4G 390, interleaved, 3 runs each (scripts/medir-vivo.mjs with SOLO_TTFF=1: only its TTFF block, ~1 min a run).
#   scripts/g63/ttff.sh <version-id> [<version-id> ...]   e.g. 8db7f25c b8554362 (first = the baseline); run with run_in_background
# Each id is the 8-char prefix of a Worker version: https://<id>-mafiatumbada.bube-ncio8.workers.dev. Output: $O/<id>-<run>/log.txt.
cd "$(dirname "$0")/../.."
O=${O:-/mnt/e/tmp/mto-g63-nuevo/ttff}
for i in 1 2 3; do
  for v in "$@"; do
    mkdir -p $O/$v-$i
    PW='E:\tmp\pw-vivo\node_modules\playwright-core' CHROME='C:\Program Files\Google\Chrome\Application\chrome.exe' SOLO_TTFF=1 WSLENV=PW:CHROME:SOLO_TTFF timeout 900 node.exe "$(wslpath -w scripts/medir-vivo.mjs)" https://$v-mafiatumbada.bube-ncio8.workers.dev/ "$(wslpath -w $O/$v-$i)" > $O/$v-$i/log.txt 2>&1
    echo "$v run $i: $(grep -o '"ttff_ms": [0-9]*' $O/$v-$i/log.txt) $(grep -o '"bytes_total": [0-9]*' $O/$v-$i/log.txt)"
  done
done
echo TTFF hecho

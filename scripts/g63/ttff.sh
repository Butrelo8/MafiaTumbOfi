#!/bin/bash
# TTFF Fast 4G 390, interleaved old / new, 3 runs each (scripts/medir-vivo.mjs). Old = d7f18f1c (the 6x6), new = the G63.
cd "/mnt/e/Cursor Projects/MTO-shookdrone"
O=/mnt/e/tmp/mto-g63-nuevo/ttff
for i in 1 2 3; do
  for v in d7f18f1c 016866e9; do
    mkdir -p $O/$v-$i
    PW='E:\tmp\pw-vivo\node_modules\playwright-core' CHROME='C:\Program Files\Google\Chrome\Application\chrome.exe' WSLENV=PW:CHROME timeout 900 node.exe "$(wslpath -w scripts/medir-vivo.mjs)" https://$v-mafiatumbada.bube-ncio8.workers.dev/ "$(wslpath -w $O/$v-$i)" > $O/$v-$i/log.txt 2>&1
    echo "$v run $i: $(grep -o '"ttff_ms": [0-9]*' $O/$v-$i/log.txt) $(grep -o '"bytes_total": [0-9]*' $O/$v-$i/log.txt)"
  done
done
echo TTFF hecho

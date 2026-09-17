#!/usr/bin/env bash
# Falla si un visitante baja más de lo que dice la spec.
#
# Objetivo 2 MB, techo duro 3 MB, y cada visitante baja un solo formato, así
# que se mide el más pesado de los dos, no la suma.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TECHO_MB=3.0

python3 - "$RAIZ" "$TECHO_MB" <<'PY'
import json
import sys

raiz, techo = sys.argv[1], float(sys.argv[2])
datos = json.load(open("%s/src/data/scene.json" % raiz, encoding="utf-8"))

peor, salida = 0.0, 0
for nombre, formato in datos["formatos"].items():
    mb = formato["bytes"] / 1024 / 1024
    estado = "OK" if mb <= techo else "PASADO"
    print("%-8s %5.2f MB  %s" % (nombre, mb, estado))
    peor = max(peor, mb)
    if mb > techo:
        salida = 1

print("peor caso %.2f MB de %.1f MB de techo (objetivo 2.0)" % (peor, techo))
sys.exit(salida)
PY

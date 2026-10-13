#!/usr/bin/env bash
# Puerta antes de lanzar una tanda: comprueba lo que un script puede comprobar. Lo único que queda para el usuario es
# aprobar la hoja de Cycles por estación (abajo). Cada punto salió de un fallo real (docs/skills-audit-2026-10-12.md).
#
#   puerta-tanda.sh blender <movil|escritorio> [volcado.json]   antes de `blender/render.py -- tramos …`
#   puerta-tanda.sh comfy                                       antes de encolar H3/Klein
#
# Flujo fijar → puerta → tanda (Blender):
#   1. Fijar: el usuario coloca en el visor; `poses.volcar(tmp/poses-referencia.json)` ANTES de reconstruir; pasar las
#      poses a constantes de altar.py; reconstruir; `poses.comparar` sin diferencias; volver a volcar la referencia.
#   2. Hoja de Cycles por estación (no Eevee: oro y cromo salen negros y el humo no se ve), a pocas muestras:
#        r = {}; exec(open(r"E:\Cursor Projects\MTO\blender\render.py").read(), r); r["MUESTRAS"] = 32
#        r["estaciones"]("<formato>", r"E:\Cursor Projects\MTO\tmp\frames\prueba-<formato>")
#      y `scripts/comparar.sh hoja tmp/frames/hoja-prueba tmp/frames/prueba-<formato>`. La aprueba el usuario.
#   3. Puerta: este script. 4. Tanda en segundo plano (la orden sale al final) y, ante un cambio tardío, sólo los
#      tramos donde se ve lo que cambió: `-- tramos <formato> <desde> <hasta>`, nunca el render completo.
set -uo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER=${BLENDER:-/mnt/e/Blender/blender.exe}
que=${1:?uso: puerta-tanda.sh blender <movil|escritorio> [volcado.json] | comfy}
fallos=0
mal() { echo "FALLA $*"; fallos=$((fallos + 1)); }
bien() { echo "OK    $*"; }

case $que in
blender)
  formato=${2:?formato: movil|escritorio}; volcado=${3:-$RAIZ/tmp/poses-referencia.json}
  [ -f "$volcado" ] || { mal "no existe el volcado $volcado"; volcado=""; }
  [ -n "$volcado" ] && echo "      volcado: $volcado ($(date -r "$volcado" '+%F %R')); tiene que ser el del visor de hoy"

  # 1-2. Escena recién construida (como la construye render.py) contra el volcado, y banderas de los pases.
  arg=None; [ -n "$volcado" ] && arg="r\"$(wslpath -w "$volcado")\""
  py=$(mktemp --suffix=.py -p "$RAIZ/tmp")
  cat > "$py" <<EOF
import json
r = {"__name__": "puerta"}
exec(open(r"$(wslpath -w "$RAIZ/blender/render.py")", encoding="utf-8").read(), r)
r["construir"]()
pt = {}
exec(open(r"$(wslpath -w "$RAIZ/blender/puerta.py")", encoding="utf-8").read(), pt)
print("PUERTA " + json.dumps(pt["revisar"]($arg), ensure_ascii=False))
EOF
  sal=$("$BLENDER" -b --python "$(wslpath -w "$py")" 2>&1); rm -f "$py"
  res=$(grep '^PUERTA ' <<<"$sal" | cut -c8-)
  if [ -z "$res" ]; then
    mal "la escena no se construyó en segundo plano:"; grep -iE 'error|traceback' <<<"$sal" | tail -5
  else
    python3 -c 'import json,sys; r=json.loads(sys.argv[1]); [print("FALLA", p) for p in r["problemas"]]; sys.exit(not r["ok"])' "$res" \
      && bien "escena: poses iguales al volcado y banderas de render en su sitio" || fallos=$((fallos + 1))
  fi

  # 3. Un PNG de destino abierto en un visor de Windows hace fallar el render con "cannot save" (64d1fcbf).
  dest="$RAIZ/tmp/frames/$formato"
  if [ -d "$dest" ] && compgen -G "$dest/*" >/dev/null; then
    bloqueados=$(powershell.exe -NoProfile -Command "Get-ChildItem -Recurse -Filter *.png '$(wslpath -w "$dest")' | ForEach-Object {
      try { \$f = [IO.File]::Open(\$_.FullName, 'Open', 'ReadWrite', 'None'); \$f.Close() } catch { \$_.TargetObject; \$_.Exception.Message } }" 2>&1 | tr -d '\r')
    [ -z "$bloqueados" ] && bien "ningún PNG de $dest abierto en otro programa" || mal "PNG abiertos (cerrar el visor): $bloqueados"
  else
    bien "sin PNG previos en $dest"
  fi

  # 4. Disco: un pase en PNG de 16 bits ocupó 933 MB (docs/HANDOFF.md).
  libre=$(df -BG --output=avail "$RAIZ" | tail -1 | tr -dc 0-9)
  [ "$libre" -ge "${MIN_GB:-5}" ] && bien "disco: $libre GB libres" || mal "disco: $libre GB libres (< ${MIN_GB:-5})"

  echo
  echo "Tanda (segundo plano):"
  echo "  \"$BLENDER\" -b -P \"$(wslpath -w "$RAIZ/blender/render.py")\" -- tramos $formato [desde hasta] > tmp/tanda-$formato.log 2>&1"
  echo "  scripts/esperar.sh --tope 21600 log tmp/tanda-$formato.log '^render: '"
  ;;
comfy)
  API=http://$(ip route | awk '/default/{print $3; exit}'):8188
  if q=$(curl -sm5 "$API/queue"); then
    read -r corre espera < <(python3 -c 'import json,sys; q=json.loads(sys.argv[1]); print(len(q["queue_running"]), len(q["queue_pending"]))' "$q")
    bien "ComfyUI responde ($corre en curso, $espera en cola)"
    # Colgado en "Model Initializing" (4 veces): la cola no baja. POST /interrupt no basta.
    [ "$corre" -gt 0 ] && echo "      hay un trabajo en curso: si no avanza, powershell.exe -File 'E:\\ComfyUI\\start-comfy.ps1'"
  else
    mal "ComfyUI no responde en $API"
  fi
  libre=$(df -BG --output=avail /mnt/e | tail -1 | tr -dc 0-9)
  [ "$libre" -ge "${MIN_GB:-5}" ] && bien "disco E: $libre GB libres" || mal "disco E: $libre GB libres"
  ;;
*) echo "no conozco '$que': blender|comfy"; exit 1 ;;
esac
exit $fallos

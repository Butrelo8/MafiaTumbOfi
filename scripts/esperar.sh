#!/usr/bin/env bash
# Espera algo con tope de tiempo, sin bloquear el hilo: lanzarlo con run_in_background o desde Monitor,
# nunca en primer plano (el arnés bloquea `sleep`).
#
#   esperar.sh [--tope S] archivos N <glob>     hasta que existan N archivos que casan con <glob> (entre comillas)
#   esperar.sh [--tope S] cola                  hasta que la cola de ComfyUI quede vacía (running + pending)
#   esperar.sh [--tope S] log <archivo> <regex> hasta que <regex> aparezca en el log; ERROR/Traceback cortan antes
#
# Salida: 0 = listo, 1 = tope de tiempo, 2 = error (log con ERROR, ComfyUI no responde).
# Tope por omisión 3600 s. Una cola que no baja en el tope suele ser el cuelgue en "Model Initializing":
# `powershell.exe -File 'E:\ComfyUI\start-comfy.ps1'` lo reinicia (~1 min; POST /interrupt no basta).
set -euo pipefail
TOPE=3600
[ "${1:-}" = --tope ] && { TOPE=$2; shift 2; }
modo=${1:?uso: esperar.sh [--tope S] archivos N <glob> | cola | log <archivo> <regex>}; shift
API=http://$(ip route | awk '/default/{print $3; exit}'):8188  # ComfyUI en Windows visto desde WSL, como gen.sh
fin=$(( $(date +%s) + TOPE ))

listo() {
  case $modo in
    archivos) local n; n=$(compgen -G "$2" | wc -l || true); [ "$n" -ge "$1" ] ;;
    cola)
      local q; q=$(curl -sm5 "$API/queue") || { echo "ComfyUI no responde en $API"; exit 2; }
      python3 -c 'import json,sys; q=json.load(sys.stdin); sys.exit(len(q["queue_running"])+len(q["queue_pending"])>0)' <<<"$q" ;;
    log)
      [ -f "$1" ] || return 1
      if grep -qE 'ERROR|Traceback' "$1"; then echo "error en $1:"; grep -E 'ERROR|Traceback' "$1" | tail -3; exit 2; fi
      grep -qE "$2" "$1" ;;
    *) echo "modo desconocido: $modo"; exit 2 ;;
  esac
}

until listo "$@"; do
  [ "$(date +%s)" -ge "$fin" ] && { echo "tope de $TOPE s: $modo $*"; exit 1; }
  sleep 5
done
echo "listo: $modo $*"

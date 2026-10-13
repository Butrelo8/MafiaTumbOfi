#!/usr/bin/env bash
# Comprueba el entorno al arrancar sesión, antes de que falle a mitad de una tanda:
# el puerto del MCP de Blender, que ComfyUI responda y que `uv run --with numpy,pillow` funcione.
# Salida: 0 si todo está bien; si no, el número de comprobaciones que fallaron.
set -uo pipefail
HOST=$(ip route | awk '/default/{print $3; exit}')  # Windows visto desde WSL (en modo NAT)
PUERTO=${BLENDER_MCP_PORT:-9877}
fallos=0

abierto() { timeout 3 bash -c "exec 3<>/dev/tcp/$1/$2" 2>/dev/null; }

if abierto 127.0.0.1 "$PUERTO" || abierto "$HOST" "$PUERTO"; then
  echo "OK    Blender MCP escucha en $PUERTO"
elif win=$(powershell.exe -NoProfile -Command "(Get-NetTCPConnection -State Listen -LocalPort $PUERTO -ErrorAction SilentlyContinue).LocalAddress" 2>/dev/null | tr -d '\r') && [ -n "$win" ]; then
  # El servidor MCP (uvx.exe) corre en Windows: le basta que el add-on escuche en el localhost de Windows.
  echo "OK    Blender MCP escucha en Windows $win:$PUERTO (WSL no lo ve; para el MCP no hace falta)"
else
  fallos=$((fallos + 1))
  cat <<EOF
FALLA Blender MCP: nadie escucha en $PUERTO, ni desde WSL ni en Windows
      - ¿Blender abierto con el add-on del MCP iniciado? (tasklist.exe | grep -i blender)
      - El add-on de Blender va en $PUERTO, no en 9876: el 9876 es de CursorBridge (Resolve). Ver .mcp.json.
      - Con WSL en modo NAT, el add-on tiene que escuchar en 0.0.0.0 (no en 127.0.0.1) para que WSL lo vea en $HOST.
        Con networking mirrored (.wslconfig) basta 127.0.0.1.
      - Si Blender ya está arriba con el add-on conectado, reconectar el MCP con /mcp.
EOF
fi

API=http://$HOST:8188
if curl -sm5 "$API/system_stats" >/dev/null; then
  q=$(curl -sm5 "$API/queue" | python3 -c 'import json,sys; q=json.load(sys.stdin); print(len(q["queue_running"]), len(q["queue_pending"]))' 2>/dev/null)
  echo "OK    ComfyUI responde en $API (cola: ${q:-?} en curso/pendientes)"
else
  fallos=$((fallos + 1))
  echo "FALLA ComfyUI no responde en $API: powershell.exe -File 'E:\\ComfyUI\\start-comfy.ps1' (gen.sh lo arranca solo)"
fi

if out=$(uv run -q --with numpy --with pillow python -I -c 'import numpy, PIL; print(numpy.__version__, PIL.__version__)' 2>&1); then
  echo "OK    uv run --with numpy --with pillow: $out"
else
  fallos=$((fallos + 1))
  echo "FALLA uv run --with numpy --with pillow: $(tail -1 <<<"$out")"
fi
exit $fallos

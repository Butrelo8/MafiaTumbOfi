#!/usr/bin/env bash
# PreToolUse de Bash: frena dos errores que se re-aprendían pese a estar escritos (research/skills-audit-2026-10-12.md, propuesta 7).
# 1. `sleep` en primer plano (bucles until/while que bloquean el hilo esperando un trabajo: 2.17 h en 21 sesiones).
# 2. python/python3 del sistema con numpy, cv2 o PIL (no están instalados: 3 sesiones).
entrada=$(cat)
cmd=$(jq -r '.tool_input.command // ""' <<<"$entrada")
fondo=$(jq -r '.tool_input.run_in_background // false' <<<"$entrada")

negar() {
  jq -n --arg r "$1" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}

if [ "$fondo" != true ] && grep -qE '(^|[;&|(]|\bdo|\bthen)[[:space:]]*sleep[[:space:]]+[0-9]' <<<"$cmd"; then
  negar "sleep en primer plano bloquea el hilo. Espera con scripts/esperar.sh (archivos N <glob> | cola | log <archivo> <regex>, siempre con --tope) lanzado con run_in_background, o desde Monitor."
fi

# python directo (no detrás de `uv run … python`) que carga numpy/cv2/PIL
if grep -qE '(^|[;&|(]|\bthen|\bdo)[[:space:]]*python3?([[:space:]]|$)' <<<"$cmd" && grep -qE '\b(numpy|cv2|PIL)\b' <<<"$cmd"; then
  negar "El python3 del sistema no tiene numpy/cv2/PIL. Usa: uv run -q --with numpy --with opencv-python-headless --with pillow python -I …"
fi
exit 0

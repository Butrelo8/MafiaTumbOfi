"""Regression probe for the glovebox "weird triangle" (owner, 03:30): the cut door must be the front skin only. The triangle was
the bin's sloped floor riding up with the door; its back corner sat at y 1.3465, 0.11 m behind the dash face. Builds the scene
through utileria.py without renders, cuts the glovebox and checks how deep the door's vertices reach before the swing
(CORTE["hi"].y against GUANTERA.y). Exit 1 above TOPE. Old code (a38984e): 0.112 FAIL; fixed: 0.001 PASS.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/probe_guantera.py)" -- \
    "$(wslpath -w /mnt/e/Cursor\ Projects/MTO/blender/escena.py)" "$(wslpath -w tmp/utileria)" 1 ninguno 1280x720 "$(wslpath -w blender/utileria.py)"
"""
import sys

TOPE = 0.04  # m behind the dash face: the skin's own lean stays inside it, the bin floor and side walls run 0.2 m deep
U = sys.argv[sys.argv.index("--") + 1 + 5]
g = {"__file__": U, "__name__": "u"}
exec(compile(open(U, encoding="utf8").read(), U, "exec"), g)
c = g["cortar_guantera"]()
fondo = c["hi"].y - g["GUANTERA"].y
print("PROBE fondo", round(fondo, 4), "tope", TOPE, "FAIL" if fondo > TOPE else "PASS")
sys.exit(1 if fondo > TOPE else 0)

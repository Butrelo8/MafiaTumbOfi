"""Regression probe for the glovebox "weird triangle" (owner, 03:30): the cut door must be the front skin only. The triangle was
the bin's sloped floor riding up with the door; its back corner sat at y 1.3465, 0.11 m behind the dash face. Builds the scene
through utileria.py without renders, cuts the glovebox and checks how deep the door's vertices reach before the swing
(CORTE["hi"].y against GUANTERA.y). Exit 1 above TOPE. Old code (a38984e): 0.112 FAIL; fixed: 0.001 PASS.
CORTE["lo"/"hi"] must stay the DOOR's bbox: if the inner box is resized to the full cut, give it its own keys and leave these.
Second check: the dark inner box (CORTE["caja_lo"/"caja_hi"]) must cover the hole left in the dash (CORTE["hueco_lo"/"hueco_hi"],
every vertex of the removed faces) in x and z. After the door became the front skin only (11.6 cm), the box spanned z 1.279-1.395
while the hole reached z 1.194: a dark band under the door in guantera2-borde. Box from the door: falta 0.082 FAIL; from the hole: -0.003 PASS.

Third check: nothing of the box may stand in front of the dash face below the hinge (lo.z). Box slabs started at the top of the
leaning skin (y lo.y), 9 cm in front of the dash at the hinge (y hi.y): a second ledge under the open door. Horizontal rays from the
cabin at the walls and the centre, z between the hole's bottom and 1 cm under the hinge (the open door hangs above that); the
box's first hit (material u_hueco; the open door hangs in front on purpose) must lie no more than 1 cm in front of hi.y.

Fourth check ("asoma"): no vertex of the door copies may stand above the liner's top face inside its footprint (the liner sat 2-10
mm off the skin's mid plane, the skin bulges, and a door edge showed through as a dark sliver on the left in guantera2-borde).

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
EPS = 0.002
falta = max(c["caja_lo"].x - c["hueco_lo"].x, c["hueco_hi"].x - c["caja_hi"].x, c["caja_lo"].z - c["hueco_lo"].z, c["hueco_hi"].z - c["caja_hi"].z)
print("PROBE hueco", tuple(round(v, 3) for v in (*c["hueco_lo"], *c["hueco_hi"])), "caja", tuple(round(v, 3) for v in (*c["caja_lo"], *c["caja_hi"])),
      "falta", round(falta, 4), "FAIL" if falta > EPS else "PASS")
import bpy
from mathutils import Vector
for o in g["FIGURAS"]:  # Héctor sits in front of the glovebox
    o.hide_viewport = True
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
lo, hi, hlo, hhi = c["lo"], c["hi"], c["hueco_lo"], c["hueco_hi"]
sale = -1.0
for x in (hlo.x + 0.002, (hlo.x + hhi.x) / 2, hhi.x - 0.002):
    for z in (hlo.z + 0.001, (hlo.z + lo.z) / 2, lo.z - 0.01):
        o = Vector((x, hi.y - 0.3, z))
        for _ in range(20):  # the box's own first hit: the open door and its liner hang in front of the dash on purpose
            hit, loc, n, i, ob, m = bpy.context.scene.ray_cast(dg, o, Vector((0, 1, 0)))
            if not hit:
                break
            if any(ms.material and ms.material.name.startswith("u_hueco") for ms in ob.material_slots):
                sale = max(sale, hi.y - loc.y)
                break
            o = loc + Vector((0, 0.0005, 0))
print("PROBE sale", round(sale, 4), "tope 0.01", "FAIL" if sale > 0.01 else "PASS")
# Fourth check: no door vertex may stand above the liner's top face inside its footprint. The skin is not flat, so with the liner
# 2-10 mm off the skin's mid plane a door edge poked through on the left: a thin dark sliver in guantera2-borde (05:35 handoff).
liner = next(o for o in c["objs"] if o.type == "MESH" and any(ms.material and ms.material.name == "u_guantera_int" for ms in o.material_slots))
inv, sy = liner.matrix_world.inverted(), liner.scale.y
asoma = -1.0
for o in c["objs"]:
    if o.type != "MESH" or any(ms.material and ms.material.name.startswith("u_") for ms in o.material_slots):
        continue  # door copies only (the truck's own materials)
    for v in o.data.vertices:
        l = inv @ (o.matrix_world @ v.co)
        if abs(l.x) <= 1 and abs(l.z) <= 1:
            asoma = max(asoma, (l.y - 1) * sy)
print("PROBE asoma", round(asoma, 4), "tope 0", "FAIL" if asoma > 0 else "PASS")
sys.exit(1 if fondo > TOPE or falta > EPS or sale > 0.01 or asoma > 0 else 0)

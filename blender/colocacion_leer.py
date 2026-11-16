"""Reads the owner's placement back from a colocar-*.blend (blender/colocacion_blend.py) into blender/props/colocacion.json: the
screen's empty `pantalla_consola`, the stickers' `calca_<id>` and the instruments' `inst_<id>`, whichever the file holds. Run once per
file; it prints each value it changed.

  /mnt/e/Blender/blender.exe -b "$(wslpath -w colocar-calcas.blend)" --python "$(wslpath -w blender/colocacion_leer.py)"
"""
import bpy, json, os

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "props", "colocacion.json")
d = json.load(open(RUTA, encoding="utf8"))
r = lambda v: [round(x, 4) + 0.0 for x in v]  # + 0.0: no -0.0


def poner(sec, clave, nuevo):
    viejo = d[sec].get(clave)
    if viejo != nuevo:
        print("COLOCACION", sec, clave, viejo, "->", nuevo)
    d[sec][clave] = nuevo


for e in bpy.data.objects:
    if e.type != "EMPTY" or e.hide_select:  # only this file's item: colocar-calcas also holds the screen and instruments, locked
        continue
    loc, rot, s = e.matrix_world.translation, e.matrix_world.to_euler("XYZ"), round(e.matrix_world.to_scale().x, 4)
    if e.name == "pantalla_consola":
        poner("pantalla", "loc", r(loc)); poner("pantalla", "rot", r(rot)); poner("pantalla", "escala", s)
    elif e.name.startswith("calca_"):
        c = dict(d["calcas_r1"][e["calca"]])
        c.update(u=round(loc.x - e["cx"] if e["cara"] == "porton" else loc.y, 4), z=round(loc.z, 4), rot=round(e.rotation_euler.y, 4), escala=s)
        poner("calcas_r1", e["calca"], c)
    elif e.name.startswith("inst_"):
        k = e.name[5:]
        poner("instrumentos", k, {"loc": r(loc), "rot": r(rot), "escala": s})
with open(RUTA, "w", encoding="utf8", newline="\n") as f:  # Windows Blender would write CRLF
    f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("COLOCACION escrito", RUTA)

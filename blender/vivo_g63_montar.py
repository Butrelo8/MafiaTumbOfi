"""Live scene with the new G63, step 1 (owner 2026-11-20): on blender/g63_rack.py's output (car + rack + load + net) it adds the cab
dressing the old truck carried (strawberry, pennant, fringe with its velvet plates and banner, MT emblem, Veracruz plate), each as its
own object or empty so the owner can drop or move it, and measures what vivo.json needs (headlamps, wheel radius, boxes).
The old bed's rail bulbs and wire, the roof LED row and the Tripo seats / console / roof pod are NOT carried (owner: bulbs out; the
new car has its own seats and console).

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <g63-rack.blend> --python-exit-code 1 --python blender/vivo_g63_montar.py \
    -- <out .blend (Windows)> <live escena.glb with the dressing (Windows)>

Writes <out>.blend and <out>-datos.json.
"""
import bpy, json, math, os, sys
from mathutils import Matrix, Vector

SAL = sys.argv[sys.argv.index("--") + 1]
VIEJO = sys.argv[sys.argv.index("--") + 2]
O = bpy.data.objects
sc = bpy.context.scene
cam = O["camion"]

for n in ("carga_correas", "carga_cable"):
    if n in O:
        O.remove(O[n], do_unlink=True)

# ---------------------------------------------------------------- dressing from the live scene's own glb
GRUPOS = {  # empty -> the old materials it carries, and its offset from the old truck's coordinates (dy, dz): the windshield header
    # of the old cab sat at y 1.05-1.15, z 1.95-2.04; the new one at y ~1.08, z ~1.80
    "vest_flecos": (("pp_fleco", "pp_terciopelo", "pp_oro_luz_1.5", "pp_franja", "pp_franja_letra"), (0.0, -0.20)),
    "vest_fresa": (("semilla_oro", "tripo_material_1f145cae-61f3-42c1-9906-b0e6cc88165a"), (0.12, -0.33)),
    "vest_banderin": (("u_oro",), (0.55, -0.62)),
}
SUELTOS = {"vest_emblema": ("pp_oro_marca",), "vest_placa": ("u_placa_alu", "u_placa_vz")}  # placed by ray against the new nose
antes = set(O)
bpy.ops.import_scene.gltf(filepath=VIEJO)
nuevos = [o for o in O if o not in antes]
por_grupo = {k: [] for k in list(GRUPOS) + list(SUELTOS)}
for o in nuevos:
    if o.type != "MESH":
        continue
    mats = {m.name.split(".")[0] for m in o.data.materials if m}
    for k, (ms, _) in GRUPOS.items():
        if mats & set(ms):
            por_grupo[k].append(o)
    for k, ms in SUELTOS.items():
        if mats & set(ms):
            por_grupo[k].append(o)
for o in nuevos:  # bake world coordinates of the old truck into every kept mesh
    if o.type == "MESH" and any(o in v for v in por_grupo.values()):
        if o.data.users > 1:  # the 44 fringe strands share one mesh: transforming it once per user compounds (first run: x 75, y 46)
            o.data = o.data.copy()
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(mw)
        o.matrix_world = Matrix.Identity(4)
for o in nuevos:
    if not any(o in v for v in por_grupo.values()):
        O.remove(o, do_unlink=True)
# this glb was already imported by g63_rack.py (the props): its materials came back as pp_fleco.001 ... and the page matches the exact
# names (vivoSecciones.ts flecoMats), so every kept slot goes back to its un-suffixed material
import re
for k in por_grupo.values():
    for o in k:
        for sl in o.material_slots:
            m = sl.material
            if m and re.search(r"\.\d{3}$", m.name):
                base = bpy.data.materials.get(m.name.rsplit(".", 1)[0])
                if base:
                    sl.material = base
for k, (ms, (dy, dz)) in GRUPOS.items():
    e = O.new(k, None) if hasattr(O, "new") else bpy.data.objects.new(k, None)
    sc.collection.objects.link(e)
    e.parent = cam
    e.matrix_parent_inverse = Matrix.Identity(4)
    e.location = (0, dy, dz)
    for o in por_grupo[k]:
        o.parent = e
        o.matrix_parent_inverse = Matrix.Identity(4)
    print("G63 vestuario", k, len(por_grupo[k]), "objetos, desplazado", (0, dy, dz), flush=True)

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
cuerpo = [o for o in cam.children if o.name.startswith("g63_")]


def rayo(origen, dir):
    ok, loc, n, i, o, M = sc.ray_cast(dg, origen, dir)
    return (loc, n, o) if ok and o.parent == cam and o.name.startswith("g63_") else (None, None, None)


# emblem and plate on the new nose: ray from 3 m ahead along -y at the cars's centre line
for k, z in (("vest_emblema", 1.17), ("vest_placa", 0.50)):
    objs = por_grupo[k]
    vs = [v.co for o in objs for v in o.data.vertices]
    c = Vector((sum(v.x for v in vs) / len(vs), sum(v.y for v in vs) / len(vs), sum(v.z for v in vs) / len(vs)))
    ext = Vector((max(v.x for v in vs) - min(v.x for v in vs), max(v.y for v in vs) - min(v.y for v in vs), max(v.z for v in vs) - min(v.z for v in vs)))
    loc, n, ob = rayo(Vector((1.72, 4.0, z)), Vector((0, -1, 0)))
    print("G63", k, "extension", [round(v, 3) for v in ext], "superficie en", [round(v, 3) for v in loc] if loc else None, ob.name if ob else None, flush=True)
    e = bpy.data.objects.new(k, None)
    sc.collection.objects.link(e)
    e.parent = cam
    e.matrix_parent_inverse = Matrix.Identity(4)
    y_sup = loc.y if loc else 2.9
    # the emblem's flat face looks along +y (its thickness is the y extent): its back sits on the surface
    e.location = (1.72 - c.x, y_sup - (c.y - ext.y / 2) + 0.004, z - c.z)
    for o in objs:
        o.parent = e
        o.matrix_parent_inverse = Matrix.Identity(4)
    print("G63 vestuario", k, len(objs), "objetos en", [round(v, 3) for v in e.location], flush=True)

# ---------------------------------------------------------------- numbers for vivo.json
bpy.context.view_layer.update()
drl = O.get("g63_luz_drl")
faros = []
if drl:
    vs = [v.co.copy() for v in drl.data.vertices]
    for lado in (-1, 1):
        g = [v for v in vs if (v.x - 1.72) * lado > 0]
        c = sum(g, Vector()) / len(g)
        faros.append({"pos": [round(c.x, 4), round(max(v.y for v in g) + 0.05, 4), round(c.z, 4)], "mira": [round(c.x, 4), round(max(v.y for v in g) + 10.0, 4), round(c.z - 0.6, 4)]})
ru = [o for o in cam.children if o.name.startswith("rueda")]
radio = 0.0
for r in ru:
    vs = [v.co for v in r.data.vertices]
    radio = max(radio, max(math.hypot(v.y, v.z) for v in vs))
print("G63 faros", faros, "radio rueda", round(radio, 3), flush=True)


def caja(objs):
    ps = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return {"min": [min(p[i] for p in ps) for i in range(3)], "max": [max(p[i] for p in ps) for i in range(3)]}


cuerpo_vis = [o for o in cam.children if o.type == "MESH" and not o.name.startswith(("rueda", "k3_", "rack_", "carga_", "vest_"))]
carga = [o for o in cam.children_recursive if o.type == "MESH" and o.name.startswith(("k3_", "rack_", "carga_"))]
datos = {"faros": faros, "radio_rueda": radio, "cuerpo": caja(cuerpo_vis), "ruedas": caja(ru), "carga": caja(carga),
         "ruedas_nombres": sorted(r.name for r in ru)}
json.dump(datos, open(os.path.splitext(SAL)[0] + "-datos.json", "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("G63 montado", SAL, flush=True)

"""The owner's new G63 (blender/assets/g63-nuevo/g63.blend, 2026-11-20) made ready for the live page: baked into world space, scaled to
the real car, standing on the road in the cast's lane, its node-group shaders replaced by ~20 flat web materials (the glTF
exporter cannot read node groups), the four wheels split into rueda0-3 (rim, tyre, disc; hung from camion with their pivot at the
hub) and decimated hard, the rest joined per material. Interior meshes keep every triangle.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <g63.blend> --python-exit-code 1 --python blender/g63_nuevo.py \
    -- <out g63-listo.blend (Windows)>

Scale: the model's axle centres are 2.00 m apart (y -0.97 / +1.03) and the W463A's wheelbase is 2.890 m (cars-data.com, vehiclescore.co.uk),
so x1.445: length 4.93 m (spec 4.873), height 1.95 m (spec 1.966-1.969). The nose points -Y in the model; the page's trucks face +Y.
"""
import bpy, math, os, sys, json
from mathutils import Matrix, Vector

ESCALA = 1.445
CARRIL_X = 1.72           # the cast's lane (blender/escena.py MUNDO["carril_x"])
DY = 0.60                 # along the road: puts the front seats where the old cab's cast sat (hips y 0.59 front, -0.30 rear)
RUEDA = {"Rubber": 3500, "Rims ": 5000, "Rims 2": 5000, "Brake Disc": 900, "Brakes": 1500}   # tris per big wheel part
RESTO_RUEDA = 0.06        # the small bits of a wheel (hub, bolts, valve): this share of their triangles
CAP_EXT = 12000           # exterior parts above this are decimated to it (Carpaint, glass and the interior keep everything)
INTERIOR = ("Interior", "Leather", "Alcantara", "Stitch", "Belt", "Speakers", "Romb", "Display", "Clock", "Symbols", "Button")

# the model's material -> the canonical web material (specs below, from the model's own group colours, linear)
CANON = {
    "Carpaint": "carpaint",
    "Matte Plastic": "plastico", "Matte Plastic Interior": "plastico", "Glossy Plastic": "plastico", "Black gloss": "plastico",
    "Metal hex": "plastico", "Blue": "plastico", "Speakers": "plastico", "Symbols": "plastico", "Stitch ": "plastico",
    "Stitch 2": "plastico", "Engine sticker": "plastico",
    "Satin Metallic": "aluminio", "Satin Interior": "aluminio", "Aluminum": "aluminio", "Aluminum 2": "aluminio",
    "Button": "aluminio", "Heat protective foil": "aluminio",
    "Chrome": "cromo", "Chrome 2": "cromo", "Chrome 3": "cromo", "G Logo": "cromo",
    "Satin Metallic Black": "rin_negro", "Rims ": "rin_negro", "Rims 2": "rin_plata",
    "Rubber": "goma", "Brake Disc": "disco", "Brakes": "pinza", "Satin Metallic Red": "pinza", "Red plastic": "pinza",
    "Leather White": "piel_blanca", "Leather Perforated White": "piel_blanca", "Alcantara White": "piel_blanca",
    "Matte Plastic Interior White": "piel_blanca", "Romb": "piel_blanca", "Belt": "piel_blanca",
    "Leather Dark Brown": "piel_cafe", "Leather Perforated Brown": "piel_cafe", "Alcantara Dark Brown": "piel_cafe",
    "Carbon Fiber Glossy": "carbono", "Carbon Fiber Interior": "carbono",
    "Glass": "vidrio", "Rear glass": "vidrio", "Headlight glass": "vidrio_faro", "Tail glass": "vidrio_cola",
    "Front DRL": "luz_drl", "Tail lights": "luz_calavera", "Display": "pantalla", "Clock": "pantalla",
    "Reflector White": "reflector", "White Plastic": "reflector",
}
# canonical -> (base colour linear, metallic, roughness, emission colour or None, emission strength)
SPEC = {
    "carpaint": ((0.018, 0.059, 0.102), 0.55, 0.22, None, 0), "plastico": ((0.006, 0.006, 0.006), 0.2, 0.45, None, 0),
    "aluminio": ((0.35, 0.35, 0.35), 1.0, 0.3, None, 0), "cromo": ((0.8, 0.8, 0.8), 1.0, 0.08, None, 0),
    "rin_negro": ((0.02, 0.02, 0.02), 1.0, 0.35, None, 0), "rin_plata": ((0.513, 0.513, 0.513), 1.0, 0.3, None, 0),
    "goma": ((0.012, 0.012, 0.012), 0.0, 0.68, None, 0), "disco": ((0.3, 0.3, 0.3), 1.0, 0.5, None, 0),
    "pinza": ((0.5, 0.0, 0.01), 0.8, 0.5, None, 0), "piel_blanca": ((0.80, 0.72, 0.60), 0.0, 0.7, None, 0),
    "piel_cafe": ((0.022, 0.008, 0.007), 0.0, 0.7, None, 0), "carbono": ((0.012, 0.012, 0.012), 0.4, 0.35, None, 0),
    "vidrio": ((0.8, 0.8, 0.8), 1.0, 0.03, None, 0), "vidrio_faro": ((0.9, 0.9, 0.9), 0.0, 0.05, None, 0),
    "vidrio_cola": ((0.6, 0.02, 0.01), 0.0, 0.05, None, 0),
    "luz_drl": ((0.68, 0.815, 1.0), 0.0, 0.2, (0.68, 0.815, 1.0), 4.0),
    "luz_calavera": ((0.503, 0.0, 0.0), 0.0, 0.3, (0.9, 0.02, 0.01), 4.0),
    "pantalla": ((0.01, 0.012, 0.02), 0.0, 0.3, None, 0), "reflector": ((0.8, 0.8, 0.8), 0.0, 0.3, None, 0),
}


def material(nombre):
    m = bpy.data.materials.get("web_" + nombre)
    if m:
        return m
    col, met, rug, emi, est = SPEC[nombre]
    m = bpy.data.materials.new("web_" + nombre)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Metallic"].default_value = met
    p.inputs["Roughness"].default_value = rug
    if emi:
        p.inputs["Emission Color"].default_value = (*emi, 1)
        p.inputs["Emission Strength"].default_value = est
    return m


def caja(o):
    """Bounds from the vertices: Object.bound_box stays stale after Mesh.transform() until a depsgraph update."""
    import numpy as np
    a = np.empty(len(o.data.vertices) * 3, dtype=np.float32)
    o.data.vertices.foreach_get("co", a)
    a = a.reshape(-1, 3)
    return Vector(a.min(0)), Vector(a.max(0))


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def decimar(o, objetivo):
    n = tris(o)
    if objetivo >= n:
        return
    m = o.modifiers.new("dec", "DECIMATE")
    m.ratio = max(0.002, objetivo / n)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="dec")


def unir(objs, nombre):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    objs[0].name = nombre
    objs[0].data.name = nombre
    return objs[0]


def preparar():
    sc = bpy.context.scene
    O = bpy.data.objects
    for o in list(O):
        if o.type == "MESH" and o.data.users > 1:
            o.data = o.data.copy()
    mallas = [o for o in O if o.type == "MESH"]
    for o in mallas:  # world space, no hierarchy: the doors' empties carry scale 0.7 and rotation
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(mw)
        o.matrix_world = Matrix.Identity(4)
    for o in [o for o in O if o.type != "MESH"]:
        O.remove(o)
    pts = [v.co for o in mallas for v in o.data.vertices]
    zmin = min(p.z for p in pts)  # tyre bottom to z 0: the model's lowest vertex sits at -0.007
    M = Matrix.Translation((CARRIL_X, DY, -zmin * ESCALA)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(ESCALA, 4)
    for o in mallas:
        o.data.transform(M)
    gomas = [o for o in mallas if o.data.materials and o.data.materials[0].name == "Rubber" and tris(o) > 40000]
    assert len(gomas) == 4, len(gomas)
    centros = []
    for o in gomas:
        a, b = caja(o)
        centros.append((a + b) / 2)
    centros.sort(key=lambda c: (c.y, c.x))  # rueda0/1 rear, rueda2/3 front (+Y is forward now); x low = left
    partes = [[] for _ in centros]
    for o in mallas:
        a, b = caja(o)
        c, s = (a + b) / 2, b - a
        for i, w in enumerate(centros):
            if abs(c.x - w.x) < 0.17 and abs(c.y - w.y) < 0.46 and abs(c.z - w.z) < 0.43 and s.y < 0.9 and s.z < 0.9 and s.x < 0.43:
                partes[i].append(o)
                break
    ruedas = []
    for i, (w, ps) in enumerate(zip(centros, partes)):
        print("G63 grupo rueda", i, [round(v, 3) for v in w], len(ps), sorted((o.data.materials[0].name if o.data.materials else "-", tris(o)) for o in ps)[-6:], flush=True)
        for o in ps:
            mat = o.data.materials[0].name if o.data.materials else ""
            if mat in RUEDA and tris(o) > 8000:
                decimar(o, RUEDA[mat])
            else:
                decimar(o, max(60, tris(o) * RESTO_RUEDA))
        pinzas = [o for o in ps if o.data.materials and o.data.materials[0].name == "Brakes"]
        giran = [o for o in ps if o not in pinzas]
        for o in giran:
            o.data.transform(Matrix.Translation(-w))
            o.location = w
        r = unir(giran, f"rueda{i}")
        ruedas.append(r)
        print("G63 rueda", i, [round(v, 3) for v in w], "tris", tris(r), "pinzas", len(pinzas), flush=True)
    rueda_objs = {o for ps in partes for o in ps}
    resto = [o for o in mallas if o not in rueda_objs]
    for o in resto:
        mat = o.data.materials[0].name if o.data.materials else ""
        if tris(o) > CAP_EXT and mat != "Carpaint" and "lass" not in mat and not any(k in mat for k in INTERIOR):
            antes = tris(o)
            decimar(o, CAP_EXT)
            print("G63 exterior", o.name, mat, antes, "->", tris(o), flush=True)
    # one object per canonical material (static body, calipers included)
    resto = [o for o in O if o.type == "MESH" and not o.name.startswith("rueda")]
    por_mat = {}
    for o in resto:
        mats = [m.name if m else "" for m in o.data.materials]
        for n in mats:
            if n not in CANON:
                print("G63 SIN MAPA", o.name, n, flush=True)
        c = CANON.get(mats[0], "plastico") if mats else "plastico"  # one slot per mesh in this model (checked)
        o.data.materials.clear()
        o.data.materials.append(material(c))
        por_mat.setdefault(c, []).append(o)
    for r in ruedas:  # a joined wheel has one slot per source material
        for sl in r.material_slots:
            sl.material = material(CANON.get(sl.material.name, "goma") if sl.material else "goma")
    cuerpo = []
    for c, objs in por_mat.items():
        cuerpo.append(unir(objs, f"g63_{c}"))
    cam = bpy.data.objects.new("camion", None)
    sc.collection.objects.link(cam)
    for o in cuerpo + ruedas:
        o.parent = cam
        o.matrix_parent_inverse = Matrix.Identity(4)
    tot = sum(tris(o) for o in cuerpo + ruedas)
    vs = [v.co for o in cuerpo for v in o.data.vertices]
    lo = [min(v[k] for v in vs) for k in range(3)]
    hi = [max(v[k] for v in vs) for k in range(3)]
    print("G63 listo tris", tot, "cuerpo", sum(tris(o) for o in cuerpo), "ruedas", sum(tris(o) for o in ruedas),
          "bbox", [round(v, 3) for v in lo], [round(v, 3) for v in hi], flush=True)
    print("G63 materiales", sorted({m.name for o in cuerpo + ruedas for m in o.data.materials}), flush=True)
    json.dump({"tris": tot, "ruedas": [{"nombre": r.name, "centro": [round(v, 4) for v in r.location]} for r in ruedas],
               "bbox": [lo, hi], "escala": ESCALA}, open(os.path.splitext(bpy.data.filepath)[0] + "-datos.json", "w"), indent=1)
    return cam


sal = sys.argv[sys.argv.index("--") + 1]
preparar()
bpy.ops.wm.save_as_mainfile(filepath=sal, copy=True)
print("G63 guardado", sal, flush=True)

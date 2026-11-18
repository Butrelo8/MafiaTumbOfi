"""Live sections spike, step 2: from step 1's vivo-montado.blend to the page's files (public/vivo/, git-ignored: the Tripo cast is
licensed; the preview may serve it, buggyship 2026-11-18 12:40).

  GPU=0 /mnt/e/Blender/blender.exe -b --python-exit-code 1 "$(wslpath -w tmp/vivo/vivo-montado.blend)" \
    --python "$(wslpath -w blender/vivo_secciones_exportar.py)" -- <out_dir (Windows)> <vivo-montado.json (Windows)> \
    [truck_tris=150000] [fig_tris=40000] [tex=1024]

Dressing (one live scene carries one set; the stills differ per stop): every stop's common set plus scene 6's truck picks and
scene 1's cab picks (pennant, strawberry); the screen truck as built for scene 3, moved per stop by the page.
Writes escena.glb (truck, dressing, cast with one baked idle clip each, screen truck), mundo.glb (the whole road3 world, the
page moves it and wraps it every period) and vivo.json (stop cameras, boxes, lanes, lamps).
"""
import bpy, json, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, JS = argv[0], argv[1]
TRUCK = int(argv[2]) if len(argv) > 2 else 150000
FIG = int(argv[3]) if len(argv) > 3 else 40000
TEX = int(argv[4]) if len(argv) > 4 else 1024
NFR = 240  # one world period (192 m at 0.8 m/frame) = the stand-ins' NLA (80 f) x 3; the cast's clip window
d = json.load(open(JS, encoding="utf8"))
sc = bpy.context.scene
O = bpy.data.objects
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- dressing
g = d["grupos"]
comun = set.intersection(*(set(v) for v in g.values()))
quiero = set(g["montaje-esc6"]) | {n for n in g["montaje-esc1"] if n.split(".")[0] in ("pp_banderin", "pp_fresa")}
pantalla = [O[n] for n in g["montaje-esc3"] if n.startswith("p3_")]
pantalla = list({o for p in pantalla for o in [p, *p.children_recursive]})
for n in quiero | comun:
    O[n].hide_render = False
print("VIVO vestuario", len(quiero | comun), "objetos; pantalla", len(pantalla), flush=True)

mundo = O["mundo"]
del_mundo = set(mundo.children_recursive)
FIGS = [O[q + "_v5"] for q in ("manager", "hector", "alejandro", "diego")]
RIGS = [O[q + "_v5_rig"] for q in ("manager", "hector", "alejandro", "diego")]


def visible(o):
    return not o.hide_render and o.visible_get() and o.type in ("MESH", "ARMATURE", "EMPTY", "CURVE", "FONT")


escena = [o for o in O if visible(o) and o not in del_mundo and o is not mundo and o.name != "cerros" and o not in pantalla]
dg = bpy.context.evaluated_depsgraph_get()


def tris(o):
    e = o.evaluated_get(dg)
    me = e.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    e.to_mesh_clear()
    return n


# ---------------------------------------------------------------- the cast: bake one idle clip per rig, then decimate the skin
sc.frame_start, sc.frame_end = 0, NFR
for rig in RIGS:
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.nla.bake(frame_start=0, frame_end=NFR, step=2, only_selected=True, visual_keying=True, clear_constraints=True,
                     clear_parents=False, use_current_action=False, bake_types={"POSE", "OBJECT"})
    bpy.ops.object.mode_set(mode="OBJECT")
    act = rig.animation_data.action
    act.name = rig.name.replace("_v5_rig", "")
    sc.frame_set(0); p0 = [b.matrix.copy() for b in rig.pose.bones]
    sc.frame_set(NFR); p1 = [b.matrix.copy() for b in rig.pose.bones]
    costura = max((a.translation - b.translation).length for a, b in zip(p0, p1))
    print("VIVO clip", act.name, "costura f0-f%d max hueso %.4f m" % (NFR, costura), flush=True)
sc.frame_set(0)
for f in FIGS:
    n = tris(f)
    m = f.modifiers.new("dec", "DECIMATE")
    m.ratio = min(1.0, FIG / n * 0.97)
    bpy.context.view_layer.objects.active = f
    bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
    bpy.ops.object.modifier_apply(modifier="dec")
    print("VIVO figura", f.name, n, "->", len(f.data.polygons), flush=True)

# ---------------------------------------------------------------- the truck: one decimate ratio for its heavy meshes
pesados = [o for o in escena if o.type == "MESH" and o not in FIGS and not any(m.type == "ARMATURE" for m in o.modifiers)]
total = sum(tris(o) for o in pesados)
r = min(1.0, TRUCK / total * 0.97)
for o in pesados:
    if tris(o) > 300:
        o.modifiers.new("dec", "DECIMATE").ratio = r
print("VIVO camion tris", total, "ratio", round(r, 4), flush=True)
for im in bpy.data.images:
    if im.size[0] > TEX or im.size[1] > TEX:
        k = TEX / max(im.size)
        im.scale(max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k)))

# ---------------------------------------------------------------- export
camion = O["camion"]
camion.name = "camion"
pr = pantalla[0]
while pr.parent in pantalla:
    pr = pr.parent
pr.name = "pantalla_camion"


def exportar(nombre, objs, anim=False):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    ruta = os.path.join(OUT, nombre)
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                              export_lights=False, export_cameras=False, export_animations=anim, export_skins=anim,
                              export_animation_mode="ACTIONS", export_force_sampling=True, export_frame_step=2,
                              export_image_format="WEBP", export_draco_mesh_compression_enable=True,
                              export_draco_mesh_compression_level=6)
    print("VIVO GLB", nombre, os.path.getsize(ruta), flush=True)


exportar("escena.glb", escena + pantalla + [O["cerros"]], anim=True)
exportar("mundo.glb", [o for o in del_mundo if visible(o)])

# ---------------------------------------------------------------- page data (Blender axes)
ruedas = [o.name for o in escena if o.name.lower().startswith(("rueda", "llanta", "wheel"))]


def caja(objs):
    ps = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    return {"min": [min(p[i] for p in ps) for i in range(3)], "max": [max(p[i] for p in ps) for i in range(3)]}


cuerpo = [o for o in camion.children_recursive if o.type == "MESH" and o.name not in ruedas]
cam = d["camaras"]
c1 = cam["montaje-esc1"]["pos"]
p3 = pr.matrix_world.translation
faros = [o for o in O if o.type == "LIGHT" and o.name.startswith("faro_")]
datos = {
    "camaras": [cam[k] for k in sorted(cam)],
    "camion": caja(cuerpo),
    "cabina": {"min": [c1[0] - 0.85, c1[1] - 0.9, 1.0], "max": [c1[0] + 0.85, c1[1] + 1.75, 2.2]},  # refine from the cab mesh
    "parabrisas": c1[1] + 1.6,
    "periodo": 192.0, "velocidad": 19.2,
    "postes": [list(o.matrix_world.translation) for o in O if o.type == "LIGHT" and o.name.startswith("luz_poste")],
    # screen truck per stop, relative to where it was built (scene 3): ahead in the left lane, alongside (3), ahead in our lane (5)
    # (montar.log: PANTALLA3D box x -2.28 y -1.82..3.44 in scene 3, x 1.72 y 10.92..16.18 in scene 5)
    "pantalla": [[0, 40, 0], [0, 40, 0], [0, 0, 0], [0, 40, 0], [4.0, 12.74, 0], [0, 40, 0]],
    "carriles": {"mismo": [-1.775], "contrario": [-7.8, -11.3]},
    "faros": [{"pos": list(o.matrix_world.translation), "mira": list(o.matrix_world @ Vector((0, 0, -10)))} for o in faros],
    "ruedas": ruedas,
}
json.dump(datos, open(os.path.join(OUT, "vivo.json"), "w", encoding="utf8"), indent=1)
print("VIVO listo", flush=True)

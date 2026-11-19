"""Live sections spike, step 2: from step 1's vivo-montado.blend to the page's files (public/vivo/, git-ignored: the Tripo cast is
licensed; the preview may serve it, buggyship 2026-11-18 12:40).

  GPU=0 /mnt/e/Blender/blender.exe -b --python-exit-code 1 "$(wslpath -w tmp/vivo/vivo-montado.blend)" \
    --python "$(wslpath -w blender/vivo_secciones_exportar.py)" -- <out_dir (Windows)> <vivo-montado.json (Windows)> \
    [truck_tris=150000] [fig_tris=40000] [tex=1024]

Since 2026-11-19 the live recipe builds step 1 with CABINA_TRIPO=1 (the Tripo seats and console) and runs this step with
VIVO_POSE=<blender/vivo_reparto_volcar.py's dump of the owner's colocar-reparto-v3.blend> (WSLENV=VIVO_POSE): the cast at his
placement, held static. Without it the cast keeps the stand-ins' clips.

Dressing (one live scene carries one set; the stills differ per stop): every stop's common set plus scene 6's truck picks and
scene 1's cab picks (pennant, strawberry); the screen truck as built for scene 3, moved per stop by the page.
Writes escena.glb (truck, dressing, cast with one baked idle clip each, screen truck), mundo.glb (the whole road3 world, the
page moves it and wraps it every period) and vivo.json (stop cameras, boxes, lanes, lamps).
"""
import bpy, json, os, sys
from mathutils import Matrix, Vector

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
for n in quiero | comun:
    O[n].hide_render = O[n].hide_viewport = False  # viewport-hidden objects are skipped by visible() and keep stale matrices
# the bed keeps only the cases, the donut and the alien (montaje.QUITAR_CAJA, owner 2026-11-19 00:24): the unhide above brought
# the removed load back, and the console water bottle (k5_bebida_agua) left caja5 but older dumps still carry it
QUITAR = {"k3_amp", "k3_bocina", "k3_cables", "k3_cerveza", "k3_cobijas", "k3_hielera", "k4_red", "inst_bajo_sexto",
          "inst_requinto", "inst_tololoche", "k3_correa_alien", "k5_bebida_agua"}
for o in [o for o in O if o.name.split(".")[0] in QUITAR]:
    for c in [o, *o.children_recursive]:
        c.hide_render = c.hide_viewport = True


# the screen truck as built for scene 3: its cab (p3_*) plus the box, LED panels, frames and lettering that pantalla_3d.py
# builds as loose objects (parent=False). They are render-hidden outside scene 3, so take every scene-3-only object in its
# footprint (montar.log: PANTALLA3D x -2.28, box y -1.82..3.44, cab ahead; the G-wagon starts at x 0.63) and hang them
# from one empty the page can move per stop (first run: none of it reached escena.glb)
cand = [O[n] for n in set(g["montaje-esc3"]) - comun - quiero if O[n].type in ("MESH", "CURVE", "FONT", "EMPTY")]
for o in cand:
    o.hide_viewport = False  # hidden in the viewport, their matrices and bounds are stale (all at the origin)
bpy.context.view_layer.update()
_dg = bpy.context.evaluated_depsgraph_get()


def centro(o):
    e = o.evaluated_get(_dg)
    if o.type == "EMPTY":
        return e.matrix_world.translation
    return sum((e.matrix_world @ Vector(c) for c in e.bound_box), Vector()) / 8


pantalla = [o for o in cand if -4.0 < centro(o).x < -0.9 and -3.0 < centro(o).y < 11.0]
pantalla = list({o for p in pantalla for o in [p, *p.children_recursive]})
for o in pantalla:
    o.hide_render = o.hide_viewport = False
    o.hide_set(False)
raiz_p = bpy.data.objects.new("pantalla_camion", None)
sc.collection.objects.link(raiz_p)
raiz_p.location = (-2.28, 0.81, 0.0)
bpy.context.view_layer.update()
for o in pantalla:
    if o.parent not in pantalla:
        mw = o.matrix_world.copy()
        o.parent = raiz_p
        o.matrix_world = mw
pantalla.append(raiz_p)
print("VIVO vestuario", len(quiero | comun), "objetos; pantalla", len(pantalla), sorted(o.name for o in pantalla)[:40], flush=True)

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
def asentar_reparto(rigs, padre):
    """Hang each cast rig straight from `padre` (the truck), keeping its frame-0 world matrix, with an identity parent inverse.
    Call it before baking a cast for glTF (any lane's cast export can). Why: the v5 rigs hung from the old stand-in rigs (Diego
    from mx < diego_raiz, outside the truck) with a non-identity matrix_parent_inverse; the baked object keys and the glTF
    node then carried the old parent-relative transform, and live the heads sat 0.06-0.22 m low (Diego 0.9 m, out of his
    seat). vivo-optimizar.mjs zeroed the rigs' translation to hide it."""
    sc.frame_set(0)
    bpy.context.view_layer.update()
    for r in rigs:
        mw = r.matrix_world.copy()
        r.parent = padre
        r.matrix_parent_inverse = Matrix.Identity(4)
        r.matrix_world = mw
    bpy.context.view_layer.update()
    for r in rigs:
        top = next(b for b in r.pose.bones if "HeadTop" in b.name)
        print("VIVO reparto", r.name, "cuelga de", padre.name, "cabeza", [round(v, 3) for v in r.matrix_world @ top.head], flush=True)


asentar_reparto(RIGS, O["camion"])


def poner_pose(js):
    """The owner's placement (blender/vivo_reparto_volcar.py's dump of colocar-reparto-v3.blend): each rig at his world matrix with his
    evaluated pose, held static (saltyship 2026-11-19 02:25: no idle clips until gate 3), Héctor's bottle where his hand holds it and
    the Tripo console as he moved it. The drivers (stand-in constraints, Diego's sip clip) are cut."""
    p = json.load(open(js, encoding="utf8"))
    T = O["camion"].matrix_world @ Matrix(p["camion"]).inverted()  # his file's truck to this one's
    for q, r in p["rigs"].items():
        rig = O[q + "_v5_rig"]
        rig.animation_data_clear()
        for c in list(rig.constraints):
            rig.constraints.remove(c)
        for b in rig.pose.bones:
            for c in list(b.constraints):
                b.constraints.remove(c)
            b.location, b.rotation_quaternion, b.rotation_euler, b.scale = (0, 0, 0), (1, 0, 0, 0), (0, 0, 0), (1, 1, 1)
        rig.matrix_world = T @ Matrix(r["mundo"])
        bpy.context.view_layer.update()
        for b in sorted(rig.pose.bones, key=lambda b: len(b.parent_recursive)):  # parents first
            b.matrix = Matrix(r["huesos"][b.name])
            bpy.context.view_layer.update()
        err = max((Matrix(r["huesos"][b.name]).translation - b.matrix.translation).length for b in rig.pose.bones)
        top = next(b for b in rig.pose.bones if "HeadTop" in b.name)
        print("VIVO pose", q, "cabeza", [round(v, 4) for v in rig.matrix_world @ top.head], "dueño", r["cabeza"],
              "error hueso max %.5f m" % err, flush=True)
    # the bottle: every copy of the k5_bebida_mano tree takes the copy his viewport shows (the others' matrices are stale)
    vis = [n for n, o in p["objetos"].items() if n.split(".")[0] == "k5_bebida_mano" and o["visible"]]
    mb = T @ Matrix(p["objetos"][vis[0]]["mundo"])
    copias = [o for o in O if o.name.split(".")[0] == "k5_bebida_mano"]
    for o in copias:
        o.parent = None
        o.matrix_world = mb
    for o in [o for o in copias if not o.hide_render][1:]:  # one bottle, not stacked copies
        for c in [o, *o.children_recursive]:
            c.hide_render = True
    con = O.get("tripo_consola")
    if con:
        con.matrix_world = T @ Matrix(p["objetos"]["tripo_consola"]["mundo"])
    print("VIVO pose botella de", vis[0], "consola", bool(con), flush=True)
    bpy.context.view_layer.update()


POSE = os.environ.get("VIVO_POSE")
if POSE:
    poner_pose(POSE)
    NFR = 2  # a static pose: a two-frame clip keeps the page's one-mixer-per-rig path
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
pr = raiz_p


def soltar(objs):
    """The glTF sampler raises KeyError: None on an object parented to a bone of an armature left out of the export
    (first run, 2026-11-18): keep its world transform and drop the parent. Parents outside the set go the same way."""
    s = set(objs)
    for o in objs:
        if o.parent and o.parent not in s:
            print("VIVO soltar", o.name, "de", o.parent.name, o.parent_type, o.parent_bone, flush=True)
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw


# one clip per rig: each baked action on its own NLA track named after the rig (exported as NLA_TRACKS, so a rig's clip
# never lands on another rig that shares its bone names); no other object in escena.glb carries animation
for rig in RIGS:
    ad = rig.animation_data
    act = ad.action
    ad.action = None
    for t in list(ad.nla_tracks):
        ad.nla_tracks.remove(t)
    tr = ad.nla_tracks.new()
    tr.name = act.name
    st = tr.strips.new(act.name, 0, act)
    st.name = act.name
for o in escena + pantalla:
    if o.animation_data and o not in RIGS:
        o.animation_data_clear()
print("VIVO pantalla materiales", sorted({s.material.name for o in pantalla if o.type == "MESH" for s in o.material_slots if s.material}), flush=True)
print("VIVO camion en", [round(v, 3) for v in O["camion"].matrix_world.translation], flush=True)


colgados = set()  # what al_camion hung on the truck: props, not the body (vivo.json's truck box stays the body's)


def al_camion(objs):
    """The page sways the truck root (vivoSecciones.ts): a prop on the truck with no parent stays put and floats (cookingdrone measured
    the MT emblem drifting 8 px). Every root object whose box centre lies on the truck (its body box + 0.3 m) hangs from `camion`."""
    ps = [o.matrix_world @ Vector(c) for o in camion.children_recursive if o.type == "MESH" and visible(o) for c in o.bound_box]
    lo = Vector([min(p[i] for p in ps) - 0.3 for i in range(3)])
    hi = Vector([max(p[i] for p in ps) + 0.3 for i in range(3)])
    for o in objs:
        if o.parent or o in (camion, pr, O["cerros"]):
            continue
        c = o.matrix_world.translation if o.type == "EMPTY" else sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8
        if all(lo[i] <= c[i] <= hi[i] for i in range(3)):
            mw = o.matrix_world.copy()
            o.parent = camion
            o.matrix_parent_inverse = Matrix.Identity(4)
            o.matrix_world = mw
            colgados.update([o, *o.children_recursive])
            print("VIVO al camion", o.name, flush=True)
        else:
            print("VIVO raiz fuera del camion", o.name, [round(v, 2) for v in c], flush=True)


def exportar(nombre, objs, anim=False):
    soltar(objs)
    if nombre == "escena.glb":
        al_camion(objs)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    ruta = os.path.join(OUT, nombre)
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                              export_lights=False, export_cameras=False, export_animations=anim, export_skins=anim,
                              export_animation_mode="NLA_TRACKS", export_force_sampling=True, export_frame_step=2,
                              export_image_format="WEBP", export_draco_mesh_compression_enable=True,
                              export_draco_mesh_compression_level=6)
    print("VIVO GLB", nombre, os.path.getsize(ruta), flush=True)


exportar("escena.glb", escena + pantalla + [O["cerros"]], anim=True)
exportar("mundo.glb", [o for o in del_mundo if visible(o)])
_ys = [(o.matrix_world @ Vector(c)).y for o in del_mundo if visible(o) and o.type == "MESH" for c in o.bound_box]
print("VIVO mundo y", round(min(_ys)), round(max(_ys)), "objetos", sum(visible(o) for o in del_mundo), flush=True)

# ---------------------------------------------------------------- page data (Blender axes)
ruedas = [o.name for o in escena if o.name.lower().startswith(("rueda", "llanta", "wheel"))]


def caja(objs):
    ps = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    return {"min": [min(p[i] for p in ps) for i in range(3)], "max": [max(p[i] for p in ps) for i in range(3)]}


cuerpo = [o for o in camion.children_recursive if o.type == "MESH" and o.name not in ruedas and visible(o) and o not in colgados]  # a hidden helper cube made x, z min -1.0
cam = d["camaras"]
c1 = cam["montaje-esc1"]["pos"]
p3 = pr.matrix_world.translation
faros = [o for o in O if o.type == "LIGHT" and o.name.startswith("faro_")]
datos = {
    "camaras": [cam[k] for k in sorted(cam)],
    "camion": caja(cuerpo),  # min x mirrored below: something on the left side reached x -0.23 and swallowed stop 3
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
datos["camion"]["min"][0] = 2 * c1[0] - datos["camion"]["max"][0]  # the body is symmetric about the cab stop's x (1.72)
# stop 4 = four shots, one per member (owner 2026-11-18 19:11; blender/vivo_p1_stills.py CAM4 4-man-4, 4-hec-3, 4-ale-1, 4-die-3):
# camera, look-at (the face), lens, and the end of each one's straight exit leg (P1 SALIDA: no surface crossed, >= 0.257 m)
# look-at moved with each head to the owner's placement (2026-11-19, head tops old -> new: manager +0.245 y -0.013 z, Héctor
# +0.241 y, Alejandro +0.240 y, Diego -0.009 x +0.148 y +0.052 z); cameras and exit legs unchanged (the truck did not move)
datos["banda"] = [
    {"pos": [1.25, 1.45, 2.05], "mira": [1.33, 0.735, 1.827], "lens": 20.0, "salida": [1.25, 3.45, 2.05]},  # manager, windshield
    {"pos": [2.72, 1.05, 2.0], "mira": [2.08, 0.691, 1.80], "lens": 20.0, "salida": [3.4, 1.05, 2.0]},     # Héctor, his window
    {"pos": [0.72, -0.15, 2.0], "mira": [1.33, -0.32, 1.94], "lens": 20.0, "salida": [0.04, -0.15, 2.0]},  # Alejandro, rear left
    {"pos": [2.72, -0.15, 2.0], "mira": [2.111, -0.302, 1.812], "lens": 18.0, "salida": [3.4, -0.15, 2.0]},   # Diego, rear right
]
datos["camaras"][3] = datos["banda"][0]
# stop 3 sits 0.4 m off the body's left side, inside the orbit's 0.35 m margin band: its moves to 4b / 4d lifted 11.8 / 6.9 m.
# A 0.42 m leg straight out to the left (away from the body; the screen truck's side stays 0.92 m off) -> 2.77 / 3.05 m
datos["camaras"][2]["salida"] = [-0.2, -1.9, 2.0]
json.dump(datos, open(os.path.join(OUT, "vivo.json"), "w", encoding="utf8"), indent=1)
print("VIVO listo", flush=True)

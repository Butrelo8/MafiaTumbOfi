"""Live-proof GLB for scene 1 + the 1->2 move (escenas-plan §3): the v3 scene (G63, glass, the four figures as
transicion.py seats them at frame 0, bed instruments, roadside props, hills) decimated for three.js.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/vivo.py)" \
    -- <escena.py path (Windows)> <out.glb (Windows)> [truck_tris=80000] [figure_tris=30000] [tex=1024]

Truck <= truck_tris (Decimate collapse, one ratio for all its meshes), each figure <= figure_tris (posed at frame 0, then
decimated), textures scaled to <= tex px, Draco meshes, WebP images (KTX2 needs toktx, not installed here).
Not for git: the output carries the licensed Tripo figures (repo is public); write it under tmp/.
"""
import bpy, os, sys

argv = sys.argv[sys.argv.index("--") + 1:]
ESCENA, OUT = argv[0], argv[1]
TRUCK = int(argv[2]) if len(argv) > 2 else 80000
FIG = int(argv[3]) if len(argv) > 3 else 30000
TEX = int(argv[4]) if len(argv) > 4 else 1024

src = open(ESCENA, encoding="utf8").read()
g = {"__file__": ESCENA, "__name__": "escena_vivo"}
exec(compile(src.rstrip()[: -len("main()")], ESCENA, "exec"), g)
sys.path.insert(0, os.path.dirname(ESCENA))
import transicion as T

s = g["build"]()
T.preparar(s, 1280, 720, g["islas"])
sc = bpy.context.scene
sc.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get()


def tris(o):
    me = o.evaluated_get(dg).to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    o.evaluated_get(dg).to_mesh_clear()
    return n


def hornear(o, ratio=None):
    """Apply every modifier (armature pose included) plus an optional decimate; result is a plain posed mesh."""
    if ratio is not None and ratio < 1:
        md = o.modifiers.new("dec", "DECIMATE")
        md.ratio = ratio
    bpy.ops.object.select_all(action="DESELECT")
    o.hide_set(False)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    mw = o.matrix_world.copy()
    bpy.ops.object.convert(target="MESH")
    o.parent = None
    o.matrix_world = mw


FIGS = [bpy.data.objects[n] for n in ("hector", "diego", "alejandro", "manager") if n in bpy.data.objects]
extra = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("guitarra_", "estuche_"))]
camion = [o for o in s["camion"].children_recursive if o.type == "MESH" and o not in FIGS and o not in extra]
total = sum(tris(o) for o in camion)
print("CAMION_TRIS", total, len(camion))
r = min(1.0, TRUCK / total * 0.97)
for o in camion:
    if tris(o) > 200:
        o.modifiers.new("dec", "DECIMATE").ratio = r
for o in FIGS:
    n = tris(o)
    hornear(o, FIG / n * 0.97)
dg = bpy.context.evaluated_depsgraph_get()
print("CAMION_TRIS_FINAL", sum(tris(o) for o in camion))
for o in FIGS:
    print("FIG_TRIS", o.name, tris(o))
for im in bpy.data.images:
    if im.size[0] > TEX or im.size[1] > TEX:
        k = TEX / max(im.size)
        im.scale(max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k)))

keep = set(camion) | set(FIGS) | set(extra) | {s["camion"], s["cerros"], *s["props"], *s["ruedas"]}
keep |= {p for o in list(keep) for p in [o.parent] if p}
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.hide_set(False)
    o.select_set(True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                          export_lights=False, export_cameras=False, export_animations=False, export_skins=False,
                          export_image_format="WEBP", export_draco_mesh_compression_enable=True,
                          export_draco_mesh_compression_level=6)
print("GLB", OUT, os.path.getsize(OUT))

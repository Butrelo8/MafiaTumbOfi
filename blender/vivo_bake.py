"""Night bake for /vivo-secciones (P1 phase 1, 2026-11-18): the live world's look rendered once in Cycles, so the page can show it
with unlit materials. Runs on step 1's vivo-montado.blend at frame 0 (the frame mundo.glb was exported at).

  /mnt/e/Blender/blender.exe -b tmp/vivo/vivo-montado.blend --python-exit-code 1 --python "$(wslpath -w blender/vivo_bake.py)" \
    -- <out_dir (Windows)> [suelo,ancho,faros,arboles] [samples=64]

Outputs (PNG, 8-bit):
- suelo.png: one 192 m road period, top-down orthographic, x -17.6..11.6 (road, paint, shoulders, gravel, verge), y -16..192.
  Rendered with the scene's own AgX look, so the page shows it unlit and not tone-mapped. The last 16 m are cross-faded with
  the 16 m before y 0 by scripts/vivo-bake-post.py, so the tile wraps without a seam.
- ancho.png: the same period, x -70..50, low resolution: the terrain beyond the gravel.
- faros.png: the truck's two headlights and its emissive parts on a white ground, the truck shadowing it but unseen (Standard
  view, light only), x -8.5..12.5, y -12..44: an additive pool.
- arboles_der.png / arboles_izq.png: the tree scatter seen side-on from the road (orthographic, transparent film): treeline cards.
Lighting for suelo/ancho/arboles: the sky, the moon and the pole lamp (luz_poste) instanced at every lamp post, so the light
repeats with the period. The truck's lights, the fog volume and the one-off buildings are off.
"""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
MODOS = (argv[1] if len(argv) > 1 else "suelo,ancho,faros,arboles").split(",")
SPP = int(argv[2]) if len(argv) > 2 else 64
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
sc.frame_set(0)
bpy.context.view_layer.update()
O = bpy.data.objects
P = 192.0
Y0, Y1 = -16.0, P  # rendered span; the post step cross-fades [176, 192] with [-16, 0]

SUELO = ("w_carretera", "w_borde", "w_carril", "w_op_", "w_grava", "w_acot", "w_terreno", "w_boton", "w_pasto+", "w_pasto-")
ARBOLES = ("w_copa", "w_arbusto")

sc.render.engine = "CYCLES"
sc.cycles.device = "GPU"
sc.cycles.samples = SPP
sc.cycles.use_denoising = True
sc.render.film_transparent = False
sc.render.use_motion_blur = False
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "OPTIX"
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == "OPTIX"

# the pole lamps: luz_poste lives in the instanced collection w_farola (pole, arm, lamp, light; blender/mundo.py farolas()),
# instanced every 64 m under mundo, so keeping the instancers renders one light per post and the light repeats with the
# period. Their pole and arm stay out of the camera (they would print on the top-down tile) but still cast shadows.
for o in bpy.data.collections["w_farola"].all_objects:
    if o.type != "LIGHT":
        o.visible_camera = False
FAROLAS = [o for o in O if o.name.startswith("w_farola_") and o.name[9:].lstrip("-").isdigit()]  # not the x1..x3 sign lamps (one-off)
copias = [O["luz_poste"]]
print("BAKE farolas", len(FAROLAS), "luz_poste en", [c.name for c in O["luz_poste"].users_collection], flush=True)


def solo(prefijos, luces):
    """Render only meshes whose name starts with one of `prefijos` (and their instancers), plus the lights in `luces`."""
    for o in O:
        if o.type == "LIGHT":
            o.hide_render = o not in luces
        elif o.type in ("MESH", "CURVE", "FONT", "EMPTY", "CURVES", "POINTCLOUD"):
            o.hide_render = not (o.name.startswith(prefijos) or (o in FAROLAS and luces is not FAROS))


def camara(centro, mira_dir, escala, w, h):
    cd = bpy.data.cameras.new("bake")
    cd.type, cd.ortho_scale, cd.clip_start, cd.clip_end = "ORTHO", escala, 0.1, 2000
    co = bpy.data.objects.new("bake", cd)
    sc.collection.objects.link(co)
    co.location = centro
    co.rotation_euler = Vector(mira_dir).to_track_quat("-Z", "Y").to_euler()  # local Y (image up) toward world Z; straight down it keeps world Y up
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    return co


def render(nombre):
    sc.render.filepath = os.path.join(OUT, nombre)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if sc.render.film_transparent else "RGB"
    sc.render.image_settings.color_depth = "8"
    bpy.ops.render.render(write_still=True)
    print("BAKE escrito", nombre, sc.render.resolution_x, sc.render.resolution_y, flush=True)


luna = [o for o in O if o.type == "LIGHT" and o.name == "luna"]
FAROS = [o for o in O if o.type == "LIGHT" and o.name.startswith("faro_")]
mira_abajo = (0, 0, -1)
if "suelo" in MODOS:
    solo(SUELO, luna + copias)
    x0, x1 = -17.6, 11.6
    h = 4096
    w = round(h * (x1 - x0) / (Y1 - Y0) / 8) * 8
    x1 = x0 + (Y1 - Y0) * w / h
    camara(((x0 + x1) / 2, (Y0 + Y1) / 2, 60), mira_abajo, Y1 - Y0, w, h)
    print("BAKE suelo x", x0, round(x1, 3), "y", Y0, Y1, flush=True)
    render("suelo.png")
if "ancho" in MODOS:
    solo(SUELO, luna + copias)
    camara((-10, (Y0 + Y1) / 2, 60), mira_abajo, Y1 - Y0, 576, 1000)
    print("BAKE ancho x", -10 - (Y1 - Y0) * 576 / 1000 / 2, -10 + (Y1 - Y0) * 576 / 1000 / 2, "y", Y0, Y1, flush=True)
    render("ancho.png")
if "arboles" in MODOS:
    solo(ARBOLES, luna + copias)
    sc.render.film_transparent = True
    for lado, sx in (("der", 1), ("izq", -1)):
        zc, alto = 14.0, 32.0  # z -2..30
        w = 2048
        hpx = round(w * alto / (Y1 - Y0) / 8) * 8
        camara((0, (Y0 + Y1) / 2, zc), (sx, 0, 0), Y1 - Y0, w, hpx)
        print("BAKE arboles", lado, "z", zc - (Y1 - Y0) * hpx / w / 2, zc + (Y1 - Y0) * hpx / w / 2, flush=True)
        render(f"arboles_{lado}.png")
    sc.render.film_transparent = False
if "faros" in MODOS:
    faros = FAROS
    me = bpy.data.meshes.new("bake_suelo")
    me.from_pydata([(-40, -20, 0), (40, -20, 0), (40, 80, 0), (-40, 80, 0)], [], [(0, 1, 2, 3)])
    pl = bpy.data.objects.new("bake_suelo", me)
    sc.collection.objects.link(pl)
    m = bpy.data.materials.new("bake_blanco")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    me.materials.append(m)
    solo(("bake_suelo",), faros)
    # the truck stays in the light paths but not in the camera: its body shadows the pool, its emissive parts (underglow, tail
    # lamps) light the ground under it. The pool is fixed to the truck in the page, so these shadows are right there too.
    for o in O["camion"].children_recursive:
        if o.type in ("MESH", "CURVE", "FONT"):
            o.hide_render, o.visible_camera = False, False
    wl = sc.world.node_tree.nodes["Background"].inputs[1]
    fuerza = wl.default_value
    wl.default_value = 0.0
    vt = sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure
    sc.view_settings.view_transform, sc.view_settings.look = "Standard", "None"
    sc.view_settings.exposure = float(os.environ.get("FAROS_EV", "-4"))
    camara((2.0, 16.0, 60), mira_abajo, 56.0, 384, 1024)
    print("BAKE faros x -8.5..12.5 y -12..44, Standard, EV", sc.view_settings.exposure, [(o.name, [round(v, 2) for v in o.matrix_world.translation]) for o in faros], flush=True)
    render("faros.png")
    wl.default_value = fuerza
    sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure = vt
print("BAKE listo", flush=True)

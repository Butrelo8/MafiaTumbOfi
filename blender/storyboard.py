"""Storyboard frames for the scene plan (docs/design/escenas-plan.md): one still per scene, 16:9 and 9:16.

Builds the night scene of the main checkout's blender/escena.py + transicion.py (truck, glass, figures), then applies the
owner's 2026-11-12 23:52 answers: all four ride in the cab (Alexandro and Diego move to the rear seats), the bed carries
the instruments and playful props, and the truck never parks (the other vehicle drives too). New props are simple shapes
standing in for models still to be made; the truck is the G63 on disk, the owner's pick (2026-11-13 00:21).

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/storyboard.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples=24] [only=name,name]
"""
import bpy, math, os, sys
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
ESCENA, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 24
SOLO = argv[3].split(",") if len(argv) > 3 else None

src = open(ESCENA, encoding="utf8").read()
assert src.rstrip().endswith("\nmain()"), "escena.py no longer ends in a bare main()"
g = {"__file__": ESCENA, "__name__": "escena_storyboard"}
exec(compile(src.rstrip()[: -len("main()")], ESCENA, "exec"), g)
sys.path.insert(0, os.path.dirname(ESCENA))
import transicion as T

s = g["build"]()
g["mundo_render"](s, "noche")
g["motor"](SAMPLES, "noche")
T.preparar(s, 960, 540, g["islas"])
sc = bpy.context.scene
sc.frame_set(0)
CX = T.CX
dg = bpy.context.evaluated_depsgraph_get()


def rayo(o, d):
    hit, loc, *_ , ob, _m = sc.ray_cast(dg, Vector(o), Vector(d))
    return loc if hit else None


# ---- the rear seats: measure, then move Alexandro and Diego in, facing forward like the front pair
ys = [(o.matrix_world @ Vector(c)).y for o in s["camion"].children_recursive if o.type == "MESH" for c in o.bound_box]
FRENTE, COLA = max(ys), min(ys)
for nombre, x_bed, lado in (("alejandro", CX - 0.36, -1), ("diego", CX + 0.36, 1)):
    x = CX + 0.39 * lado
    respaldo = rayo((x, 0.10, 1.40), (0, -1, 0))   # from between the rows, backwards: the rear seat back
    cojin = rayo((x, -0.55, 2.10), (0, 0, -1))      # straight down onto the rear cushion
    print("ASIENTO", nombre, respaldo, cojin)
    y_hip = (respaldo.y + 0.20) if respaldo else -0.62
    z_hip = (cojin.z + 0.07) if cojin and cojin.z < 1.5 else T.CABINA_Z + 0.07
    arm = bpy.data.objects[nombre + "_rig"]
    bed_hip = Vector((x_bed, -1.62, T.CAJA_Z + T.CASE_H + 0.07))
    mover = Matrix.Translation(Vector((x, y_hip, z_hip))) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-bed_hip)
    gt = bpy.data.objects["guitarra_" + nombre]
    gt.parent = None
    arm.matrix_world = mover @ arm.matrix_world
    # the guitar stays in the bed, lying face up on its case
    gt.matrix_world = Matrix.Translation(Vector((x_bed - 0.05, -1.55, T.CAJA_Z + T.CASE_H + 0.05))) @ Matrix.Rotation(-math.pi / 2, 4, "X")


def emis(name, color, strength, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    if strength:
        bs.inputs["Emission Color"].default_value = (*color, 1)
        bs.inputs["Emission Strength"].default_value = strength
    return m


def caja(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    o.parent = s["camion"]
    o.matrix_parent_inverse = s["camion"].matrix_world.inverted()
    return o


# ---- playful bed props (stand-ins): inflatable donut, cooler, piñata; stickers on the tailgate and rear window
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.13, location=(CX + 0.45, -2.45, T.CAJA_Z + 0.45), rotation=(0.9, 0.3, 0))
dona = bpy.context.object
dona.data.materials.append(emis("dona", (0.95, 0.35, 0.55), 0.0, 0.2))
dona.parent = s["camion"]
caja("hielera", (0.55, 0.38, 0.40), (CX - 0.55, -2.50, T.CAJA_Z + 0.20), emis("hielera", (0.7, 0.05, 0.04), 0.0, 0.3))
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.22, location=(CX + 0.05, -2.35, T.CAJA_Z + 0.55))
pinata = bpy.context.object
pinata.data.materials.append(emis("pinata", (0.95, 0.75, 0.1), 0.0))
pinata.parent = s["camion"]
for i, (dx, dz, ang, col) in enumerate(((-0.55, 1.05, 0.25, (0.9, 0.3, 0.6)), (-0.1, 1.15, -0.15, (0.1, 0.1, 0.1)),
                                         (0.35, 1.02, 0.35, (0.2, 0.8, 0.4)), (0.15, 1.85, -0.3, (0.9, 0.15, 0.1)))):
    y = -1.05 if dz > 1.6 else COLA - 0.03  # the high one goes on the cab's rear window, the rest on the tailgate
    caja(f"calca_{i}", (0.20, 0.01, 0.14), (CX + dx, y, dz), emis(f"calca_{i}", col, 0.8), rot=(0, ang, 0))

# ---- the LED-screen ad truck (pantalla móvil) that rides with the band: videos on its side, dates on its back
OTRO = bpy.data.objects.new("pantalla_movil", None)
sc.collection.objects.link(OTRO)
GRIS = emis("pm_gris", (0.08, 0.08, 0.09), 0.0, 0.4)
PANT = emis("pm_pantalla", (0.85, 0.8, 0.7), 2.2)
for name, size, loc, m in (("pm_cabina", (2.3, 2.0, 2.5), (0, 3.6, 1.55), GRIS), ("pm_caja", (2.5, 5.8, 3.0), (0, -0.4, 2.0), GRIS),
                           ("pm_lado", (0.03, 5.2, 2.4), (1.27, -0.4, 2.1), PANT), ("pm_atras", (2.2, 0.03, 2.4), (0, -3.32, 2.1), PANT)):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name, o.scale = name, (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    o.parent = OTRO
for y in (-2.6, 2.2, 3.6):
    for x in (-1.0, 1.0):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.35, location=(x, y, 0.5), rotation=(0, math.pi / 2, 0))
        bpy.context.object.data.materials.append(GRIS)
        bpy.context.object.parent = OTRO


def camara(name, pos, mira, lens, w, h):
    cd = bpy.data.cameras.new(name)
    cd.clip_start, cd.clip_end, cd.lens, cd.sensor_fit = 0.03, 3000, lens, "HORIZONTAL"
    co = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(co)
    co.location = Vector(pos)
    co.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100


def v(lens):  # 9:16 keeps 75 % of the 16:9 horizontal angle, as transicion.py does
    return 18 / math.tan(0.75 * math.atan(18 / lens))


W, H = (960, 540), (540, 960)
c0, c1 = T.CAMINO[0], T.CAMINO[-1]
TOMAS = [
    # name, pantalla_movil placement (x, y) or None, (pos, look-at, lens) 16:9, the same 9:16
    ("1-cabina", None, (c0[1], c0[2], c0[3]), (c0[1], c0[2], v(c0[3]))),
    ("2-caja", None, (c1[1], c1[2], c1[3]), (c1[1], c1[2], v(c1[3]))),
    ("3-pantalla", (-4.2, 1.5), ((CX + 0.4, -8.0, 2.7), (-1.6, 2.0, 1.9), 26), ((CX - 0.2, -7.0, 2.5), (-1.4, 2.0, 2.0), 22)),
    ("4-costado", None, ((CX + 6.2, -0.3, 1.9), (CX, -0.3, 1.6), 24), ((CX + 3.0, 0.15, 1.95), (CX + 0.4, 0.15, 1.8), 22)),
    ("5-gira", (CX, FRENTE + 13.0), ((CX - 0.35, 2.3, 2.45), (CX, FRENTE + 10, 2.1), 30), ((CX - 0.2, 2.3, 2.45), (CX, FRENTE + 10, 2.1), 26)),
    ("6-placa", None, ((CX + 0.9, FRENTE + 9.5, 1.0), (CX, FRENTE - 1.5, 1.1), 32), ((CX + 0.4, FRENTE + 7.5, 0.9), (CX, FRENTE - 1.0, 1.2), 26)),
]
for nombre, otro, a, b in TOMAS:
    if SOLO and nombre not in SOLO:
        continue
    OTRO.location = (otro[0], otro[1], 0) if otro else (0, 0, -100)
    for (pos, mira, lens), (w, h) in ((a, W), (b, H)):
        camara("cam_" + nombre, pos, mira, lens, w, h)
        sc.render.filepath = os.path.join(OUT, f"{nombre}-{w}x{h}.png")
        bpy.ops.render.render(write_still=True)
        print("TOMA", nombre, w, h)

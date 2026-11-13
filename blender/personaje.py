"""Style test: one band member as a "cabezon" (big-head toy figure built from primitives, flat colours, waist-up).

    blender.exe -b --factory-startup --python blender/personaje.py -- <out dir (Windows path)> [samples] [formas|estilos]

Writes <out>/alexandro-<style>.png for the four test styles (720x900, three-quarter view, neutral studio light).
Character faces -Y, Z up, metres. The character's right is -X.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS else os.path.join(os.path.dirname(os.path.abspath(__file__)), "render", "personajes")
SAMPLES = int(ARGS[1]) if len(ARGS) > 1 else 48

HEAD = Vector((0, 0, 0.78))
A, B, C = 0.28, 0.26, 0.25  # head half-axes: x, y, z


def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (1, 3, 5))


ESTILO = "vinilo"  # vinilo | plastilina | madera | oro (set per render by the loop at the bottom)
ORO = {"pelo", "puno", "papel", "filtro", "oro", "negro", "blanco"}  # style "oro": these parts gold, the rest black lacquer


def rampa(nt, src, p0, p1, v0, v1):
    r = nt.nodes.new("ShaderNodeValToRGB")
    e = r.color_ramp.elements
    e[0].position, e[1].position = p0, p1
    e[0].color, e[1].color = (v0, v0, v0, 1), (v1, v1, v1, 1)
    nt.links.new(src, r.inputs[0])
    return r.outputs[0]


def ruido(nt, pos, escala, detalle=2.0, estirar=None):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value, n.inputs["Detail"].default_value = escala, detalle
    if estirar:
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = estirar
        nt.links.new(pos, mp.inputs[0])
        pos = mp.outputs[0]
    nt.links.new(pos, n.inputs["Vector"])
    return n.outputs[0]


def relieve(nt, alto, fuerza, dist, normal=None):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value, bp.inputs["Distance"].default_value = fuerza, dist
    nt.links.new(alto, bp.inputs["Height"])
    if normal:
        nt.links.new(normal, bp.inputs["Normal"])
    return bp.outputs[0]


def mezcla(nt, fac, a, b):
    """fac 0 -> a, 1 -> b; a and b are RGBA tuples or sockets."""
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    nt.links.new(fac, mx.inputs[0])
    for i, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            mx.inputs[i].default_value = v
        else:
            nt.links.new(v, mx.inputs[i])
    return mx.outputs[2]


def mat(name, hexa, rough=0.6, emit=0.0, metal=0.0):
    m = bpy.data.materials.new(name)
    if not (m.node_tree and m.node_tree.nodes):
        m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = lin(hexa)
    if ESTILO == "oro" and not emit and name != "piso":
        rgb, rough, metal = (lin("#d4a437"), 0.25, 1.0) if name in ORO else (lin("#050505"), 0.12, 0.0)
        if name not in ORO:
            p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*rgb, 1)
        p.inputs["Emission Strength"].default_value = emit
    liso = emit or metal or name in ("negro", "blanco", "piso")
    # World position drives the textures: fine for a still, to be baked to the parts before anything moves.
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    if ESTILO == "plastilina" and not liso:
        p.inputs["Roughness"].default_value = 0.85
        bulto, grano = ruido(nt, pos, 9, 2), ruido(nt, pos, 75, 3)
        nt.links.new(mezcla(nt, bulto, tuple(c * 0.8 for c in rgb) + (1,), (*rgb, 1)), p.inputs["Base Color"])
        nt.links.new(relieve(nt, grano, 0.12, 0.004, relieve(nt, bulto, 0.5, 0.03)), p.inputs["Normal"])
    if ESTILO == "madera" and not liso:
        p.inputs["Roughness"].default_value = 0.45
        p.inputs["Coat Weight"].default_value = 0.35
        veta = ruido(nt, pos, 30, 4, estirar=(1, 1, 0.08))
        pintura = mezcla(nt, rampa(nt, veta, 0.35, 0.65, 0, 1), tuple(c * 0.72 for c in rgb) + (1,), (*rgb, 1))
        golpes = rampa(nt, ruido(nt, pos, 13, 3), 0.66, 0.68, 0, 1)  # chips where the bare wood shows
        nt.links.new(mezcla(nt, golpes, pintura, (*lin("#a87f52"), 1)), p.inputs["Base Color"])
        nt.links.new(relieve(nt, veta, 0.25, 0.004), p.inputs["Normal"])
    return m


def objeto(name, bm, m, loc, scale=(1, 1, 1), rot=None, subsurf=0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    ob.location, ob.scale = loc, scale
    if rot is not None:
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = rot
    if subsurf:
        s = ob.modifiers.new("sub", "SUBSURF")
        s.levels = s.render_levels = subsurf
    bpy.context.scene.collection.objects.link(ob)
    return ob


def esfera(name, m, loc, scale, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
    return objeto(name, bm, m, loc, scale, rot)


def caja(name, m, loc, scale, rot=None, taper=1.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= taper
            v.co.y *= taper
    return objeto(name, bm, m, loc, scale, rot, subsurf=3)


def cilindro(name, m, base, eje, largo, r):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r, depth=largo)
    return objeto(name, bm, m, base + eje * (largo / 2), rot=Vector((0, 0, 1)).rotation_difference(eje))


MENTON = 0.0  # how much the head narrows towards the chin (0 = ball)

# Body shapes, from toy to closer to a person. Half-sizes in metres.
FORMAS = {
    "cabezon": dict(cabeza=(0.28, 0.26, 0.25), menton=0.0, cuello=0.0, torso=(0.23, 0.17, 0.27), hombros=0.0, codo=False),
    "muneco": dict(cabeza=(0.205, 0.205, 0.23), menton=0.22, cuello=0.035, torso=(0.19, 0.14, 0.25), hombros=0.25, codo=True),
    "titere": dict(cabeza=(0.15, 0.165, 0.19), menton=0.3, cuello=0.07, torso=(0.2, 0.13, 0.29), hombros=0.28, codo=True),
}


def cara(x, dz, fuera=0.0):
    """Point on the front of the head at offset x, dz from its centre, pushed out by `fuera`."""
    a = A * (1 - MENTON * max(0.0, -dz / C))
    y = -B * math.sqrt(max(0.0, 1 - (x / a) ** 2 - (dz / C) ** 2))
    return HEAD + Vector((x, y - fuera, dz))


def tramo(name, m, p1, p2, r):
    """Ellipsoid limb from p1 to p2."""
    d = p2 - p1
    return esfera(name, m, (p1 + p2) / 2, (r, r, d.length / 2 + r * 0.6), rot=Vector((0, 0, 1)).rotation_difference(d.normalized()))


def alexandro(forma):
    global HEAD, A, B, C, MENTON
    f = FORMAS[forma]
    A, B, C = f["cabeza"]
    MENTON = f["menton"]
    tw, td, th = f["torso"]
    alto = 0.03 + 2 * th  # top of the torso
    HEAD = Vector((0, 0, alto + f["cuello"] + C * 0.9))
    k, kz = A / 0.28, C / 0.25  # face features scale with the head

    piel = mat("piel", "#b9825c", 0.55)
    pelo = mat("pelo", "#080605", 0.5)
    negro = mat("negro", "#0a0a0c", 0.25)
    chamarra = mat("chamarra", "#121216", 0.7)
    puno = mat("puno", "#d8d2c4", 0.8)
    oro = mat("oro", "#d4a437", 0.3, metal=1.0)
    papel = mat("papel", "#eeeae0", 0.8)
    filtro = mat("filtro", "#c98a4b", 0.8)
    brasa = mat("brasa", "#ff5a1e", 0.5, emit=12.0)
    blanco = mat("blanco", "#ffffff", 0.2)

    cab = esfera("cabeza", piel, HEAD, (A, B, C))
    for v in cab.data.vertices:  # unit sphere before the object scale: narrow the lower half into a chin
        if v.co.z < 0:
            v.co.x *= 1 - MENTON * -v.co.z
    esfera("torso", chamarra, (0, 0, 0.03 + th), (tw, td, th))
    caja("cierre", puno, (0, -td * 0.96, 0.03 + th), (0.006, 0.01, th * 0.6))
    if f["cuello"]:
        cilindro("cuello", piel, Vector((0, 0.01, alto - 0.05)), Vector((0, 0, 1)), f["cuello"] + 0.12, A * 0.42)
        esfera("solapa", chamarra, (0, 0.01, alto - 0.015), (A * 0.62, A * 0.6, 0.04))
    if f["hombros"]:
        esfera("hombros", chamarra, (0, 0, alto - 0.085), (f["hombros"], td * 0.85, 0.085))

    # Curly mop: balls on the top of the head, fringe to the brows, short over the ears, long at the back.
    n, oro_ang = 170, math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        d = Vector((r * math.cos(i * oro_ang), r * math.sin(i * oro_ang), z))
        frente = -d.y / max(r, 1e-6)  # 1 front, -1 back
        lim = 72 - 14 * frente if frente > 0 else 72 - 28 * frente
        if math.degrees(math.acos(z)) > lim:
            continue
        rr = (0.062 + 0.03 * ((i * 37) % 11) / 10) * (0.35 + 0.65 * k)
        esfera(f"rizo{i:03d}", pelo, HEAD + Vector((d.x * A, d.y * B, d.z * C)) * 1.03, (rr, rr, rr))

    for s in (-1, 1):
        ex = s * 0.105 * k
        esfera(f"ojo{s}", negro, cara(ex, 0.0, -0.004), (0.044 * k, 0.016, 0.024 * k))  # wide low ovals: half asleep
        esfera(f"brillo{s}", blanco, cara(ex - 0.014 * k, 0.008 * k, 0.012), (0.006, 0.004, 0.006))
        caja(f"ceja{s}", pelo, cara(ex, 0.062 * kz, 0.004), (0.05 * k, 0.012, 0.011),
             rot=Vector((1, 0, 0)).rotation_difference(Vector((1, 0, -s * 0.16)).normalized()))
        esfera(f"oreja{s}", piel, HEAD + Vector((s * A * 0.98, 0.01, -0.02)), (0.028, 0.045 * k, 0.06 * k))
        if f["codo"]:
            hombro = Vector((s * f["hombros"] * 0.86, 0, alto - 0.09))
            codo = hombro + Vector((s * 0.035, 0.03, -th * 0.95))
            mano = codo + Vector((-s * 0.05, -0.2, -0.03))
            tramo(f"brazo{s}", chamarra, hombro, codo, 0.062)
            tramo(f"antebrazo{s}", chamarra, codo, mano, 0.055)
        else:
            hombro = Vector((s * (tw - 0.035), -0.01, alto - 0.07))
            mano = Vector((s * (tw + 0.055), -0.075, 0.145))
            tramo(f"brazo{s}", chamarra, hombro, mano + Vector((0, 0.01, 0.07)), 0.07)
        dir_mano = (mano - hombro).normalized() if not f["codo"] else (mano - codo).normalized()
        esfera(f"puno{s}", puno, mano - dir_mano * 0.005, (0.07, 0.07, 0.028),
               rot=Vector((0, 0, 1)).rotation_difference(dir_mano))
        esfera(f"mano{s}", piel, mano + dir_mano * 0.05, (0.055, 0.055, 0.052))
    esfera("nariz", piel, cara(0, -0.05 * kz, 0.012), (0.03, 0.03, 0.026 + 0.012 * (1 - k)))
    esfera("marca", negro, cara(-0.105 * k, -0.05 * kz, 0.0), (0.008, 0.004, 0.011))  # mark under his right eye
    esfera("arete", oro, HEAD + Vector((-A * 1.0, 0.0, -0.085 * kz)), (0.014, 0.014, 0.014))
    esfera("boca", negro, cara(0.012 * k, -0.118 * kz, -0.002), (0.04 * k, 0.012, 0.007))

    # Cigarette from the left corner of the mouth, pointing forward, down and out.
    eje = Vector((0.35, -1, -0.3)).normalized()
    p = cara(0.05 * k, -0.118 * kz, -0.01)
    q = max(k, 0.75)
    cilindro("filtro", filtro, p, eje, 0.035 * q, 0.011 * q)
    cilindro("papel", papel, p + eje * 0.035 * q, eje, 0.085 * q, 0.011 * q)
    cilindro("brasa", brasa, p + eje * 0.12 * q, eje, 0.008 * q, 0.0105 * q)


def estudio():
    s = bpy.context.scene
    w = s.world or bpy.data.worlds.new("w")
    s.world = w
    if not (w.node_tree and w.node_tree.nodes):
        w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.12, 0.12, 0.13, 1)
    bg.inputs[1].default_value = 1.0
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
    objeto("piso", bm, mat("piso", "#5a5a5e", 0.9), (0, 0, 0.03))
    for name, loc, w_, size, col in (("key", (-1.6, -2.2, 2.2), 500, 1.6, (1, 0.93, 0.85)),
                                     ("rim", (1.6, 1.6, 1.8), 350, 1.0, (0.8, 0.88, 1))):
        l = bpy.data.lights.new(name, "AREA")
        l.energy, l.size, l.color = w_, size, col
        ob = bpy.data.objects.new(name, l)
        ob.location = loc
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = (Vector((0, 0, 0.5)) - Vector(loc)).to_track_quat("-Z", "Y")
        s.collection.objects.link(ob)


def render(nombre, pos, mira=(0, 0, 0.52), lens=70):
    s = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = lens
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y")
    s.collection.objects.link(cam)
    s.camera = cam
    s.render.filepath = os.path.join(OUT, nombre + ".png")
    bpy.ops.render.render(write_still=True)


def motor():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = 720, 900, 100
    s.cycles.samples = SAMPLES
    s.cycles.use_denoising = True
    try:
        pr = bpy.context.preferences.addons["cycles"].preferences
        pr.compute_device_type = "OPTIX"
        pr.get_devices()
        for d in pr.devices:
            d.use = True
        s.cycles.device = "GPU"
    except Exception as e:  # no GPU: CPU still renders the test
        print("GPU not set:", e)


motor()
TEST = ARGS[2] if len(ARGS) > 2 else "formas"
# formas: the three body shapes in plasticine; estilos: the big-head shape in the four materials.
for ESTILO, forma in ([("plastilina", f) for f in FORMAS] if TEST == "formas"
                      else [(e, "cabezon") for e in ("vinilo", "plastilina", "madera", "oro")]):
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    estudio()
    alexandro(forma)
    render("alexandro-" + (forma if TEST == "formas" else ESTILO), (-1.0, -2.5, 0.75))

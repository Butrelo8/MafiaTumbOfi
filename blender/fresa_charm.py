"""P5 strawberry charm (the PUTIFRESA joke, ref [9]) as one swappable asset file: builds the charm and exports it as .glb.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/fresa_charm.py)" \
    -- <out.glb (Windows path)> [fruta|resina|peluche]

Contract (props_placement.py relies on it, a friend's model must keep it): one .glb, Z up, metres, origin at the hang point
(top of the ring), the charm hanging down -Z, about 4 cm tall including the ring. Every mesh in the file is part of the charm;
the cord comes from the scene. Styles: fruta = a real berry (seeds in pits, calyx, clear-coated red), resina = an enamel
charm (smooth gloss red, gold seeds and cap), peluche = a felt plush (matte red, sheen, stitched seeds).
"""
import bpy, bmesh, math, sys
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
ESTILO = argv[1] if len(argv) > 1 else "fruta"

bpy.ops.wm.read_factory_settings(use_empty=True)
H, R = 0.034, 0.0135          # berry height and widest radius (the ring adds ~6 mm)
TOP = -0.007                  # berry top under the hang point
ORO = (1.0, 0.766, 0.336)     # gold F0


def mat(nombre, color, rough, metal=0.0, coat=0.0, sheen=0.0, sss=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Subsurface Radius"].default_value = (0.004, 0.0008, 0.0006)
    return m


def radio(t):
    """Profile from the top (t=0) to the tip (t=1): rounded shoulders, widest at 0.3, a convex taper to a blunt tip."""
    hombro = math.sin(min(t / 0.3, 1.0) * math.pi / 2) ** 0.5
    return R * hombro * math.cos(max(t - 0.3, 0) / 0.7 * math.pi / 2) ** 0.62 + (0.0004 if t > 0.98 else 0)


def z_hombro(rr):
    """Body surface height at radius rr on the shoulder (where the sepals lie)."""
    for i in range(200):
        t = 0.3 * i / 199
        if radio(t) >= rr:
            return TOP - t * H
    return TOP - 0.3 * H


def semillas(n):
    """Achenes on a golden-angle spiral down the body: (t, phi) per seed."""
    ga = math.pi * (3 - math.sqrt(5))
    return [((i + 0.5) / n * 0.9 + 0.06, (i * ga) % (2 * math.pi)) for i in range(n)]


def superficie(t, phi, lobulo=0.035):
    r = radio(t) * (1 + lobulo * math.sin(5 * phi + 1.3) + 0.02 * noise.noise(Vector((math.cos(phi) * 3, math.sin(phi) * 3, t * 4))))
    return Vector((r * math.cos(phi), r * math.sin(phi), TOP - t * H))


def cuerpo(nombre, m, n_sem, hondo):
    """The berry body as a lathe grid, pits pressed in at each seed (hondo = pit depth in metres)."""
    NT, NP = 72, 96
    sem = semillas(n_sem)
    bm = bmesh.new()
    filas = []
    for i in range(NT + 1):
        t = 0.001 + 0.999 * i / NT
        fila = []
        for j in range(NP):
            phi = 2 * math.pi * j / NP
            p = superficie(t, phi)
            d = 0.0
            for ts, ps in sem:
                dphi = (phi - ps + math.pi) % (2 * math.pi) - math.pi
                dx, dz = dphi * radio(ts), (t - ts) * H
                d += math.exp(-(dx * dx + dz * dz) / (2 * 0.0011 ** 2))
            n = Vector((p.x, p.y, 0)).normalized() if p.xy.length > 1e-6 else Vector((0, 0, -1))
            fila.append(bm.verts.new(p - n * hondo * min(d, 1.0)))
        filas.append(fila)
    for i in range(NT):
        for j in range(NP):
            bm.faces.new((filas[i][j], filas[i][(j + 1) % NP], filas[i + 1][(j + 1) % NP], filas[i + 1][j]))
    tapa = bm.verts.new((0, 0, TOP + 0.0006))
    for j in range(NP):
        bm.faces.new((tapa, filas[0][(j + 1) % NP], filas[0][j]))
    punta = bm.verts.new((0, 0, TOP - H - 0.0004))
    for j in range(NP):
        bm.faces.new((filas[-1][j], filas[-1][(j + 1) % NP], punta))
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    return o, sem


def semilla_objs(sem, m, largo, ancho, sale):
    """One mesh holding every seed: a small ellipsoid in each pit, pointing down the berry."""
    bm = bmesh.new()
    for ts, ps in sem:
        p = superficie(ts, ps)
        n = Vector((p.x, p.y, 0)).normalized()
        g = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0)
        eje_z = Vector((0, 0, 1))
        tan = n.cross(eje_z).normalized()
        baja = tan.cross(n).normalized()
        for v in g["verts"]:
            c = v.co.copy()
            v.co = p + n * (sale - c.y * ancho * 0.6) + tan * c.x * ancho + baja * c.z * largo
    me = bpy.data.meshes.new("fresa_semillas")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("fresa_semillas", me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    return o


def caliz(m, n=8, largo=0.0125, grueso=0.0008):
    """Sepals: n pointed leaves from the top, lying over the shoulders and curling up at the tips."""
    bm = bmesh.new()
    for k in range(n):
        phi = 2 * math.pi * k / n + 0.2 * math.sin(k * 2.3)
        L = largo * (0.85 + 0.3 * ((k * 37) % 7) / 7)
        cols = []
        for i in range(9):
            s = i / 8
            w = 0.0036 * math.sin(math.pi * min(s * 1.1, 1)) ** 0.7 * (1 - 0.55 * s)
            rr = 0.0012 + s * L
            zz = z_hombro(min(rr, R * 0.98)) + 0.0005 + 0.0025 * s ** 3   # lies on the shoulder, the tip lifts
            c = Vector((rr * math.cos(phi), rr * math.sin(phi), zz))
            lat = Vector((-math.sin(phi), math.cos(phi), 0))
            cols.append([bm.verts.new(c + lat * w * u + Vector((0, 0, grueso * (1 - abs(u)) * 0.5))) for u in (-1, 0, 1)])
        for i in range(8):
            for a in range(2):
                bm.faces.new((cols[i][a], cols[i][a + 1], cols[i + 1][a + 1], cols[i + 1][a]))
    me = bpy.data.meshes.new("fresa_caliz")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("fresa_caliz", me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    o.modifiers.new("grosor", "SOLIDIFY").thickness = grueso
    for p in me.polygons:
        p.use_smooth = True
    return o


def tallo_y_aro(m_tallo, m_aro):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0011, depth=0.005, location=(0, 0, TOP + 0.0028), vertices=12)
    t = bpy.context.object
    t.name = "fresa_tallo"
    t.data.materials.append(m_tallo)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0022, minor_radius=0.00045, location=(0, 0, -0.0022), rotation=(math.pi / 2, 0, 0),
                                     major_segments=24, minor_segments=8)
    a = bpy.context.object
    a.name = "fresa_aro"
    a.data.materials.append(m_aro)
    for o in (t, a):
        for p in o.data.polygons:
            p.use_smooth = True


if ESTILO == "fruta":
    rojo = mat("fresa_roja", (0.55, 0.012, 0.018), 0.36, coat=0.35, sss=0.25)
    cuerpo("fresa_cuerpo", rojo, 150, 0.0006)
    semilla_objs(semillas(150), mat("fresa_aquenio", (0.62, 0.42, 0.08), 0.45), 0.0008, 0.00045, -0.0002)
    verde = mat("fresa_sepalo", (0.06, 0.2, 0.03), 0.55, sss=0.1)
    caliz(verde)
    tallo_y_aro(verde, mat("fresa_aro", ORO, 0.25, metal=1.0))
elif ESTILO == "resina":
    rojo = mat("fresa_esmalte", (0.62, 0.008, 0.02), 0.08, coat=1.0)
    cuerpo("fresa_cuerpo", rojo, 60, 0.0003)
    oro = mat("fresa_oro", ORO, 0.2, metal=1.0)
    semilla_objs(semillas(60), oro, 0.0009, 0.0006, 0.0)
    caliz(oro, n=6, largo=0.012, grueso=0.0007)
    tallo_y_aro(oro, oro)
else:  # peluche
    rojo = mat("fresa_fieltro", (0.6, 0.02, 0.03), 0.9, sheen=1.0)
    cuerpo("fresa_cuerpo", rojo, 40, 0.0)
    semilla_objs(semillas(40), mat("fresa_hilo", (0.85, 0.75, 0.3), 0.8, sheen=0.5), 0.0016, 0.0004, 0.0002)
    verde = mat("fresa_fieltro_verde", (0.05, 0.25, 0.04), 0.9, sheen=1.0)
    caliz(verde, n=6, largo=0.012, grueso=0.0018)
    tallo_y_aro(verde, mat("fresa_aro", ORO, 0.25, metal=1.0))

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_apply=True, export_yup=True)
print("FRESA", ESTILO, OUT, len(bpy.data.objects), "objects")

"""P1 "more alive", phase 1 (spec: mothership queue 2026-11-18-mto-vivo-p1-phase1.md): Cycles stills per stop with the P1 look
mocked, on montaje.py's chain (the montaje-esc1..6 stills are the "before"). Runs the chain up to utileria's render loop, as
blender/vivo_secciones_montar.py does, then for each requested shot builds the montaje option, adds the shot's mocks and renders.

  MONTAJE_PANTALLA=c MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta P1_TOMAS=all P1_MODO=cycles \
  WSLENV=MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA:P1_TOMAS:P1_MODO \
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/vivo_p1_stills.py)" \
    -- "$(wslpath -w blender/escena.py)" <out_dir (Windows, absolute)> 64 all 960x540

P1_TOMAS: comma list of shot names (P1_TOMAS_ below) or all. P1_MODO: cycles (stills), p1_holgura (stop-4 clearance only, no render),
previz (stop-4 orbit, Workbench frames to <out>/orbita/). Textures: scripts/p1-texturas.py -> tmp/p1/tex (run it first).
Livery c (Marquesina: bulbs round the screens, the owner's round-2 pick in pantalla_3d.py) carries the edge bulbs P1 asks for.

Mocked per shot (the live build is phase 2): the stop's gantry title on ickdrone's portico_b (y 120) and arco_c (y 24), as the
page places them; drizzle and insects in the headlight cones (1, 5, 6); an oncoming car whose lights rake the cab (1); the dash
screen with a cover, title and ‹ › (1); the bulb chase (every third bulb dim) and LED rear screen with the crawl (3, 5); the
name plate at Héctor's window (4); the headlight flash (6). Glare sprites are a post pass on the PNGs (scripts/p1-destellos.py).
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_MONTAJE = os.path.join(AQUI, "montaje.py")
_src = open(_MONTAJE, encoding="utf8").read()
_LAZO = "# ---------------------------------------------------------------- utileria.py's render loop, over the options above"
assert _src.count(_LAZO) == 1, "montaje.py's render-loop marker moved"
exec(compile(_src.split(_LAZO)[0], _MONTAJE, "exec"), globals())

import json, math, random, time  # every top-level name below is new to the chain or p1_-prefixed: a shared name (choques) broke caja5
import bmesh
from mathutils import Vector, Matrix

P1_MODO_ = os.environ.get("P1_MODO", "cycles")
P1_TEX = os.path.join(REPO, "tmp", "p1", "tex")
VIVO = os.path.join(REPO, "public", "vivo")
p1_mundo = bpy.data.objects["mundo"]


def mat_img(nombre, ruta, emit=0.0, alfa=True, rough=0.4):
    """Image material with alpha (cutout) and optional emission from the image."""
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt, b = m.node_tree, m.node_tree.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(ruta, check_existing=True)
    tx.extension = "CLIP"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if alfa:
        nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    b.inputs["Roughness"].default_value = rough
    return m


def p1_importar(glb):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    return [o for o in bpy.data.objects if o not in antes]


def centro_mundo(o):
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(ps, Vector()) / 8, Vector([max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3)])


def estirar(o, ancho, alto):
    """Scale a flat panel about its centre to ancho (world X) x alto (world Z), in world space (the GLB's 1 x 1 green fields)."""
    c, t = centro_mundo(o)
    mw, inv = o.matrix_world.copy(), o.matrix_world.inverted()
    for v in o.data.vertices:
        p = mw @ v.co
        v.co = inv @ Vector((c.x + (p.x - c.x) * ancho / max(t.x, 1e-3), p.y, c.z + (p.z - c.z) * alto / max(t.z, 1e-3)))


# ---------------------------------------------------------------- gantry and arch with the stop's title (as the live page)
TITULOS = [mat_img(f"p1_titulo_{k}", os.path.join(P1_TEX, f"titulo-{k}.png"), emit=1.2) for k in range(1, 7)]
ROTULOS = []
for glb, y_glb, y, (zt, yt, w) in (("portico_b.glb", 100.0, 120.0, (7.0, 0.09, 3.2)), ("arco_c.glb", 200.0, 24.0, (6.2, 0.49, 3.0))):
    objs = p1_importar(os.path.join(VIVO, glb))
    for o in objs:
        if o.parent is None:
            o.location.y += y - y_glb
    bpy.context.view_layer.update()
    for o in objs:
        if o.type != "MESH":
            continue
        c, t = centro_mundo(o)
        m0 = o.data.materials[0].name if o.data.materials else ""
        if o.name.startswith("st_txt") and m0.startswith("u_blanco_refl") and abs(c.z - zt) < 0.5 and abs(c.x - CX) < 1.2:
            print("P1 rotulo viejo fuera", glb, o.name, [round(v, 2) for v in c], flush=True)
            o.hide_render = o.hide_viewport = True  # REDES / GIRA
        if m0.startswith("u_verde_sct") and t.x < 1.2:
            estirar(o, *((3.64, 2.04) if glb.startswith("portico") else (3.04, 1.04)))
            print("P1 campo verde estirado", glb, o.name, flush=True)
    r = plano(w, w * 170 / 1024, (CX, y - yt, zt), TITULOS[0], parent=False)
    if r in GRUPO:
        GRUPO.remove(r)
    ROTULOS.append(r)
    bpy.context.view_layer.update()  # plano() sets scale after the add: a stale matrix_world here dropped it (labels 1 m wide)
    for o in objs + [r]:
        if o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = p1_mundo
            o.matrix_world = mw


def titulo(k):
    for r in ROTULOS:
        r.data.materials[0] = TITULOS[k - 1]


# ---------------------------------------------------------------- mocks
def llovizna(cam, n=1800, semilla=7):
    """Drizzle streaks (falling, streaming back past the truck) and a few insects, in the volume ahead of the headlights; lit
    only where the beams reach them. One mesh, riding with the truck. Nothing within 3 m of the camera: drops at the lens (stops 5
    and 6 sit inside this volume) rendered as big bright blobs over the rear-screen copy in the first run."""
    rnd = random.Random(semilla)
    bm = bmesh.new()
    eje = Vector((0, -0.45, -1)).normalized()
    rot = eje.to_track_quat("Z", "Y").to_matrix().to_4x4()
    for _ in range(n):
        p = Vector((rnd.uniform(-1.6, 5.0), rnd.uniform(3.3, 30.0), rnd.uniform(0.1, 3.0)))
        if (p - Vector(cam)).length < 3.0:
            continue
        L = rnd.uniform(0.06, 0.18)
        bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=0.0022, radius2=0.0022, depth=L, matrix=Matrix.Translation(p) @ rot)
    me = bpy.data.meshes.new("p1_llovizna")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("p1_llovizna", me)
    sc.collection.objects.link(o)
    m = bpy.data.materials.new("p1_gota")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.85, 0.88, 0.92, 1)
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Alpha"].default_value = 0.75
    me.materials.append(m)
    bichos = []
    pol = mat("p1_bicho", (0.75, 0.72, 0.65), 0.6)
    for _ in range(40):
        q = Vector((rnd.uniform(0.0, 3.4), rnd.uniform(3.4, 9.0), rnd.uniform(0.6, 1.9)))
        if (q - Vector(cam)).length >= 3.0:
            bichos.append(esfera(0.009, q, pol, parent=False))
    for b_ in bichos:
        if b_ in GRUPO:
            GRUPO.remove(b_)
    return [o] + bichos


def coche_contrario(y):
    """A Quaternius car (ickdrone's export, CC0) on the opposite carriageway, facing -Y, with two spots aimed at the cab."""
    objs = p1_importar(os.path.join(VIVO, "coche_basic.glb"))
    raiz = bpy.data.objects.new("p1_coche", None)
    sc.collection.objects.link(raiz)
    bpy.context.view_layer.update()
    ps = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    c = Vector([(min(p[i] for p in ps) + max(p[i] for p in ps)) / 2 for i in range(3)])
    largo = max(p.y for p in ps) - min(p.y for p in ps)
    raiz.location = (c.x, c.y, 0)
    for o in objs:
        if o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = raiz
            o.matrix_world = mw
    raiz.location, raiz.rotation_euler = (-7.8, y, 0), (0, 0, math.pi)  # it faces +Y as exported: turn it to face the band
    bpy.context.view_layer.update()
    luces, focos = [], mat("p1_faro_coche", (1, 1, 1), 0.2, emit=40)
    for dx in (-0.55, 0.55):
        p = Vector((-7.8 + dx, y - largo / 2 - 0.05, 0.62))
        ld = bpy.data.lights.new("p1_faro_coche", "SPOT")
        ld.energy, ld.color, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 1500, (0.93, 0.96, 1.0), math.radians(70), 0.5, 0.05
        lo = bpy.data.objects.new("p1_faro_coche", ld)
        sc.collection.objects.link(lo)
        lo.location = p
        lo.rotation_euler = (Vector((CX, -0.3, 1.6)) - p).to_track_quat("-Z", "Y").to_euler()
        luces += [lo, esfera(0.06, p + Vector((0, 0.02, 0)), focos, parent=False)]
    for o in luces:
        if o in GRUPO:
            GRUPO.remove(o)
    return [raiz] + objs + luces


def borrar(objs):
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)


def pantalla_tablero():
    """radio2-a's floating wide screen on the dash top (utileria), with the P1 face: cover, title, Escuchar, ‹ › (tablero.png)."""
    import shutil
    shutil.copy(os.path.join(P1_TEX, "tablero.png"), os.path.join(PANTALLAS, "p1-tablero.png"))
    y = TABLERO.y + 0.06
    z = techo_tablero(y) + 0.095
    caja((0.05, 0.03, 0.06), (CX, y + 0.03, z - 0.07), CRISTAL, bevel=0.004)
    cara_pantalla(0.36, 0.12, (CX, y, z), 0.12, "p1-tablero")


def focos_en_a():
    """Livery A (owner 16:42) with the Marquesina bulbs kept as the box's own edge light: pantalla_3d.py's livery-c bulb ring,
    same spacing, size and p3_foco material (so persecucion() finds them), on the A truck already built in GRUPO."""
    t = next(o for o in GRUPO if o.name.startswith("p3_camion"))  # earlier shots leave hidden copies: take this shot's
    x, yb = t.location.x, t.location.y
    xs, yc, ya = x + P3_W / 2 + 0.006, yb + P3_L / 2, yb - 0.008
    (w, h, zc), (wa, ha, za) = P3_LADO, P3_ATRAS
    foco = mat("p3_foco", (1.0, 0.75, 0.4), 0.3, emit=12)
    n = int((w + 0.2) / 0.2) + 1
    for i in range(n):
        for zz in (zc - h / 2 - 0.07, zc + h / 2 + 0.07):
            esfera(0.045, (xs + 0.03, yc - (n - 1) * 0.1 + i * 0.2, zz), foco, parent=False)
    n = int((wa + 0.2) / 0.2) + 1
    for i in range(n):
        for zz in (za - ha / 2 - 0.07, za + ha / 2 + 0.07):
            esfera(0.045, (x - (n - 1) * 0.1 + i * 0.2, ya - 0.03, zz), foco, parent=False)
    for dx in (-1, 1):
        for i in range(1, int(ha / 0.2) + 1):
            esfera(0.045, (x + dx * (wa / 2 + 0.07), ya - 0.03, za - ha / 2 - 0.07 + i * 0.2), foco, parent=False)


def persecucion():
    """Bulb chase as a still: every third Marquesina bulb (p3_foco) dims, so the frozen frame shows the chase's phase."""
    tenue = mat("p1_foco_tenue", (1.0, 0.75, 0.4), 0.3, emit=1.5)
    focos = sorted((o for o in GRUPO if o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith("p3_foco")),
                   key=lambda o: (round(o.location.z, 1), o.location.x + o.location.y))
    for i, o in enumerate(focos):
        if i % 3 == 0:
            o.data = o.data.copy()
            o.data.materials[0] = tenue
    print("P1 focos", len(focos), "tenues", len(focos[::3]), flush=True)


def trasera(variante):
    """The rear board as an LED panel with the stop-5 copy: the old PRÓXIMAS FECHAS / MUY PRONTO lettering goes."""
    negro = [o for o in GRUPO if o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith("p3_led_negro")]
    for o in [o for o in GRUPO if o.type == "FONT" and o.data.body in ("PRÓXIMAS FECHAS", "MUY PRONTO")]:
        o.hide_render = True
    p = negro[0].location
    pl = panel_led(2.0, 2.05, (p.x, p.y - 0.003, p.z), ATRAS_ROT, os.path.join(P1_TEX, f"trasera-{variante}.png"), 180)
    for n in pl.data.materials[0].node_tree.nodes:  # img_mat's LED cells are cols x cols/2 per UV unit (16:9 panels): square here
        if n.type == "VECT_MATH" and n.operation == "MULTIPLY":
            n.inputs[1].default_value = (180, 185, 1)
        if n.type == "BSDF_PRINCIPLED":
            # an LED wall is black where it doesn't emit: with the image as base colour our headlights washed the copy milky
            for l in list(n.inputs["Base Color"].links):
                pl.data.materials[0].node_tree.links.remove(l)
            n.inputs["Base Color"].default_value = (0.004, 0.004, 0.004, 1)
            n.inputs["Emission Strength"].default_value = 6.0  # 2.0 sank into the headlit fog volume between camera and truck; the old board used 6
    return pl


def placa_nombre(cam):
    """Héctor's name plate at the passenger window (front right), turned toward the camera."""
    p = Vector((CX + 1.2, 0.35, 1.78))
    m = mat_img("p1_placa", os.path.join(P1_TEX, "placa-hector.png"), emit=1.5, alfa=False)
    o = plano(0.62, 0.62 * 384 / 1024, p, m, parent=False)
    d = Vector(cam) - p
    o.rotation_euler = (math.pi / 2, 0, math.atan2(d.x, -d.y))  # the plane's -Y face (the readable one) turned toward the camera
    return o


def lamparas_cara():
    """Stop 4's cab lamps (utileria.luz_costado 'cabina': 6 W over each seat at z 1.98, x CX +-0.4, y 0.2 / -0.6) predate the v5
    cast: the rear two sit inside Alejandro's and Diego's heads, the front two light the backs of the front heads. Mock: each lamp
    0.3 m in front of its member's face, just under the roof, hidden from the camera. Returns the moves to undo."""
    lamparas = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "POINT" and abs(o.location.z - 1.98) < 0.01
                and abs(abs(o.location.x - CX) - 0.4) < 0.01 and min(abs(o.location.y - 0.2), abs(o.location.y + 0.6)) < 0.01
                and not o.hide_render]
    hechos = []
    for o in lamparas:
        hx, hy, hz = min(P1_BANDA.values(), key=lambda h: (Vector(h[:2]) - o.location.xy).length)
        hechos.append((o, o.location.copy(), o.visible_camera))
        o.location, o.visible_camera = (hx, hy + 0.3, 2.12), False
    print("P1 LAMPARAS", len(lamparas), [tuple(round(v, 2) for v in o.location) for o, _, _ in hechos], flush=True)
    return hechos


def destello(on):
    """Stop 6's flash: both headlights at 3x, and their lenses as bright spheres for the glare pass."""
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("faro_"):
            o.data.energy = 7200 if on else 2400


# ---------------------------------------------------------------- stop 4 cameras (hood side, looking in through the windshield)
P1_C4 = Vector((CX, -0.35, 1.55))
R4, Z4 = 2.9, 1.9
orbita = lambda a: (Vector((CX + R4 * math.sin(math.radians(a)), P1_C4.y + R4 * math.cos(math.radians(a)), Z4)), P1_C4, 24)
CAM4 = {
    "4a": ((CX + 1.03, 2.05, 1.85), (CX - 0.12, -0.5, 1.5), 20),  # corner: front passenger corner of the hood
    "4b": ((CX, 2.35, 1.79), (CX, -0.45, 1.55), 20),              # middle: the 11-16 hood pose (ruta.json 695)
    "4c1": orbita(-70), "4c2": orbita(0), "4c3": orbita(70),      # orbit over the hood, driver side -> passenger side
}
# owner 17:33: stop 4 = four shots, one per member, the camera rigged on a corner of the cab roof. Ref: Collateral's cab
# hard-mounts (one face per window, the night road behind). Heads (p1_banda, stop 4's build): manager front-left, Héctor
# front-right, Alejandro rear-left, Diego rear-right, z ~2.0; roof z 2.23. First guesses on the roof (z 2.3) and inside were
# blocked by the roof edge at 0.3-0.46 m or under 0.10 m; p1_buscar found free spots only at window height (z 2.0) just outside
# the side windows. Changed from the ref: the rig hangs from the roof corner down to the window. Per member, 1 = the corner in
# front of the face (front row: the cab's front corner; rear row: the rear window's front edge), 2 = the alternative
# (front row: further out, 24 mm; rear row: the cab's rear corner, over the shoulder)
P1_BANDA = {"manager": (1.33, 0.49, 2.0), "hector": (2.08, 0.45, 2.0), "alejandro": (1.33, -0.56, 2.02), "diego": (2.12, -0.45, 1.98)}
for _q, _s, (_x, _y, _z) in (("man", -1, P1_BANDA["manager"]), ("hec", 1, P1_BANDA["hector"]),
                             ("ale", -1, P1_BANDA["alejandro"]), ("die", 1, P1_BANDA["diego"])):
    _m = (_x, _y, _z - 0.08)  # the face, a little under the head's top
    if _y > 0:
        CAM4[f"4-{_q}-1"] = ((CX + _s * 0.90, 0.9, 2.0), _m, 20)
        CAM4[f"4-{_q}-2"] = ((CX + _s * 1.00, 1.05, 2.0), _m, 24)
    else:
        CAM4[f"4-{_q}-1"] = ((CX + _s * 1.00, -0.15, 2.0), _m, 20)
        CAM4[f"4-{_q}-2"] = ((CX + _s * 0.90, -0.9, 2.0), _m, 20)
# 3 = the sheet's fix for 2 (Héctor) and 1 (Diego): their chins were cut; aimed 0.2 m lower (the face, not the cap), wider lens
CAM4["4-hec-3"] = ((CX + 1.00, 1.05, 2.0), (2.08, 0.45, 1.80), 20)
CAM4["4-die-3"] = ((CX + 1.00, -0.15, 2.0), (2.12, -0.45, 1.76), 18)
# the manager from his own window was unlit (the cab light is on the passenger side) and Héctor, lit, read as the subject:
# from the front-left corner through the windshield instead
CAM4["4-man-3"] = ((1.0, 1.6, 2.0), (1.33, 0.49, 1.84), 24)
CAM4["4-man-4"] = ((1.25, 1.45, 2.05), (1.33, 0.49, 1.84), 20)

P1_VIDRIOS = ("vidrio", "VIDRIO", "mica", "k3_vidrio", "p1_gota")
P1_DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]


def p1_material(r, dg):
    if r[4].type != "MESH":
        return "?"
    me = r[4].evaluated_get(dg).data
    if r[3] >= len(me.polygons) or me.polygons[r[3]].material_index >= len(me.materials) or not me.materials[me.polygons[r[3]].material_index]:
        return "?"
    return me.materials[me.polygons[r[3]].material_index].name


def p1_holgura(p, alcance=1.0):
    """ruta.py's clearance (meltingdrone, apertura-espiral.md): nearest non-glass surface along 26 rays from p."""
    dg = bpy.context.evaluated_depsgraph_get()
    cerca = (alcance, None)
    for d in P1_DIRS:
        o, rec = Vector(p), 0.0
        for _ in range(4):
            r = sc.ray_cast(dg, o, d, distance=alcance - rec)
            if not r[0]:
                break
            rec += (r[1] - o).length
            if not p1_material(r, dg).startswith(P1_VIDRIOS):
                if rec < cerca[0]:
                    cerca = (rec, r[4].name)
                break
            o = r[1] + d * 1e-4
    return round(cerca[0], 3), cerca[1]


def p1_choques(puntos):
    """ruta.py's p1_choques: a ray between consecutive camera positions, any non-glass surface it crosses."""
    dg = bpy.context.evaluated_depsgraph_get()
    malos = []
    for i in range(len(puntos) - 1):
        a, b = Vector(puntos[i]), Vector(puntos[i + 1])
        r = sc.ray_cast(dg, a, (b - a).normalized(), distance=(b - a).length)
        if r[0] and not p1_material(r, dg).startswith(P1_VIDRIOS):
            malos.append((i, r[4].name, p1_material(r, dg)))
    return malos


def p1_vista(pos, mira, propio=None):
    """Is the look-at point seen, or does a non-glass surface sit between the camera and the cab (hood, mirror, A-pillar)?
    propio: a member shot's own member (hector_v5: any object named hector*), the only cast hit
    skipped; without it every cast hit is skipped. With it, the strict gate: no other member between the lens and the face."""
    dg = bpy.context.evaluated_depsgraph_get()
    a, b = Vector(pos), Vector(mira)
    o, rec, n = a.copy(), 0.0, (b - a).length
    while rec < n:
        r = sc.ray_cast(dg, o, (b - a).normalized(), distance=n - rec)
        if not r[0]:
            return "libre"
        salta = r[4].name.split(".")[0].split("_")[0] == propio.split("_")[0] if propio else r[4].name in [f.name for f in FIGURAS]
        if not p1_material(r, dg).startswith(P1_VIDRIOS) and not salta:
            return f"tapa {r[4].name} ({p1_material(r, dg)}) a {rec + (r[1] - o).length:.2f} m"
        rec += (r[1] - o).length
        o = r[1] + (b - a).normalized() * 1e-4
    return "libre"


ORBITA_N = 72  # 3 s at 24 fps: a quick orbit
ORBITA = [orbita(-80 + 160 * (0.5 - 0.5 * math.cos(math.pi * i / (ORBITA_N - 1))))[0] for i in range(ORBITA_N)]

# ---------------------------------------------------------------- shots
P1_TOMAS_ = {
    "1a": ("montaje-esc1", 1, dict(gotas=True, coche=46, tablero=True)),
    "1b": ("montaje-esc1", 1, dict(gotas=True, coche=17, tablero=True)),
    "2": ("montaje-esc2", 2, dict()),
    "3": ("montaje-esc3", 3, dict(chase=True)),
    "4a": ("montaje-esc4", 4, dict(cam="4a", placa=True)),
    "4b": ("montaje-esc4", 4, dict(cam="4b", placa=True)),
    "4c1": ("montaje-esc4", 4, dict(cam="4c1")),
    "4c2": ("montaje-esc4", 4, dict(cam="4c2", placa=True)),
    "4c3": ("montaje-esc4", 4, dict(cam="4c3")),
    "5v1": ("montaje-esc5", 5, dict(gotas=True, chase=True, trasera="v1")),
    "5v2": ("montaje-esc5", 5, dict(gotas=True, chase=True, trasera="v2")),
    "5v3": ("montaje-esc5", 5, dict(gotas=True, chase=True, trasera="v3")),
    # livery A (MONTAJE_PANTALLA=a) with the edge bulbs kept; plain 3 and 5v1 on A are the bulbs-dropped way
    "3focos": ("montaje-esc3", 3, dict(focos=True, chase=True)),
    "5v1focos": ("montaje-esc5", 5, dict(gotas=True, focos=True, chase=True, trasera="v1")),
    **{k: ("montaje-esc4", 4, dict(cam=k)) for k in CAM4 if k.startswith("4-")},  # the per-member candidates (owner 17:33)
    **{k + "L": ("montaje-esc4", 4, dict(cam=k, lamparas=True)) for k in CAM4 if k.startswith("4-")},  # with the lamps moved
    "6": ("montaje-esc6", 6, dict(gotas=True)),
    "6flash": ("montaje-esc6", 6, dict(gotas=True, flash=True)),
}
pedidas = os.environ.get("P1_TOMAS", "all")
pedidas = list(P1_TOMAS_) if pedidas == "all" else pedidas.split(",")
os.makedirs(OUT, exist_ok=True)

if P1_MODO_ in ("p1_holgura", "cycles") and any(t.startswith("4") for t in pedidas):
    GRUPO.clear()
    OPC["montaje-esc4"]()  # stop 4's own props and lights in place, as the stills will have them
    P1_QUIEN = {"man": "manager_v5", "hec": "hector_v5", "ale": "alejandro_v5", "die": "diego_v5"}
    for k, (pos, mira, lens) in CAM4.items():
        quien = P1_QUIEN[k.split("-")[1]] if k.startswith("4-") else None
        print("P1 HOLGURA", k, p1_holgura(pos), "p1_vista", p1_vista(pos, mira, quien), flush=True)
    # live build (owner 19:11): each member shot leaves on one straight leg to a point outside the body's box (vivoRuta);
    # the leg must cross no non-glass surface and keep clear of the body
    P1_SALIDAS = {"4-man-4": [(1.25, 3.45, 2.05), (1.25, 3.45, 2.4)], "4-hec-3": [(3.4, 1.05, 2.0), (3.4, 1.6, 2.0), (3.4, 1.05, 2.4)],
                  "4-ale-1": [(0.04, -0.15, 2.0), (0.04, -0.15, 2.3)], "4-die-3": [(3.4, -0.15, 2.0), (3.4, -0.15, 2.3)]}
    for k, ss in P1_SALIDAS.items():
        for sal in ss:
            a, b = Vector(CAM4[k][0]), Vector(sal)
            pts = [a.lerp(b, t / 20) for t in range(21)]
            print("P1 SALIDA", k, sal, "choques", p1_choques(pts), "holgura min", min(p1_holgura(x, 0.5)[0] for x in pts[1:]), flush=True)
    # the cab lamps vs the v5 heads: nearest member surface to each lamp, and whether the lamp is inside that mesh
    dg = bpy.context.evaluated_depsgraph_get()
    for o in [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "POINT" and abs(o.location.z - 1.98) < 0.01 and not o.hide_render]:
        mejor = None
        for q in P1_QUIEN.values():
            f = bpy.data.objects[q]
            e = f.evaluated_get(dg)
            ok, c, nrm, _ = e.closest_point_on_mesh(e.matrix_world.inverted() @ o.location)
            if ok:
                cw = e.matrix_world @ c
                d = (cw - o.location).length
                dentro = (o.location - cw).dot((e.matrix_world.to_3x3() @ nrm).normalized()) < 0
                if mejor is None or d < mejor[1]:
                    mejor = (q, round(d, 3), dentro)
        print("P1 LAMPARA", tuple(round(v, 2) for v in o.location), "->", mejor, flush=True)
    peor = min((p1_holgura(p) + (i,) for i, p in enumerate(ORBITA)), key=lambda x: x[0])
    print("P1 HOLGURA orbita min", peor, "cuadros < 0.10 m", sum(p1_holgura(p)[0] < 0.10 for p in ORBITA), "CHOQUES", p1_choques(ORBITA), flush=True)
    for o in GRUPO:
        o.hide_render = True

for nombre in pedidas if P1_MODO_ == "cycles" else []:
    op, parada, cfg = P1_TOMAS_[nombre]
    t1 = time.time()
    GRUPO.clear()
    sc.frame_set(0)
    pos, mira, lens = OPC[op]()
    extra = []
    titulo(parada)
    if cfg.get("coche"):
        extra += coche_contrario(cfg["coche"])
    if cfg.get("tablero"):
        pantalla_tablero()
    if cfg.get("focos"):
        focos_en_a()
    if cfg.get("chase"):
        persecucion()
    if cfg.get("trasera"):
        trasera(cfg["trasera"])
    lamparas = lamparas_cara() if cfg.get("lamparas") else []
    if cfg.get("cam"):
        pos, mira, lens = CAM4[cfg["cam"]]
    if cfg.get("placa"):
        placa_nombre(pos)
    if cfg.get("gotas"):
        extra += llovizna(pos)
    destello(cfg.get("flash", False))
    cd = bpy.data.cameras.new("cam_" + nombre)
    cd.clip_start, cd.clip_end, cd.lens, cd.sensor_fit = 0.01, 3000, lens, "HORIZONTAL"
    co = bpy.data.objects.new("cam_" + nombre, cd)
    sc.collection.objects.link(co)
    co.location = Vector(pos)
    co.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = RW, RH, 100
    sc.render.filepath = os.path.join(OUT, f"p1-{nombre}.png")
    _pr = bpy.context.preferences.addons["cycles"].preferences
    t_r = time.time()
    bpy.ops.render.render(write_still=True)
    # owner 16:24: renders on the GPU only. The device and the time inside render() (the rest of a shot is the props build)
    print("P1 RENDER", nombre, sc.cycles.device, _pr.compute_device_type, [d.name for d in _pr.devices if d.use], round(time.time() - t_r, 1), "s", flush=True)
    for o in GRUPO:
        o.hide_render = True
    for o in FIGURAS:
        o.hide_render = False
    borrar(extra)
    for o, loc, vis in lamparas:
        o.location, o.visible_camera = loc, vis
    destello(False)
    print("P1 TOMA", nombre, round(time.time() - t1, 1), "s", json.dumps({"pos": list(pos), "mira": list(mira), "lens": lens}), flush=True)

if P1_MODO_ == "p1_banda":
    # stop 4 as four shots, one per member (owner 17:33): where each member's head sits in stop 4's build, and the cab's top
    GRUPO.clear()
    sc.frame_set(0)
    OPC["montaje-esc4"]()
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.split(".")[0].endswith("_v5") and not o.hide_render:
            e = o.evaluated_get(dg)
            vs = [e.matrix_world @ v.co for v in e.to_mesh().vertices]
            zt = max(v.z for v in vs)
            cab = [v for v in vs if v.z > zt - 0.22]
            c = sum(cab, Vector()) / len(cab)
            print("P1 BANDA", o.name, "cabeza", [round(x, 3) for x in c], "z min", round(min(v.z for v in vs), 3), flush=True)
            e.to_mesh_clear()
    for x in (CX - 0.9, CX - 0.6, CX + 0.6, CX + 0.9):
        for y in (-1.6, -1.2, 0.0, 0.6, 1.0):
            r = sc.ray_cast(dg, Vector((x, y, 4.0)), Vector((0, 0, -1)), distance=4.0)
            print("P1 TECHO", round(x, 2), y, round(r[1].z, 3) if r[0] else None, r[4].name if r[0] else "", flush=True)

if P1_MODO_ == "p1_buscar":
    # the roof-corner guesses were all blocked (trim at 0.3-0.46 m) or under 0.10 m: search a grid per member and print the
    # positions with clearance >= 0.12 m and a free sight line to the face, nearest to the member's roof corner first
    GRUPO.clear()
    sc.frame_set(0)
    OPC["montaje-esc4"]()
    dentro_cab = lambda p: abs(p[0] - CX) < 0.8 and -0.9 < p[1] < 0.95 and 1.0 < p[2] < 2.2
    for q, (hx, hy, hz) in P1_BANDA.items():
        s, f = (1 if hx > CX else -1), (1 if hy > 0 else -1)
        esquina = Vector((CX + s * 0.85, f * 0.95, 2.23))
        cara = (hx, hy, hz - 0.08)
        buenos = []
        for x in [CX + s * (-0.7 + 0.1 * i) for i in range(22)]:
            for y in [f * (-0.6 + 0.15 * j) for j in range(17)]:
                for z in (1.85, 2.0, 2.15, 2.3, 2.45, 2.6):
                    p = Vector((x, y, z))
                    if (p - Vector(cara)).length < 0.45:
                        continue
                    if p1_vista(p, cara) != "libre":
                        continue
                    h = p1_holgura(p, 0.5)[0]
                    if h >= 0.12:
                        buenos.append(((p - esquina).length, [round(x, 2), round(y, 2), z], h))
        buenos.sort()
        print("P1 BUSCAR", q, len(buenos), "posiciones; cerca de la esquina:", buenos[:6], flush=True)
        ins = [b for b in buenos if dentro_cab(b[1])]
        print("P1 BUSCAR", q, "dentro de la cabina:", sorted(ins, key=lambda b: -b[2])[:4], flush=True)

if P1_MODO_ == "previz":
    # Workbench (montaje's pase_wb: flat colours, glass hidden), stop 4's build, the orbit keyed frame by frame while the world drives
    OPC["montaje-esc4"]()
    pase_wb()
    titulo(4)
    cd = bpy.data.cameras.new("cam_orbita")
    cd.clip_start, cd.clip_end, cd.lens, cd.sensor_fit = 0.01, 3000, 24, "HORIZONTAL"
    co = bpy.data.objects.new("cam_orbita", cd)
    sc.collection.objects.link(co)
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 640, 360, 100
    os.makedirs(os.path.join(OUT, "orbita"), exist_ok=True)
    for i, p in enumerate(ORBITA):
        sc.frame_set(i)
        co.location = p
        co.rotation_euler = (P1_C4 - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "orbita", f"f{i:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("P1 PREVIZ", len(ORBITA), "cuadros", flush=True)
print("P1 listo", flush=True)

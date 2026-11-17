"""The whole site as one moving run (downbaddrone, 2026-11-16; docs/design/movimiento-plan.md). Builds montaje.py's scene once,
dressed with every scene's picks at the same time, and keys the camera, the pantalla móvil, the section signs and the headlight
flash from src/lib/ruta.json, the file the page's src/lib/ruta.ts reads. Then it writes src/lib/ruta.bake.json (the camera as
rendered, for the parity test `bun test src/lib/ruta.test.ts`) and renders the frames.

  RUTA_PERIODOS=8 MONTAJE_PANTALLA=b MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta \
  WSLENV=RUTA_PERIODOS:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA:RUTA_PASO:RUTA_DESDE:RUTA_HASTA:RUTA_RENDER:RUTA_PREVIA:RUTA_PREVIA_DESDE \
    /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/ruta.py)" -- \
    "$(wslpath -w blender/escena.py)" <out_dir (Windows)> <samples> ruta 960x540 [wb]

RUTA_RENDER=0 keys and bakes only. RUTA_PASO=n renders every n-th frame; RUTA_DESDE / RUTA_HASTA bound the range;
RUTA_CUADROS="36,647" renders only those frames (add it to WSLENV).
The band loop (ruta.json bucles, 480 frames) is keyed at its `clip` frame (1127..1606) after the run: render it alone with
RUTA_DESDE=1127 RUTA_HASTA=1606. RUTA_PREVIA=<ticks.json, Windows path> (+ RUTA_PREVIA_DESDE, the world frame of tick 0) renders the
page's own stepping instead, one still per tick into <out>/previa/: the ticks come from ruta.ts paso() (a bun script writes
[[f, t|null], ...]). RUTA_PERIODOS must be at least the last world frame / 240 + 2: 9 for the loop clip.
The road is straight in the clips (owner 2026-11-16, option A: road3's bend does not scroll with `mundo`); RUTA_PERIODOS=7 builds
the road 7 loop periods ahead, because the run slides about 980 m and never wraps.
"""
import bpy, json, math, os, sys, time
from mathutils import Matrix, Vector, Quaternion

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO_R = os.path.dirname(AQUI)
RUTA = json.load(open(os.path.join(REPO_R, "src", "lib", "ruta.json"), encoding="utf8"))
PERIODO_V = 240

# ---------------------------------------------------------------- montaje.py, without utileria's still loop
_M = os.path.join(AQUI, "montaje.py")
_LAZO_M = "# ---------------------------------------------------------------- utileria.py's render loop, over the options above"
_src_m = open(_M, encoding="utf8").read()
assert _LAZO_M in _src_m
exec(compile(_src_m.split(_LAZO_M)[0], _M, "exec"), globals())
t_r = time.time()


# ---------------------------------------------------------------- the sampler: the same math as src/lib/ruta.ts
def tangentes(ps, val, ext=None):
    n = len(ps)

    def sec(i):
        return [(y - x) / (ps[i + 1]["fr"] - ps[i]["fr"]) for x, y in zip(val(ps[i]), val(ps[i + 1]))]

    def tan(i):  # monotone tangents, as ruta.ts: zero where a component turns back, capped at 3x the slower slope
        if i == 0:
            return ext[0] if ext else sec(0)
        if i == n - 1:
            return ext[1] if ext else sec(n - 2)
        d0, d1 = sec(i - 1), sec(i)
        h0, h1 = ps[i]["fr"] - ps[i - 1]["fr"], ps[i + 1]["fr"] - ps[i]["fr"]
        out = []
        for a, b in zip(d0, d1):
            if a * b <= 0:
                out.append(0.0)
                continue
            m = (a * h1 + b * h0) / (h0 + h1)
            out.append(math.copysign(min(abs(m), 3 * abs(a), 3 * abs(b)), m))
        return out
    return tan


def hermite(ps, val, f, ext=None, tan=None):
    if f <= ps[0]["fr"]:
        return val(ps[0])
    if f >= ps[-1]["fr"]:
        return val(ps[-1])
    k = 0
    while ps[k + 1]["fr"] < f:
        k += 1
    tan = tan or tangentes(ps, val, ext)
    h = ps[k + 1]["fr"] - ps[k]["fr"]
    s = (f - ps[k]["fr"]) / h
    s2, s3 = s * s, s * s * s
    h00, h10, h01, h11 = 2 * s3 - 3 * s2 + 1, s3 - 2 * s2 + s, -2 * s3 + 3 * s2, s3 - s2
    p0, p1, m0, m1 = val(ps[k]), val(ps[k + 1]), tan(k), tan(k + 1)
    return [h00 * x + h10 * h * a + h01 * y + h11 * h * b for x, a, y, b in zip(p0, m0, p1, m1)]


def _norm(v):
    l = math.sqrt(sum(x * x for x in v))
    return [x / l for x in v]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _ondas(o, f):
    return sum(g * math.sin(2 * math.pi * c * f / PERIODO_V) for g, c in o) * math.pi / 180


def _girar(cols, eje, a):
    c, s = math.cos(a), math.sin(a)
    u, v = ((1, 2), (2, 0), (0, 1))[eje]
    out = list(cols)
    out[u] = [c * x + s * y for x, y in zip(cols[u], cols[v])]
    out[v] = [-s * x + c * y for x, y in zip(cols[u], cols[v])]
    return out


def cam_val(p):
    return p["pos"] + p["mira"] + [p["mm"]]


def muestra(f):
    """(columns x, y, z, pos) in three.js axes, lens mm."""
    return orientar(hermite(RUTA["camara"], cam_val, f), f)


# the band station's loop, as ruta.ts bucle(): loop frame t in [0, hasta - desde] is the run's own stretch; the rest runs from the
# run's pose at `hasta` through the loop points back to its pose at `desde`, with the run's tangents at both ends
BUC = RUTA["bucles"][0]
L1 = BUC["hasta"] - BUC["desde"]
_corr = {p["fr"]: i for i, p in enumerate(RUTA["camara"])}
_tan_c = tangentes(RUTA["camara"], cam_val)
EXT_B = [_tan_c(_corr[BUC["hasta"]]), _tan_c(_corr[BUC["desde"]])]


def tangentes_c2(T, Y, e0, e1):  # ruta.ts tangentesC2: the clamped cubic spline's knot tangents (C2), Thomas algorithm
    n = len(T)
    h = [T[i + 1] - T[i] for i in range(n - 1)]
    d = [[(y - x) / h[i] for x, y in zip(Y[i], Y[i + 1])] for i in range(n - 1)]
    a = [h[i] if 0 < i < n - 1 else 0 for i in range(n)]
    c = [h[i - 1] if 0 < i < n - 1 else 0 for i in range(n)]
    b = [2 * (h[i - 1] + h[i]) if 0 < i < n - 1 else 1 for i in range(n)]
    r = [list(e0) if i == 0 else list(e1) if i == n - 1 else [3 * (h[i] * p + h[i - 1] * q) for p, q in zip(d[i - 1], d[i])]
         for i in range(n)]
    for i in range(1, n):
        w = a[i] / b[i - 1]
        b[i] -= w * c[i - 1]
        r[i] = [x - w * y for x, y in zip(r[i], r[i - 1])]
    m = [None] * n
    m[n - 1] = [x / b[n - 1] for x in r[n - 1]]
    for i in range(n - 2, -1, -1):
        m[i] = [(x - c[i] * y) / b[i] for x, y in zip(r[i], m[i + 1])]
    return m


# moves 2-3 as eased: scripts/bucle-suave.py's `suave` rows [t, pos, mira, mm], a C2 spline through them (no acceleration jump)
PTS_S = [{"fr": r[0], "v": r[1:]} for r in BUC["suave"]]
TAN_S = tangentes_c2([p["fr"] for p in PTS_S], [p["v"] for p in PTS_S], EXT_B[0], EXT_B[1])


def bucle(t):
    u = t % BUC["largo"]
    if u <= L1:
        return muestra(BUC["desde"] + u)
    return orientar(hermite(PTS_S, lambda p: p["v"], u, tan=lambda i: TAN_S[i]), BUC["desde"] + u)


def orientar(v, f):
    pos, mira, mm = v[0:3], v[3:6], v[6]
    z = _norm([a - b for a, b in zip(pos, mira)])
    x = _norm(_cross([0, 1, 0], z))
    cols = [x, _cross(z, x), z]
    vb = RUTA["vibra"]
    cols = _girar(cols, 0, _ondas(vb["cabeceo"], f))
    cols = _girar(cols, 1, _ondas(vb["giro"], f))
    cols = _girar(cols, 2, _ondas(vb["alabeo"], f))
    return cols + [pos], mm


def flash_v(f):
    k = RUTA["flash"]
    if f <= k[0][0] or f >= k[-1][0]:
        return 0.0
    i = 0
    while k[i + 1][0] < f:
        i += 1
    return k[i][1] + (k[i + 1][1] - k[i][1]) * (f - k[i][0]) / (k[i + 1][0] - k[i][0])


a_bl = lambda v: Vector((v[0], -v[2], v[1]))        # three.js -> Blender (escena.b)
a_tj = lambda v: [v[0], v[2], -v[1]]                # Blender -> three.js
NFR_R = RUTA["camara"][-1]["fr"] + 1


def iter_fcurves(ob):  # escena.py's, which lives in its own namespace (Blender 5 layered actions)
    act = ob.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:
        return [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]


def lineal(ob):
    for fc in iter_fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def nuevos(f, *a, **k):
    """Run a builder and return the objects it added."""
    antes = set(bpy.data.objects)
    r = f(*a, **k)
    return r, [o for o in bpy.data.objects if o not in antes]


# ---------------------------------------------------------------- 1. one scene with every scene's dressing
sc.frame_set(0)
cama(); base_escena(); calcas3_mix(); bebida_en_mano(); placa3(); P["camion"]()
P["flecos"](partida=True, largo=0.025); P["banderin_tablero"](CX + 0.14); P["fresa"](0.045, P["VAR"]["fresa"])
P["monos"]((1, -1)); P["bajo_luz"](w=150); P["franja"]("parabrisas")
luz_costado("cabina", 1)  # 4B: the cab lit from inside (point lights the camera does not see)
viejo_diego()
for o in bpy.data.objects:  # road3's chevrons belong to the bend, which the clips do not have
    if o.name.startswith("e3_chev"):
        o.hide_render = True


def tira(tr, nombre, inicio, act, a0, a1, slot, reversa=False):
    st = tr.strips.new(nombre, inicio, act)
    if slot is not None:
        st.action_slot = slot
    st.action_frame_start, st.action_frame_end = a0, a1
    st.use_reverse = reversa
    return st


DIEGO_A = 210  # Diego's clip: seated from about 120 on; 210-330 is the sip (the right hand rises 26 cm and comes back)
FIN_CAST = 2400  # past the loop clip (1127 + 480) and the preview


def reparto_en_bucle():
    """The cast keeps moving and loops in 240 frames (owner: no holds; the band loop's clip must wrap clean).
    The three stand-ins' actions sway with an 80-frame period but end at 192: their frames 0-80 now repeat on the NLA.
    Diego's Mixamo clip (sitting_drinking) slides its Hips 1 m forward by frame 120 (root motion), into Héctor's seat, and holds
    from 457: he is re-anchored so his Hips at DIEGO_A sit where the clip's frame 0 put them (the seat), and the 120 frames from
    DIEGO_A ping-pong (forward, then reversed: period 240, no jump at either turn)."""
    for n in ("manager", "hector", "alejandro"):
        ad = bpy.data.objects[n + "_rig"].animation_data
        act, slot = ad.action, getattr(ad, "action_slot", None)
        ad.action = None
        st = tira(ad.nla_tracks.new(), "ciclo80", 0, act, 0, 80, slot)
        st.repeat = FIN_CAST / 80
    mx = bpy.data.objects["mx"]
    raiz = bpy.data.objects["diego_raiz"]
    sc.frame_set(0)
    asiento = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    sc.frame_set(DIEGO_A)
    sentado = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    # facing: the truck faces +Y (Blender), so a figure facing forward has its right shoulder at +X. The Workbench preview showed
    # him facing the bed (the back of his head from inside the cab): turn him about his hips when that is so
    hombros = (mx.matrix_world @ mx.pose.bones["mixamorig:RightShoulder"].head - mx.matrix_world @ mx.pose.bones["mixamorig:LeftShoulder"].head).x
    giro = Matrix.Rotation(math.pi, 4, "Z") if hombros < 0 else Matrix.Identity(4)
    raiz.matrix_world = Matrix.Translation(asiento) @ giro @ Matrix.Translation(-sentado) @ raiz.matrix_world
    print("RUTA Diego hombros dx", round(hombros, 3), "-> girado 180" if hombros < 0 else "-> ya mira al frente", flush=True)
    ad = mx.animation_data
    tr = ad.nla_tracks[0]
    vieja = tr.strips[0]
    act, slot = vieja.action, getattr(vieja, "action_slot", None)
    tr.strips.remove(vieja)
    for k in range(FIN_CAST // 240 + 1):
        tira(tr, f"ida{k}", k * 240, act, DIEGO_A, DIEGO_A + 120, slot)
        tira(tr, f"vuelta{k}", k * 240 + 120, act, DIEGO_A, DIEGO_A + 120, slot, reversa=True)
    bpy.context.view_layer.update()
    sc.frame_set(0)
    h0 = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    print("RUTA reparto en bucle: Diego anclado", [round(x, 3) for x in asiento - sentado], "cadera f0", [round(x, 3) for x in h0], flush=True)


reparto_en_bucle()

# the pantalla móvil: built at its first point, carried by one keyed empty
p3_0 = a_bl(RUTA["pantalla"][0]["pos"])
_, p3_objs = nuevos(pantalla_c, p3_0.x, p3_0.y)
actor = bpy.data.objects.new("ruta_pantalla", None)
sc.collection.objects.link(actor)
for o in p3_objs:
    if o.parent is None:
        o.parent = actor
for fr in range(NFR_R):
    actor.location = a_bl(hermite(RUTA["pantalla"], lambda p: p["pos"], fr)) - p3_0
    actor.keyframe_insert("location", frame=fr)
lineal(actor)
print("RUTA pantalla", len(p3_objs), "objetos", flush=True)

# section signs: fixed in the world (children of `mundo`), adelante_m ahead at frame 0
mundo_o = bpy.data.objects["mundo"]
for L in RUTA["letreros"]:
    _, objs = nuevos(portico_b, L["titulo"], L["sub"], L["adelante_m"])
    for o in objs:
        if o.parent is None:
            o.parent = mundo_o
            o.matrix_parent_inverse = mundo_o.matrix_world.inverted()
    print("RUTA letrero", L["titulo"], "|", L["sub"], "y", L["adelante_m"], len(objs), "objetos", flush=True)

# the headlight flash (esc6-flash): lens emission x8 and a forward spot per lamp at 6x, keyed by ruta.json flash
emis = bpy.data.materials["faros"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
E0 = emis.default_value
focos = []
for f_ in [o for o in bpy.data.objects if o.name.startswith("faro_") and o.type == "LIGHT"]:
    p = f_.matrix_world.translation
    focos.append((luz("SPOT", p, 0.0, (1.0, 0.95, 0.88), mira=p + Vector((0, 20, -0.6)), parent=False), f_.data.energy * 6))
for fr in sorted({k[0] for k in RUTA["flash"]} | {0}):
    v = flash_v(fr)
    emis.default_value = E0 * (1 + 7 * v)
    emis.keyframe_insert("default_value", frame=fr)
    for o, e in focos:
        o.data.energy = e * v
        o.data.keyframe_insert("energy", frame=fr)
lineal(bpy.data.materials["faros"].node_tree)  # the page reads the flash piecewise linear
for o, _ in focos:
    lineal(o.data)

# ---------------------------------------------------------------- 2. the camera
cd = bpy.data.cameras.new("cam_ruta")
cd.clip_start, cd.clip_end, cd.sensor_fit, cd.sensor_width = 0.03, 3000, "HORIZONTAL", 36.0
co = bpy.data.objects.new("cam_ruta", cd)
sc.collection.objects.link(co)
sc.camera = co
co.rotation_mode = "QUATERNION"
q_prev = None
CLIP = BUC["clip"]  # the loop keyed after the run for its own render (CLIP..CLIP+largo-1), with one pad frame each side so the
# gap after the run is not interpolated (motion blur at the seam frames); CLIP = desde mod 240, so world and vibra phases match
assert CLIP % PERIODO_V == BUC["desde"] % PERIODO_V and CLIP > NFR_R and BUC["largo"] % PERIODO_V == 0
CUADROS_CAM = [(fr, muestra) for fr in range(NFR_R)] + [(fr, lambda f: bucle(f - CLIP)) for fr in range(CLIP - 1, CLIP + BUC["largo"] + 1)]
for fr, fn in CUADROS_CAM:
    cols, mm = fn(fr)
    c4 = [a_bl(c) for c in cols]
    m = Matrix([[c4[j][i] for j in range(4)] for i in range(3)] + [[0, 0, 0, 1]])
    loc, q, _ = m.decompose()
    if q_prev is not None and q.dot(q_prev) < 0:
        q.negate()
    q_prev = q
    co.location, co.rotation_quaternion = loc, q
    co.keyframe_insert("location", frame=fr)
    co.keyframe_insert("rotation_quaternion", frame=fr)
    cd.lens = mm
    cd.keyframe_insert("lens", frame=fr)
lineal(co)
lineal(cd)

# ---------------------------------------------------------------- 3. checks: the camera through metal, and the bake
def material(r):
    """The hit face's material, read on the evaluated mesh (the ray's face index is the evaluated one: modifiers change it)."""
    if r[4].type != "MESH":
        return "?"
    me = r[4].evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    if r[3] >= len(me.polygons) or me.polygons[r[3]].material_index >= len(me.materials) or not me.materials[me.polygons[r[3]].material_index]:
        return "?"
    return me.materials[me.polygons[r[3]].material_index].name


VIDRIOS = ("vidrio", "VIDRIO", "mica")


def choques(pares):
    """A ray from each camera position to the next: any surface it crosses except glass."""
    malos = []
    for fa, fb in pares:
        sc.frame_set(fa); a = co.matrix_world.translation.copy()
        sc.frame_set(fb); b = co.matrix_world.translation.copy()
        if (b - a).length < 1e-6:
            continue
        r = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), a, (b - a).normalized(), distance=(b - a).length)
        if r[0] and r[4].type == "MESH" and not material(r).startswith(VIDRIOS):
            malos.append((fa, r[4].name, material(r)))
    return malos


malos = choques([(fr, fr + 1) for fr in range(NFR_R - 1)])
print("RUTA CHOQUES", len(malos), malos[:12], flush=True)
# the loop on its own, wrap included (CLIP + largo is keyed with the loop's frame 0)
malos_b = choques([(fr, fr + 1) for fr in range(CLIP, CLIP + BUC["largo"])])
print("RUTA CHOQUES BUCLE", len(malos_b), malos_b[:12], flush=True)

_DIRS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]


def holgura(cuadros, alcance=0.5):
    """Clearance: per frame, the nearest non-glass surface along 26 rays from the camera (a ray between camera positions misses a
    head the path only grazes: the v3 move's frame 96). Returns (min m, frame, object) and the frames under 0.10 m."""
    peor, bajos = (alcance, None, None), []
    for fr in cuadros:
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        p = co.matrix_world.translation.copy()
        cerca = (alcance, None)
        for d in _DIRS:
            o, recorrido = p.copy(), 0.0
            for _ in range(4):  # through glass
                r = sc.ray_cast(dg, o, d, distance=alcance - recorrido)
                if not r[0]:
                    break
                recorrido += (r[1] - o).length
                if not material(r).startswith(VIDRIOS):
                    if recorrido < cerca[0]:
                        cerca = (recorrido, r[4].name)
                    break
                o = r[1] + d * 1e-4
        if cerca[0] < peor[0]:
            peor = (round(cerca[0], 3), fr, cerca[1])
        if cerca[0] < 0.10:
            bajos.append((fr, round(cerca[0], 3), cerca[1]))
    return peor, bajos


HOLG = holgura(range(CLIP, CLIP + BUC["largo"]))
print("RUTA HOLGURA BUCLE min", HOLG[0], "cuadros < 0.10 m", len(HOLG[1]), HOLG[1][:20], flush=True)


def asomados(paso=12, franja=0.12):
    """Figures poking out of the cab (owner 06:40: "the top of the hair is coming out of the truck"): every `paso` frames, a ray
    straight up from each figure vertex within `franja` m of that figure's top; a vertex whose ray meets no non-figure surface
    within 1.5 m is outside the roof. Returns {figure: (vertices out, worst frame, max z out)}."""
    figs = [o for o in FIGURAS + DIEGO_OBJS if o.type == "MESH" and not o.hide_render]
    nombres = {o.name for o in figs}
    out = {}
    for fr in range(0, NFR_R, paso):
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        for o in figs:
            e = o.evaluated_get(dg)
            me = e.to_mesh()
            zs = [(e.matrix_world @ v.co) for v in me.vertices]
            e.to_mesh_clear()
            if not zs:
                continue
            top = max(p.z for p in zs)
            n, zmax, cx, cy = 0, -1.0, 0.0, 0.0
            altos = [p for p in zs if p.z > top - franja]
            for p in altos[::max(1, len(altos) // 300)]:  # at most ~300 rays per figure and frame
                q, techo = p.copy(), False
                for _ in range(60):  # layered meshes (cap, hair, head) in the way: keep going
                    r = sc.ray_cast(dg, q + Vector((0, 0, 1e-4)), Vector((0, 0, 1)), distance=1.5)
                    if not r[0]:
                        break
                    if r[4].name in nombres or r[4].original.name in nombres:
                        q = r[1]
                        continue
                    techo = True
                    break
                if not techo:
                    n, zmax, cx, cy = n + 1, max(zmax, p.z), cx + p.x, cy + p.y
            if n and n > out.get(o.name, (0,))[0]:
                out[o.name] = (n, fr, round(zmax, 3), "xy", round(cx / n, 2), round(cy / n, 2))
    return out


def encoger(nombre, dz, k):
    """Lower a seated stand-in by dz and scale it by k about its hip, through its armature only (its children follow)."""
    arm = bpy.data.objects[nombre + "_rig"]
    cad = arm.matrix_world @ arm.pose.bones["cadera"].head
    arm.matrix_world = Matrix.Translation(cad - Vector((0, 0, dz))) @ Matrix.Scale(k, 4) @ Matrix.Translation(-cad) @ arm.matrix_world
    bpy.context.view_layer.update()


# Alexandro's stand-in reached z 2.288 under a 2.187 ceiling (RUTA ASOMADOS, 6758 vertices out at frame 36): his hair showed
# through the roof (owner 06:40). Down 4 cm (into the cushion, hidden) and 0.92 about the hip puts his top near 2.17.
encoger("alejandro", 0.04, 0.92)
ASOM = asomados(paso=int(os.environ.get("RUTA_PASO_ASOM", 24)))
print("RUTA ASOMADOS", len(ASOM), ASOM, flush=True)

cuadros = []
for fr in range(0, NFR_R, 2):
    sc.frame_set(fr)
    mw = co.matrix_world
    m = []
    for j in range(3):
        m += a_tj(mw.col[j][0:3]) + [0]
    m += a_tj(mw.translation) + [1]
    pant = a_tj(actor.matrix_world.translation + p3_0)
    cuadros.append({"fr": fr, "m": [round(x, 6) for x in m], "mm": round(cd.lens, 5), "pantalla": [round(x, 5) for x in pant],
                    "flash": round((emis.default_value / E0 - 1) / 7, 5)})
def mat_tj(mw):
    m = []
    for j in range(3):
        m += a_tj(mw.col[j][0:3]) + [0]
    return [round(x, 6) for x in m + a_tj(mw.translation) + [1]]


cuadros_b = []
for t in range(0, BUC["largo"] + 1, 2):
    sc.frame_set(CLIP + t)
    cuadros_b.append({"t": t, "m": mat_tj(co.matrix_world), "mm": round(cd.lens, 5)})
json.dump({"_doc": "Written by blender/ruta.py from the keyed camera (matrix_world in three.js axes, column-major), the pantalla actor and the flash; read by src/lib/ruta.test.ts. bucle: the band loop as keyed at CLIP + t.", "cuadros": cuadros, "bucle": cuadros_b},
          open(os.path.join(REPO_R, "src", "lib", "ruta.bake.json"), "w", encoding="utf8"), separators=(",", ":"))
print("RUTA bake", len(cuadros), "cuadros", round(time.time() - t_r, 1), "s", flush=True)

# ---------------------------------------------------------------- 4. render
def sin_vidrio():
    """Workbench draws glass opaque, and pase_wb hides only objects whose first material is glass: the windshield and the side
    windows are faces of mixed objects (vidrio_falso). Delete every face whose material starts like the glass the checks skip."""
    import bmesh
    n = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.data.materials:
            continue
        idx = {i for i, m in enumerate(o.data.materials) if m and m.name.startswith(VIDRIOS)}
        if not idx:
            continue
        if o.data.users > 1:
            o.data = o.data.copy()
        bm = bmesh.new()
        bm.from_mesh(o.data)
        caras = [f for f in bm.faces if f.material_index in idx]
        n += len(caras)
        bmesh.ops.delete(bm, geom=caras, context="FACES")
        bm.to_mesh(o.data)
        bm.free()
    print("RUTA sin vidrio (Workbench)", n, "caras", flush=True)


if os.environ.get("RUTA_RENDER", "1") != "0":
    if WB:
        pase_wb()
        sin_vidrio()
    else:
        sc.render.use_persistent_data = True
    sc.frame_start = int(os.environ.get("RUTA_DESDE", 0))
    sc.frame_end = int(os.environ.get("RUTA_HASTA", NFR_R - 1))
    sc.frame_step = int(os.environ.get("RUTA_PASO", 1))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = RW, RH, 100
    sc.render.filepath = os.path.join(OUT, "cuadros", "")
    sc.render.image_settings.file_format = "PNG"
    print("RUTA render", sc.frame_start, sc.frame_end, "paso", sc.frame_step, sc.render.engine, flush=True)
    t_a = time.time()
    if os.environ.get("RUTA_PREVIA"):
        # the page's own stepping (ruta.ts paso(), written per tick by a bun script): [[f, t|null], ...]. Tick k renders at world
        # frame RUTA_PREVIA_DESDE + k (the world and the cast run on the clock), with the camera from the run (t null) or the
        # loop, and the pantalla where the run puts it at f (desde while in the loop)
        ticks = json.load(open(os.environ["RUTA_PREVIA"], encoding="utf8"))
        w0 = int(os.environ.get("RUTA_PREVIA_DESDE", 600))
        co.animation_data_clear(); cd.animation_data_clear(); actor.animation_data_clear()
        for k, (f, t) in enumerate(ticks):
            sc.frame_set(w0 + k)
            cols, mm = muestra(f) if t is None else bucle(t)
            c4 = [a_bl(c) for c in cols]
            co.matrix_world = Matrix([[c4[j][i] for j in range(4)] for i in range(3)] + [[0, 0, 0, 1]])
            cd.lens = mm
            actor.location = a_bl(hermite(RUTA["pantalla"], lambda p: p["pos"], f if t is None else BUC["desde"])) - p3_0
            sc.render.filepath = os.path.join(OUT, "previa", f"{k:04d}.png")
            bpy.ops.render.render(write_still=True)
    elif os.environ.get("RUTA_CUADROS"):  # a list of frames to check before a long run, e.g. "36,647,695"
        for f in [int(x) for x in os.environ["RUTA_CUADROS"].split(",")]:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(OUT, "cuadros", f"{f:04d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
    print("RUTA render total", round(time.time() - t_a, 1), "s", flush=True)

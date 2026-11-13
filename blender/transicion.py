"""Inside -> outside shot: the band in the G63 and one camera move from the cab out over the truck.

Called by escena.py (mode `transicion`) after build() + mundo_render() + motor():
  preparar(s) -> glass, interior lights, the four figures seated and animated, instruments, the camera move.
Figures: blender/assets/reparto/<name>.glb (Tripo exports: one unrigged mesh, 1.0 m tall, facing -Y, feet at z 0).
Each gets a 9-bone armature with distance weights computed here (bone heat is unreliable on these meshes).
Every periodic motion divides 240 frames.
"""
import bpy, math, os
import numpy as np
from mathutils import Vector, Matrix, Quaternion

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPARTO = os.path.join(REPO, "blender", "assets", "reparto")
CX = 1.72          # truck centre line (escena.json mundo.carril_x)
S = 1.25           # figure scale: 1.25 m standing; Héctor seated clears the 2.19 roof by ~5 cm
NFR = 192          # 8 s at 24 fps

# Landmarks per figure, in the GLB's own units (read off horizontal slices, scratchpad perfil.txt):
# yc body centre (y), crotch z, neck z, shoulder root (x, z), wrist (x, z), finger tip (x, z), back = max y of the torso
FIG = {
    "manager":   dict(yc=0.07, crotch=0.20, neck=0.59, root=(0.14, 0.47), wrist=(0.34, 0.38), tip=(0.41, 0.36), back=0.18),
    "hector":    dict(yc=-0.03, crotch=0.15, neck=0.58, root=(0.17, 0.46), wrist=(0.36, 0.37), tip=(0.43, 0.35), back=0.12),
    "alejandro": dict(yc=0.01, crotch=0.16, neck=0.56, root=(0.15, 0.48), wrist=(0.35, 0.39), tip=(0.43, 0.36), back=0.14),
    "diego":     dict(yc=0.02, crotch=0.21, neck=0.57, root=(0.12, 0.46), wrist=(0.32, 0.36), tip=(0.40, 0.33), back=0.11),
}


# ---------------------------------------------------------------- materials, glass, lights

def nodos(nombre):
    m = bpy.data.materials.new(nombre)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    return m, nt, next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")


def vidrio_falso():
    """Thin glass: transparent + a Fresnel glossy. No refraction offset, and it lets light into the cab."""
    m, nt, out = nodos("vidrio_falso")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.82, 0.86, 0.88, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.25
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def vidrios(camion_e, islas):
    """The model's windshield, rear window and some side windows are opaque charcoal sheets; the rest use a refractive
    glass. Find the window sheets by shape (flat, nearly full, in the cab's window band) and give them thin glass."""
    vf = vidrio_falso()
    n_vid = 0
    for o in camion_e.children:
        if o.type != "MESH" or not o.data.polygons:
            continue
        me = o.data
        if me.materials[0].name.startswith("vidrio"):
            me.materials[0] = vf
            n_vid += 1
            continue
        if not me.materials[0].name.startswith("plastico"):
            continue
        slot = None
        for isla in islas(me):
            pol = [me.polygons[i] for i in isla]
            area = sum(p.area for p in pol)
            if area < 0.1:
                continue
            vs = np.array([me.vertices[v].co[:] for p in pol for v in p.vertices])
            lo, hi = vs.min(0), vs.max(0)
            if not (lo[2] > 1.45 and hi[2] < 2.2 and hi[2] - lo[2] > 0.2 and lo[1] > -1.12 and hi[1] < 1.42):
                continue
            nrm = sum((p.normal * p.area for p in pol), Vector())
            if nrm.length < 1e-6:
                continue
            nrm.normalize()
            if sum(p.area for p in pol if abs(p.normal.dot(nrm)) > 0.95) < 0.85 * area:
                continue  # not flat (a pane may have thin edge faces, so measure by area)
            eje = min((Vector(e) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1))), key=lambda e: abs(e.dot(nrm)))
            u = (eje - nrm * eje.dot(nrm)).normalized()  # panes are square to the car: measure along its axes
            v = nrm.cross(u)
            pu, pv = vs @ np.array(u[:]), vs @ np.array(v[:])
            if area / ((pu.max() - pu.min()) * (pv.max() - pv.min())) < 0.6:
                continue  # a frame, not a pane
            if slot is None:
                me.materials.append(vf)
                slot = len(me.materials) - 1
            for p in pol:
                p.material_index = slot
            n_vid += 1
            print("VIDRIO", o.name, "area %.2f" % area, tuple(round(x, 2) for x in lo), tuple(round(x, 2) for x in hi))
    print("VIDRIOS", n_vid)


def area(nombre, loc, mira, w, h, energia, color, padre):
    ld = bpy.data.lights.new(nombre, "AREA")
    ld.shape = "RECTANGLE"
    ld.size, ld.size_y = w, h
    ld.energy = energia
    ld.color = color
    o = bpy.data.objects.new(nombre, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.parent = padre
    return o


def luces_interior(camion_e):
    # cab: a warm dome light under the roof and the cool glow of the instrument panel on the faces
    area("luz_domo", (CX, 0.25, 2.12), (CX, 0.45, 1.3), 0.4, 0.2, 4, (1.0, 0.78, 0.55), camion_e)
    area("luz_tablero", (CX, 1.08, 1.45), (CX, 0.2, 1.8), 1.0, 0.08, 25, (0.55, 0.75, 1.0), camion_e)
    # bed: the roof light bar spills back over the cab into the bed
    area("luz_caja", (CX, -1.0, 2.6), (CX, -2.2, 1.2), 1.4, 0.2, 90, (1.0, 0.82, 0.6), camion_e)


# ---------------------------------------------------------------- figures

HUESOS = ("cadera", "columna", "cabeza", "muslo_n", "pierna_n", "muslo_p", "pierna_p",
          "brazo_n", "antebrazo_n", "mano_n", "brazo_p", "antebrazo_p", "mano_p")
PADRE = {"columna": "cadera", "cabeza": "columna", "muslo_n": "cadera", "pierna_n": "muslo_n", "muslo_p": "cadera",
         "pierna_p": "muslo_p", "brazo_n": "columna", "antebrazo_n": "brazo_n", "mano_n": "antebrazo_n",
         "brazo_p": "columna", "antebrazo_p": "brazo_p", "mano_p": "antebrazo_p"}


def esqueleto(f):
    """Rest joints (head, tail) per bone in the GLB's units. _n = -X side (the figure's right), _p = +X side."""
    yc, zc, zn = f["yc"], f["crotch"], f["neck"]
    j = {"cadera": ((0, yc, zc + 0.02), (0, yc, zc + 0.12)), "columna": ((0, yc, zc + 0.12), (0, yc, zn)),
         "cabeza": ((0, yc, zn), (0, yc, 1.0))}
    for s, k in ((-1, "n"), (1, "p")):
        x = 0.065 * s
        j[f"muslo_{k}"] = ((x, yc, zc + 0.02), (x, yc, zc * 0.5))
        j[f"pierna_{k}"] = ((x, yc, zc * 0.5), (x, yc - 0.02, 0.03))
        r, w, t = f["root"], f["wrist"], f["tip"]
        codo = ((r[0] + w[0]) / 2, (r[1] + w[1]) / 2)
        j[f"brazo_{k}"] = ((r[0] * s, yc, r[1]), (codo[0] * s, yc, codo[1]))
        j[f"antebrazo_{k}"] = ((codo[0] * s, yc, codo[1]), (w[0] * s, yc, w[1]))
        j[f"mano_{k}"] = ((w[0] * s, yc, w[1]), (t[0] * s, yc, t[1]))
    return {k: (Vector(a), Vector(b)) for k, (a, b) in j.items()}


def suave(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def pesos(me, j, f):
    """Inverse-distance weights to each bone segment, with region masks so a leg never pulls the belly, a hand never
    pulls the hip, and the head keeps the hair and cap."""
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    x, z = co[:, 0], co[:, 2]
    zc, zn, rx = f["crotch"], f["neck"], f["root"][0]
    pierna = suave(z, zc + 0.06, zc - 0.02)
    brazo_n = suave(-x, rx - 0.03, rx + 0.02) * suave(z, zc + 0.01, zc + 0.07)
    brazo_p = suave(x, rx - 0.03, rx + 0.02) * suave(z, zc + 0.01, zc + 0.07)
    cabeza = suave(z, zn - 0.04, zn + 0.02)
    brazo_n, brazo_p = brazo_n * (1 - cabeza), brazo_p * (1 - cabeza)  # ears, hood and cap stay with the head
    mascara = {"cadera": (1 - pierna) * (1 - cabeza), "columna": (1 - pierna) * (1 - cabeza), "cabeza": cabeza,
               "muslo_n": pierna * (x < 0.01), "pierna_n": pierna * (x < 0.01),
               "muslo_p": pierna * (x > -0.01), "pierna_p": pierna * (x > -0.01)}
    for k, m in (("n", brazo_n), ("p", brazo_p)):
        for b in ("brazo", "antebrazo", "mano"):
            mascara[f"{b}_{k}"] = m
    W = np.zeros((n, len(HUESOS)), dtype=np.float32)
    for i, h in enumerate(HUESOS):
        a, b = np.array(j[h][0][:]), np.array(j[h][1][:])
        ab = b - a
        t = np.clip(((co - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(co - (a + t[:, None] * ab), axis=1)
        W[:, i] = mascara[h] / (d + 0.01) ** 4
    W /= W.sum(1, keepdims=True) + 1e-12
    W = np.round(W * 20) / 20  # quantised so each group is filled with a few batch calls
    return W


def figura(nombre, tiny=False):
    f = FIG[nombre]
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(REPARTO, nombre + ".glb"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    malla = next(o for o in nuevos if o.type == "MESH")
    for o in nuevos:
        if o is not malla:
            bpy.data.objects.remove(o)
    mw = malla.matrix_world.copy()
    malla.parent = None
    malla.data.transform(mw)
    malla.matrix_world = Matrix.Identity(4)
    malla.name = nombre
    j = esqueleto(f)
    ad = bpy.data.armatures.new(nombre + "_rig")
    arm = bpy.data.objects.new(nombre + "_rig", ad)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for h in HUESOS:
        eb = ad.edit_bones.new(h)
        eb.head, eb.tail = j[h]
        eb.roll = 0
    for h, p in PADRE.items():
        ad.edit_bones[h].parent = ad.edit_bones[p]
    bpy.ops.object.mode_set(mode="OBJECT")
    W = pesos(malla.data, j, f)
    for i, h in enumerate(HUESOS):
        vg = malla.vertex_groups.new(name=h)
        for q in range(1, 21):
            idx = np.nonzero(W[:, i] == q / 20)[0].tolist()
            if idx:
                vg.add(idx, q / 20, "REPLACE")
    malla.parent = arm
    md = malla.modifiers.new("rig", "ARMATURE")
    md.object = arm
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm, malla, j


def ik(S, T, l1, l2, polo):
    """Two-bone IK: elbow and the reachable end point, in any one space."""
    d = T - S
    dist = min(max(d.length, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    u = d.normalized()
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    p = (polo - u * polo.dot(u)).normalized()
    return S + u * a + p * h, S + u * dist


class Pose:
    """Builds a pose from desired bone directions in armature space (the GLB's units, facing -Y) and keys it.
    For a bone with rest rotation R, parent rest Rp and world deltas D (bone) and Dp (parent):
    local q = R^-1 Dp^-1 D R. Heads follow their parents because every child head sits on its parent's tail."""

    def __init__(self, arm, j):
        self.arm, self.j = arm, j
        self.rest = {b.name: b.matrix_local.to_quaternion() for b in arm.data.bones}
        self.dir0 = {h: (b - a).normalized() for h, (a, b) in j.items()}
        self.largo = {h: (b - a).length for h, (a, b) in j.items()}

    def poner(self, dirs, frame, cadera_loc=Vector()):
        D = {}
        for h in HUESOS:  # parents come first in HUESOS
            D[h] = self.dir0[h].rotation_difference(dirs[h]) if h in dirs else (D[PADRE[h]] if h in PADRE else Quaternion())
        for h in HUESOS:
            R = self.rest[h]
            Dp = D[PADRE[h]] if h in PADRE else Quaternion()
            pb = self.arm.pose.bones[h]
            pb.rotation_quaternion = R.inverted() @ Dp.inverted() @ D[h] @ R
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb = self.arm.pose.bones["cadera"]
        pb.location = self.rest["cadera"].inverted() @ cadera_loc
        pb.keyframe_insert("location", frame=frame)
        return D

    def punta(self, D, h):
        """Posed tail of bone h in armature space (walks the chain from the hip)."""
        cadena = [h]
        while cadena[-1] in PADRE:
            cadena.append(PADRE[cadena[-1]])
        p = self.j[cadena[-1]][0].copy()
        for b in reversed(cadena):
            p = p + (D[b] @ self.dir0[b]) * self.largo[b]
        return p


def brazo(P, lado, objetivo, polo):
    """Directions for the three arm bones so the hand ends at `objetivo` (armature space)."""
    k = "n" if lado < 0 else "p"
    S = P.j[f"brazo_{k}"][0]
    l1, l2 = P.largo[f"brazo_{k}"], P.largo[f"antebrazo_{k}"]
    E, T = ik(S, objetivo, l1, l2, polo)
    return {f"brazo_{k}": (E - S).normalized(), f"antebrazo_{k}": (T - E).normalized(),
            f"mano_{k}": (T - E).normalized()}


def onda(fr, periodo, fase=0.0):
    return math.sin(2 * math.pi * (fr / periodo + fase))


def sentar(nombre, cadera_mundo, mirando_atras, manos, extra=None, frames=range(0, NFR + 1, 2)):
    """Seat a figure with its hip joint at `cadera_mundo`. manos(fr, P) -> dict of arm directions.
    mirando_atras: True for the bed (faces -Y), False for the cab (turned to face +Y)."""
    arm, malla, j = figura(nombre)
    f = FIG[nombre]
    rot = Matrix.Identity(4) if mirando_atras else Matrix.Rotation(math.pi, 4, "Z")
    cadera = Vector((0, f["yc"], f["crotch"] + 0.02))
    arm.matrix_world = Matrix.Translation(cadera_mundo) @ rot @ Matrix.Scale(S, 4) @ Matrix.Translation(-cadera)
    P = Pose(arm, j)
    a_local = arm.matrix_world.inverted()
    for fr in frames:
        nod = 0.035 * onda(fr, 20, extra.get("fase", 0) if extra else 0)
        dirs = {"columna": Vector((0, 0.10, 1)).normalized(),
                "cabeza": Vector((0, -0.03 + nod, 1)).normalized() if not extra or "cabeza" not in extra else extra["cabeza"](fr),
                "muslo_n": Vector((-0.12, -1, -0.04)).normalized(), "muslo_p": Vector((0.12, -1, -0.04)).normalized(),
                "pierna_n": Vector((-0.05, -0.25, -1)).normalized(), "pierna_p": Vector((0.05, -0.25, -1)).normalized()}
        dirs.update(manos(fr, P, a_local))
        P.poner(dirs, fr, Vector((0, 0, 0.004 * abs(onda(fr, 20)))))
    for fc in iter_fc(arm):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    return arm, malla, P


def iter_fc(ob):
    act = ob.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:
        return [fc for l in act.layers for s in l.strips for bag in s.channelbags for fc in bag.fcurves]


# ---------------------------------------------------------------- props

def pbsdf(nombre, color, rough, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(nombre)
    if not m.node_tree:
        m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    return m


def guitarra(nombre, tapa, padre_mw):
    """A toy guitar 0.62 m long, built along +X (neck) with the face towards -Y; returned as one empty."""
    raiz = bpy.data.objects.new(nombre, None)
    bpy.context.scene.collection.objects.link(raiz)
    m_tapa = pbsdf(nombre + "_tapa", tapa, 0.35, coat=0.6)
    m_osc = pbsdf(nombre + "_diapason", (0.012, 0.008, 0.006), 0.5)
    partes = []
    for cx, r in ((0.0, 0.13), (0.15, 0.10)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(cx, 0, 0), segments=32, ring_count=12)
        o = bpy.context.object
        o.scale = (r, 0.045, r)
        o.data.materials.append(m_tapa)
        partes.append(o)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.01, location=(0.08, -0.046, 0), rotation=(math.pi / 2, 0, 0))
    partes.append(bpy.context.object)
    bpy.context.object.data.materials.append(m_osc)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.38, -0.02, 0))
    o = bpy.context.object
    o.scale = (0.34, 0.025, 0.045)
    o.data.materials.append(m_osc)
    partes.append(o)
    for o in partes:
        o.parent = raiz
    raiz.matrix_world = padre_mw
    return raiz


def estuche(nombre, loc, size, padre, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = nombre
    o.scale = size
    bev = o.modifiers.new("bisel", "BEVEL")
    bev.width, bev.segments = 0.02, 2
    o.data.materials.append(m)
    o.parent = padre
    return o


# ---------------------------------------------------------------- the cast in place

CABINA_Z = 1.08  # seat cushion (ray cast)
CAJA_Z = 0.93    # bed floor
CASE_H = 0.40


def sin_cabeceras(camion_e):
    """Delete the two front headrests. The toy heads are ~0.55 m deep and sit ~0.2 m inside them (BVH overlap on every
    frame, any lean), so their wings poked through the back of both caps. Faces wholly inside the boxes go; seat backs stay."""
    import bmesh
    cajas = [(CX + x0, CX + x1) for x0, x1 in ((-0.57, -0.20), (0.22, 0.59))]  # seat x 1.19-1.48 and 1.98-2.27
    n = 0
    for o in camion_e.children:
        if o.type != "MESH" or not o.data.polygons:
            continue
        bm = bmesh.new()
        bm.from_mesh(o.data)
        fuera = [f for f in bm.faces if any(all(x0 <= v.co.x <= x1 and 0.05 <= v.co.y <= 0.50 and 1.74 <= v.co.z <= 2.05
                                                for v in f.verts) for x0, x1 in cajas)]
        if fuera:
            bmesh.ops.delete(bm, geom=fuera, context="FACES")
            bm.to_mesh(o.data)
            n += len(fuera)
        bm.free()
    print("CABECERAS", n)


def reparto(camion_e):
    figs = []
    # manager drives: hands at ten and two on the wheel (centre about x -0.39, y 0.95, z 1.6, d 0.38)
    def volante(fr, P, a_local):
        giro = 0.03 * onda(fr, 120)
        out = {}
        for lado in (-1, 1):  # lado in armature x: -1 = his right = world +X after the turn
            ang = math.radians(60) * lado + giro
            mundo = Vector((CX - 0.39 - 0.17 * math.sin(ang), 0.9, 1.6 + 0.17 * math.cos(ang) - 0.05))
            out.update(brazo(P, lado, a_local @ mundo, Vector((lado * 1.0, 0.3, -1.0))))
        return out
    figs.append(sentar("manager", Vector((CX - 0.39, 0.47, CABINA_Z + 0.07)), False, volante, {"fase": 0.0}))
    # Héctor beside him: hands resting on his thighs, head turned a little towards the driver
    def regazo(fr, P, a_local):
        out = {}
        for lado in (-1, 1):
            k = "n" if lado < 0 else "p"
            rodilla = P.j[f"muslo_{k}"][0] + Vector((0.02 * lado, -0.16, 0.06))
            out.update(brazo(P, lado, rodilla, Vector((lado * 1.0, 0.5, -0.6))))
        return out
    h_cabeza = lambda fr: Vector((0.10, -0.03 + 0.03 * onda(fr, 20, 0.25), 1)).normalized()
    figs.append(sentar("hector", Vector((CX + 0.39, 0.50, CABINA_Z + 0.07)), False, regazo, {"cabeza": h_cabeza}))
    # bed: Alexandro and Diego on cases with their backs to the cab, facing the road behind, guitars on their laps
    m_case = pbsdf("estuche", (0.02, 0.018, 0.016), 0.45, coat=0.3)
    for nombre, x, tapa, fase in (("alejandro", CX - 0.36, (0.30, 0.12, 0.05), 0.5), ("diego", CX + 0.36, (0.62, 0.40, 0.20), 0.0)):
        estuche(f"estuche_{nombre}", (x, -1.55, CAJA_Z + CASE_H / 2), (0.62, 0.42, CASE_H), camion_e, m_case)
        def toca(fr, P, a_local, fase=fase):
            cad = P.j["cadera"][0]
            rasgueo = 0.025 * onda(fr, 10, fase)
            boca = cad + Vector((-0.06, -0.20, 0.10 + rasgueo))          # strumming hand at the sound hole
            mastil = cad + Vector((0.26, -0.20, 0.20 + 0.01 * onda(fr, 40)))  # fretting hand up the neck
            return {**brazo(P, -1, boca, Vector((-1, 0.6, -0.4))), **brazo(P, 1, mastil, Vector((1, 0.4, -0.8)))}
        arm, malla, P = sentar(nombre, Vector((x, -1.62, CAJA_Z + CASE_H + 0.07)), True, toca, {"fase": fase})
        cad = P.j["cadera"][0]
        mw = arm.matrix_world @ Matrix.Translation(cad + Vector((-0.04, -0.22, 0.13))) @ Matrix.Rotation(math.radians(-28), 4, "Y") @ Matrix.Scale(1 / S, 4)
        g = guitarra(f"guitarra_{nombre}", tapa, mw)
        g.parent = arm
        g.matrix_parent_inverse = arm.matrix_world.inverted()
        figs.append((arm, malla, P))
    estuche("estuche_bajo", (CX, -2.45, CAJA_Z + 0.14), (1.1, 0.4, 0.28), camion_e, m_case)
    for arm, malla, P in figs:
        arm.parent = camion_e
        arm.matrix_parent_inverse = camion_e.matrix_world.inverted()
    return figs


# ---------------------------------------------------------------- camera

# Control points (position, look-at, lens mm) and the frame each one lands on. Truck faces +Y, world moves -Y.
# Inside: between the rear headrests, the two in front and the road through the windshield. Out through the
# windshield over the hood, up, and the truck drives on beneath the camera, which settles high behind the bed.
CAMINO = [
    (0,   (CX, -0.75, 1.88), (CX, 6.0, 1.45), 20),
    (40,  (CX, 0.45, 1.80),  (CX, 8.0, 1.55), 18),
    (72,  (CX, 1.55, 1.95),  (CX, 9.0, 1.30), 20),
    (100, (CX, 2.3, 3.0),    (CX, 7.0, 1.0), 22),
    (140, (CX - 0.3, -1.2, 5.2), (CX, -0.3, 1.2), 24),
    (191, (CX - 0.8, -6.8, 3.6), (CX, -0.6, 1.35), 28),
]


def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def muestra(fr, i):
    """Value i (1 = position, 2 = look-at, 3 = lens) at frame fr: Catmull-Rom through the control points, with the
    frame -> segment map eased at both ends of the move (smoothstep over the whole shot)."""
    fs = [c[0] for c in CAMINO]
    u = fr / fs[-1]
    u = u * u * (3 - 2 * u)
    g = u * fs[-1]
    k = max(i0 for i0 in range(len(fs) - 1) if fs[i0] <= g) if g < fs[-1] else len(fs) - 2
    t = (g - fs[k]) / (fs[k + 1] - fs[k])
    val = lambda n: (Vector(CAMINO[min(max(n, 0), len(CAMINO) - 1)][i]) if i < 3 else CAMINO[min(max(n, 0), len(CAMINO) - 1)][i])
    return catmull(val(k - 1), val(k), val(k + 1), val(k + 2), t)


def camara(w, h, camion_e):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam_transicion")
    cd.clip_start, cd.clip_end = 0.03, 3000
    cd.sensor_fit = "HORIZONTAL"
    co = bpy.data.objects.new("cam_transicion", cd)
    sc.collection.objects.link(co)
    sc.camera = co
    vertical = h > w
    for fr in range(NFR):
        p, m, lens = muestra(fr, 1), muestra(fr, 2), muestra(fr, 3)
        co.location = p
        co.rotation_euler = (m - p).to_track_quat("-Z", "Y").to_euler()
        # 9:16 keeps 75 % of the 16:9 horizontal angle: the two front seats still fit inside the cab
        cd.lens = 18 / math.tan(0.75 * math.atan(18 / lens)) if vertical else lens
        co.keyframe_insert("location", frame=fr)
        co.keyframe_insert("rotation_euler", frame=fr)
        cd.keyframe_insert("lens", frame=fr)
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.frame_start, sc.frame_end = 0, NFR - 1
    return co


def choques(co):
    """Ray from the camera at each frame to the next: any hit that is not glass means the move cuts through metal."""
    sc = bpy.context.scene
    malos = []
    for fr in range(NFR - 1):
        sc.frame_set(fr)
        a = co.matrix_world.translation.copy()
        sc.frame_set(fr + 1)
        b = co.matrix_world.translation.copy()
        dg = bpy.context.evaluated_depsgraph_get()
        r = sc.ray_cast(dg, a, (b - a).normalized(), distance=(b - a).length)
        if r[0]:
            mt = r[4].data.materials[r[4].data.polygons[r[3]].material_index].name if r[4].type == "MESH" else "?"
            if not mt.startswith("vidrio"):
                malos.append((fr, r[4].name, mt))
    print("CHOQUES", len(malos), malos[:10])
    return malos


def preparar(s, w, h, islas):
    vidrios(s["camion"], islas)
    luces_interior(s["camion"])
    sin_cabeceras(s["camion"])
    reparto(s["camion"])
    co = camara(w, h, s["camion"])
    choques(co)
    return co

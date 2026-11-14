"""The cast as sitcom vinyl toys, built from primitives, with a 10 s loop baked as keyframes.

    blender.exe -b --factory-startup --python blender/reparto.py -- retrato <name> <out.png> [samples]

`construir()` is what blender/escena.py imports: it returns {name: figure} with every figure seated at its root empty
(root = seat point, figure faces -Y, its right is -X, Z up, metres). Periods divide NFR, so frame NFR == frame 0.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Quaternion, Euler, Matrix

NFR = 240
BEAT = 20  # frames per beat of the song the cast nods to
ZV = Vector((0, 0, 1))
TAU = 2 * math.pi

# ---------------------------------------------------------------- materials and primitives


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, hexa, rough=0.4, metal=0.0, emit=0.0, coat=0.2, trans=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    if not (m.node_tree and m.node_tree.nodes):
        m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = lin(hexa)
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.15
    p.inputs["Transmission Weight"].default_value = trans
    if emit:
        p.inputs["Emission Color"].default_value = (*rgb, 1)
        p.inputs["Emission Strength"].default_value = emit
    return m


def objeto(name, bm, m, parent, loc=(0, 0, 0), scale=(1, 1, 1), rot=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    ob.rotation_mode = "QUATERNION"
    ob.location, ob.scale = loc, scale
    if rot is not None:
        ob.rotation_quaternion = rot
    ob.parent = parent
    bpy.context.scene.collection.objects.link(ob)
    return ob


def vacio(name, parent, loc=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.05
    ob.location = loc
    ob.parent = parent
    bpy.context.scene.collection.objects.link(ob)
    return ob


def esfera(name, m, parent, loc, scale, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
    if isinstance(scale, (int, float)):
        scale = (scale,) * 3
    return objeto(name, bm, m, parent, loc, scale, rot)


def casco(name, m, parent, loc, scale, pred, grosor=0.05):
    """Shell: the part of a unit sphere where pred(x, y, z) holds, thickened outwards."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not pred(*v.co)], context="VERTS")
    ob = objeto(name, bm, m, parent, loc, scale)
    s = ob.modifiers.new("grosor", "SOLIDIFY")
    s.thickness, s.offset = grosor, 1.0
    return ob


def hacia(eje):
    return ZV.rotation_difference(Vector(eje).normalized())


def cilindro(name, m, parent, base, eje, largo, r, segs=20):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=largo)
    eje = Vector(eje).normalized()
    return objeto(name, bm, m, parent, Vector(base) + eje * (largo / 2), rot=hacia(eje))


def caja(name, m, parent, loc, half, rot=None, bisel=0.3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    ob = objeto(name, bm, m, parent, loc, half, rot)
    for p in ob.data.polygons:
        p.use_smooth = False
    if bisel:
        bv = ob.modifiers.new("bisel", "BEVEL")
        bv.width, bv.segments = bisel * min(half), 3
    return ob


def caja_r(name, m, parent, loc, half, radio, taper=1.0, segs=6):
    """Rounded box with its real size in the mesh (so the rounding is even), narrower at the top by `taper`."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2)
    for v in bm.verts:
        k = taper if v.co.z > 0 else 1.0
        v.co = Vector((v.co.x * half[0] * k, v.co.y * half[1] * k, v.co.z * half[2]))
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=radio, segments=segs, profile=0.5, affect="EDGES")
    return objeto(name, bm, m, parent, loc)


def tubo(name, m, parent):
    """Unit cylinder along Z (radius 1, length 1), to be placed with poner_tramo."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=1, radius2=1, depth=1)
    return objeto(name, bm, m, parent)


def toro(name, m, parent, loc, R, r, eje=(0, 0, 1), nu=48, nv=10):
    bm = bmesh.new()
    vs = [[bm.verts.new(((R + r * math.cos(TAU * j / nv)) * math.cos(TAU * i / nu),
                         (R + r * math.cos(TAU * j / nv)) * math.sin(TAU * i / nu),
                         r * math.sin(TAU * j / nv))) for j in range(nv)] for i in range(nu)]
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((vs[i][j], vs[(i + 1) % nu][j], vs[(i + 1) % nu][(j + 1) % nv], vs[i][(j + 1) % nv]))
    return objeto(name, bm, m, parent, loc, rot=hacia(eje))


def estrella(name, m, parent, loc, r, eje=(0, -1, 0)):
    bm = bmesh.new()
    vs = [bm.verts.new((math.sin(TAU * i / 10) * (r if i % 2 == 0 else r * 0.45),
                        math.cos(TAU * i / 10) * (r if i % 2 == 0 else r * 0.45), 0)) for i in range(10)]
    bm.faces.new(vs)
    ob = objeto(name, bm, m, parent, loc, rot=hacia(eje) @ Quaternion((0, 0, 1), 0))
    for p in ob.data.polygons:
        p.use_smooth = False
    s = ob.modifiers.new("grosor", "SOLIDIFY")
    s.thickness, s.offset = r * 0.3, 0.0
    return ob


def poner_tramo(ob, p1, p2, r):
    """Cylinder limb (a `tubo`) from p1 to p2. Its roll is carried over from the last call, so it never flips between frames."""
    d = (p2 - p1).normalized()
    if "q" in ob:
        q0 = Quaternion(ob["q"])
        q = (q0 @ ZV).rotation_difference(d) @ q0
    else:
        q = hacia(d)
    ob["q"] = q[:]
    ob.location = (p1 + p2) / 2
    ob.rotation_quaternion = q
    ob.scale = (r, r, (p2 - p1).length)


def orientar(d, lado):
    """Hand frame: local Z along d, local X fixed by the side vector (the same every loop, unlike a carried roll)."""
    z = Vector(d).normalized()
    x = Vector(lado).cross(z).normalized()
    return Matrix((x, z.cross(x), z)).transposed().to_quaternion()


def codo(S, T, l1, l2, polo):
    """Two-bone IK: elbow position and the reachable target."""
    d = T - S
    L = min(d.length, (l1 + l2) * 0.995)
    dn = d.normalized()
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    perp = Vector(polo) - Vector(polo).project(dn)
    return S + dn * a + perp.normalized() * h, S + dn * L


# ---------------------------------------------------------------- the shared body

L1 = L2 = 0.15  # upper arm, forearm: stubby, like the reference toys
NECK = Vector((0, 0, 0.315))
HC = Vector((0, -0.01, 0.2))  # head centre, relative to the neck pivot


class Figura:
    def __init__(self, nombre, piel, cabeza=(0.25, 0.225, 0.215), torso=(0.19, 0.14, 0.165)):
        self.n = nombre
        self.A, self.B, self.C = cabeza
        self.torso = torso
        self.root = vacio(nombre, None)
        self.cab = vacio(nombre + "_cab", self.root, NECK)
        self.cab.rotation_mode = "XYZ"
        self.piel = mat(nombre + "_piel", piel, 0.42)
        self.negro = mat("negro", "#0b0b0d", 0.3)
        self.blanco = mat("blanco_ojo", "#f4f1ea", 0.25)
        self.seg, self.art = {}, {}  # limb cylinders and joint balls, placed every frame
        self.parp = []               # eyelids
        self.manos = {}
        self.S = {s: Vector((s * (torso[0] + 0.015), 0, 0.265)) for s in (-1, 1)}
        c = esfera(nombre + "_cabeza", self.piel, self.cab, HC, cabeza)
        for v in c.data.vertices:  # fuller cheeks and a flatter chin than a ball
            if v.co.z < 0:
                v.co.x *= 1 + 0.1 * math.sin(math.pi * -v.co.z)
                v.co.z *= 0.93

    def cara(self, x, dz, fuera=0.0):
        """Point on the front of the head (in the head pivot's space), pushed out by `fuera`."""
        y = -self.B * math.sqrt(max(0.0, 1 - (x / self.A) ** 2 - (dz / self.C) ** 2))
        return HC + Vector((x, y - fuera, dz))

    def rostro(self, lid=0.0, mirada=(0.0, 0.0), ceja="#1a1410", ceja_inc=0.1, ceja_alto=0.0):
        """Big eyes that touch, a skin lid with a dark edge over each, brows resting on the lids."""
        n = self.n
        self.lid0 = lid
        cj = mat(n + "_ceja", ceja, 0.5)
        for s in (-1, 1):
            c = self.cara(s * 0.076, 0.03, -0.036)
            esfera(f"{n}_ojo{s}", self.blanco, self.cab, c, (0.076, 0.056, 0.078))
            esfera(f"{n}_pupila{s}", self.negro, self.cab, c + Vector((mirada[0] * 0.04, -0.053, -0.02 + mirada[1] * 0.03)), (0.02, 0.008, 0.021))
            p = casco(f"{n}_parpado{s}", self.piel, self.cab, c, (0.079, 0.06, 0.081), lambda x, y, z: z > 0.04, 0.05)
            p.rotation_mode = "XYZ"
            p.rotation_euler.x = lid
            casco(f"{n}_linea{s}", self.negro, p, (0, 0, 0), (1.012, 1.02, 1.012), lambda x, y, z: -0.03 < z < 0.1 and y < 0.2, 0.03)
            self.parp.append(p)
            esfera(f"{n}_ceja{s}", cj, self.cab, self.cara(s * 0.08, 0.125 + ceja_alto, 0.008), (0.07, 0.018, 0.021),
                   Vector((1, 0, 0)).rotation_difference(Vector((1, 0, -s * ceja_inc)).normalized()))
            esfera(f"{n}_oreja{s}", self.piel, self.cab, HC + Vector((s * self.A * 0.99, 0.02, -0.04)), (0.03, 0.034, 0.048))
        esfera(n + "_nariz", self.piel, self.cab, self.cara(0, -0.045, 0.012), (0.035, 0.042, 0.034))

    def miembro(self, nombre, m, p1, p2, r):
        poner_tramo(tubo(f"{self.n}_{nombre}", m, self.root), p1, p2, r)
        esfera(f"{self.n}_{nombre}_a", m, self.root, p1, r * 0.97)  # a hair smaller than the tube: equal radii z-fight
        esfera(f"{self.n}_{nombre}_b", m, self.root, p2, r * 0.97)

    def cuerpo(self, m_torso, m_manga, m_antebrazo, m_pierna, m_zapato, r_brazo=0.07, manga_corta=False, de_pie=False, torso=True):
        n, (tw, td, th) = self.n, self.torso
        if torso:
            self.tor = caja_r(n + "_torso", m_torso, self.root, (0, 0, th), (tw, td, th), 0.08, taper=0.9)
        self.r_brazo, self.manga_corta = r_brazo, manga_corta
        for s in (-1, 1):
            esfera(f"{n}_hombro{s}", m_manga, self.root, self.S[s], r_brazo * (1.1 if manga_corta else 0.97))
            self.seg[f"brazo{s}"] = tubo(f"{n}_brazo{s}", self.piel if manga_corta else m_manga, self.root)
            self.seg[f"ante{s}"] = tubo(f"{n}_ante{s}", m_antebrazo, self.root)
            self.seg[f"puno{s}"] = tubo(f"{n}_puno{s}", m_manga, self.root)  # cuff, or the rim of a short sleeve
            self.art[f"codo{s}"] = esfera(f"{n}_codo{s}", self.piel if manga_corta else m_manga, self.root, (0, 0, 0), r_brazo * 0.97)
            mano = esfera(f"{n}_mano{s}", self.piel, self.root, (0, 0, 0), (0.062, 0.05, 0.064))
            esfera(f"{n}_pulgar{s}", self.piel, mano, (-s * 0.8, -0.2, 0.05), (0.4, 0.45, 0.5))
            for i in range(4):
                esfera(f"{n}_dedo{s}{i}", self.piel, mano, ((i - 1.5) * 0.4, -0.05, 0.62), (0.26, 0.7, 0.45))
            self.manos[s] = mano
            cad = Vector((s * 0.09, 0, 0.03))
            if de_pie:
                tob = Vector((s * 0.095, 0, -0.1))
                self.miembro(f"pierna{s}", m_pierna, cad, tob, 0.088)
                esfera(f"{n}_zapato{s}", m_zapato, self.root, tob + Vector((0, -0.03, -0.055)), (0.09, 0.115, 0.04))
            else:
                rod, tob = Vector((s * 0.1, -0.17, 0.06)), Vector((s * 0.1, -0.19, -0.1))
                self.miembro(f"muslo{s}", m_pierna, cad + Vector((0, 0, 0.03)), rod, 0.08)
                self.miembro(f"pierna{s}", m_pierna, rod, tob, 0.074)
                esfera(f"{n}_zapato{s}", m_zapato, self.root, tob + Vector((0, -0.04, -0.035)), (0.078, 0.115, 0.05))

    def cadena(self, estrella_=True, y=None, z0=0.3, z1=0.17):
        """A thin chain as a V from the collar to the chest, like the reference figures."""
        plata = mat("plata", "#c9c9cc", 0.25, metal=1.0, coat=0.0)
        y = -self.torso[1] - 0.004 if y is None else y
        bajo = Vector((0, y, z1))
        for s in (-1, 1):
            alto = Vector((s * 0.085, y + 0.03, z0))
            cilindro(f"{self.n}_cadena{s}", plata, self.root, alto, bajo - alto, (bajo - alto).length, 0.004, 8)
        if estrella_:
            estrella(self.n + "_estrella", plata, self.root, bajo + Vector((0, -0.006, -0.02)), 0.028)

    # ---- animation
    def clave(self, ob, path, f):
        ob.keyframe_insert(path, frame=f)

    def posar(self, f, cabeza=(0, 0, 0), manos=None, lid=None):
        """manos: {side: (target, pole[, hand quaternion])} in root space."""
        self.cab.rotation_euler = cabeza
        self.clave(self.cab, "rotation_euler", f)
        for p in self.parp:
            p.rotation_euler.x = self.lid0 if lid is None else lid
            self.clave(p, "rotation_euler", f)
        r = self.r_brazo
        for s, v in (manos or {}).items():
            E, T = codo(self.S[s], Vector(v[0]), L1, L2, v[1])
            d = (T - E).normalized()
            poner_tramo(self.seg[f"brazo{s}"], self.S[s], E, r * (0.9 if self.manga_corta else 1.0))
            poner_tramo(self.seg[f"ante{s}"], E, T, r * (0.86 if self.manga_corta else 1.0))
            if self.manga_corta:
                poner_tramo(self.seg[f"puno{s}"], self.S[s], self.S[s].lerp(E, 0.6), r * 1.1)
            else:
                poner_tramo(self.seg[f"puno{s}"], T - d * 0.03, T + d * 0.02, r * 1.14)
            self.art[f"codo{s}"].location = E
            self.clave(self.art[f"codo{s}"], "location", f)
            mano = self.manos[s]
            mano.location = T + d * 0.05
            q = v[2] if len(v) > 2 else orientar(d, (s, 0, 0))
            if "q" in mano and Quaternion(mano["q"]).dot(q) < 0:
                q = -q
            mano["q"] = q[:]
            mano.rotation_quaternion = q
            for ob in (mano, self.seg[f"brazo{s}"], self.seg[f"ante{s}"], self.seg[f"puno{s}"]):
                for path in ("location", "rotation_quaternion", "scale"):
                    self.clave(ob, path, f)


def parpadeo(f, inicios, base, cerrado=0.75):
    """Eyelid angle at frame f: blinks start at `inicios`, 2 frames down, 1 shut, 3 up."""
    for i in inicios:
        d = (f - i) % NFR
        if d < 6:
            k = (0.5, 1, 1, 0.66, 0.33, 0.1)[d]
            return base + (cerrado - base) * k
    return base


def onda(f, periodo, fase=0.0):
    return math.sin(TAU * (f / periodo + fase))


def humo(fig, nombre, n=5):
    m = mat("humo", "#b9b9b8", 0.9, coat=0.0)
    return [esfera(f"{fig.n}_{nombre}{i}", m, fig.root, (0, 0, 0), 0.001) for i in range(n)]


def posar_humo(fig, puffs, f, origen, deriva, periodo=60, r=0.05):
    """Solid toy puffs: born at `origen` at size 0, drift along `deriva`, die at size 0 (so the wrap is invisible)."""
    for i, p in enumerate(puffs):
        u = (f / periodo + i / len(puffs)) % 1.0
        w = Vector((math.sin(TAU * (u * 1.5 + i * 0.37)), 0, math.cos(TAU * (u + i * 0.21)))) * 0.025 * u
        p.location = Vector(origen) + Vector(deriva) * u + w
        k = r * math.sin(math.pi * u) ** 0.8 * (0.45 + u)
        p.scale = (k * 1.25, k, k)
        for path in ("location", "scale"):
            fig.clave(p, path, f)


# ---------------------------------------------------------------- the four

def alexandro(viento=(0.3, -0.05, 0.35), de_pie=False):
    """Curly mop, half asleep, charcoal hoodie open over a white tank top, chain with a star, a cigarette in the mouth corner."""
    g = Figura("alexandro", "#e8bba6")
    n = g.n
    sudadera = mat("sudadera", "#2e2f33", 0.75, coat=0.0)
    blanca = mat("camiseta_blanca", "#e9e7e1", 0.8, coat=0.0)
    g.rostro(lid=0.2, mirada=(0.3, 0.0), ceja="#241812", ceja_inc=0.2, ceja_alto=-0.012)
    g.cuerpo(blanca, sudadera, sudadera, mat("pantalon_gris", "#2a2a2d", 0.8, coat=0.0), mat("tenis_mate", "#232326", 0.8, coat=0.0), de_pie=de_pie, torso=False)
    tw, td, th = g.torso
    caja_r(n + "_camiseta", blanca, g.root, (0, 0, th), (tw - 0.012, td - 0.012, th - 0.004), 0.075, taper=0.9)
    sud = caja_r(n + "_sudadera", sudadera, g.root, (0, 0, th + 0.004), (tw, td, th), 0.08, taper=0.9)
    corte = caja_r(n + "_corte", sudadera, g.root, (0, -td, th), (0.07, td * 0.75, th * 1.3), 0.02, taper=1.2)
    corte.hide_render = corte.hide_viewport = True
    bo = sud.modifiers.new("abierta", "BOOLEAN")
    bo.operation, bo.object, bo.solver = "DIFFERENCE", corte, "EXACT"
    caja_r(n + "_resorte", sudadera, g.root, (0, 0, 0.04), (tw + 0.008, td + 0.008, 0.035), 0.03).modifiers.new("abierta", "BOOLEAN").object = corte
    for s in (-1, 1):  # the two front edges with their drawstrings
        cilindro(f"{n}_borde{s}", sudadera, g.root, (s * 0.076, -td - 0.002, 0.02), (s * 0.04, 0.16, 1), 0.29, 0.013, 12)
        cilindro(f"{n}_cordon{s}", mat("cordon", "#55565b", 0.8, coat=0.0), g.root, (s * 0.108, -td - 0.006, 0.17), (s * 0.02, 0.05, 1), 0.09, 0.005, 8)
    toro(n + "_capucha", sudadera, g.root, (0, 0.075, 0.33), 0.125, 0.042, (0, -0.5, 1))
    esfera(n + "_capucha_atras", sudadera, g.root, (0, 0.135, 0.28), (0.15, 0.07, 0.1))
    pelo = mat("rizos", "#2a1b15", 0.6, coat=0.05)
    N, ang = 120, math.pi * (3 - math.sqrt(5))
    for i in range(N):  # few big overlapping lumps: one mass of curls, not separate balls
        z = 1 - 2 * (i + 0.5) / N
        r = math.sqrt(1 - z * z)
        dd = Vector((r * math.cos(i * ang), r * math.sin(i * ang), z))
        frente = -dd.y / max(r, 1e-6)
        lim = 62 - 8 * frente if frente > 0 else 80 - 50 * frente  # fringe to the brows, down to the neck behind
        if math.degrees(math.acos(z)) > lim:
            continue
        rr = 0.062 + 0.03 * ((i * 37) % 11) / 10
        esfera(f"{n}_rizo{i:03d}", pelo, g.cab, HC + Vector((dd.x * g.A, dd.y * g.B, dd.z * g.C)) * 1.06, rr)
    esfera(n + "_boca", g.negro, g.cab, g.cara(-0.004, -0.125, 0.0), (0.045, 0.012, 0.007), Quaternion((0, 1, 0), 0.08))
    g.cadena(y=-td + 0.006)
    eje = Vector((0.45, -1, -0.18)).normalized()
    p = g.cara(0.04, -0.123, -0.012)
    cilindro(n + "_filtro", mat("filtro", "#c98a4b", 0.8, coat=0.0), g.cab, p, eje, 0.035, 0.0095)
    cilindro(n + "_papel", mat("papel", "#eeeae0", 0.8, coat=0.0), g.cab, p + eje * 0.035, eje, 0.075, 0.0095)
    brasa = mat("brasa", "#ff5a1e", 0.5, emit=14.0)
    cilindro(n + "_brasa", brasa, g.cab, p + eje * 0.11, eje, 0.008, 0.009)
    puffs = humo(g, "humo")
    emi = next(x for x in brasa.node_tree.nodes if x.type == "BSDF_PRINCIPLED").inputs["Emission Strength"]

    def pose(f):
        cab = (0.0 + 0.04 * onda(f, 2 * BEAT), 0.03 * onda(f, 80), 0.06 * onda(f, 240))
        if de_pie:
            manos = {s: (Vector((s * 0.285, -0.02, 0.0 + 0.004 * onda(f, 2 * BEAT, 0.5))), (s, 0.4, 0.2)) for s in (-1, 1)}
        else:
            manos = {s: (Vector((s * 0.105, -0.2, 0.135 + 0.004 * onda(f, 2 * BEAT, 0.5))), (s, 0.5, -0.3)) for s in (-1, 1)}
        g.posar(f, cab, manos, parpadeo(f, (40, 46, 170), g.lid0))
        posar_humo(g, puffs, f, NECK + Euler(cab).to_matrix() @ (p + eje * 0.12), viento, r=0.028)
        emi.default_value = 14.0 + 10.0 * max(0.0, onda(f, 120)) ** 6  # the ember flares on a slow drag
        emi.keyframe_insert("default_value", frame=f)
    g.pose = pose
    return g


def construir(volante=None, viento=(0.3, -0.05, 0.35), quien=("alexandro",), de_pie=False):
    hacer = {"alexandro": lambda: alexandro(viento, de_pie)}
    figs = {k: hacer[k]() for k in quien}
    for g in figs.values():
        for f in range(NFR + 1):
            g.pose(f)
    return figs


# ---------------------------------------------------------------- studio

def estudio(figs, cam_pos, mira, lens):
    s = bpy.context.scene
    w = bpy.data.worlds.new("w")
    s.world = w
    if not (w.node_tree and w.node_tree.nodes):
        w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.1, 0.1, 0.11, 1)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=8)
    objeto("piso", bm, mat("piso", "#6a6a6e", 0.9, coat=0.0), None, (0, 0, -0.2))
    for i, g in enumerate(figs.values()):
        g.root.location = ((i - (len(figs) - 1) / 2) * 0.7, 0, 0)
    for name, loc, pw, size, col in (("key", (-2.2, -3.2, 2.6), 300, 2.2, (1, 0.96, 0.9)), ("rim", (2.4, 2.0, 2.2), 250, 1.2, (0.85, 0.9, 1)),
                                     ("fill", (2.5, -2.5, 0.8), 90, 2.5, (1, 1, 1))):
        l = bpy.data.lights.new(name, "AREA")
        l.energy, l.size, l.color = pw, size, col
        ob = bpy.data.objects.new(name, l)
        ob.location = loc
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = (Vector((0, 0, 0.3)) - Vector(loc)).to_track_quat("-Z", "Y")
        s.collection.objects.link(ob)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = lens
    cam.location = cam_pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (Vector(mira) - cam.location).to_track_quat("-Z", "Y")
    s.collection.objects.link(cam)
    s.camera = cam


def motor(samples, w, h):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = w, h, 100
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.view_settings.view_transform = "Standard"
    s.render.fps = 24
    s.frame_start, s.frame_end = 0, NFR - 1
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = "OPTIX"
    pr.get_devices()
    for d in pr.devices:
        d.use = d.type == "OPTIX"
    s.cycles.device = "GPU"


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    sc = bpy.context.scene
    if argv[0] == "retrato":  # one standing figure framed like its Klein image: retrato <name> <out.png> [samples]
        figs = construir(quien=(argv[1],), de_pie=True)
        estudio(figs, (-1.0, -2.6, 0.95), (0, 0, 0.27), 85)
        motor(int(argv[3]) if len(argv) > 3 else 64, 720, 720)
        sc.frame_set(0)
        sc.render.filepath = argv[2]
        bpy.ops.render.render(write_still=True)

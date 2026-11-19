"""The Mercedes-AMG G63 6x6 grille (owner 2026-11-18 18:58; the model came with a Brabus slatted grille and a "B" badge).
Reference: ~/cc-out/mto-asset-fixes/parrilla/ref-frente-g63-6x6.png and the sharper luces/refs/Mercedes-Benz_G63_AMG_6__6__W463__front.JPG:
a satin surround, a black diamond-wire mesh, two thin chrome bars on each side at the star's height, the three-pointed star
in a ring at the centre, the mesh visible inside the ring.
Kept from the model on purpose: the opening's size and place (x CX +-0.42, z 1.04-1.29, front face y 2.80, measured from a
close render, blender/tripo/parrilla_sondeo.py), so the new grille sits on the body as is; the real grille is a little
taller for its width (2.9:1 vs the model's 3.4:1). Proportions inside it from the photo: star ring 0.67 of the opening's
height, bars at the star's centre +-0.06 of the height, 0.045 of it thick.
One mesh, `parrilla_g63`, two materials (parrilla_cromo, parrilla_malla): live, two draw calls. It sits a few mm in front of the old
grille, which it hides; nothing is deleted from the model. Coordinates are the truck's local frame at rest (escena.py).
"""
import math
import os
import bpy
import bmesh
from mathutils import Vector

Y, ZC, ANCHO, ALTO = 2.80, 1.163, 0.85, 0.25  # front face, centre height, opening outside size
MARCO = 0.02  # surround band
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "texturas", "parrilla_malla.png")  # texturas/parrilla_malla.py
CELDA = 0.03  # one texture tile (2 x 2 diamonds): 15 mm diamonds, as in the photo
RUGOSIDAD = 0.3  # the surround, bars and star


def _mats():
    # satin chrome, not the scene's mirror "cromo" (roughness 0.12): mirrored, the bars on one side took the night's black
    cromo = bpy.data.materials.get("parrilla_cromo") or bpy.data.materials.new("parrilla_cromo")
    cromo.use_nodes = True
    p = cromo.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.85, 0.85, 0.86, 1)
    p.inputs["Metallic"].default_value, p.inputs["Roughness"].default_value = 1.0, RUGOSIDAD
    m = bpy.data.materials.get("parrilla_malla") or bpy.data.materials.new("parrilla_malla")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value, p.inputs["Metallic"].default_value = 0.5, 0.0
    tx = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(TEX, check_existing=True)
    nt.links.new(tx.outputs["Color"], p.inputs["Base Color"])
    return cromo, m


def _caja(bm, x0, x1, y0, y1, z0, z1, idx):
    vs = [bm.verts.new((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    for c in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in c]).material_index = idx


def parrilla(parent, cx=1.72):
    """Builds the grille mesh at the opening and parents it to the truck. Returns it."""
    cromo, malla = _mats()
    me = bpy.data.meshes.new("parrilla_g63")
    me.materials.append(cromo)
    me.materials.append(malla)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    x0, x1, z0, z1 = cx - ANCHO / 2, cx + ANCHO / 2, ZC - ALTO / 2, ZC + ALTO / 2
    # surround: four bars, 18 mm proud of the face and 30 mm into the body (4 mm in floated 6 mm off it)
    yf = Y + 0.018
    _caja(bm, x0, x1, Y - 0.03, yf, z1 - MARCO, z1, 0)
    _caja(bm, x0, x1, Y - 0.03, yf, z0, z0 + MARCO, 0)
    _caja(bm, x0, x0 + MARCO, Y - 0.03, yf, z0, z1, 0)
    _caja(bm, x1 - MARCO, x1, Y - 0.03, yf, z0, z1, 0)
    # the mesh: one quad 6 mm in front of the old grille (its slats and badge end at y 2.799), tiled
    ym = Y + 0.006
    q = [bm.verts.new((x, ym, z)) for x, z in ((x0 + MARCO, z0 + MARCO), (x1 - MARCO, z0 + MARCO), (x1 - MARCO, z1 - MARCO), (x0 + MARCO, z1 - MARCO))]
    f = bm.faces.new(q)
    f.material_index = 1
    abiertas = [f]  # open pieces (the mesh quad, the star's blades): they must face the front, +y
    for l in f.loops:
        l[uv].uv = (l.vert.co.x / CELDA, l.vert.co.z / CELDA)
    # the star's ring and the three blades, chrome, proud of the mesh
    R = 0.67 * ALTO / 2
    yr = Y + 0.016
    n, t = 32, 0.007
    anillo = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = Vector((math.cos(a), 0, math.sin(a)))
        anillo.append([bm.verts.new(Vector((cx, 0, ZC)) + d * r + Vector((0, yy, 0))) for r, yy in ((R - t, yr), (R, yr + 0.004), (R + t, yr), (R, ym))])
    for i in range(n):
        a_, b_ = anillo[i], anillo[(i + 1) % n]
        for k in range(4):
            bm.faces.new((a_[k], b_[k], b_[(k + 1) % 4], a_[(k + 1) % 4])).material_index = 0
    for ang in (90, 210, 330):
        d = Vector((math.cos(math.radians(ang)), 0, math.sin(math.radians(ang))))
        lado = Vector((-d.z, 0, d.x))
        c0 = Vector((cx, ym, ZC))
        base = [bm.verts.new(c0 + lado * s * 0.016) for s in (-1, 1)]
        punta = bm.verts.new(c0 + d * (R - t))
        cresta = bm.verts.new(c0 + Vector((0, 0.012, 0)))
        for a_, b_ in ((base[0], punta), (punta, base[1])):
            f = bm.faces.new((a_, b_, cresta))
            f.material_index = 0
            abiertas.append(f)
    # bars: two each side, from the surround to the ring, at the star's centre +-0.06 of the height
    for zb in (ZC + 0.06 * ALTO, ZC - 0.06 * ALTO):
        for xa, xb in ((x0 + MARCO, cx - R - t), (cx + R + t, x1 - MARCO)):
            _caja(bm, xa, xb, ym, Y + 0.02, zb - 0.0056, zb + 0.0056, 0)
    bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f not in abiertas])  # the closed parts: outward
    bm.normal_update()
    for f in abiertas:
        if f.normal.y < 0:
            f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("parrilla_g63", me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o

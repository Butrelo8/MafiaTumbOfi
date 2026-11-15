"""Regression test for placing a rigged clip in the scene (docs/lanes.md › Findings, the raw sheet's hallazgos #6).

Appends a Mixamo clip twice into an empty file and moves each copy to the rear-right seat (scale 1.25, turned 180°):
  crudo: matrix_world = M @ matrix_world on every object (crudo.py's loop) -> bone-parented children move twice (expected off)
  raiz:  the top-level objects under one empty that carries M (montaje.py's diego_interino) -> must stay on the bone
Pass: in 'raiz' the bone child's z span from the hips equals the unmoved one × 1.25 within 1 cm. Exit 1 otherwise.

  blender/montaje_rig_test.sh [clip.blend (Windows path)]
"""
import bpy, sys, math
from mathutils import Matrix

a = sys.argv[sys.argv.index("--") + 1:]
CLIP = a[0]
K = 1.25
sc = bpy.context.scene
sc.frame_set(1)


def cargar():
    with bpy.data.libraries.load(CLIP, link=False) as (s, d):
        d.objects = list(s.objects)
    nuevos = [o for o in d.objects if o is not None and o.type in ("MESH", "ARMATURE", "EMPTY")]
    for o in nuevos:
        sc.collection.objects.link(o)
    mx = next(o for o in nuevos if o.type == "ARMATURE")
    hijo = next(o for o in nuevos if o.type == "MESH" and o.parent and (o.parent.type == "EMPTY" or o.parent_type == "BONE"))
    return nuevos, mx, hijo


def tramo(mx, hijo):
    sc.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    h = (mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head).z
    e = hijo.evaluated_get(dg)
    me = e.to_mesh()
    zs = [(e.matrix_world @ v.co).z for v in me.vertices]
    e.to_mesh_clear()
    return min(zs) - h, max(zs) - h


res = {}
for modo in ("nada", "crudo", "raiz"):
    nuevos, mx, hijo = cargar()
    sc.frame_set(1)
    hips = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    M = Matrix.Translation((2.11, -0.53, 1.259)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(K, 4) @ Matrix.Translation(-hips)
    if modo == "crudo":
        for o in nuevos:
            o.matrix_world = M @ o.matrix_world
    elif modo == "raiz":
        r = bpy.data.objects.new("raiz", None)
        sc.collection.objects.link(r)
        r.matrix_world = M
        for o in nuevos:
            if o.parent is None:
                o.parent = r
                o.matrix_parent_inverse = Matrix.Identity(4)
    res[modo] = tramo(mx, hijo)
    print(f"RIGTEST {modo} {hijo.name} z from hips {res[modo][0]:+.3f}..{res[modo][1]:+.3f}", flush=True)
    for o in nuevos:  # out of the way of the next copy
        o.hide_viewport = o.hide_render = True

esperado = (res["nada"][0] * K, res["nada"][1] * K)
err = {m: max(abs(res[m][0] - esperado[0]), abs(res[m][1] - esperado[1])) for m in ("crudo", "raiz")}
print(f"RIGTEST expected {esperado[0]:+.3f}..{esperado[1]:+.3f}; off by: crudo {err['crudo']:.3f} m (known bad), raiz {err['raiz']:.3f} m", flush=True)
ok = err["raiz"] < 0.01
print("RIGTEST", "PASS" if ok else "FAIL", flush=True)
sys.exit(0 if ok else 1)

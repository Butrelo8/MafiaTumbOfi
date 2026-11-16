"""Pantalla móvil 3D, step 1: turn the found model into the base the build places (docs/design/pantalla-3d.md).

Source: "Mitsubishi Fuso Canter" by Raed Almaharmah (sketchfab.com/raedalmaharmah6), CC-BY-4.0,
sketchfab.com/3d-models/mitsubishi-fuso-canter-2b58376d6aaf4641adf30d4c9044de74, fetched from the Objaverse mirror
(huggingface.co/datasets/allenai/objaverse, glbs/000-063/2b58376d….glb; 129,583 triangles, the same as Sketchfab's faceCount).
A light-duty cabover box truck, the ELF class of the references, at real scale (tyre radius 0.38 m) with dual rear wheels.

What this does: imports the glb, joins it, turns it to face +Y, removes the ribbed cargo box (the build puts the LED box there),
sorts the remaining islands into paint / tyre / chassis / tail lamp / headlamp material slots, puts the origin on the floor at the
old box's back face on the centre line, and saves one mesh object `pantalla3d_base` in <out.blend>.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/pantalla_3d_prep.py)" \
    -- <fuso-canter.glb (Windows)> <out.blend (Windows)>
"""
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

a = sys.argv[sys.argv.index("--") + 1:]
GLB, OUT = a[0], a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]

# glb frame (measured): length on X, cab at +X (bumper 3.48, mirrors 3.72), old box X -3.65..1.61 Z 0.78..3.21,
# width Y -2.31..0.02 (centre -1.145), rear axle X -1.74 (duals), front axle X 2.26, tyre radius 0.38
BOX_X0, BOX_X1, YC = -3.65, 1.61, -1.145
RUEDAS = [(-1.74, 0.385), (2.26, 0.385)]  # axle x, radius

bm = bmesh.new()
for o in ms:
    me = o.data.copy()
    me.transform(o.matrix_world)
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()


def islas():
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        st, fs = [f], []
        seen.add(f.index)
        while st:
            g = st.pop()
            fs.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        st.append(h)
        vs = {v for g in fs for v in g.verts}
        lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
        hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
        out.append((fs, lo, hi))
    return out


PINTURA, LLANTA, CHASIS, CALAVERA, FARO = range(5)
quitar, n_box = [], 0
cuenta = [0] * 5
for fs, lo, hi in islas():
    if lo.x > BOX_X0 - 0.1 and hi.x < BOX_X1 + 0.06 and hi.z > 1.0 and lo.z > 0.7:
        quitar.extend(fs)  # the old cargo box: panels, ribs, posts, doors (the low subframe, z ≤ 0.91, stays)
        n_box += 1
        continue
    c = (lo + hi) / 2
    if any(abs(c.x - ax) < r + 0.02 and hi.z < 2 * r + 0.05 and abs(hi.x - lo.x) < 2 * r + 0.06 for ax, r in RUEDAS):
        k = LLANTA
    elif hi.x < -3.3 and 0.55 < lo.z and hi.z < 0.95 and (hi - lo).length < 0.4:
        k = CALAVERA  # tail lamp clusters on the rear crossmember
    elif lo.x > 3.3 and 0.6 < lo.z and hi.z < 0.9 and (hi - lo).length < 0.4:
        k = FARO
    elif hi.z < 1.0 and hi.x < 1.7:
        k = CHASIS
    else:
        k = PINTURA
    cuenta[k] += 1
    for f in fs:
        f.material_index = k
bmesh.ops.delete(bm, geom=list(set(quitar)), context="FACES")
# face +Y (cab forward), centre line on x 0, origin at the old box's back face on the floor
bm.transform(Matrix.Translation((0, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))  # +X -> +Y, Y -> -X
bm.transform(Matrix.Translation((YC, -BOX_X0, 0)))  # x' = -y: centre -1.145 -> +1.145, so add YC; y' = x: -3.65 -> 0
me = bpy.data.meshes.new("pantalla3d_base")
bm.to_mesh(me)
bm.free()
for n in ("p3_pintura", "p3_llanta", "p3_chasis", "p3_calavera", "p3_faro"):
    me.materials.append(bpy.data.materials.new(n))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
ob = bpy.data.objects.new("pantalla3d_base", me)
bpy.context.scene.collection.objects.link(ob)
lo = Vector([min(v.co[i] for v in me.vertices) for i in range(3)])
hi = Vector([max(v.co[i] for v in me.vertices) for i in range(3)])
print(f"PREP old box islands removed {n_box}; slots paint/tyre/chassis/tail/head {cuenta}; tris {sum(len(p.vertices) - 2 for p in me.polygons)}")
print(f"PREP bbox {tuple(round(x, 3) for x in lo)} .. {tuple(round(x, 3) for x in hi)}")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("PREP OK", OUT)

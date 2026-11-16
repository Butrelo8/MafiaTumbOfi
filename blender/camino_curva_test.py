"""Check of camino_curva.py's mapping, CPU only (no render, no GPU):
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/camino_curva_test.py)"
1. doblar() maps y < S0 to itself exactly, keeps x as the offset along the normal (lane widths), is continuous at S0 and S1.
2. The geometry-nodes group (the scatters' version) puts instances where doblar() does, turns them by ph, and deletes the ones on the
   inside of the bend beyond 0.45 R.
"""
import os
import sys

import bmesh
import bpy
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, "camino_curva.py"), encoding="utf8").read().split("# ---------------------------------------------------------------- the sweep")[0]
exec(compile(fuente, "camino_curva.py", "exec"), globals())

# 1. the mapping
y = np.array([-300.0, -1.0, 0.0, 39.999, 40.0])
x = np.array([-13.0, -5.0, 0.0, 3.5, 9.0])
xs, ys, ph = doblar(x, y)
assert np.array_equal(xs, x) and np.array_equal(ys, y) and not ph.any(), "y <= S0 must map to itself"
s0, s1, R = CURVA["s0"], CURVA["s1"], CURVA["radio"]
for yy in (s0 + 0.001, s1 - 0.001, s1 + 0.001, s1 + 300.0):   # continuous, and a lane is still 3.5 m wide after the bend
    a, b = doblar(np.array([0.0, 3.5]), np.array([yy, yy]))[:2]
    assert abs(np.hypot(a[1] - a[0], b[1] - b[0]) - 3.5) < 1e-6, (yy, "lane width")
e1, e2 = doblar(0.0, s1 - 1e-6)[:2], doblar(0.0, s1 + 1e-6)[:2]
assert abs(e1[0] - e2[0]) < 1e-4 and abs(e1[1] - e2[1]) < 1e-4, "S1 not continuous"
print("TEST mapa OK")

# 2. the node group on instances
pts = [(px, py) for px in (-120.0, -60.0, -5.0, 3.0, 9.0, 40.0) for py in (-50.0, 10.0, 39.0, 41.0, 100.0, 200.0, 260.0, 400.0)]
bm = bmesh.new()
for px, py in pts:
    bm.verts.new((px, py, 0.0))
me = bpy.data.meshes.new("t"); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("t", me); bpy.context.scene.collection.objects.link(o)
ng = bpy.data.node_groups.new("t", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
gi, go = ng.nodes.new("NodeGroupInput"), ng.nodes.new("NodeGroupOutput")
mp = ng.nodes.new("GeometryNodeMeshToPoints")
cu = ng.nodes.new("GeometryNodeMeshCube"); cu.inputs["Size"].default_value = (2.0, 4.0, 1.0)
iop = ng.nodes.new("GeometryNodeInstanceOnPoints")
g = ng.nodes.new("GeometryNodeGroup"); g.node_tree = _grupo_doblar()
re = ng.nodes.new("GeometryNodeRealizeInstances")
for a, b in ((gi.outputs[0], mp.inputs[0]), (mp.outputs[0], iop.inputs["Points"]), (cu.outputs[0], iop.inputs["Instance"]),
             (iop.outputs[0], g.inputs[0]), (g.outputs[0], re.inputs[0]), (re.outputs[0], go.inputs[0])):
    ng.links.new(a, b)
o.modifiers.new("n", "NODES").node_group = ng
ev = bpy.context.evaluated_depsgraph_get().objects["t"].to_mesh()
v = np.array([tuple(p.co) for p in ev.vertices]).reshape(-1, 8, 3)
quedan = [(px, py) for px, py in pts if not (py > s0 and px < -0.45 * R)]
assert len(v) == len(quedan), f"{len(v)} instances, expected {len(quedan)} (the inside of the bend is deleted)"
for (px, py), cubo in zip(quedan, v):
    ex, ey, eph = doblar(px, py)
    c = cubo.mean(axis=0)
    assert abs(c[0] - ex) < 1e-3 and abs(c[1] - ey) < 1e-3, ((px, py), c[:2], (ex, ey))
    lados = [cubo[j] - cubo[i] for i in range(8) for j in range(i + 1, 8) if abs(np.linalg.norm(cubo[j] - cubo[i]) - 4.0) < 1e-4]
    assert lados, "no 4 m edge"
    assert all(abs(abs(l[:2] @ np.array([-np.sin(eph), np.cos(eph)])) / 4.0 - 1) < 1e-3 for l in lados), ((px, py), "yaw: the 4 m side must run along the heading")
print("TEST grupo OK", len(v), "instancias,", len(pts) - len(v), "borradas")

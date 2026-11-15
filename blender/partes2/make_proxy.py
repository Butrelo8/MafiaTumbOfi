# make_proxy.py -- <skin.blend> <out dir> <name> [voxel_m] [faces]: a rig proxy of the joined skin for Mixamo, whose
# Auto-Rigger bounced the 274k-face, four-shell skin twice with no error (frfrbrowser 11-14). Voxel remesh (one closed,
# manifold surface, no overlapping shells at the neck and wrists), then decimate to <faces>, no textures. The full skin
# gets the proxy's weights back by Data Transfer (nearest face, interpolated). Prints the finger runs across each hand
# (fingers must stay separate through the remesh) and writes <name>.fbx in export_rerig.py's frame and axes.
import bpy, sys, os
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]
out, name = a[0], a[1]; vox = float(a[2]) if len(a) > 2 else 0.002; faces = int(a[3]) if len(a) > 3 else 90000
o = bpy.data.objects["Diego"]
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x, do_unlink=True)
bpy.context.view_layer.objects.active = o; o.select_set(True)
m = o.modifiers.new("vox", "REMESH"); m.mode = "VOXEL"; m.voxel_size = vox; m.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier="vox")
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.fill_holes(sides=0); bpy.ops.mesh.quads_convert_to_tris(); bpy.ops.object.mode_set(mode="OBJECT")
import bmesh; bm = bmesh.new(); bm.from_mesh(o.data)
print("@@ boundary edges after fill:", sum(e.is_boundary for e in bm.edges), "loose parts kept"); bm.free()
n0 = len(o.data.polygons)
d = o.modifiers.new("dec", "DECIMATE"); d.ratio = min(1.0, faces / n0); bpy.ops.object.modifier_apply(modifier="dec")
o.data.materials.clear(); o.name = o.data.name = "Diego"
P = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", P); P = P.reshape(-1, 3)
print("@@ proxy: voxel %.1f mm, %d faces after remesh, %d after decimate, %d verts" % (vox * 1000, n0, len(o.data.polygons), len(o.data.vertices)))
import json
for side, sd in (("right", -1), ("left", 1)):      # finger runs: slices across the hand, perpendicular to the forearm axis
    H = [p for p in P if sd * p[0] > 0.30]
    H = np.array(H); ax = np.array([sd * 0.86, -0.03, -0.51]); ax /= np.linalg.norm(ax)
    t = H @ ax; e1 = np.cross(ax, [0, 0, 1.0]); e1 /= np.linalg.norm(e1)
    for f in (0.70, 0.80, 0.90):
        tt = t.min() + f * np.ptp(t); S = np.sort(H[np.abs(t - tt) < 0.001] @ e1)
        gaps = np.diff(S); cut = gaps > 0.0015
        print("@@ %s hand %d%% along: %d runs, gaps mm %s" % (side, f * 100, cut.sum() + 1, np.round(gaps[cut] * 1000, 1).tolist()))
bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"{name}.fbx"), use_selection=True, object_types={"MESH"},
    apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
print("@@ fbx %.1f MB" % (os.path.getsize(os.path.join(out, f"{name}.fbx")) / 1e6))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"{name}.blend"))

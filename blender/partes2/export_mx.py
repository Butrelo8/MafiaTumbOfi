# export_mx.py -- <assembled.blend> <out dir> <name> <hand.json>: the upload FBX for Mixamo plus a marker guide.
# FBX as export_rerig.py (Y-up, -Z forward, scale baked, 1.0 m frame, feet on z = 0, facing -Y), textures cut to
# 1024² and embedded (Mixamo's ~20 MB upload limit; geometry is what it rigs). Markers measured on this mesh:
#   chin   = the neck cut height (assemble.py CUT), centre line
#   groin  = top of the gap between the legs (lowest point of the mesh on the centre line above z 0.12)
#   wrists = hand.json wrist rings; elbows = the arm path halfway between the armpit (x 0.14) and the wrist
#   knees  = each leg's centre halfway between the groin and the ankle (narrowest leg slice under z 0.12)
# Writes <name>.fbx, <name>_front.png (1024 x 1280, 1.1 m tall frame centred at z 0.5), <name>_markers.png, markers.json.
import bpy, sys, os, json
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]
blend_out, out, name, hjson = a[:4]
CUT = float(a[4]) if len(a) > 4 else 0.598
o = bpy.data.objects["Diego"]
P = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", P); P = P.reshape(-1, 3)
for img in bpy.data.images:
    if img.size[0] > 1024: img.scale(1024, 1024)
    img.pack()
mk = {"chin": [0.0, CUT]}
# groin: the lowest height where the mesh reaches the centre line (below it, the legs leave a gap at x = 0)
mid = P[np.abs(P[:, 0]) < 0.004]; mk["groin"] = [0.0, float(mid[(mid[:, 2] > 0.12) & (mid[:, 2] < 0.45), 2].min())]
H = json.load(open(hjson))
for side, sd in (("right", -1), ("left", 1)):
    w = H[side]["wrist"]; mk["wrist_" + side] = [w[0], w[2]]
    xm = (0.14 + abs(w[0])) / 2; S = P[(np.abs(sd * P[:, 0] - xm) < 0.003) & (P[:, 2] > 0.3) & (P[:, 2] < 0.6)]
    mk["elbow_" + side] = [sd * xm, float(S[:, 2].mean())]
    L = P[(sd * P[:, 0] > 0.01) & (sd * P[:, 0] < 0.15) & (P[:, 2] < mk["groin"][1])]
    best = None
    for z in np.arange(0.03, 0.12, 0.004):
        S = L[np.abs(L[:, 2] - z) < 0.002]
        if len(S) > 10 and (best is None or np.ptp(S[:, 0]) < best[1]): best = (z, np.ptp(S[:, 0]))
    zk = (mk["groin"][1] + best[0]) / 2; S = L[np.abs(L[:, 2] - zk) < 0.003]
    mk["knee_" + side] = [float(S[:, 0].mean()), float(zk)]; mk["ankle_" + side] = [float(S[:, 0].mean()), float(best[0])]
for k, v in mk.items(): print("@@ marker %-12s x %+.3f z %.3f  (%.0f %% height, %.1f %% side)" % (k, v[0], v[1], v[1] * 100, v[0] * 100))
json.dump(mk, open(os.path.join(out, "markers.json"), "w"), indent=1)
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x, do_unlink=True)
o.select_set(True); bpy.context.view_layer.objects.active = o
bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"{name}.fbx"), use_selection=True, object_types={"MESH"},
    apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True,
    mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
print("@@ fbx", os.path.getsize(os.path.join(out, f"{name}.fbx")) / 1e6, "MB", len(o.data.vertices), "verts", len(o.data.polygons), "faces")
sc = bpy.context.scene; cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.1; cam.location = (0, -3, 0.5); cam.rotation_euler = (1.5708, 0, 0)
sc.camera = cam; sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.color_type = "TEXTURE"
sc.display.shading.light = "STUDIO"; sc.render.resolution_x, sc.render.resolution_y = 1024, 1280
sc.world = sc.world or bpy.data.worlds.new("w")
sc.render.filepath = os.path.join(out, f"{name}_front.png"); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=blend_out)

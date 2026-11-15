# look.py -- <rig blend open> <out.blend>: the owner's look picks (2026-11-15 00:13), all matched to diego.png:
#   skin  : every skin texture (the four "Diego" materials) shifted so its skin cluster's median is the source's pale
#           peach, sRGB (226, 192, 170) = the median of the source's cheek, forehead and arm patches. Per-pixel channel
#           gain in linear light, weighted by closeness to the old skin median (eye whites, pupils, brows keep theirs).
#   hair  : soft dark brown, sRGB (64, 55, 51): each dark texel becomes that colour times (L + 0.02) / (median L + 0.02),
#           clipped to 0.6-1.4 (the texture is near black, so this keeps what little shading it has); matte: roughness 1, specular 0.1 (Principled and Workbench).
#   chain : a silver chain on the shirt as in the source: a closed curve around the neck 1.5 mm off the shirt, at the
#           collar behind and dipping DIP in front, 1.1 mm bevel, metallic, bone-parented to mixamorig:Spine2.
# Prints each image's old median and the gain; saves out.blend (images re-packed).
import bpy, sys, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
SKIN = np.array([226, 192, 170]) / 255; HAIR = np.array([64, 55, 51]) / 255; DIP = 0.045
lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def base_image(mat):
    bsdf = mat.node_tree.nodes["Principled BSDF"]; ln = bsdf.inputs["Base Color"].links
    return ln[0].from_node.image if ln and ln[0].from_node.type == "TEX_IMAGE" else None


def pixels(img):
    P = np.empty(img.size[0] * img.size[1] * 4, np.float32); img.pixels.foreach_get(P); return P.reshape(-1, 4)


def store(img, P):
    img.pixels.foreach_set(P.ravel()); img.update(); img.pack()


for slot in bpy.data.objects["Diego"].material_slots:                      # skin
    img = base_image(slot.material); P = pixels(img); C = P[:, :3]          # 8-bit image: pixels are sRGB-encoded
    hue_ok = (C[:, 0] > C[:, 1]) & (C[:, 1] > C[:, 2]) & (C[:, 0] > 0.25) & (P[:, 3] > 0.5)
    med = np.median(C[hue_ok], 0)
    gain = lin(SKIN) / np.maximum(lin(med), 1e-4)
    d = np.linalg.norm(C - med, axis=1); w = np.clip(1 - d / 0.30, 0, 1)[:, None]
    Lc = lin(np.clip(C, 0, 1)) * (1 + w * (gain - 1))
    C[:] = np.clip(np.where(Lc <= 0.0031308, Lc * 12.92, 1.055 * np.power(np.clip(Lc, 0, None), 1 / 2.4) - 0.055), 0, 1)
    store(img, P)
    print("@@ skin", slot.material.name, img.name, img.colorspace_settings.name, "old median sRGB", (med * 255).round().tolist(), "gain", gain.round(2).tolist())

hm = bpy.data.objects["hair"].material_slots[0].material; img = base_image(hm); P = pixels(img); C = P[:, :3]   # hair
L = C @ np.array([0.2126, 0.7152, 0.0722]); dark = L < 0.35
med = np.median(L[dark]); rel = np.clip((L[dark] + 0.02) / (med + 0.02), 0.6, 1.4)     # the texture is near black: floor
C[dark] = np.clip(HAIR[None, :] * rel[:, None], 0, 1); store(img, P)
bsdf = hm.node_tree.nodes["Principled BSDF"]
for k in ("Roughness", "Metallic"):
    for l in list(bsdf.inputs[k].links): hm.node_tree.links.remove(l)
bsdf.inputs["Roughness"].default_value = 1.0; bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Specular IOR Level"].default_value = 0.1; hm.roughness = 1.0; hm.metallic = 0.0; hm.specular_intensity = 0.1
print("@@ hair median luminance %.3f -> sRGB %s" % (med, (HAIR * 255).round().tolist()))

sh = bpy.data.objects["shirt"]; dg = bpy.context.evaluated_depsgraph_get(); arm = bpy.data.objects["mx"]   # chain
arm.data.pose_position = "REST"; bpy.context.view_layer.update()
e = sh.evaluated_get(dg); m = e.to_mesh(); V = [sh.matrix_world @ v.co for v in m.vertices]
tree = BVHTree.FromPolygons(V, [list(p.vertices) for p in m.polygons]); e.to_mesh_clear()
top = max(v.z for v in V); ring = [v for v in V if v.z > top - 0.012]
c = sum(ring, Vector()) / len(ring); z0 = top - 0.008
pts = []
for k in range(72):
    th = 2 * math.pi * k / 72; d = Vector((math.sin(th), -math.cos(th), 0))        # th = 0 is the front (-Y)
    z = z0 - DIP * max(0.0, math.cos(th)) ** 2
    o = Vector((c.x, c.y, z)); best = None
    for t in range(0, 140):                                                        # outermost shirt hit along the ray
        hit = tree.ray_cast(o + d * (0.002 * t), d, 0.002)
        if hit[0] is not None: best = hit[0]
    pts.append((best or o + d * 0.06) + d * 0.0015)
cu = bpy.data.curves.new("chain", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0011; cu.bevel_resolution = 2
sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1); sp.use_cyclic_u = True
for p, q in zip(sp.points, pts): p.co = (*q, 1)
ch = bpy.data.objects.new("chain", cu); bpy.context.scene.collection.objects.link(ch)
cm = bpy.data.materials.new("chain_silver"); cm.use_nodes = True; b = cm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.8, 0.8, 0.82, 1); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.25
cm.diffuse_color = (0.8, 0.8, 0.82, 1); cm.metallic = 1.0; cm.roughness = 0.25; cu.materials.append(cm)
M = ch.matrix_world.copy(); ch.parent = arm; ch.parent_type = "BONE"; ch.parent_bone = "mixamorig:Spine2"
bpy.context.view_layer.update(); ch.matrix_world = M; arm.data.pose_position = "POSE"
print("@@ chain: %d points, collar z %.3f, front z %.3f, centre %s" % (len(pts), z0, z0 - DIP, tuple(round(x, 3) for x in c)))
bpy.context.scene["skin_srgb"] = (SKIN * 255).round().tolist()                     # for lids_build.py
bpy.ops.wm.save_as_mainfile(filepath=out)

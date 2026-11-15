# render_parts.py: one posed still of an entrant, framed like visual-lab's tex_probe.py (orthographic, 1024 px,
# Workbench studio light + texture colour + cavity, Standard), but the camera always comes from the SKINNED Body's
# bbox at that frame and view, so every entrant shares one framing.
#   $B -b <blend> --python render_parts.py -- <out.png> <frame> <front|side> <skinned|parts> [flat basecolor png]
# side = rig turned -90 deg about Z, as rig_figura.sh made idle_side.blend.
import bpy, sys, math
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]
out, frame, view, who = a[0], int(a[1]), a[2], a[3]; flat = a[4] if len(a) > 4 else None
sc = bpy.context.scene; rig = bpy.data.objects["rig"]
if view == "side": rig.rotation_euler.z += math.radians(-90)
sc.frame_set(frame)
body = bpy.data.objects["Body"]
for o in sc.objects:
    if o.type == "MESH":
        o.hide_render = not ((who == "skinned" and o.name == "Body") or (who == "parts" and o.name.startswith("part_")))
body.hide_render = who != "skinned"
if flat:
    for im in bpy.data.images:
        if "basecolor" in im.name.lower():
            cs = im.colorspace_settings.name
            if im.packed_file: im.unpack(method="REMOVE")
            im.filepath = flat; im.reload(); im.colorspace_settings.name = cs
dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg)
P = np.array([body.matrix_world @ v.co for v in ev.data.vertices]); lo, hi = P.min(0), P.max(0); H = hi[2] - lo[2]
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.rotation_euler = (math.radians(90), 0, 0); cam.data.ortho_scale = 1.04 * H
cam.location = ((lo[0] + hi[0]) / 2, lo[1] - 3 * H, (lo[2] + hi[2]) / 2); cam.data.clip_end = 100 * H
sc.render.resolution_x = sc.render.resolution_y = 1024; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "Standard"
import os
if os.environ.get("ENGINE") == "EEVEE":   # tex_probe.py's lit branch: the materials' own finish, one sun + grey world
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
else:
    sc.render.engine = "BLENDER_WORKBENCH"; s = sc.display.shading
    s.light = "STUDIO"; s.color_type = "TEXTURE"; s.show_cavity = True
sc.render.film_transparent = False; sc.render.use_compositing = False
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
print("@@RENDER@@", who, view, frame, "H=%.3f" % H, out, flush=True)

# export_rerig.py: the rig blend's Body as one clean, unrigged mesh for external auto-riggers (Mixamo, AccuRIG).
#   $B -b <diego_trellis_rig_full$S.blend> --python export_rerig.py -- <out dir (Windows)> <name>
# Keeps the current rig's frame (feet on z = 0, centred in XY, 1.0 m tall, facing -Y) so returned rigs compare
# without an offset. Writes <name>.fbx (Y-up, -Z forward, scale baked, base-colour texture embedded), the texture
# beside it as <name>_basecolor.png (AccuRIG wants textures in the model's folder), and <name>_front.png
# (orthographic front view, 1024 x 1280, frame = 1.1 m tall, feet at 5 % from the bottom) for marker placement.
import bpy, sys, os
out, name = sys.argv[sys.argv.index("--") + 1:][:2]
body = bpy.data.objects["Body"]
for o in list(bpy.data.objects):
    if o is not body: bpy.data.objects.remove(o, do_unlink=True)
body.parent = None
for m in list(body.modifiers): body.modifiers.remove(m)
body.vertex_groups.clear(); body.shape_key_clear() if body.data.shape_keys else None
bpy.context.view_layer.objects.active = body; body.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
body.name = body.data.name = "Diego"
src = next(n.image for m in body.data.materials if m and m.use_nodes for n in m.node_tree.nodes
           if n.type == "TEX_IMAGE" and any(l.to_socket.name == "Base Color" for l in n.outputs[0].links))
png = os.path.join(out, f"{name}_basecolor.png")
src.save(filepath=png); img = bpy.data.images.load(png); img.name = os.path.basename(png)
mat = bpy.data.materials.new("Diego"); mat.use_nodes = True; nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]; tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.6
body.data.materials.clear(); body.data.materials.append(mat)
bpy.ops.export_scene.fbx(filepath=os.path.join(out, f"{name}.fbx"), use_selection=True, object_types={"MESH"},
    apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True,
    mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
me = body.data; zs = [v.co.z for v in me.vertices]
print("@@EXPORT@@", name, len(me.vertices), len(me.polygons), "z", round(min(zs), 4), round(max(zs), 4), body.dimensions[:])
sc = bpy.context.scene; cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.1; cam.location = (0, -3, 0.5); cam.rotation_euler = (1.5708, 0, 0)
sc.camera = cam; sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.color_type = "TEXTURE"
sc.display.shading.light = "FLAT"; sc.render.resolution_x, sc.render.resolution_y = 1024, 1280
sc.render.film_transparent = False; sc.world = sc.world or bpy.data.worlds.new("w")
sc.render.filepath = os.path.join(out, f"{name}_front.png"); bpy.ops.render.render(write_still=True)

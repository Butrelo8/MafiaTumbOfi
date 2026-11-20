"""Live scene with the new G63, step 2: vivo-g63.blend (blender/vivo_g63_montar.py) -> coche.glb, the car with its rack, load, net and
dressing under one empty `camion`, uncompressed (scripts/vivo-g63-unir.mjs merges it into the live scene's cast / screen-truck file and
vivo-optimizar.mjs compresses the lot).

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <vivo-g63.blend> --python-exit-code 1 --python blender/vivo_g63_exportar.py \
    -- <coche.glb (Windows)>
"""
import bpy, os, sys

ruta = sys.argv[sys.argv.index("--") + 1]
O = bpy.data.objects
bpy.ops.object.select_all(action="DESELECT")
for o in O:
    if o.type in ("MESH", "EMPTY") and not o.hide_render:
        o.hide_set(False)
        o.select_set(True)
bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_selection=True, export_apply=True, export_yup=True, export_lights=False,
                          export_cameras=False, export_animations=False, export_image_format="WEBP",
                          export_draco_mesh_compression_enable=False)
print("G63 GLB", ruta, os.path.getsize(ruta), flush=True)

# Downsample the 1k HDRIs to 512x256 Radiance files for the page's reflections (run with blender -b).
import bpy, os, sys
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for n in ("qwantani_night_puresky", "qwantani_dusk_2_puresky"):
    im = bpy.data.images.load(os.path.join(repo, "blender", "assets", "camion", f"{n}_1k.hdr"))
    im.scale(512, 256)
    im.filepath_raw = os.path.join(repo, "public", "escena", f"{n}.hdr")
    im.file_format = "HDR"
    im.save()

"""A Tripo roof pod (overhead axle-lock / tyre-pressure panel, ref r04) to the kiln consola_techo contract that caja5._poner
places (blender/kiln_cabina.py): metres, Z up, the face toward -Y (the cab) tilted INCL degrees down, ANCHO wide in x, origin at
the top centre (it hangs from the headliner hit). One mesh, one material, Tripo's texture kept.

  blender -b --factory-startup --python pod_contrato.py -- <in.glb> <out.glb> <rx> <ry> <rz> [incl=25] [ancho=0.34]

rx ry rz (degrees, applied in that order after the importer's Y-up turn) bring the Tripo mesh's face to -Y with the long side
along x; read them off vistas.py's sheet of the raw file.
"""
import bpy, math, sys
from mathutils import Matrix

a = sys.argv[sys.argv.index("--") + 1:]
src, dst, rx, ry, rz = a[0], a[1], *map(float, a[2:5])
incl = float(a[5]) if len(a) > 5 else 25.0
ancho = float(a[6]) if len(a) > 6 else 0.34

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
mallas = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert len(mallas) == 1, f"{len(mallas)} meshes: the pod must be one draw call"
o = mallas[0]
bpy.context.view_layer.update()
M = o.matrix_world.copy()
o.parent = None
me = o.data
me.transform(M)
o.matrix_world = Matrix.Identity(4)
for x in [x for x in bpy.context.scene.objects if x is not o]:
    bpy.data.objects.remove(x)
me.transform(Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Rotation(math.radians(rx), 4, "X"))


def caja():
    xs = [v.co for v in me.vertices]
    return [min(c[i] for c in xs) for i in range(3)], [max(c[i] for c in xs) for i in range(3)]


lo, hi = caja()
s = ancho / (hi[0] - lo[0])
me.transform(Matrix.Rotation(math.radians(incl), 4, "X") @ Matrix.Scale(s, 4))  # +X turn: the -Y face tips downward
lo, hi = caja()
me.transform(Matrix.Translation((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -hi[2])))
lo, hi = caja()
o.name = me.name = "consola_techo"
print("POD tris", sum(len(p.vertices) - 2 for p in me.polygons), "mats", [m.name for m in me.materials],
      "caja", [round(v, 3) for v in lo], [round(v, 3) for v in hi], flush=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_yup=True)

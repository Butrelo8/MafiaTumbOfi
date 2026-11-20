"""Scratch check of the placement file's controls: moves objects by a world vector and saves a copy (never the owner's file). Then run
vivo_reparto_volcar.py on the copy and compare with scripts/g63/comparar_volcados.py (hand moved 10 cm: that wrist ~10 cm, the other rigs 0.0000;
roof case moved 20 cm: its handle and object, then blender/g63_red_ajustar.py for the net).

  blender-run blender.exe -b <copy.blend> --python-exit-code 1 --python blender/g63_prueba_mover.py -- <out .blend> <objeto> <dx> <dy> <dz> [<objeto> <dx> <dy> <dz> ...]
  Instead of a vector:  <objeto> agarre <0..1> sets that custom property;  <objeto> rotz <grados> turns the object about the world Z through its origin.
"""
import bpy, math, sys
from mathutils import Matrix, Vector

a = sys.argv[sys.argv.index("--") + 1:]
SAL, resto = a[0], a[1:]
O = bpy.data.objects
while resto:
    o = O[resto[0]]
    if resto[1] == "agarre":
        o["agarre"] = float(resto[2])
        resto = resto[3:]
        continue
    if resto[1] == "rotz":
        m = o.matrix_world.copy()
        t = m.translation.copy()
        o.matrix_world = Matrix.Translation(t) @ Matrix.Rotation(math.radians(float(resto[2])), 4, "Z") @ Matrix.Translation(-t) @ m
        resto = resto[3:]
        print("MOVER", o.name, "rotz", flush=True)
        continue
    m = o.matrix_world.copy()
    m.translation += Vector(float(v) for v in resto[1:4])
    o.matrix_world = m
    resto = resto[4:]
    print("MOVER", o.name, [round(v, 4) for v in o.matrix_world.translation], flush=True)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)

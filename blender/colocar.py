"""Owner placement of the Night B pole line (owner's rule 22:36: a pole line near a camera is a taste call).

  guardar: build the night scene (escena.py + mundo.py) and save a .blend where only `w_postes` can be selected (the
           wires ride on it), with the cameras of holds 4 and 6, where the line reads against the sky.
  leer:    print the TENDIDO values (x, fase, alto) the owner's save maps to; paste them into blender/mundo.py.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/colocar.py)" \
    -- guardar <out.blend (Windows)>
  /mnt/e/Blender/blender.exe -b "<saved.blend (Windows)>" --python "$(wslpath -w blender/colocar.py)" -- leer

Move the whole line (G X / G Y), or scale it in Z for the height. The line stays periodic: every mundo.PASO_POSTES from the y you set.
"""
import bpy, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]

if argv[0] == "leer":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mundo
    p = bpy.data.objects["w_postes"]
    t = dict(mundo.TENDIDO)
    print("TENDIDO", dict(x=round(t["x"] + p.location.x, 2), fase=round((t["fase"] + p.location.y) % mundo.PASO_POSTES, 2),
                          alto=round(t["alto"] * p.scale.z, 2)))
    sys.exit(0)

ESCENA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "escena.py")
src = open(ESCENA, encoding="utf8").read()
g = {"__file__": ESCENA, "__name__": "escena_colocar"}
exec(compile(src.rstrip()[: -len("main()")], ESCENA, "exec"), g)
s = g["build"]()
g["mundo_render"](s, "noche")
g["motor"](32, "noche")
sc = bpy.context.scene
sc.frame_set(0)
postes, cables = bpy.data.objects["w_postes"], bpy.data.objects["w_cables"]
mw = cables.matrix_world.copy()
cables.parent = postes
cables.matrix_world = mw
for o in s["mundo_b"]:
    o.hide_viewport = o.name == "w_niebla"  # the fog box would be a grey ceiling 81 m up in the solid view
    for m in o.modifiers:  # crowns in the viewport for context; grass and shrubs render-only (thousands of heavy instances)
        m.show_viewport = o.name.startswith("w_copa")
for o in bpy.data.objects:
    o.hide_select = o != postes
ys = [(o.matrix_world @ Vector(c)).y for o in s["camion"].children_recursive if o.type == "MESH" for c in o.bound_box]
CX, FRENTE = g["MUNDO"]["carril_x"], max(ys)
for nombre, pos, mira, lens in (("cam_esc4", (CX + 6.2, -0.3, 2.6), (CX, -0.3, 1.45), 24),       # props_placement.esc4
                                ("cam_esc6", (CX + 1.4, FRENTE + 6.5, 0.95), (CX + 0.1, FRENTE - 1.5, 1.2), 32)):  # .esc6
    cd = bpy.data.cameras.new(nombre)
    cd.lens, cd.sensor_fit, cd.clip_start, cd.clip_end = lens, "HORIZONTAL", 0.01, 3000
    co = bpy.data.objects.new(nombre, cd)
    sc.collection.objects.link(co)
    co.location = Vector(pos)
    co.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    co.hide_select = True
sc.camera = bpy.data.objects["cam_esc4"]
sc.render.resolution_x, sc.render.resolution_y = 960, 540
bpy.ops.wm.save_as_mainfile(filepath=argv[1])
print("GUARDADO", argv[1])

import bpy, sys, os
from mathutils import Vector
# Render each tie-down variant: -- <out_prefix> <cam...> (cam = name:px,py,pz:mx,my,mz:lens), toggling carga_red / carga_correas / carga_cable
exec(open(r"E:\tmp\mto-g63-nuevo\scripts\still_lib.py").read())
a = sys.argv[sys.argv.index("--") + 1:]
pre, cams = a[0], a[1:]
for v in ("red", "correas", "cable"):
    for n in ("red", "correas", "cable"):
        o = bpy.data.objects.get(f"carga_{n}")
        if o: o.hide_render = o.hide_viewport = (n != v)
    for c in cams:
        n, p, m, l = c.split(":")
        render(f"{pre}-{v}-{n}.png", p, m, l)

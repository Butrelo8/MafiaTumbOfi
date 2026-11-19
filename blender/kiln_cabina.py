"""Cab pieces the G63 model lacks (asset audit 2026-11-18), built with visual-lab's kiln-prop method: scripted parts in mm,
CC0 scans box-projected and mapped onto a palette, an overlap-first attachment check, a 512 px bake, a Draco + WebP GLB.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/kiln_cabina.py)" \
    -- <out dir (Windows)> [<1k scans dir (Windows)>]

Writes <out>/<piece>_final.glb (shipped, read by caja5.py's cabina_piezas) and <out>/<piece>_original.glb. Origins and axes,
for the placement in caja5.py:
  portavasos     defect 4  a single cup ring (the clear deck ahead of the shifter is 125 x 86 mm: one Ø 66 mm drink fits, not
                           two) with a floor and a brushed trim lip; origin under the floor's centre, +Z up. Rim 19 mm over
                           the deck, the bottle stands 3 mm up: 16 mm inside it (the audit's 10-15 mm route, one notch deeper)
  agarradera     defect 7  roof grab handle (ref r04): a 26 cm loop of 22 mm bar between two mounting pods; origin at the
                           pods' top face centre, hangs to -Z, runs along Y
  consola_techo  defect 7  the 6x6's overhead axle-lock / tyre-pressure panel (ref r04): a leather pod with three gauges, four
                           yellow and two red controls on a face tilted 25° down toward -Y (the cab); origin at its top centre
  panel_puerta   defect 8  door card insert (ref r02): a quilted pad with red stitching, a 3 cm armrest and a pull bar (the seats stand 2-4 cm off the doors); origin at
                           the back face's centre, the visible face toward +X (the left doors; the right ones turn 180° about Z)
"""
import bpy, math, os, sys

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
TEX = argv[1] if len(argv) > 1 else r"\\wsl.localhost\Ubuntu\home\black\cc-out\mto-asset-fixes\tex\1k"
KILN = r"\\wsl.localhost\Ubuntu\home\black\projects\visual-lab\blender\scripts\kiln_parts.py"
os.makedirs(OUT, exist_ok=True)
RES = 512


def k():
    K = {}
    exec(open(KILN, encoding="utf8").read(), K)
    return K


def paleta(nombre, scan, colores, rough=(0.4, 0.6), metal=0.0, escala=4.0, rango=(0.0, 1.0)):
    """kiln-prop § Materials: the scan's luminance stretched by `rango`, mapped onto [dark, mid, light] (linear); roughness
    from the scan's map remapped to `rough`; its normal map. Box projection on object coordinates (scale = tiles per metre)."""
    K = G["K"]
    m = bpy.data.materials.new(nombre); m.use_nodes = True; nt = m.node_tree; N = nt.nodes.new
    bs = nt.nodes["Principled BSDF"]; bs.inputs["Metallic"].default_value = metal
    tex = K["scanned"](nt, TEX, scan, escala)
    bw = N("ShaderNodeRGBToBW"); nt.links.new(tex("diff", False).outputs["Color"], bw.inputs["Color"])
    mr = N("ShaderNodeMapRange"); mr.clamp = True
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = rango
    nt.links.new(bw.outputs["Val"], mr.inputs["Value"])
    ramp = N("ShaderNodeValToRGB"); el = ramp.color_ramp.elements
    el[0].color, el[1].color = (*colores[0], 1), (*colores[2], 1)
    el.new(0.5).color = (*colores[1], 1)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    rr = N("ShaderNodeMapRange"); rr.inputs["To Min"].default_value, rr.inputs["To Max"].default_value = rough
    nt.links.new(tex("rough", True).outputs["Color"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], bs.inputs["Roughness"])
    nm = N("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.7
    nt.links.new(tex("nor_gl", True).outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bs.inputs["Normal"])
    return m


def liso(nombre, color, rough, metal=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*color, 1); bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    return m


G = {}
NEGRO = [(0.004, 0.004, 0.0045), (0.010, 0.0095, 0.0095), (0.024, 0.022, 0.021)]   # black nappa, as texturas_escena.py's piel
ALU = [(0.40, 0.40, 0.41), (0.55, 0.55, 0.56), (0.68, 0.68, 0.69)]
ACOLCHADO = [(0.005, 0.005, 0.0055), (0.012, 0.011, 0.011), (0.30, 0.012, 0.010)]  # quilted: the scan's pale stitches -> AMG red


def nueva():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    G["K"] = k()
    return G["K"]


def asignar(o, m):
    o.data.materials.clear(); o.data.materials.append(m)
    return o


def revisar_y_exportar(nombre, partes):
    K = G["K"]
    sueltas = K["floating"](partes)
    tris = sum(len(p.data.polygons) for p in partes)
    print(f"KILN {nombre} partes {len(partes)} caras {tris} sueltas {sueltas or 'ninguna'}", flush=True)
    out = K["export_glb"](partes, os.path.join(OUT, nombre), res=RES)
    print(f"KILN {nombre} exportado {out} {os.path.getsize(os.path.join(OUT, nombre + '_final.glb'))} B", flush=True)


# ---------------------------------------------------------------- portavasos (defect 4)
K = nueva()
piel, alu = paleta("piel", "Leather026", NEGRO, (0.38, 0.62)), paleta("alu", "Metal009", ALU, (0.22, 0.38), 1.0, 8.0)
copa = asignar(K["lathe"]("copa", [(0, 0), (41, 0), (41.5, 1), (41.5, 16), (37.5, 16), (37.0, 15), (37.0, 3), (0, 3)], 64), piel)
labio = asignar(K["lathe"]("labio", [(37.0, 15.5), (42.5, 15.5), (43.0, 16.5), (43.0, 19), (42.0, 19.5), (37.5, 19.5), (37.0, 19)], 64), alu)
revisar_y_exportar("portavasos", [copa, labio])

# ---------------------------------------------------------------- agarradera (defect 7)
K = nueva()
piel = paleta("piel", "Leather026", NEGRO, (0.38, 0.62))
pods = [asignar(K["box"](f"pod{s}", (-15, s * 130 - 20, -20), (15, s * 130 + 20, 0), bevel=4), piel) for s in (-1, 1)]
barra = asignar(K["wire"]("barra", [(0, -128, -12), (0, -122, -42), (0, -95, -58), (0, 0, -60), (0, 95, -58), (0, 122, -42), (0, 128, -12)], 11, sides=3), piel)
revisar_y_exportar("agarradera", pods + [barra])

# ---------------------------------------------------------------- consola_techo (defect 7, ref r04)
K = nueva()
piel, alu = paleta("piel", "Leather026", NEGRO, (0.38, 0.62)), paleta("alu", "Metal009", ALU, (0.22, 0.38), 1.0, 8.0)
amarillo, rojo = liso("amarillo", (0.75, 0.48, 0.02), 0.35), liso("rojo", (0.55, 0.02, 0.012), 0.35)
caratula = liso("caratula", (0.78, 0.78, 0.76), 0.25)
cuerpo = asignar(K["slab"]("cuerpo", [(45, 0), (-40, 0), (-40, -30), (-14, -66), (45, -66)], -170, 170, bevel=6, segs=3), piel)
# the face: the plane through (y -40, z -30) and (y -14, z -66), its normal toward -Y (the cab) and down; parts sit on it, sunk 2 mm
import mathutils
p0, p1 = mathutils.Vector((0, -40, -30)), mathutils.Vector((0, -14, -66))
d = (p1 - p0).normalized(); n = mathutils.Vector((0, d.z, -d.y)).normalized()  # outward: -Y and down
cen = (p0 + p1) / 2
giro = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
partes = [cuerpo]


def en_cara(o, x, s=0.0):
    o.matrix_world = mathutils.Matrix.Translation((cen + mathutils.Vector((x, 0, 0)) + d * s - n * 2) * 0.001) @ giro
    return o


for i, x in enumerate((-95, 0, 95)):
    partes.append(en_cara(asignar(K["lathe"](f"bisel{i}", [(0, 0), (22, 0), (22, 6), (19, 7), (19, 5), (0, 5)], 48), alu), x))
    partes.append(en_cara(asignar(K["lathe"](f"esfera{i}", [(0, 0), (19, 0), (19, 5.5), (0, 5.5)], 48), caratula), x))
for i, (x, s) in enumerate(((-140, -8), (-50, 8), (50, 8), (140, -8))):
    partes.append(en_cara(asignar(K["lathe"](f"perilla{i}", [(0, 0), (8, 0), (8, 13), (6.5, 15), (0, 15)], 32), amarillo), x, s))
for i, x in enumerate((-48, 48)):
    partes.append(en_cara(asignar(K["box"](f"palanca{i}", (-6, -9, 0), (6, 9, 18), bevel=2), rojo), x, -10))
revisar_y_exportar("consola_techo", partes)

# ---------------------------------------------------------------- panel_puerta (defect 8, ref r02)
K = nueva()
piel, acol = paleta("piel", "Leather026", NEGRO, (0.38, 0.62)), paleta("acolchado", "Leather034C", ACOLCHADO, (0.35, 0.6), escala=3.0, rango=(0.05, 0.6))
alu = paleta("alu", "Metal009", ALU, (0.22, 0.38), 1.0, 8.0)
inserto = asignar(K["box"]("inserto", (0, -260, -115), (10, 260, 115), bevel=4, segs=3), acol)
apoyabrazos = asignar(K["slab"]("apoyabrazos", [(-200, -150), (190, -150), (200, -170), (200, -200), (-200, -200)], 0, 30, bevel=6, segs=3), piel)
jaladera = asignar(K["wire"]("jaladera", [(4, 40, -122), (22, 60, -126), (25, 120, -128), (22, 175, -126), (4, 190, -122)], 6, sides=2), alu)
revisar_y_exportar("panel_puerta", [inserto, apoyabrazos, jaladera])

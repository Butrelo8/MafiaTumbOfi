"""Roof load, step 1 (2026-11-20): one downloaded model to a web-size .glb, centred on its box, upright, at real size.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b --python-exit-code 1 --python blender/carga_preparar.py \
    -- <unzipped downloads dir (Windows)> <textures dir from carga_texturas.py (Windows)> <out .glb (Windows)> <pieza> <tris>

  pieza  maleta    flight case 3d model.glb  (Tripo, 1.97 M tris, 4096 maps): decimated to <tris>, UV re-unwrapped, base colour / roughness-metal /
                   tangent normal baked from the full mesh at 1024 (Cycles, CPU).
         guitarra  guitar case 3d model.glb  (Tripo, 40 k tris, no image maps): decimated to <tris>, its colour attribute or flat colour kept.
         bolsa     Bag_FBX.zip's Bag.FBX     (8 k tris): decimated to <tris>, 1024 maps from carga_texturas.py.
         mochila   BackPack_Blend.blend      (32 k tris, six parts joined): the zip ships no textures, so it takes max_physical.zip's maps;
                   scaled so the body is 0.50 m tall.
Origin at the middle of the bounding box, z up, nothing rotated. The mesh is kept unrotated so two copies are the same bytes for dedup().
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

A = sys.argv[sys.argv.index("--") + 1:]
ENT, TEX, SAL, PIEZA, TRIS = A[0], A[1], A[2], A[3], int(A[4])
O = bpy.data.objects
sc = bpy.context.scene


def limpiar():
    for o in list(O):
        if o.name.split(".")[0] in ("Cube", "Light", "Camera") or o.name.startswith("Dots"):
            bpy.data.objects.remove(o, do_unlink=True)


def activar(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def aplicar_transformacion(o):
    activar(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def unir(objs):
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def decimar(o, tris):
    antes = sum(len(p.vertices) - 2 for p in o.data.polygons)
    activar(o)
    # weld first: the collapse works on shared vertices only
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY")
    bpy.ops.object.mode_set(mode="OBJECT")
    n = sum(len(p.vertices) - 2 for p in o.data.polygons)
    if n > tris:
        m = o.modifiers.new("dec", "DECIMATE")
        m.decimate_type = "COLLAPSE"
        m.ratio = tris / n
        m.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=m.name)
    print("PREPARAR decimar", antes, "->", sum(len(p.vertices) - 2 for p in o.data.polygons), flush=True)


def liso(o, grados=35):
    activar(o)
    bpy.ops.object.shade_smooth()
    o.data.set_sharp_from_angle(angle=math.radians(grados))


def centrar(o):
    vs = [v.co.copy() for v in o.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    c = (lo + hi) / 2
    o.data.transform(Matrix.Translation(-c))
    o.location = (0, 0, 0)
    print("PREPARAR dimensiones", [round(x, 4) for x in (hi - lo)], flush=True)


def material_web(nombre, base=None, rm=None, normal=None, color=(0.8, 0.8, 0.8, 1), rug=0.7, met=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    def img(ruta, no_color):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(ruta)
        n.image.colorspace_settings.name = "Non-Color" if no_color else "sRGB"
        return n
    if base:
        nt.links.new(img(base, False).outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = color
    if rm:
        s = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(img(rm, True).outputs["Color"], s.inputs["Color"])
        nt.links.new(s.outputs["Green"], p.inputs["Roughness"])
        nt.links.new(s.outputs["Blue"], p.inputs["Metallic"])
    else:
        p.inputs["Roughness"].default_value = rug
        p.inputs["Metallic"].default_value = met
    if normal:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(img(normal, True).outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m


def exportar(o):
    activar(o)
    bpy.ops.export_scene.gltf(filepath=SAL, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                              export_image_format="AUTO", export_draco_mesh_compression_enable=False, export_cameras=False, export_lights=False)
    print("PREPARAR guardado", SAL, os.path.getsize(SAL), "bytes", sum(len(p.vertices) - 2 for p in o.data.polygons), "tris", flush=True)


def hornear(alto, bajo, ruta_png_base):
    """Bake base colour, roughness+metal and the tangent normal of `alto` (the full mesh, its own material) onto `bajo` (decimated) at 1024."""
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 1
    sc.render.bake.margin = 10
    sc.render.bake.use_selected_to_active = True
    sc.render.bake.cage_extrusion = 0.012
    sc.render.bake.max_ray_distance = 0.03
    # new UVs on the low mesh
    activar(bajo)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")
    mh = alto.active_material
    nt = mh.node_tree
    salida = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    principled = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = {k: next(n for n in nt.nodes if n.type == "TEX_IMAGE" and k in n.image.name) for k in ("basecolor", "rm", "normal")}
    imgs = {}
    mb = bpy.data.materials.new("hornear")
    mb.use_nodes = True
    bajo.data.materials.clear()
    bajo.data.materials.append(mb)
    nodo = mb.node_tree.nodes.new("ShaderNodeTexImage")
    for k, no_color, tipo in (("base", False, "EMIT"), ("rm", True, "EMIT"), ("n", True, "NORMAL")):
        im = bpy.data.images.new("b_" + k, 1024, 1024, alpha=False)
        im.colorspace_settings.name = "Non-Color" if no_color else "sRGB"
        im.generated_color = (0.5, 0.5, 1, 1) if k == "n" else (0, 0, 0, 1)
        imgs[k] = im
        nodo.image = im
        mb.node_tree.nodes.active = nodo
        # the full mesh's emission carries the map to bake (the EMIT pass is the raw texel); the normal bake uses its own shading
        for l in list(nt.links):
            if l.to_node is salida:
                nt.links.remove(l)
        if tipo == "EMIT":
            em = nt.nodes.new("ShaderNodeEmission")
            nt.links.new(tex["basecolor" if k == "base" else "rm"].outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs[0], salida.inputs["Surface"])
        else:
            nt.links.new(principled.outputs[0], salida.inputs["Surface"])
        bpy.ops.object.select_all(action="DESELECT")
        alto.select_set(True)
        bajo.select_set(True)
        bpy.context.view_layer.objects.active = bajo
        bpy.ops.object.bake(type=tipo, normal_space="TANGENT", margin=10, use_selected_to_active=True,
                            cage_extrusion=0.012, max_ray_distance=0.03)
        carpeta = os.path.dirname(ruta_png_base)
        ruta = os.path.join(carpeta, f"{PIEZA}_{k}.png")
        im.filepath_raw = ruta
        im.file_format = "PNG"
        im.save()
        print("PREPARAR bake", k, ruta, flush=True)
    return {k: os.path.join(os.path.dirname(ruta_png_base), f"{PIEZA}_{k}.png") for k in ("base", "rm", "n")}


limpiar()
if PIEZA == "maleta":
    bpy.ops.import_scene.gltf(filepath=os.path.join(ENT, "flight", "flight.glb"))
    limpiar()
    alto = next(o for o in O if o.type == "MESH")
    aplicar_transformacion(alto)
    bajo = alto.copy()
    bajo.data = alto.data.copy()
    sc.collection.objects.link(bajo)
    decimar(bajo, TRIS)
    ruta_tex = os.path.join(TEX, PIEZA + "_x.png")
    imagenes = hornear(alto, bajo, ruta_tex)
    bpy.data.objects.remove(alto, do_unlink=True)
    bajo.data.materials.clear()
    bajo.data.materials.append(material_web("maleta", imagenes["base"], imagenes["rm"], imagenes["n"]))
    liso(bajo)
    centrar(bajo)
    bajo.name = bajo.data.name = "maleta"
    exportar(bajo)
elif PIEZA == "guitarra":
    bpy.ops.import_scene.gltf(filepath=os.path.join(ENT, "guitar", "guitar.glb"))
    limpiar()
    o = next(o for o in O if o.type == "MESH")
    aplicar_transformacion(o)
    me = o.data
    print("PREPARAR guitarra colores", [a.name for a in me.color_attributes], "materiales", [m.name for m in me.materials], flush=True)
    for m in me.materials:
        if m and m.use_nodes:
            for n in m.node_tree.nodes:
                print("PREPARAR guitarra nodo", n.type, n.name, {i.name: (tuple(i.default_value) if hasattr(i.default_value, "__len__") else i.default_value) for i in n.inputs if i.name in ("Base Color", "Roughness", "Metallic") and hasattr(i, "default_value")}, flush=True)
    decimar(o, TRIS)
    liso(o)
    centrar(o)
    o.name = o.data.name = "guitarra"
    exportar(o)
elif PIEZA == "bolsa":
    bpy.ops.import_scene.fbx(filepath=os.path.join(ENT, "bag", "Bag.FBX"))
    limpiar()
    o = next(o for o in O if o.type == "MESH")
    aplicar_transformacion(o)
    decimar(o, TRIS)
    o.data.materials.clear()
    o.data.materials.append(material_web("bolsa", os.path.join(TEX, "bolsa_base.jpg"), os.path.join(TEX, "bolsa_rm.jpg"), os.path.join(TEX, "bolsa_n.png")))
    liso(o)
    centrar(o)
    o.name = o.data.name = "bolsa"
    exportar(o)
elif PIEZA == "mochila":
    with bpy.data.libraries.load(os.path.join(ENT, "backpack", "BackPack_Blend.blend")) as (de, a_):
        a_.objects = [n for n in de.objects if n in ("Bag", "lit_low", "metalpiece_low", "String2_low", "String_low", "Strip2_low")]
    for o in a_.objects:
        sc.collection.objects.link(o)
    partes = [o for o in a_.objects if o]
    print("PREPARAR mochila partes", [(o.name, o.hide_viewport, o.hide_render) for o in partes], flush=True)
    for o in partes:
        aplicar_transformacion(o)
    cuerpo = next(o for o in partes if o.name == "Bag")
    k = 0.50 / (max(v.co.z for v in cuerpo.data.vertices) - min(v.co.z for v in cuerpo.data.vertices))
    o = unir(partes)
    o.data.transform(Matrix.Scale(k, 4))
    o.data.materials.clear()
    o.data.materials.append(material_web("mochila", os.path.join(TEX, "mochila_base.jpg"), os.path.join(TEX, "mochila_rm.jpg"), os.path.join(TEX, "mochila_n.png")))
    decimar(o, TRIS)
    liso(o)
    centrar(o)
    o.name = o.data.name = "mochila"
    exportar(o)
else:
    raise SystemExit("pieza?")

"""The owner's two instrument models (2026-11-18 17:05, owner-supplied Tripo GLBs: blender/assets/instrumentos/LICENSE.txt) made
ready for the bed: caja5.py's instrumento() links them from blender/assets/instrumentos/instrumentos.blend.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/instrumentos_prep.py)"

For each source (<name>.glb: the owner's file after blender/tripo/patch.py, metal zeroed and roughness median 0.3, lacquer):
  - loose parts farther than 1 cm from the largest one go (the guitar carries a floating music note from its concept image);
  - the principal axes put the neck on +Y (the headstock is the end farther from the centroid), the top on +Z (the side the
    source's front view, -Y, sees), the tail at y 0 and the back's lowest point at z 0, centred on x 0;
  - mesh `<name>` (full resolution, Cycles), `<name>_proxy` (decimated to ~4k tris, the placement's collision tests);
  - <name>_web.glb: decimated to WEB_TRIS, textures 1024 WebP, Draco (the live budget; not wired into vivo.py yet).
Real sizes are set where they are placed (caja5.INSTRUMENTOS lengths), not here: these are unit-agnostic up to scale.
"""
import bpy, bmesh, os
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

AQUI = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(AQUI, "assets", "instrumentos")
WEB_TRIS = 30000
FUENTES = {"guitarra": "guitarra.glb", "tololoche": "tololoche.glb"}


def importar(f):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    me = next(o for o in nuevos if o.type == "MESH")
    for o in nuevos:
        if o is not me:
            bpy.data.objects.remove(o)
    me.data.transform(me.matrix_world); me.matrix_world = Matrix()
    return me


def limpiar(o):
    """Delete loose parts farther than 1 cm (at the source's ~1 m scale) from the largest part."""
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    vis, partes = set(), []
    for v0 in bm.verts:
        if v0.index in vis:
            continue
        pila, p = [v0], []
        vis.add(v0.index)
        while pila:
            v = pila.pop(); p.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w.index not in vis:
                    vis.add(w.index); pila.append(w)
        partes.append(p)
    partes.sort(key=len, reverse=True)
    cos = [v.co.copy() for v in bm.verts]
    dentro, resto = [partes[0]], partes[1:]
    while resto:  # grow from the largest part: a part within 1 cm of what is kept joins (Tripo meshes are many loose shells)
        caras = [[v.index for v in f.verts] for p in dentro for f in {f for v in p for f in v.link_faces}]
        arbol = BVHTree.FromPolygons(cos, caras)
        entran = [p for p in resto if min(arbol.find_nearest(v.co)[3] for v in p[:: max(1, len(p) // 50)]) <= 0.01]
        if not entran:
            break
        dentro += entran
        resto = [p for p in resto if p not in entran]
    fuera = [v for p in resto for v in p]
    print(f"PREP {o.name}: {len(partes)} partes, se van {len(fuera)} vértices de partes sueltas", flush=True)
    bmesh.ops.delete(bm, geom=fuera, context="VERTS")
    bm.to_mesh(o.data); bm.free()


def alinear(o):
    V = np.array([v.co[:] for v in o.data.vertices])
    c = V.mean(0)
    w, ejes = np.linalg.eigh(np.cov((V - c).T))
    largo, fondo = ejes[:, 2], ejes[:, 0]  # largest spread: the neck; smallest: the body's depth
    t = (V - c) @ largo
    if abs(t.min()) > abs(t.max()):  # the headstock is the end farther from the centroid
        largo = -largo
    if fondo @ np.array([0, -1, 0]) < 0:  # the top faces the source's front camera (-Y)
        fondo = -fondo
    ancho = np.cross(largo, fondo)
    R = Matrix([list(ancho), list(largo), list(fondo)])  # rows: new x, y, z
    o.data.transform(R.to_4x4() @ Matrix.Translation(Vector(-c)))
    V = np.array([v.co[:] for v in o.data.vertices])
    o.data.transform(Matrix.Translation((-(V[:, 0].min() + V[:, 0].max()) / 2, -V[:, 1].min(), -V[:, 2].min())))
    V = np.array([v.co[:] for v in o.data.vertices])
    print(f"PREP {o.name}: caja x {np.ptp(V[:, 0]):.3f} y (cuello) {np.ptp(V[:, 1]):.3f} z (fondo) {np.ptp(V[:, 2]):.3f}", flush=True)


def diezmada(o, nombre, tris):
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nombre
    bpy.context.scene.collection.objects.link(c)
    n = sum(len(p.vertices) - 2 for p in c.data.polygons)
    d = c.modifiers.new("d", "DECIMATE"); d.ratio = min(1.0, tris / n)
    bpy.context.view_layer.objects.active = c
    bpy.ops.object.modifier_apply(modifier="d")
    return c


bpy.ops.wm.read_factory_settings(use_empty=True)
hechos = []
for nombre, f in FUENTES.items():
    o = importar(os.path.join(DIR, f)); o.name = o.data.name = nombre
    limpiar(o)
    alinear(o)
    for p in o.data.polygons:
        p.use_smooth = True
    px = diezmada(o, nombre + "_proxy", 4000)
    web = diezmada(o, nombre + "_web", WEB_TRIS)
    for im in {n.image for m in web.data.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}:
        pass  # the export below resizes copies; the full-res source keeps its 4k maps
    hechos.append((o, px, web))
# web GLBs: each alone, its images scaled to 1024 on a copy of the material
for o, px, web in hechos:
    m = web.data.materials[0].copy(); web.data.materials[0] = m
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            im = n.image.copy(); im.scale(1024, 1024); n.image = im
    bpy.ops.object.select_all(action="DESELECT"); web.select_set(True); bpy.context.view_layer.objects.active = web
    ruta = os.path.join(DIR, o.name + "_web.glb")
    bpy.ops.export_scene.gltf(filepath=ruta, export_format="GLB", use_selection=True, export_image_format="WEBP",
                              export_draco_mesh_compression_enable=True)
    print(f"PREP {o.name}_web.glb {os.path.getsize(ruta)} B, {sum(len(p.vertices) - 2 for p in web.data.polygons)} tris", flush=True)
    bpy.data.objects.remove(web)
for o, px, web in hechos:
    px.data.materials.clear()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DIR, "instrumentos.blend"))
print("PREP guardado", os.path.join(DIR, "instrumentos.blend"), flush=True)

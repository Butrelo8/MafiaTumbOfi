"""The G63's panels before the common decimate (owner 2026-11-19: "triangles at the top of the truck are showing" live): the
model is triangle soup, its faces barely share vertices, so the quadric collapse could not follow the surface and the roof's
ribs and panel lines fell into big flat triangles. soldar(o) welds coincident corners (0.1 mm in world units) so the decimate
works on one connected surface; with marcar it also marks edges sharper than 30 deg before the decimate. afilar(o) instead
marks them after the decimate (a Smooth by Angle modifier stacked on top), so the creases follow the decimated faces.
Renders: /mnt/e/tmp/mto-cabina-restos/techo/.
"""
import bpy, bmesh, math


def soldar(o, dist=1e-4, angulo=30.0, marcar=True):
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    antes = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist / max(o.matrix_world.to_scale()))
    for f in bm.faces:
        f.smooth = True
    lim = math.radians(angulo)
    for e in bm.edges:
        e.smooth = not marcar or not (len(e.link_faces) != 2 or e.calc_face_angle(0.0) > lim)
    bm.to_mesh(me)
    bm.free()
    if me.has_custom_normals:  # the importer's split normals would override the sharp edges
        bpy.context.view_layer.objects.active = o
        with bpy.context.temp_override(object=o, active_object=o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    return antes, len(me.vertices)


def razones(objs, r, mas):
    """Per-object decimate ratios: `mas` {object name: weight} gives a mesh a bigger share of the same total (Fable 2026-11-19:
    the roof paint Material3.004 at 3x); the others scale down so the sum of the ratio x tris stays what one ratio `r` gave."""
    t = {o: len(o.data.polygons) for o in objs}
    w = {o: mas.get(o.name, 1.0) for o in objs}
    k = sum(t.values()) / sum(t[o] * w[o] for o in objs)
    return {o: min(1.0, r * w[o] * k) for o in objs}


def afilar(o, angulo=30.0):
    """Edges sharper than `angulo` turn sharp on the evaluated mesh, after every modifier already on `o` (the decimate)."""
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angulo))
    return o.modifiers[-1].name

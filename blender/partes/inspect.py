# inspect.py: objects, bones (ORG/DEF heads at rest) and mesh stats of a rig blend.
import bpy
for o in bpy.data.objects:
    print("OBJ", o.name, o.type, o.parent.name if o.parent else None, [m.type for m in getattr(o, "modifiers", [])],
          len(o.data.polygons) if o.type == "MESH" else "", tuple(round(x, 3) for x in o.location), tuple(round(x, 3) for x in o.rotation_euler))
rig = bpy.data.objects["rig"]
for b in rig.data.bones:
    if b.name.startswith(("ORG-", "DEF-")):
        print("BONE", b.name, b.parent.name if b.parent else None, tuple(round(x, 3) for x in b.head_local), tuple(round(x, 3) for x in b.tail_local))
for o in bpy.data.objects:
    if o.type == "MESH":
        me = o.data; print("MESH", o.name, len(me.vertices), len(me.polygons), [m.name for m in me.materials], len(o.vertex_groups))
        for m in me.materials:
            if m and m.node_tree: print("  NODES", m.name, [(n.type, getattr(n, 'image', None) and n.image.name) for n in m.node_tree.nodes])
a = rig.animation_data.action if rig.animation_data else None
print("ACTION", a and a.name, a and tuple(a.frame_range), bpy.context.scene.frame_start, bpy.context.scene.frame_end, bpy.context.scene.render.fps)

# weights_of.py: which vertex groups drive a blend's Body (ours: DEF-*; Mixamo's: mixamorig:*), and its modifiers.
import bpy
b = bpy.data.objects["Body"]; g = [x.name for x in b.vertex_groups]
print("@@W", "groups", len(g), "DEF", sum(n.startswith("DEF-") for n in g), "mixamorig", sum(n.startswith("mixamorig") for n in g),
      "mods", [(m.type, getattr(m, "object", None) and m.object.name) for m in b.modifiers], "proxy", "Body_proxy" in bpy.data.objects)

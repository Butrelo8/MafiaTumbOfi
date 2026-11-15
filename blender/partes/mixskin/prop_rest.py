# prop_rest.py: an in-hand prop keeps the owner's placement only for the key gesture. Outside the ease window it takes
# a rest placement in the same hand space (props_fit.py's fit: base + rot, the one that clears the body while the hand
# rests); in the window it eases between the two with sip_bake.py's smoothstep weights (location lerp, rotation slerp),
# one key per frame on the prop's matrix_basis (it is parented to the "<prop>_hand" empty on the bone).
#   $B -b <sip blend> --python prop_rest.py -- <prop> <fit.json (Windows)> <fit key, e.g. bottle> <in0-in1> <out0-out1> <out.blend (Windows)>
import bpy, sys, json
from mathutils import Matrix, Vector
a = sys.argv[sys.argv.index("--") + 1:]; p = bpy.data.objects[a[0]]; fit = json.load(open(a[1]))[a[2]]
i0, i1 = map(int, a[3].split("-")); o0, o1 = map(int, a[4].split("-")); out = a[5]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]
f0, f1 = map(int, mx.animation_data.nla_tracks["clip"].strips[0].action.frame_range)
owner = p.matrix_basis.copy(); e = p.parent; sc.frame_set(f0); bpy.context.view_layer.update()
# the empty rides the bone rigidly but not at its head frame (place_build's matrix_world set landed off it): measure it
off = (mx.matrix_world @ mx.pose.bones[e.parent_bone].matrix).inverted() @ e.matrix_world
rest = off.inverted() @ Matrix.Translation(fit["base"]) @ Matrix(fit["rot"]).to_4x4()
lo, ro, so = owner.decompose(); lr, rr, sr = rest.decompose()
def ss(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
p.rotation_mode = "QUATERNION"
for f in range(f0, f1 + 1):
    w = ss((f - i0) / (i1 - i0)) * (1 - ss((f - o0) / (o1 - o0)))
    p.location = lr.lerp(lo, w); p.rotation_quaternion = rr.slerp(ro, w); p.scale = sr.lerp(so, w)
    for dp in ("location", "rotation_quaternion", "scale"): p.keyframe_insert(dp, frame=f)
sc.frame_set(305); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@PROPREST@@", p.name, [f0, f1], "owner", [round(x, 3) for x in lo], "rest", [round(x, 3) for x in lr], flush=True)

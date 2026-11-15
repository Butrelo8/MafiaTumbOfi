# act.py: choose what drives the rig of a parts blend and save it, so covers.py / joints.py / the clip scripts sample it.
#   $B -b <blend> --python act.py -- <out.blend (Windows)> <action>            one action, frames 1..its end
#   $B -b <blend> --python act.py -- <out.blend (Windows)> union <a> <b> [gap]  NLA: <a> from frame 1, <b> after it + gap
# (default 10 frames), no active action: the union of two clips for covers.py FRAMES=1-<end>:s.
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
out, mode = a[0], a[1]
sc = bpy.context.scene; rig = bpy.data.objects["rig"]; ad = rig.animation_data or rig.animation_data_create()
for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
if mode == "union":
    A, Bc = bpy.data.actions[a[2]], bpy.data.actions[a[3]]; gap = int(a[4]) if len(a) > 4 else 10
    ad.action = None; end = 0
    for act in (A, Bc):
        tr = ad.nla_tracks.new(); s0 = 1 if act is A else end + gap
        st = tr.strips.new(act.name, s0, act); st.extrapolation = "NOTHING" if act is A else "HOLD_FORWARD"
        if act is A: st.extrapolation = "HOLD"
        end = int(st.frame_end)
    sc.frame_start, sc.frame_end = 1, end
else:
    act = bpy.data.actions[mode]; ad.action = act
    sc.frame_start, sc.frame_end = 1, int(act.frame_range[1])
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@ACT@@", mode, sc.frame_start, sc.frame_end, flush=True)

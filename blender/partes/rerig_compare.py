# rerig_compare.py label=deform.json ...: one column per rig, from deform.py's output on the same clip.
# Rows: the hip, knee, shoulder and elbow regions as dmm (largest edge-length change at a vertex, mm; p99 / max),
# the knee and elbow flex peaks, wrong-way frames and forearm twist. Lower dmm = the mesh bends with less stretch.
import json, sys
cols = [(a.split("=", 1)[0], json.load(open(a.split("=", 1)[1]))) for a in sys.argv[1:]]
REG = [("hip", "DEF-pelvis"), ("thigh", "DEF-thigh"), ("knee/shin", "DEF-shin"), ("shoulder", "DEF-shoulder"),
       ("upper arm", "DEF-upper_arm"), ("elbow/forearm", "DEF-forearm")]
print(f"{'row':26s}" + "".join(f"{l:>22s}" for l, _ in cols))
for name, b in REG:
    for s in (".L", ".R"):
        cell = lambda d: (lambda r: f"{r['dmm_p99']:.1f} / {r['dmm_max']:.1f}" if r else "-")(d["stretch"].get(b + s))
        print(f"{name + s + ' dmm p99/max':26s}" + "".join(f"{cell(d):>22s}" for _, d in cols))
for k in ("knee.L", "knee.R", "elbow.L", "elbow.R", "twist.L", "twist.R", "elbow.L_wrong_frames", "elbow.R_wrong_frames"):
    print(f"{k:26s}" + "".join(f"{str(d['joints_max'].get(k, 0)):>22s}" for _, d in cols))
print(f"{'deform.py fails':26s}" + "".join(f"{len(d['fails']):>22d}" for _, d in cols))

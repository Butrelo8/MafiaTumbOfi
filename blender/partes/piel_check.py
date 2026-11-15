# piel_check.py <covers.json>: no clothing cut shows skin. A side whose rim texels are mostly cloth (dark + white > 50 %)
# must have a non-skin cap colour. Collar is hand-set (neck skin on the head side, covers.py FORCE). Exit 1 on a failure.
import sys, json
d = json.load(open(sys.argv[1]))["joints"]; bad = []
for j, v in d.items():
    for s in ("child", "parent"):
        f = v[s]["rim_class_frac"]; cloth = f["dark"] + f["white"]
        print(f"{j:11s} {s:6s} cap {v[s]['colour']:5s} rim dark {f['dark']:.2f} skin {f['skin']:.2f} white {f['white']:.2f}")
        if v[s]["colour"] == "skin" and cloth > 0.5 and not j.startswith("collar"): bad.append((j, s))
print("skin caps on clothing cuts:", bad or "none"); sys.exit(1 if bad else 0)

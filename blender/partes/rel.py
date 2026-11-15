# rel.py <bones.json>: per joint, the child's rotation relative to its parent across the idle (from rest), and how far
# the child's pivot drifts in the parent's frame. Tells which rigid part follows which bone and how much a cut must hide.
import json, numpy as np, sys
d = json.load(open(sys.argv[1])); R = {k: np.array(v) for k, v in d["rest"].items()}
pairs = [("ORG-spine.001", "ORG-spine"), ("ORG-spine.002", "ORG-spine"), ("ORG-spine.003", "ORG-spine"),
         ("ORG-spine.003", "ORG-spine.002"), ("ORG-spine.004", "ORG-spine.003"), ("ORG-spine.006", "ORG-spine.003"),
         ("ORG-spine.006", "ORG-spine.004"), ("ORG-shoulder.L", "ORG-spine.003"), ("ORG-upper_arm.L", "ORG-spine.003"),
         ("ORG-upper_arm.R", "ORG-spine.003"), ("ORG-forearm.L", "ORG-upper_arm.L"), ("ORG-forearm.R", "ORG-upper_arm.R"),
         ("ORG-hand.L", "ORG-forearm.L"), ("ORG-hand.R", "ORG-forearm.R"), ("ORG-thigh.L", "ORG-spine"),
         ("ORG-thigh.R", "ORG-spine"), ("ORG-shin.L", "ORG-thigh.L"), ("ORG-shin.R", "ORG-thigh.R"),
         ("ORG-foot.L", "ORG-shin.L"), ("ORG-foot.R", "ORG-shin.R")]
for c, p in pairs:
    angs, drift = [], []
    for f, P in d["pose"].items():
        Pc, Pp = np.array(P[c]), np.array(P[p])
        A = np.linalg.inv(Pp) @ Pc; B = np.linalg.inv(R[p]) @ R[c]
        D = A[:3, :3] @ np.linalg.inv(B[:3, :3])
        angs.append(np.degrees(np.arccos(np.clip((np.trace(D) - 1) / 2, -1, 1))))
        drift.append(np.linalg.norm(A[:3, 3] - B[:3, 3]) * 1000)
    sc = np.linalg.norm(Pc[:3, :3], axis=0)
    print(f"{c:18s} vs {p:16s} rot max {max(angs):5.1f} p50 {np.median(angs):5.1f} deg | pivot drift max {max(drift):5.1f} mm | scale {sc.round(3)}")

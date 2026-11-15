# tabla.py <label=joints.json>...: one markdown row per joint, max seam (and the old one-sided gap in brackets) per run.
import sys, json
runs = [a.split("=", 1) for a in sys.argv[1:]]; R = [(l, json.load(open(p))) for l, p in runs]
print("| joint | " + " | ".join(l for l, _ in R) + " |"); print("|---" * (len(R) + 1) + "|")
for j in R[0][1]["joints"]:
    cells = []
    for _, d in R:
        x = d["joints"].get(j, {}); cells.append(f"{x.get('seam_max_mm', '–')} ({x.get('gap_max_mm', '–')})" if x else "–")
    print(f"| {j} | " + " | ".join(cells) + " |")
for l, d in R:
    print(f"{l}: rest seam max {max(x['rest_gap_pen_mm'][2] if len(x['rest_gap_pen_mm']) > 2 else 0 for x in d['joints'].values())}, "
          f"rigid_dev {max(d.get('rigid_dev_max', {0: 0}).values())}, kiln {d.get('kiln_floating_f70')}")

# pen_table.py: pen_fix.py json(s) as a table: per contact the max depth (mm, frame; pen.py's nearest-face one and the outer-skin one), frames over 1 mm, frames with any
# vertex inside; per grip the gap range and the frames over 3 mm. Contacts that never go inside are listed as one line.
#   uv run -q python -I pen_table.py <pen_fix.json> ...
import sys, json
for p in sys.argv[1:]:
    d = json.load(open(p)); print(f"== {p}  frames {d['range']} step {d['step']}")
    clean = []
    for k, v in d["pen"].items():
        if "gap_min" in v: print(f"  {k:32s} gap {v['gap_min']:7.2f} .. {v['gap_max']:6.2f} mm   frames gap>3mm {v['n_gap_over_3']}")
        elif v["max_mm"] > 0: print(f"  {k:32s} max {v['max_mm']:6.2f} mm @f{v['max_frame']:<4d} outer {v.get('max_outer_mm', v['max_mm']):6.2f} mm @f{v.get('max_outer_frame', v['max_frame']):<4d} frames>1mm {v['n_frames_over_1mm']:4d}   any inside {v['n_frames_any_inside']}")
        else: clean.append(k)
    if clean: print("  0 inside:", ", ".join(clean))

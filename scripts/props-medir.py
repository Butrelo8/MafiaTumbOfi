"""Rules 1-4 of docs/design/props-placement/reglas.md as numbers, from the probe that blender/props_placement.py writes per still
(medidas-<still>.json + <still>-id.npy, at 1/5 size) and the rendered <still>.png.

  uv run -q --with numpy --with pillow python -I scripts/props-medir.py <dir with the stills and probes> [out.tsv]

Prints one row per still: zone cover % (rule 1, ≤ 2), new props over 0.1 % of the frame or lit (rule 2), how many read (rule 3,
budget 3 for scenes 1 and 6, 4 for 2 and 4), and the zone's total light (linear luminance summed over its pixels) against the strongest lit prop's (rule 4,
the zone must win; scene 6 compares the plate, the headlights excluded). A p95 version failed every still by construction: an
emissive bulb clips to 1.0, so area has to count. Exit 0 always: the table is the result, PASS/FAIL per column.
"""
import json, re, sys
from pathlib import Path

import numpy as np
from PIL import Image

d = Path(sys.argv[1])
salida = Path(sys.argv[2]) if len(sys.argv) > 2 else d / "medidas.tsv"
PRESUPUESTO = {"1": 3, "6": 3, "2": 4, "4": 4}
LEE = 0.1  # % of the frame

filas = ["still\tescena\tzona_cubierta_%\tr1\tprops_que_leen\tr3\tzona_luz\tprop_luz\tr4\tdetalle_props"]
for f in sorted(d.glob("medidas-*.json")):
    m = json.loads(f.read_text(encoding="utf8"))
    nombre, esc = m["still"], m["escena"]
    png = d / f"{nombre}.png"
    ids = np.load(d / f"{nombre}-id.npy")
    inv = {v: k for k, v in m["leyenda"].items()}
    cubierta = max((z["pct"] for z in m["zonas"].values()), default=0.0)  # rule 1 protects every zone, headlights included
    leen = sorted(p for p, v in m["props"].items() if v["pct_cuadro"] >= LEE or (v["luminoso"] and v["px"] > 0))
    zp95 = lp95 = float("nan")  # names kept; values are total light (sum of linear luminance over the pixels)
    if png.exists():
        im = Image.open(png).convert("RGB").resize((m["W"], m["H"]), Image.BOX)
        a = np.asarray(im, np.float32) / 255
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        Y = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        zona_ids = [i for i, k in inv.items() if k.startswith("zona:") and not (esc == "6" and k == "zona:faros")]
        zm = np.isin(ids, zona_ids)
        if zm.any():
            zp95 = float(Y[zm].sum())
        luz = [i for i, k in inv.items() if k.startswith("prop:") and m["props"][k[5:]]["luminoso"]]
        vals = [float(Y[ids == i].sum()) for i in luz if (ids == i).sum() >= 1]
        lp95 = max(vals) if vals else float("nan")
    r1 = "PASS" if cubierta <= 2 else "FAIL"
    r3 = "PASS" if len(leen) <= PRESUPUESTO[esc] else "FAIL"
    r4 = "n/a" if np.isnan(lp95) or np.isnan(zp95) else ("PASS" if zp95 > lp95 else "FAIL")
    if not re.match(r"pp\d|pv-\d", nombre):  # a close-up shows a prop; the rules hold at the scene camera
        r1 = r3 = r4 = "detalle"
    det = " ".join(f"{p}:{v['pct_cuadro']}%{'*' if v['luminoso'] else ''}" for p, v in sorted(m["props"].items()))
    filas.append(f"{nombre}\t{esc}\t{cubierta}\t{r1}\t{len(leen)} ({','.join(leen)})\t{r3}\t{zp95:.1f}\t{lp95:.1f}\t{r4}\t{det}")

salida.write_text("\n".join(filas) + "\n", encoding="utf8")
print("\n".join(filas))

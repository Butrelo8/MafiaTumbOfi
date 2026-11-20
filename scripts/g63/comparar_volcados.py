"""Compares two dumps of blender/vivo_reparto_volcar.py (the round trip of a placement file): every bone of the four rigs
(armature-space matrices: head distance in m, rotation in degrees), the rigs' world matrices, the roof load (k3_* world matrices) and the bottle.
  python3 scripts/g63/comparar_volcados.py <his dump> <new dump>      exit 1 when a bone head is off by more than 0.0001 m
"""
import json, math, sys

a, b = (json.load(open(p, encoding="utf8")) for p in sys.argv[1:3])


def t(m):
    return [m[i][3] for i in range(3)]


def d(p, q):
    return math.dist(p, q)


def giro(m, n):
    """Angle (deg) of the rotation taking m's 3x3 to n's (scale left in: his poses carry scaled bones, so normalise columns)."""
    def col(x, j):
        v = [x[i][j] for i in range(3)]
        s = math.sqrt(sum(c * c for c in v)) or 1.0
        return [c / s for c in v]
    r = [[sum(col(n, k)[i] * col(m, k)[j] for k in range(3)) for j in range(3)] for i in range(3)]
    return math.degrees(math.acos(max(-1.0, min(1.0, (r[0][0] + r[1][1] + r[2][2] - 1) / 2))))


peor = 0.0
for q in ("manager", "hector", "alejandro", "diego"):
    ra, rb = a["rigs"][q], b["rigs"][q]
    dh = max(d(t(ra["huesos"][k]), t(rb["huesos"][k])) for k in ra["huesos"])
    dg = max(giro(ra["huesos"][k], rb["huesos"][k]) for k in ra["huesos"])
    dm = d(t(ra["mundo"]), t(rb["mundo"]))
    worst = max(ra["huesos"], key=lambda k: d(t(ra["huesos"][k]), t(rb["huesos"][k])))
    print(f"{q:10s} {len(ra['huesos'])} huesos: cabeza max {dh:.4f} m ({worst.replace('mixamorig:', '')}), giro max {dg:.3f} deg, rig {dm:.4f} m")
    peor = max(peor, dh, dm)
for q, lados in a.get("manos", {}).items():
    for lado, ma in lados.items():
        mb = b["manos"][q][lado]
        if d(ma["muneca"], mb["muneca"]) > 1e-4 or d(ma["codo"], mb["codo"]) > 1e-4:
            print(f"   mano {lado} de {q}: muñeca {d(ma['muneca'], mb['muneca']):.4f} m, codo {d(ma['codo'], mb['codo']):.4f} m; control {mb['control']} a "
                  f"{d(t(mb['control_mundo']), mb['muneca']) if mb['control_mundo'] else float('nan'):.4f} m de la muñeca")
pa, pb = a.get("props", {}), b.get("props", {})
for k in sorted(pa):
    print(f"{k:12s} prop {d(t(pa[k]['mundo']), t(pb[k]['mundo'])):.4f} m, giro {giro(pa[k]['mundo'], pb[k]['mundo']):.3f} deg")
    peor = max(peor, d(t(pa[k]["mundo"]), t(pb[k]["mundo"])))
for k, o in a["objetos"].items():
    if k in b["objetos"] and k.startswith("k5_bebida"):
        print(f"{k:24s} {d(t(o['mundo']), t(b['objetos'][k]['mundo'])):.4f} m")
print("MAX %.5f m" % peor)
sys.exit(1 if peor > 1e-4 else 0)

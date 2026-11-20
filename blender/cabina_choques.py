"""Counts old G63 cab faces that clash with the new cab parts (owner 2026-11-19 16:56: old seat bits float above and beside the
Tripo seats; the centre console and the dash under the screen clip). Evaluated meshes (decimate included), world space.

  atraviesan  old faces whose triangles cross a new part's surface (BVHTree.overlap)
  dentro      old faces whose centre lies inside a new part's closed volume (ray parity, 3 axes, majority)
  flotan      old faces seen first from the live cameras (stops 1-4, the four member shots, the cab close-ups) whose centre lies in
              the old seat / console space (cabina_tripo.zona_vieja, the floor aside): leftovers of the removed seats and console
  asoman      from the outside cameras (stop 2, the three-quarter, side and top views): first hits on interior materials
              (cab_*, piel_*, tripo_*) above the belt line (z > 1.5): the cab poking through the roof or pillars

Standalone, on a montado blend:
  GPU=0 ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <vivo-montado.blend> --python-exit-code 1 \
    --python "$(wslpath -w blender/cabina_choques.py)" -- <vivo.json (Windows)> <out.json (Windows)> [borrar] [diezmar=0.0985]
  ("borrar" first runs cabina_tripo.borrar_viejos on the file: prototypes a stricter removal on an already-cut cab;
  "diezmar=r" adds the exporter's common decimate at ratio r)
The exporter calls medir() itself with CABINA_CHOQUES=<out prefix> (before and after the decimate).
"""
import bpy, json, math, os, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cabina_tripo as CT

NUEVAS = ("tripo_asiento_izq", "tripo_asiento_der", "tripo_consola", "u_consola_techo", "u_pantalla-comand", "u_bisel")
VIDRIO = ("vidrio", "vidrio_falso", "mica")
INTERIOR = ("cab_", "piel_", "tripo_")
# close-ups in Blender axes (scripts/vivo-tomas.mjs VISTAS): [camera, look-at, lens]
CERCA = {"cabina_atras": ([1.72, -0.2, 2.05], [1.72, 0.9, 1.35], 20.0), "hector_botella": ([2.45, 1.3, 1.95], [2.15, 0.87, 1.57], 20.0),
         "manco_pies": ([1.78, 1.02, 1.5], [1.3, 0.8, 1.13], 20.0), "asiento_izq_lado": ([1.30, 1.25, 2.02], [1.33, 0.4, 1.4], 20.0),
         "asiento_der_lado": ([2.10, 1.25, 2.02], [2.11, 0.4, 1.4], 20.0), "tablero": ([1.72, 0.35, 1.75], [1.72, 1.2, 1.45], 22.0)}
FUERA = {"frente34": ([-1.6, 7.2, 1.7], [1.72, 2.2, 1.25], 20.0), "lado_izq": ([-3.6, 1.6, 1.55], [0.95, 1.0, 1.28], 20.0),
         "lado_der": ([7.0, 1.6, 1.55], [2.5, 1.0, 1.28], 20.0), "tras34": ([-1.8, -7.6, 3.5], [1.72, -2.1, 1.45], 20.0),
         "caja_arriba": ([1.72, -4.6, 4.2], [1.72, -2.0, 1.4], 20.0), "techo": ([1.72, -1.2, 4.6], [1.72, 0.8, 2.1], 24.0)}


def malla(o, dg):
    """World-space verts and triangles of the evaluated mesh, plus each triangle's polygon index and material name."""
    e = o.evaluated_get(dg)
    me = e.to_mesh()
    me.calc_loop_triangles()
    v = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", v)
    W = np.array(e.matrix_world)
    v = v.reshape(-1, 3) @ W[:3, :3].T + W[:3, 3]
    t = np.empty(len(me.loop_triangles) * 3, dtype=np.int64)
    me.loop_triangles.foreach_get("vertices", t)
    p = np.empty(len(me.loop_triangles), dtype=np.int64)
    me.loop_triangles.foreach_get("polygon_index", p)
    mi = np.empty(len(me.polygons), dtype=np.int64)
    me.polygons.foreach_get("material_index", mi)
    mats = [(m.name.split(".")[0] if m else "") for m in me.materials] or [""]
    tm = [mats[min(mi[i], len(mats) - 1)] for i in p]
    e.to_mesh_clear()
    return v, t.reshape(-1, 3), p, tm


def viejas(sc):
    cam = bpy.data.objects["camion"]
    return [o for o in [cam, *cam.children_recursive] if o.type == "MESH" and o.name.startswith("Material") and o.data.polygons
            and not o.hide_render and o.name not in CT.FUERA_OBJ[1:]]


def nuevas(ocultas=False):
    """The cab's copy of each new part (stale copies sit at the origin); render-hidden ones too with `ocultas` (a montado blend
    hides the per-option dressing that the exporter shows)."""
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or (o.hide_render and not ocultas) or not o.data.polygons:
            continue
        mats = [m.name for m in o.data.materials if m]
        if not (o.name.startswith(NUEVAS) or any(m.startswith(NUEVAS) for m in mats)):
            continue
        c = sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()) / 8
        if 0.9 < c.x < 2.6 and -0.5 < c.y < 2.0 and c.z > 0.8:
            out.append(o)
    return out


def camaras(js):
    d = json.load(open(js, encoding="utf8"))
    dentro = {f"parada{k + 1}": (c["pos"], c["mira"], c["lens"]) for k, c in enumerate(d["camaras"][:4])}
    dentro.update({f"banda{k}": (c["pos"], c["mira"], c["lens"]) for k, c in enumerate(d["banda"])})
    dentro.update(CERCA)
    fuera = dict(FUERA, parada2=dentro.pop("parada2"), parada3=dentro.pop("parada3"))
    return dentro, fuera


def rayos(pos, mira, lens, w=360, h=225):
    pos, f = np.array(pos, float), np.array(mira, float) - np.array(pos, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    tx = 18.0 / lens  # three.js page: 36 mm film, horizontal
    xs, ys = np.meshgrid(np.linspace(-tx, tx, w), np.linspace(-tx * h / w, tx * h / w, h))
    d = f + xs[..., None] * r + ys[..., None] * u
    return pos, (d / np.linalg.norm(d, axis=-1, keepdims=True)).reshape(-1, 3)


def medir(js, etiqueta="", ocultas=False):
    dg = bpy.context.evaluated_depsgraph_get()
    V, N = viejas(bpy.context.scene), nuevas(ocultas)
    print("CHOQUES", etiqueta, "viejas", [o.name for o in V], "nuevas", [o.name for o in N], flush=True)
    todo_v, todo_t, quien = [], [], []  # one BVH of everything, for the camera rays
    base = 0
    datos = {}
    for o in V + N:
        v, t, p, tm = malla(o, dg)
        datos[o.name] = (v, t, p, tm)
        todo_v.append(v); todo_t.append(t + base); base += len(v)
        quien += [(o.name, int(p[i]), tm[i]) for i in range(len(t))]
    arbol = BVHTree.FromPolygons(np.concatenate(todo_v).tolist(), np.concatenate(todo_t).tolist(), all_triangles=True)
    arboles_n = {o.name: BVHTree.FromPolygons(datos[o.name][0].tolist(), datos[o.name][1].tolist(), all_triangles=True) for o in N}
    res = {"atraviesan": {}, "dentro": {}, "flotan": {}, "asoman": {}, "caras": {}}

    def sumar(clave, nuevo, viejo, mat, cara):
        k = f"{nuevo}|{viejo}|{mat}"
        res[clave][k] = res[clave].get(k, 0) + 1
        res["caras"].setdefault(clave, set()).add((viejo, cara))

    for o in V:
        v, t, p, tm = datos[o.name]
        lo_o, hi_o = v.min(0), v.max(0)
        a_v = None
        for n in N:
            nv = datos[n.name][0]
            lo, hi = nv.min(0) - 0.01, nv.max(0) + 0.01
            if np.any(hi < lo_o) or np.any(lo > hi_o):
                continue
            if a_v is None:
                a_v = BVHTree.FromPolygons(v.tolist(), t.tolist(), all_triangles=True)
            vistos = set()
            for i, _ in a_v.overlap(arboles_n[n.name]):
                if p[i] not in vistos:
                    vistos.add(p[i]); sumar("atraviesan", n.name, o.name, tm[i], int(p[i]))
            cen = v[t].mean(1)
            cerca = np.where(np.all((cen > lo) & (cen < hi), axis=1))[0]
            for i in cerca:
                if p[i] in vistos:
                    continue
                if CT.dentro(arboles_n[n.name], cen[i]):
                    vistos.add(p[i]); sumar("dentro", n.name, o.name, tm[i], int(p[i]))
    dentro, fuera = camaras(js)
    nombres_v = {o.name for o in V}
    tri_cen = np.concatenate([datos[n][0][datos[n][1]].mean(1) for n in [o.name for o in V + N]])
    por_vista = {}
    for clave, vistas in (("flotan", dentro), ("asoman", fuera)):
        for vista, (pos, mira, lens) in vistas.items():
            o_, ds = rayos(pos, mira, lens)
            o_ = Vector(o_)
            vistos = set()
            for d in ds:
                hit = arbol.ray_cast(o_, Vector(d), 60.0)
                if hit[2] is None:
                    continue
                nom, cara, mat = quien[hit[2]]
                if nom not in nombres_v or (nom, cara) in vistos:
                    continue
                c = tri_cen[hit[2]]
                if clave == "flotan":
                    if mat == CT.PISO_MAT or CT.zona_vieja(c, mat.split(".")[0]) is None:
                        continue
                else:
                    if mat in VIDRIO or not mat.startswith(INTERIOR) or c[2] < 1.5:
                        continue
                vistos.add((nom, cara)); sumar(clave, vista, nom, mat, cara)
            por_vista[f"{clave}:{vista}"] = len(vistos)
    out = {k: dict(sorted(res[k].items(), key=lambda x: -x[1])) for k in ("atraviesan", "dentro", "flotan", "asoman")}
    out["totales"] = {k: len(res["caras"].get(k, ())) for k in ("atraviesan", "dentro", "flotan", "asoman")}
    out["por_vista"] = por_vista
    out["caras"] = {k: sorted([list(x) for x in s]) for k, s in res["caras"].items()}
    print("CHOQUES", etiqueta, "totales", out["totales"], flush=True)
    for k in ("atraviesan", "dentro", "flotan", "asoman"):
        for kk, n in list(out[k].items())[:25]:
            print("CHOQUES", etiqueta, k, kk, n, flush=True)
    return out


def diezmar(ratio, soldar=False, mas=None, despues=False):
    """The exporter's common decimate on the G63's heavy meshes (lamp, lens and grille materials exempt), as a modifier;
    `soldar` welds them first, as the exporter does (blender/vivo_normales.py); `mas` {object: weight} reweights the ratio at
    the same total; `despues` marks the sharp edges after the decimate instead of before (vivo_normales.afilar), "ambos" before and after."""
    import vivo_normales
    cam = bpy.data.objects["camion"]
    objs = [o for o in [cam, *cam.children_recursive]
            if o.type == "MESH" and o.name.startswith(("Material", "rueda")) and len(o.data.polygons) > 300 and not any(
                m and m.name.startswith(("faros", "calaveras", "mica", "g63_")) for m in o.data.materials)]
    r = vivo_normales.razones(objs, ratio, mas or {})
    for o in objs:
        if soldar:
            print("SOLDAR", o.name, *vivo_normales.soldar(o, marcar=despues != True), flush=True)
        o.modifiers.new("dec", "DECIMATE").ratio = r[o]
        if despues:
            vivo_normales.afilar(o)


def pesos(args):
    """mas=Material3.004:3,obj:w -> {"Material3.004": 3.0, ...}"""
    m = next((x[4:] for x in args if x.startswith("mas=")), "")
    return {k: float(v) for k, v in (p.split(":") for p in m.split(",") if p)}


if __name__ == "__main__" and "--" in sys.argv:
    a = sys.argv[sys.argv.index("--") + 1:]
    if os.environ.get("VIVO_POSE"):  # the console as the exporter ships it: the owner's matrix (vivo_secciones_exportar.poner_pose)
        from mathutils import Matrix
        bpy.data.objects["tripo_consola"].matrix_world = Matrix(json.load(open(os.environ["VIVO_POSE"], encoding="utf8"))["objetos"]["tripo_consola"]["mundo"])
        bpy.context.view_layer.update()
    if "borrar" in a[2:]:
        CT.borrar_viejos(bpy.data.objects["camion"], [o for o in nuevas() if o.name.startswith("tripo_")])
    for x in a[2:]:
        if x.startswith("diezmar="):
            diezmar(float(x.split("=")[1]), "soldar" in a[2:], pesos(a[2:]), "ambos" if "ambos" in a[2:] else "despues" in a[2:])
    r = medir(a[0], "suelto", ocultas=True)
    json.dump(r, open(a[1], "w", encoding="utf8"), indent=1)

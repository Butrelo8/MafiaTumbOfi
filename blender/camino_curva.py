"""road3's curve (ref 2: the highway bends left, the chevron signs stand on the outside). Exec'd last by camino_mx140.py in its
namespace (MONTAJE_CAMINO=road3), after every object is built on the straight road. One post-build pass that bends only the road
beyond S0 m ahead: the truck, the cameras, the lane and src/lib/escena.json do not change (y < S0 maps to itself, bit for bit).

  Mapping (x = metres right of the road line, y = metres ahead; z untouched):  a circular arc of radius R from y = S0 to S1
  (the road turns left), then a straight line at the final heading. With ph = clamp(y - S0, 0, S1 - S0) / R and
  ell = min(y - S0, 0) + max(y - S1, 0):
      x' = R (cos ph - 1) - ell sin ph + x cos ph        y' = S0 + R sin ph + ell cos ph + x sin ph        yaw += ph
  x stays the offset from the road's centre line, so lanes, shoulders and the barrier keep their widths.

What each kind of object does (counts are printed):
  malla    long strips, markings, the barrier, poles: subdivided to <= 4 m along y, vertices mapped. The materials read Object-space
           x and y (lane bands, dirt edges, noise), so every vertex carries its straight position in the attribute `p0` and the
           materials read that instead of the Object coordinate (an unbent mesh sharing one of them gets p0 = its position).
  curva    the wires' points are mapped.
  objeto   buildings, signs, lamps (empties that instance the lamp collection), the canopy, the car: origin mapped, yaw added.
  scatter  geometry-nodes scatters: a Set Position + Rotate Instances after their join (the same formula as a node group); the
           instances on the inside of the bend beyond 0.45 R are deleted (the arc would fold them over).
  quieto   the ground and the fog box stay as they are.
The bend holds for a still: `mundo` scrolls 192 m over a loop, so the clips would need the bend to scroll with it (not done).
CURVA_PRUEBA="radio=250;s0=40;s1=250" overrides for one run; "vista" also registers the top-down option `curva-arriba`.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

CURVA = dict(radio=220.0, s0=40.0, s1=260.0, paso=4.0)
CURVA_VISTA = False
for _kv in filter(None, os.environ.get("CURVA_PRUEBA", "").split(";")):
    if _kv == "vista":
        CURVA_VISTA = True
    else:
        _k, _v = _kv.split("=")
        CURVA[_k] = float(_v)


def doblar(x, y):
    """(x, y) on the straight road -> (x', y', ph): the position on the bent road and the heading change there."""
    R, s0, s1 = CURVA["radio"], CURVA["s0"], CURVA["s1"]
    x, y = np.asarray(x, float), np.asarray(y, float)
    ph = np.clip(y - s0, 0.0, s1 - s0) / R
    ell = np.minimum(y - s0, 0.0) + np.maximum(y - s1, 0.0)
    c, s = np.cos(ph), np.sin(ph)
    return R * (c - 1.0) - ell * s + x * c, s0 + R * s + ell * c + x * s, ph


# ---------------------------------------------------------------- geometry-nodes version of the same formula
def _grupo_doblar():
    ng = bpy.data.node_groups.new("curva_doblar", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    R, s0, s1 = CURVA["radio"], CURVA["s0"], CURVA["s1"]

    def m(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, float):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    pos = N.new("GeometryNodeInputPosition")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(pos.outputs[0], sep.inputs[0])
    x, y = sep.outputs["X"], sep.outputs["Y"]
    d = m("SUBTRACT", y, s0)
    ph = m("DIVIDE", m("MINIMUM", m("MAXIMUM", d, 0.0), s1 - s0), R)
    ell = m("ADD", m("MINIMUM", d, 0.0), m("MAXIMUM", m("SUBTRACT", y, s1), 0.0))
    c, s = m("COSINE", ph), m("SINE", ph)
    xn = m("ADD", m("SUBTRACT", m("MULTIPLY", m("SUBTRACT", c, 1.0), R), m("MULTIPLY", ell, s)), m("MULTIPLY", x, c))
    yn = m("ADD", m("ADD", m("ADD", s0 + 0.0, m("MULTIPLY", s, R)), m("MULTIPLY", ell, c)), m("MULTIPLY", x, s))
    nuevo = N.new("ShaderNodeCombineXYZ"); L.new(xn, nuevo.inputs["X"]); L.new(yn, nuevo.inputs["Y"]); L.new(sep.outputs["Z"], nuevo.inputs["Z"])
    giro = N.new("ShaderNodeCombineXYZ"); L.new(ph, giro.inputs["Z"])
    # inside of the bend, past the start: out (x < -0.45 R and y > s0)
    c1 = N.new("FunctionNodeCompare"); c1.data_type, c1.operation = "FLOAT", "LESS_THAN"; L.new(x, c1.inputs[0]); c1.inputs[1].default_value = -0.45 * R
    c2 = N.new("FunctionNodeCompare"); c2.data_type, c2.operation = "FLOAT", "GREATER_THAN"; L.new(y, c2.inputs[0]); c2.inputs[1].default_value = s0
    y_ = N.new("FunctionNodeBooleanMath"); y_.operation = "AND"; L.new(c1.outputs[0], y_.inputs[0]); L.new(c2.outputs[0], y_.inputs[1])
    borra = N.new("GeometryNodeDeleteGeometry"); borra.domain = "INSTANCE"
    L.new(gi.outputs[0], borra.inputs["Geometry"]); L.new(y_.outputs[0], borra.inputs["Selection"])
    # rotate first (the fields read the straight positions), about each instance's own position; then move
    ro = N.new("GeometryNodeRotateInstances"); L.new(borra.outputs[0], ro.inputs["Instances"]); L.new(giro.outputs[0], ro.inputs["Rotation"])
    ro.inputs["Local Space"].default_value = False
    L.new(pos.outputs[0], ro.inputs["Pivot Point"])
    sp = N.new("GeometryNodeSetPosition"); L.new(ro.outputs[0], sp.inputs["Geometry"]); L.new(nuevo.outputs[0], sp.inputs["Position"])
    L.new(sp.outputs[0], go.inputs[0])
    return ng


# ---------------------------------------------------------------- the sweep
def _subdividir(bm):
    """Edges longer than `paso` that run along y (|dy| > 3 |dx|) are cut so every piece is <= paso."""
    por_cortes = {}
    for e in bm.edges:
        a, b = e.verts[0].co, e.verts[1].co
        dy, dx = abs(a.y - b.y), abs(a.x - b.x)
        if dy > CURVA["paso"] * 1.5 and dy > 3 * dx and abs(a.z - b.z) < 0.01:
            por_cortes.setdefault(int(math.ceil(dy / CURVA["paso"])) - 1, []).append(e)
    for cortes, edges in por_cortes.items():
        bmesh.ops.subdivide_edges(bm, edges=[e for e in edges if e.is_valid], cuts=cortes, use_grid_fill=True)


def _p0_materiales(mats):
    n = 0
    for m in mats:
        if not m or not m.use_nodes:
            continue
        nt = m.node_tree
        for tc in [t for t in nt.nodes if t.type == "TEX_COORD"]:
            if tc.outputs["Object"].links:
                at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type, at.attribute_name = "GEOMETRY", "p0"
                for l in list(tc.outputs["Object"].links):
                    nt.links.new(at.outputs["Vector"], l.to_socket)
                n += 1
    return n


def curvar():
    cuenta, otros = {}, []
    grupo = _grupo_doblar()
    mallas, mats = [], set()
    for o in list(bpy.data.objects):
        if o.parent is not MUNDO_ROOT:
            continue
        n = o.name.split(".")[0]
        if n in ("w_terreno", "w_niebla"):
            clase = "quieto"
        elif o.type == "MESH" and any(md.type == "NODES" for md in o.modifiers):
            clase = "scatter"
        elif n.startswith(("e_", "e3_", "w_farola_", "tramo_")):
            clase = "objeto"
        elif o.type == "MESH":
            clase = "malla"
        elif o.type == "CURVE":
            clase = "curva"
        else:
            clase, _ = "otro", otros.append(o.name)
        cuenta[clase] = cuenta.get(clase, 0) + 1
        if clase == "objeto":
            x, y, ph = doblar(o.location.x, o.location.y)
            o.location.x, o.location.y = float(x), float(y)
            o.rotation_euler = (Matrix.Rotation(float(ph), 3, "Z") @ o.rotation_euler.to_matrix()).to_euler()
        elif clase == "scatter":
            for md in o.modifiers:
                if md.type == "NODES" and md.node_group and md.node_group.name != "curva_doblar":
                    ng = md.node_group
                    go = next(nd for nd in ng.nodes if nd.type == "GROUP_OUTPUT")
                    src = go.inputs[0].links[0].from_socket
                    gn = ng.nodes.new("GeometryNodeGroup"); gn.node_tree = grupo
                    ng.links.new(src, gn.inputs[0]); ng.links.new(gn.outputs[0], go.inputs[0])
        elif clase == "curva":
            for sp in o.data.splines:
                pts = sp.points if sp.type == "POLY" else sp.bezier_points
                for p in pts:
                    x, y, _ = doblar(p.co.x, p.co.y)
                    p.co.x, p.co.y = float(x), float(y)
        elif clase == "malla":
            if tuple(o.location[:2]) != (0.0, 0.0) or o.rotation_euler.z or tuple(o.scale[:2]) != (1.0, 1.0):
                otros.append(f"{o.name} (malla con transformacion)")
                continue
            mallas.append(o)
    for o in mallas:
        me = o.data
        bm = bmesh.new(); bm.from_mesh(me)
        _subdividir(bm)
        bm.to_mesh(me); bm.free()
        co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        at = me.attributes.get("p0") or me.attributes.new("p0", "FLOAT_VECTOR", "POINT")
        at.data.foreach_set("vector", co.ravel())
        x, y, _ = doblar(co[:, 0], co[:, 1])
        co2 = co.copy(); co2[:, 0], co2[:, 1] = x, y
        me.vertices.foreach_set("co", co2.ravel()); me.update()
        mats.update(me.materials)
    n_mat = _p0_materiales(mats)
    sin_p0 = []
    for o in bpy.data.objects:   # an unbent mesh sharing a rewritten material reads its own position as p0
        if o.type == "MESH" and o not in mallas and any(m in mats for m in o.data.materials) and "p0" not in o.data.attributes:
            co = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", co)
            o.data.attributes.new("p0", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", co)
            sin_p0.append(o.name)
    print("CAMINO curva: R", CURVA["radio"], "S0", CURVA["s0"], "S1", CURVA["s1"], "clases", cuenta, "mallas curvadas", len(mallas),
          "materiales con p0", n_mat, "sin curvar (compartian material)", sin_p0, "sin clase", otros, flush=True)
    return mallas


if CURVA_VISTA:
    @opcion("curva-arriba")
    def _arriba():
        """Layout check, no truck: the bent world from 400 m up, y 15..285 ahead (use with `wb`)."""
        if WB:
            pase_wb()
        return ((-40.0, 150.0, 400.0), (-40.0, 151.0, 0.0), 30)

curvar()

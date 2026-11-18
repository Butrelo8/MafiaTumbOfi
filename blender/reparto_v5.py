"""The Tripo v5 cast (apedrone, docs/tripo-reparto-v5.md) in the chain's seats, driven live by the rigs already there
(caughtdrone, 2026-11-18; owner: "change the 3d figures we have on the scenes for the tripo ones and render them as they is").

montaje.py calls montar() at the end of montar_reparto(). Each Tripo rig follows the figure it replaces:
  manager, hector, alejandro -> the stand-in rigs from transicion.py figura()/sentar() (13 bones, the old GLBs)
  diego                      -> colddrone's interim clip (`mx`, sitting_drinking, under diego_raiz)
The drivers stay in the scene, animated and hidden from render (ocultar_dobles(), called from montaje's viejo_diego()), so
everything that reads them keeps working: ruta.py's 80-frame NLA cycles and Diego's ping-pong, caja5's drink in Héctor's
hand, the bottle on Diego's hand, the ray probes. Nothing is baked: the constraints follow every later change.

Per Tripo rig: Hips copies the driver's hip point (world space); each mapped bone gets a Damped Track toward an empty that
rides 10 driver-armature units beyond its driver bone's tail, so it points the way the driver bone points whatever the
difference in bone lengths. Then an IK (chain 2) on each forearm puts the wrist on the driver's wrist, so hands stay on the
wheel and around the drinks. Unmapped bones (shoulders, feet, fingers) keep their rest pose relative to their parent. Twist
is not carried (Damped Track only swings). medir() prints the cast's numbers: head top, hands, gap from each drink to the mesh.

Input (git-ignored): blender/assets/reparto-v5/<apedrone name>/rig.fbx, copied from MTO-apedrone's
reparto-v5/<name>/rig/tripo-out/*/model.fbx, and cast_alturas/cast.json (uniform scale per figure, the owner's heights).
The FBX faces +X with its left at +Y; the chain's figures face -Y in their own space.
"""
import bpy, json, os
import numpy as np
from mathutils import Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
V5 = os.path.join(AQUI, "assets", "reparto-v5")
APEDRONE = {"diego": "diego", "hector": "hector", "alejandro": "alexandro", "manager": "manager"}  # chain name -> apedrone's
LARGO = 10.0  # how far past the driver bone's tail its aim empty sits (driver armature units)

# stand-in bone -> Tripo (mixamo) bones that take its direction; _n is the figure's right
MAPA_DOBLE = {"cadera": ["Hips"], "columna": ["Spine", "Spine1", "Spine2"], "cabeza": ["Neck", "Head"],
              "muslo_n": ["RightUpLeg"], "pierna_n": ["RightLeg"], "muslo_p": ["LeftUpLeg"], "pierna_p": ["LeftLeg"],
              "brazo_n": ["RightArm"], "antebrazo_n": ["RightForeArm"], "mano_n": ["RightHand"],
              "brazo_p": ["LeftArm"], "antebrazo_p": ["LeftForeArm"], "mano_p": ["LeftHand"]}
FIGS = []  # (name, tripo armature, tripo mesh, driver meshes to hide)


def mx(n):
    return "mixamorig:" + n


def marco(derecha, arriba):
    """Rotation whose columns are (right, forward, up) for a figure, forward = up x right (the figure faces it)."""
    a = arriba.normalized()
    d = (derecha - a * derecha.dot(a)).normalized()
    f = a.cross(d)
    return Matrix((d, f, a)).transposed()


def importar(quien):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(V5, APEDRONE[quien], "rig.fbx"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next(o for o in nuevos if o.type == "ARMATURE")
    malla = next(o for o in nuevos if o.type == "MESH")
    for o in nuevos:
        o.animation_data_clear()
    arm.name, arm.data.name, malla.name = quien + "_v5_rig", quien + "_v5_rig", quien + "_v5"
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm, malla, nuevos


def apuntar(arm, hueso, drv, drv_hueso):
    """Damped Track on `hueso` toward an empty LARGO past the tail of the driver's bone."""
    e = bpy.data.objects.new(f"{arm.name}_mira_{hueso.split(':')[-1]}", None)
    e.empty_display_size = 0.02
    bpy.context.scene.collection.objects.link(e)
    e.parent, e.parent_type, e.parent_bone = drv, "BONE", drv_hueso
    e.matrix_parent_inverse = Matrix.Identity(4)
    e.matrix_basis = Matrix.Translation((0, LARGO, 0))
    c = arm.pose.bones[hueso].constraints.new("DAMPED_TRACK")
    c.target, c.track_axis = e, "TRACK_Y"
    return e


def cadera_en(arm, drv, drv_hueso, punto_mundo):
    """Copy Location (world) on Hips toward an empty riding the driver's hip bone, placed at `punto_mundo` now."""
    pb = drv.pose.bones[drv_hueso]
    e = bpy.data.objects.new(f"{arm.name}_cadera", None)
    e.empty_display_size = 0.03
    bpy.context.scene.collection.objects.link(e)
    e.parent, e.parent_type, e.parent_bone = drv, "BONE", drv_hueso
    e.matrix_parent_inverse = Matrix.Identity(4)
    padre = drv.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))  # a bone child's frame: the bone's tail
    e.matrix_basis = padre.inverted() @ Matrix.Translation(punto_mundo)
    c = arm.pose.bones[mx("Hips")].constraints.new("COPY_LOCATION")
    c.target = e
    arm.pose.bones[mx("Hips")].constraints.move(len(arm.pose.bones[mx("Hips")].constraints) - 1, 0)
    return e


def verts(o):
    """World positions of every evaluated vertex, (n, 3)."""
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = e.to_mesh()
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    e.to_mesh_clear()
    m = np.array(e.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def zs(malla):
    return verts(malla)[:, 2]


def en_mano(drv):
    """Visible meshes riding a driver's hand bones (the drinks), through any chain of parents."""
    manos = {"mano_n", "mano_p", "puno_n", "puno_p", "antebrazo_n", "antebrazo_p", mx("RightHand"), mx("LeftHand")}
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        p = o
        while p.parent and not (p.parent is drv and p.parent_type == "BONE"):
            p = p.parent
        if p.parent is drv and p.parent_type == "BONE" and p.parent_bone in manos:
            out.append(o)
    return out


def alto_reposo(arm, malla):
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    z = zs(malla)
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    return float(z.max() - z.min())


def poner(quien, drv, escala, coleccion, figuras):
    """One Tripo figure in place of the driver armature `drv` (stand-in rig or Diego's `mx`)."""
    sc = bpy.context.scene
    arm, malla, nuevos = importar(quien)
    for o in nuevos:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coleccion.objects.link(o)
    W = drv.matrix_world
    if drv.pose.bones.get("cadera"):  # stand-in: rest joints from its bones, facing -Y in its own space
        b = drv.data.bones
        cad = W @ b["cadera"].head_local
        der = (W @ b["muslo_n"].head_local) - (W @ b["muslo_p"].head_local)
        arriba = (W @ b["columna"].tail_local) - cad
        mapa = {t: d for d, ts in MAPA_DOBLE.items() for t in ts}
        mapa = {mx(t): d for t, d in mapa.items()}
        hueso_cadera = "cadera"
    else:  # Diego's clip: a mixamo rig in its own axes (Y up in armature space)
        b = drv.data.bones
        cad = W @ ((b[mx("LeftUpLeg")].head_local + b[mx("RightUpLeg")].head_local) / 2)
        der = (W @ b[mx("RightUpLeg")].head_local) - (W @ b[mx("LeftUpLeg")].head_local)
        arriba = (W @ b[mx("Head")].head_local) - cad
        mapa = {n.name: n.name for n in arm.data.bones if n.name in drv.data.bones and n.name != mx("Hips")}
        mapa[mx("Hips")] = mx("Hips")
        hueso_cadera = mx("Hips")
    tb = arm.data.bones
    t_cad = (tb[mx("LeftUpLeg")].head_local + tb[mx("RightUpLeg")].head_local) / 2
    t_der = tb[mx("RightUpLeg")].head_local - tb[mx("LeftUpLeg")].head_local
    t_arriba = tb[mx("Head")].head_local - t_cad
    giro = marco(der, arriba) @ marco(t_der, t_arriba).transposed()  # Tripo armature space -> world
    rest_w = Matrix.Translation(cad) @ giro.to_4x4() @ Matrix.Scale(escala, 4) @ Matrix.Translation(-t_cad)
    arm.parent = drv
    arm.matrix_parent_inverse = W.inverted()
    arm.matrix_basis = rest_w
    bpy.context.view_layer.update()
    alto = alto_reposo(arm, malla)
    # the driver's hip point now (posed) + the Tripo Hips head's offset above its hip joints, turned with the driver's pelvis
    pbd = drv.pose.bones[hueso_cadera]
    if hueso_cadera == "cadera":
        cad_ahora = W @ pbd.head
        pelvis = (W.to_3x3() @ pbd.matrix.to_3x3()) @ (W.to_3x3() @ drv.data.bones["cadera"].matrix_local.to_3x3()).inverted()
        hips_w = cad_ahora + pelvis.normalized() @ (giro @ ((tb[mx("Hips")].head_local - t_cad) * escala))
        cadera_en(arm, drv, hueso_cadera, hips_w)
    else:
        c = arm.pose.bones[mx("Hips")].constraints.new("COPY_LOCATION")
        c.target, c.subtarget = drv, mx("Hips")
    for t, d in mapa.items():
        if t in arm.pose.bones and d in drv.pose.bones:
            apuntar(arm, t, drv, d)
    # the hands reach the driver's wrists (the wheel, Héctor's bottle, Diego's bottle): an IK on each forearm, chain 2, to an
    # empty at the driver forearm's tail; the Damped Tracks above set the arm's bend plane before the solve
    for lado in ("Right", "Left"):
        d_ante = next(d for t, d in mapa.items() if t == mx(lado + "ForeArm"))
        e = bpy.data.objects.new(f"{arm.name}_muñeca_{lado}", None)
        e.empty_display_size = 0.03
        bpy.context.scene.collection.objects.link(e)
        e.parent, e.parent_type, e.parent_bone = drv, "BONE", d_ante
        e.matrix_parent_inverse = Matrix.Identity(4)
        c = arm.pose.bones[mx(lado + "ForeArm")].constraints.new("IK")
        c.target, c.chain_count = e, 2
    bpy.context.view_layer.update()
    hips = arm.matrix_world @ arm.pose.bones[mx("Hips")].head
    print(f"V5 {quien}: escala {escala} alto en reposo {alto:.3f} m, {len(mapa)} huesos siguen a {drv.name}; cadera f{sc.frame_current} "
          f"({hips.x:.3f}, {hips.y:.3f}, {hips.z:.3f}); tris {sum(len(p.vertices) - 2 for p in malla.data.polygons)}", flush=True)
    figuras.extend([arm, malla])
    return arm, malla


def montar(figuras, dobles, colecciones):
    """dobles: chain name -> (driver armature, [driver meshes to hide]). figuras: utileria's FIGURAS list, extended in place."""
    escalas = {f["name"]: f["scale"] for f in json.load(open(os.path.join(V5, "cast_alturas", "cast.json"), encoding="utf8"))["figs"]}
    for quien, (drv, ocultar) in dobles.items():
        arm, malla = poner(quien, drv, escalas[APEDRONE[quien]], colecciones[quien], figuras)
        FIGS.append((quien, arm, malla, ocultar))
    ocultar_dobles()


def ocultar_dobles():
    for _q, arm, _m, ocultar in FIGS:
        for o in ocultar:
            o.hide_render = True
        seguir_punos(arm)


def seguir_punos(arm):
    """caja5.puno() adds a fist bone `puno_<n|p>` (wrist ring -> hand centroid of the stand-in's mesh, child of mano_<n|p>) and
    turns it to show the drink. When it exists, the Tripo hand aims along it and the wrist goes to its head."""
    drv = arm.parent
    for k, lado in (("n", "Right"), ("p", "Left")):
        b = drv.data.bones.get("puno_" + k)
        if b is None:
            continue
        mira, muneca = bpy.data.objects[f"{arm.name}_mira_{lado}Hand"], bpy.data.objects[f"{arm.name}_muñeca_{lado}"]
        mira.parent_bone = muneca.parent_bone = b.name
        muneca.matrix_basis = Matrix.Translation((0, -b.length, 0))


def medir():
    """Numbers per figure at the current frame: lowest and highest mesh point, hands."""
    out = {}
    for quien, arm, malla, _o in FIGS:
        z = zs(malla)
        manos = [arm.matrix_world @ arm.pose.bones[mx(l + "Hand")].head for l in ("Right", "Left")]
        muñecas = [bpy.data.objects[f"{arm.name}_muñeca_{l}"].matrix_world.translation for l in ("Right", "Left")]
        print(f"V5 MANOS {quien}: mano -> muñeca del doble der {(manos[0] - muñecas[0]).length * 1000:.0f} mm, "
              f"izq {(manos[1] - muñecas[1]).length * 1000:.0f} mm", flush=True)
        print(f"V5 MEDIDA {quien} f{bpy.context.scene.frame_current}: z {z.min():.3f}..{z.max():.3f}; manos der "
              f"({manos[0].x:.3f}, {manos[0].y:.3f}, {manos[0].z:.3f}) izq ({manos[1].x:.3f}, {manos[1].y:.3f}, {manos[1].z:.3f})", flush=True)
        out[quien] = (float(z.min()), float(z.max()))
        drv = arm.parent
        cuerpo = None
        for o in en_mano(drv):
            cuerpo = verts(malla) if cuerpo is None else cuerpo
            v = verts(o)
            cerca = cuerpo[np.linalg.norm(cuerpo - v.mean(0), axis=1) < 0.4]
            if not len(cerca):
                print(f"V5 PROP {quien} {o.name}: no Tripo vertex within 0.4 m", flush=True)
                continue
            d = np.sqrt(((v[::max(1, len(v) // 400), None, :] - cerca[None, ::max(1, len(cerca) // 4000), :]) ** 2).sum(-1)).min()
            print(f"V5 PROP {quien} {o.name}: gap to the Tripo mesh {d * 1000:.0f} mm (sampled)", flush=True)
    return out

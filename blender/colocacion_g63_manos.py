"""Hands and roof-load controls for the owner's G63 placement file (queue 2026-11-20-mto-g63-hands-props-controls).

Takes a COPY of his saved colocar-g63.blend and adds, without moving anything he placed (the four crosses `posicion_*`, every bone, every roof
object keep their world transforms, measured by the round trip in vivo_reparto_volcar.py):

  - per cast member and side: `mano_izq_<nombre>` / `mano_der_<nombre>` (an arrows empty at the wrist: G moves the hand and the arm follows,
    R turns it) and `codo_izq_<nombre>` / `codo_der_<nombre>` (a small sphere: where the elbow points). Both are children of his
    `posicion_<nombre>` cross, so moving the whole body carries the hands. Under the hood: an IK constraint on the forearm (chain of 2:
    forearm + upper arm, effector = the wrist, target = the hand control at the wrist, pole = the elbow control, pole angle fitted so the pose he left is
    reproduced) and a Copy Rotation on the hand bone (world, from the hand control). The fingers are not touched: his finger pose rides
    along with the hand.
  - `agarre` (0..1) on each hand control: curls the four fingers and the thumb. Drivers on the finger bones' Euler X/Z
    (his quaternion is converted to the same rotation as Euler first); 0 = his pose, exactly.
  - `techo_<pieza>`: one selectable handle per roof object (`k3_*`: bajo, docerola, requinto, teclado, tarola, dona, alien), at the
    object's origin, which now hangs from it. G moves it, R turns it.
  - Héctor's bottle hangs from the control of the hand that holds it (it was on his cross), so it travels with the hand.

Only the crosses, the hand/elbow controls and the roof handles are selectable; the file opens on the Cabina camera.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <his colocar-g63.blend (a copy)> --python-exit-code 1 \
    --python blender/colocacion_g63_manos.py -- <out .blend (Windows)>
"""
import bpy, math, sys
from mathutils import Matrix, Vector

SAL = sys.argv[sys.argv.index("--") + 1]
O = bpy.data.objects
sc = bpy.context.scene
NOMBRES = ("manager", "hector", "alejandro", "diego")
LADOS = (("izq", "Left"), ("der", "Right"))
DEDOS = ("Index", "Middle", "Ring", "Pinky", "Thumb")
GRADOS = {"Index": (70, 80, 55), "Middle": (70, 80, 55), "Ring": (70, 80, 55), "Pinky": (70, 80, 55), "Thumb": (25, 30, 30)}

LEEME = """COLOCACIÓN DEL REPARTO EN EL G63 NUEVO: manos y cosas del techo

Se pueden seleccionar: las cuatro cruces «posicion_manager / hector / alejandro / diego» (mueven al personaje entero),
los controles de manos y codos, y las piezas del techo. Todo lo demás está bloqueado.

MANOS (en la cabina)
  mano_izq_<nombre> / mano_der_<nombre>   flechas en la muñeca. G mueve la mano y el brazo la sigue; R gira la mano.
  codo_izq_<nombre> / codo_der_<nombre>   bolita hacia donde apunta el codo. Muévela para subir, bajar o abrir el codo.
  «izq» y «der» son la izquierda y la derecha del personaje, no las tuyas.
  Agarre: selecciona la mano, Propiedades (abajo a la derecha) > pestaña Objeto > Propiedades personalizadas > agarre (0 = tu pose, 1 = puño).
  Los dedos conservan tu pose. Si la mano queda lejos del hombro, el brazo se estira al máximo y la mano no llega al control.

TECHO
  techo_bajo, techo_docerola, techo_requinto, techo_teclado, techo_tarola, techo_dona, techo_alien   cruz en el centro de cada pieza.
  G mueve, R gira. La red NO sigue a las piezas mientras acomodas: se vuelve a tender sola al reconstruir.

TECLAS: G mover · R girar (Z para girar sobre el piso) · NO uses S. Teclea un número después (G, Z, -0.05, Enter). Clic derecho o Esc cancela.
Las cámaras están marcadas en la línea de tiempo (abajo): «Cabina» y las cuatro tomas de la banda. Numpad 0 vuelve a la vista de la cámara.
Ctrl+S guarda en este mismo archivo. Avísale a Claude o a la nave nodriza: «leer reparto de <ruta de tu archivo>».
"""

coleccion = bpy.data.collections.get("controles") or bpy.data.collections.new("controles")
if coleccion.name not in sc.collection.children:
    sc.collection.children.link(coleccion)


def sin_escala(m):
    return Matrix.LocRotScale(m.to_translation(), m.to_quaternion(), None)


def vacio(nombre, tipo, tam, mw, padre, nombre_visible=False):
    """An empty at world matrix `mw`, child of `padre` with its parent inverse set so the world matrix does not change."""
    e = bpy.data.objects.new(nombre, None)
    coleccion.objects.link(e)
    e.empty_display_type, e.empty_display_size = tipo, tam
    e.show_in_front, e.show_name = True, nombre_visible
    bpy.context.view_layer.update()
    e.parent = padre
    e.matrix_parent_inverse = padre.matrix_world.inverted()
    e.matrix_world = mw
    return e


def snapshot():
    bpy.context.view_layer.update()
    return {n: {b.name: b.matrix.copy() for b in O[n + "_v5_rig"].pose.bones} for n in NOMBRES}


def error(antes, despues):
    """Max bone-head distance (m) and max bone rotation (deg) between two snapshots, per rig."""
    out = {}
    for n in NOMBRES:
        dt = max((antes[n][k].translation - despues[n][k].translation).length for k in antes[n])
        dr = max(math.degrees((antes[n][k].to_quaternion().rotation_difference(despues[n][k].to_quaternion())).angle) for k in antes[n])
        out[n] = (dt, dr)
    return out


BASE = snapshot()
CRUCES = {n: O["posicion_" + n].matrix_world.copy() for n in NOMBRES}
CAMION = O["camion"].matrix_world.copy()
PROPS = {o.name: o.matrix_world.copy() for o in O if o.type == "MESH" and o.name.split(".")[0].startswith("k3_")}
bpy.context.view_layer.update()

# ---------------------------------------------------------------- hands: IK + rotation, controls
# The importer left the arm bones disconnected, a gap along the bone's own axis between each tail and its child's head (upper arm 1.8 cm,
# forearm 2.0 cm in rest): Blender's IK assumes the chain is continuous, so with the gaps it could not reproduce his pose (2-4 cm off).
# The tails go to the child's head: same head, same direction, same roll, so no pose matrix moves (checked below).
bpy.ops.object.select_all(action="DESELECT")
for n in NOMBRES:
    rig = O[n + "_v5_rig"]
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for H in ("Left", "Right"):
        eb = rig.data.edit_bones
        for padre, hijo in (("Arm", "ForeArm"), ("ForeArm", "Hand")):
            eb[f"mixamorig:{H}{padre}"].tail = eb[f"mixamorig:{H}{hijo}"].head
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.objects.active = None
e0 = error(BASE, snapshot())
print("COLA de brazos al hueso hijo: error", {n: (round(e0[n][0], 7), round(e0[n][1], 5)) for n in NOMBRES}, flush=True)
controles = []
manos_ctrl = {}
for n in NOMBRES:
    rig, cruz = O[n + "_v5_rig"], O["posicion_" + n]
    MW = rig.matrix_world
    for lado, H in LADOS:
        brazo, ante, mano = (rig.pose.bones[f"mixamorig:{H}{k}"] for k in ("Arm", "ForeArm", "Hand"))
        hombro, codo, muneca = MW @ brazo.head, MW @ ante.head, MW @ mano.head
        linea = muneca - hombro
        pie = hombro + linea * ((codo - hombro).dot(linea) / linea.length_squared)
        desvio = codo - pie
        if desvio.length < 0.004:  # an almost straight arm: take the forearm's own side axis
            lado_ = MW.to_3x3() @ ante.x_axis
            desvio = lado_ - linea.normalized() * lado_.dot(linea.normalized())
        polo_pos = codo + desvio.normalized() * 0.12
        c_mano = vacio(f"mano_{lado}_{n}", "ARROWS", 0.05, sin_escala(MW @ mano.matrix), cruz)
        c_codo = vacio(f"codo_{lado}_{n}", "SPHERE", 0.03, Matrix.Translation(polo_pos), cruz)
        c_mano["agarre"] = 0.0
        c_mano.id_properties_ui("agarre").update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, description="0 = tu pose de dedos, 1 = puño")
        # IK on the hand bone with use_tail off: the effector is the hand's HEAD (the wrist), not the forearm's tail (the importer's bone
        # tails do not meet the children's heads), and the chain moves the forearm and the upper arm (the hand bone itself is not turned)
        ik = mano.constraints.new("IK")
        ik.name = "IK_mano"
        ik.target, ik.pole_target = c_mano, c_codo
        ik.chain_count, ik.use_tail, ik.use_stretch = 2, False, False
        cr = mano.constraints.new("COPY_ROTATION")
        cr.name = "rotacion_mano"
        cr.target = c_mano  # world -> world, all axes

        def f(a, ik=ik, MW=MW, ante=ante, codo=codo):
            ik.pole_angle = a
            bpy.context.view_layer.update()
            return (MW @ ante.head - codo).length

        # pole angle: the one that puts the elbow back where he left it
        a0 = min((math.radians(g) for g in range(-180, 180, 5)), key=f)
        lo, hi = a0 - math.radians(5), a0 + math.radians(5)
        for _ in range(40):  # golden-section refinement
            m1, m2 = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
            lo, hi = (lo, m2) if f(m1) < f(m2) else (m1, hi)
        ik.pole_angle = (lo + hi) / 2
        bpy.context.view_layer.update()
        manos_ctrl[(n, lado)] = (c_mano, c_codo)
        controles += [c_mano, c_codo]
    e = error(BASE, snapshot())[n]
    print(f"MANOS {n}: IK de ambas manos, error de hueso max {e[0]:.6f} m, giro max {e[1]:.4f} grados", flush=True)


# ---------------------------------------------------------------- grip: drivers on the finger bones
def curl_dir(rig, H):
    """Palm side in armature space: the average way the four fingers already bend in his pose (their tips deviate from the base line)."""
    s = Vector()
    for d in DEDOS[:4]:
        p = [rig.pose.bones[f"mixamorig:{H}Hand{d}{i}"].head.copy() for i in (1, 2, 3, 4)]
        eje = (p[1] - p[0]).normalized()
        dev = (p[3] - p[0]) - eje * (p[3] - p[0]).dot(eje)
        s += dev
    return s.normalized() if s.length > 1e-6 else None


for n in NOMBRES:
    rig = O[n + "_v5_rig"]
    for lado, H in LADOS:
        c_mano = manos_ctrl[(n, lado)][0]
        S = curl_dir(rig, H)
        for d in DEDOS:
            for i in (1, 2, 3):
                pb = rig.pose.bones[f"mixamorig:{H}Hand{d}{i}"]
                punta = rig.pose.bones[f"mixamorig:{H}Hand{d}4"]
                q = pb.rotation_quaternion.copy()
                pb.rotation_mode = "XYZ"
                pb.rotation_euler = q.to_euler("XYZ")
                base = list(pb.rotation_euler)
                bpy.context.view_layer.update()
                p0 = punta.head.copy()
                mejor = (0.0, 0, 1)
                for eje in (0, 2):
                    for sg in (1, -1):
                        pb.rotation_euler = [base[k] + (sg * 0.3 if k == eje else 0.0) for k in range(3)]
                        bpy.context.view_layer.update()
                        g = (punta.head - p0).dot(S) if S else 0.0
                        if g > mejor[0]:
                            mejor = (g, eje, sg)
                pb.rotation_euler = base
                _, eje, sg = mejor
                fc = pb.driver_add("rotation_euler", eje)
                dr = fc.driver
                dr.type = "SCRIPTED"
                v = dr.variables.new()
                v.name = "a"
                v.type = "SINGLE_PROP"
                v.targets[0].id = c_mano
                v.targets[0].data_path = '["agarre"]'
                dr.expression = f"{base[eje]:.7f}{sg * math.radians(GRADOS[d][i - 1]):+.7f}*a"
bpy.context.view_layer.update()
e_dedos = error(BASE, snapshot())
print("AGARRE (=0)", {n: (round(e_dedos[n][0], 6), round(e_dedos[n][1], 4)) for n in NOMBRES}, flush=True)

# ---------------------------------------------------------------- Héctor's bottle rides on the hand that holds it
botella = next(o for o in O if o.name.split(".")[0] == "k5_bebida_mano" and o.parent is not None and o.parent.name == "posicion_hector")
mb = botella.matrix_world.copy()
sosten = min((manos_ctrl[("hector", l)][0] for l, _ in LADOS), key=lambda c: (c.matrix_world.translation - mb.translation).length)
botella.parent = sosten
botella.matrix_parent_inverse = sosten.matrix_world.inverted()
botella.matrix_world = mb
print("BOTELLA cuelga de", sosten.name, "a", round((sosten.matrix_world.translation - mb.translation).length, 3), "m", flush=True)

# ---------------------------------------------------------------- roof: one handle per load object
camion = O["camion"]
for nombre, mw in sorted(PROPS.items()):
    o = O[nombre]
    h = vacio(f"techo_{nombre.split('.')[0][3:]}", "PLAIN_AXES", 0.18, sin_escala(mw), camion, nombre_visible=True)
    o.parent = h
    o.matrix_parent_inverse = h.matrix_world.inverted()
    o.matrix_world = mw
    controles.append(h)

# ---------------------------------------------------------------- lock everything but the crosses and the controls, LEEME, camera, save
sueltos = [O["posicion_" + n] for n in NOMBRES] + controles
bpy.context.view_layer.update()
for o in O:
    o.hide_select = o not in sueltos
    o.select_set(False)
bpy.context.view_layer.objects.active = None
sc.camera = O["cam_cabina"]
sc.frame_set(0)
t = bpy.data.texts.get("LEEME") or bpy.data.texts.new("LEEME")
t.clear()
t.write(LEEME)
for scr in bpy.data.screens:
    for a in scr.areas:
        if a.type == "VIEW_3D":
            a.spaces[0].region_3d.view_perspective = "CAMERA"
        elif a.type == "TEXT_EDITOR":
            a.spaces[0].text = t

# ---------------------------------------------------------------- what must not have moved
dc = max((CRUCES[n].to_translation() - O["posicion_" + n].matrix_world.to_translation()).length for n in NOMBRES)
dm = max(sum(abs(CRUCES[n][i][j] - O["posicion_" + n].matrix_world[i][j]) for i in range(4) for j in range(4)) for n in NOMBRES)
dp = max((PROPS[k].translation - O[k].matrix_world.translation).length for k in PROPS)
dcam = sum(abs(CAMION[i][j] - O["camion"].matrix_world[i][j]) for i in range(4) for j in range(4))
fin = error(BASE, snapshot())
print("COLOCACION cruces: mover %.7f m, matriz (suma abs) %.7f" % (dc, dm), flush=True)
print("COLOCACION props max %.7f m, camion %.7f" % (dp, dcam), flush=True)
print("COLOCACION huesos", {n: (round(fin[n][0], 6), round(fin[n][1], 4)) for n in NOMBRES}, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("COLOCACION guardado", SAL, len(sueltos), "seleccionables", flush=True)

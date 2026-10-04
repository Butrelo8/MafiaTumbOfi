"""Pase visual 2026-09-23: los assets elegidos, puestos a ojo para moverlos a mano.

Se corre DESPUÉS de `build()` + `aplicar()`. Todo cae en la colección `PASE` y
las cajas que sustituye se esconden (no se borran): volver a correr `meter()`
rehace la colección desde cero. Cuando las poses queden, se congelan en
`altar.py` / `look.py` con `poses.py`, como siempre.

Lista y licencias: docs/pase-visual-2026-09-23.md y blender/assets/*/LICENSE.txt.
"""

import bpy
import math
import os
import random
from mathutils import Matrix, Vector

A = r"E:\Cursor Projects\MTO\blender\assets"
COL = "PASE"

# Lo que el pase sustituye: se esconde, no se borra.
SUSTITUYE = ("BANCA_", "COLUMNA_", "FOCO_", "VELADORA_", "LLAMA_")


# --- utilidades ---------------------------------------------------------------

def _col():
    col = bpy.data.collections.get(COL)
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o)
    else:
        col = bpy.data.collections.new(COL)
        bpy.context.scene.collection.children.link(col)
    return col


def _caja(verts):
    mn = Vector([min(v[i] for v in verts) for i in range(3)])
    mx = Vector([max(v[i] for v in verts) for i in range(3)])
    return mn, mx


def _plantilla(nombre, objetos, escala):
    """Une `objetos` en una malla con el origen en el centro de la base.

    `escala` es un número (uniforme) o una función (dims) -> (sx, sy, sz).
    La plantilla no se enlaza a la escena: se copia con `_poner`.
    """
    mallas = [o for o in objetos if o.type == "MESH"]
    otros = [o.name for o in objetos if o != mallas[0]]   # join invalida las referencias
    for o in mallas:
        o.data = o.data.copy()
        o.data.transform(o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix()
    if len(mallas) > 1:
        with bpy.context.temp_override(active_object=mallas[0], object=mallas[0],
                                       selected_objects=mallas, selected_editable_objects=mallas):
            bpy.ops.object.join()
    base = mallas[0]
    for n in otros:
        if n in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[n])
    mn, mx = _caja([v.co for v in base.data.vertices])
    dims = mx - mn
    base.data.transform(Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
    s = escala(dims) if callable(escala) else (escala,) * 3
    base.data.transform(Matrix.Diagonal((*s, 1)))
    for c in base.users_collection:
        c.objects.unlink(base)
    base.name = base.data.name = "PASE_" + nombre
    return base


def _glb(carpeta, escala):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(A, carpeta, carpeta + ".glb"))
    return _plantilla(carpeta, [o for o in bpy.data.objects if o not in antes], escala)


def _blend(carpeta, piezas, escala, nombre=None):
    archivo = next(f for f in os.listdir(os.path.join(A, carpeta)) if f.endswith("_2k.blend"))
    with bpy.data.libraries.load(os.path.join(A, carpeta, archivo), link=False) as (_, dst):
        dst.objects = list(piezas)
    _texturas(carpeta)
    for o in dst.objects:                     # join sólo opera sobre la escena
        bpy.context.scene.collection.objects.link(o)
    return _plantilla(nombre or carpeta, dst.objects, escala)


def _texturas(carpeta):
    """Las rutas relativas de Poly Haven apuntan a su propio .blend: se reanclan."""
    for img in bpy.data.images:
        if img.filepath and not os.path.exists(bpy.path.abspath(img.filepath)):
            ruta = os.path.join(A, carpeta, "textures", os.path.basename(img.filepath))
            if os.path.exists(ruta):
                img.filepath = ruta
                img.reload()


def _poner(col, plantilla, nombre, ubicacion, giro_z=0.0, escala=1.0):
    ob = bpy.data.objects.new(nombre, plantilla.data)   # malla compartida
    col.objects.link(ob)
    ob.location = ubicacion
    ob.rotation_euler = (0, 0, giro_z)
    ob.scale = (escala,) * 3
    return ob


def _mat_ph(carpeta, nombre, lado):
    """Material de superficie de Poly Haven, proyectado en caja en espacio mundo.

    Las cajas de la escena no tienen UV útiles: la posición del mundo dividida
    por `lado` (metros por repetición) hace de coordenada.
    """
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]
    archivo = next(f for f in os.listdir(os.path.join(A, carpeta)) if f.endswith("_2k.blend"))
    with bpy.data.libraries.load(os.path.join(A, carpeta, archivo), link=False) as (_, dst):
        dst.materials = [nombre]
    _texturas(carpeta)
    m = dst.materials[0]
    nt = m.node_tree
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.inputs["Scale"].default_value = (1 / lado,) * 3
    nt.links.new(geo.outputs["Position"], mapa.inputs["Vector"])
    for n in nt.nodes:
        if n.type == "TEX_IMAGE":
            n.projection = "BOX"
            n.projection_blend = 0.25
            nt.links.new(mapa.outputs["Vector"], n.inputs["Vector"])
    return m


def _vestir(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def _mat(nombre, color, rugosidad=0.5, emision=None, fuerza=0.0, metal=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rugosidad
    p.inputs["Metallic"].default_value = metal
    if emision:
        p.inputs["Emission Color"].default_value = (*emision, 1)
        p.inputs["Emission Strength"].default_value = fuerza
    return m


def _cera_roja():
    """Rojo de veladora gastado: la cera se aclara y se ensucia a manchas."""
    m = _mat("PASE_cera_roja", (0.30, 0.012, 0.01), 0.6)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    for k, v in (("Subsurface Weight", 0.35), ("Subsurface Radius", (0.08, 0.02, 0.01))):
        if k in p.inputs:
            p.inputs[k].default_value = v
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 18
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].color = (0.12, 0.008, 0.006, 1)   # hollín
    rampa.color_ramp.elements[1].color = (0.42, 0.03, 0.02, 1)     # cera limpia
    nt.links.new(ruido.outputs["Fac"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], p.inputs["Base Color"])
    return m


def _oscurecer(mat, color):
    """Multiplica el color base: piedra sucia, terciopelo vino. La luz ya lava."""
    nt = mat.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    entrada = p.inputs["Base Color"]
    mezcla = nt.nodes.new("ShaderNodeMix")
    mezcla.data_type, mezcla.blend_type = "RGBA", "MULTIPLY"
    mezcla.inputs["Factor"].default_value = 1.0
    a, b = (next(s for s in mezcla.inputs if s.identifier == i) for i in ("A_Color", "B_Color"))
    res = next(s for s in mezcla.outputs if s.identifier == "Result_Color")
    b.default_value = (*color, 1)
    if entrada.links:
        nt.links.new(entrada.links[0].from_socket, a)
    else:
        a.default_value = entrada.default_value
    nt.links.new(res, entrada)


def _bb(ob):
    ps = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return _caja(ps)


def _encajar(col, plantilla, nombre, caja, eje_fino):
    """Estira la plantilla (fina en `eje_fino` de origen) hasta llenar `caja`."""
    mn, mx = caja
    pmn, pmx = _caja([v.co for v in plantilla.data.vertices])
    d = pmx - pmn
    ob = _poner(col, plantilla, nombre, ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    if eje_fino == "y":                        # gira para que lo fino quede en X
        ob.rotation_euler.z = math.pi / 2
        ancho = mx.y - mn.y
    else:
        ancho = mx.x - mn.x
    s = min(ancho / d.x, (mx.z - mn.z) / d.z)
    ob.scale = (s, s, s)
    return ob


# --- el pase ------------------------------------------------------------------

def meter():
    esc = bpy.context.scene
    col = _col()
    for o in esc.objects:
        if o.name.startswith(SUSTITUYE) and not o.name.endswith("_ancla"):
            o.hide_set(True)
            o.hide_render = True
    random.seed(23)

    # Superficies (Poly Haven, proyección en caja)
    muro = _mat_ph("muro-yeso-roto", "rough_plaster_broken", 2.5)
    piso = _mat_ph("piso-losa", "slab_tiles", 2.0)
    tela = _mat_ph("tela-terciopelo", "velour_velvet", 0.8)
    if not tela.get("oscurecido"):
        _oscurecer(tela, (0.45, 0.06, 0.07))       # vino, no rosa
        tela["oscurecido"] = True
    cuero = _mat_ph("cuero", "fabric_leather_02", 0.4)
    madera = _mat_ph("madera-bancas", "dark_paneled_wood", 1.2)
    for n, m in (("NAVE_muro_izq", muro), ("NAVE_muro_der", muro), ("NAVE_piso", piso),
                 ("ESCALON_0", piso), ("ESCALON_1", piso), ("ALTAR_bloque", tela),
                 ("ALTAR_mesa", tela), ("PROP_cinturon", cuero)):
        if n in esc.objects:
            _vestir(esc.objects[n], m)

    # 2 · Bancas: el modelo, estirado a la medida de las cajas (1.5 × 0.55 × 0.95)
    banca = _glb("banca", lambda d: (1.5 / d.x, 0.55 / d.y, 0.95 / d.z))
    _vestir(banca, madera)
    # El respaldo tiene que quedar hacia -Y (el altar está en +Y)
    alto = [v.co for v in banca.data.vertices if v.co.z > 0.75]
    giro = math.pi if sum(v.y for v in alto) / len(alto) > 0 else 0.0
    for lado, x in (("izq", -1.95), ("der", 1.95)):
        for i, y in enumerate((-5.5, -3.4, -1.3, 0.8, 2.9)):
            if f"BANCA_{lado}_{i}" in esc.objects:
                _poner(col, banca, f"PASE_banca_{lado}_{i}", (x, y, 0), giro)

    # 4 · Columnas: una sola del kit (el de nueve en círculo), en cada sitio
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(A, "columnas-goticas", "columnas-goticas.glb"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    fuste = next(o for o in nuevos if o.type == "MESH" and o.data.materials[0].name.startswith("GothCol"))
    fuste.data.transform(fuste.matrix_world)
    fuste.matrix_world = Matrix()
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(fuste.data)
    fuera = [v for v in bm.verts if not (-2.8 < v.co.x < 3.4 and -28.2 < v.co.y < -21.8)]
    bmesh.ops.delete(bm, geom=fuera, context="VERTS")
    bm.to_mesh(fuste.data)
    bm.free()
    for o in nuevos:
        if o != fuste:
            bpy.data.objects.remove(o)
    columna = _plantilla("columna", [fuste], lambda d: (0.7 / d.x, 0.7 / d.y, 9.35 / d.z))
    piedra = columna.data.materials[0]
    _oscurecer(piedra, (0.3, 0.27, 0.24))
    for lado, x in (("izq", -2.95), ("der", 2.95)):
        for i, y in enumerate((-8, -4.8, -1.6, 1.6, 4.8, 8)):
            _poner(col, columna, f"PASE_columna_{lado}_{i}", (x, y, 0))

    # 5 · Arcos: arcada lateral entre columnas y arcos fajones de lado a lado
    arco = _glb("arco-gotico", 1.0)
    _vestir(arco, piedra)
    amn, amx = _caja([v.co for v in arco.data.vertices])
    ad = amx - amn
    s = 3.2 / ad.x
    for lado, x in (("izq", -2.95), ("der", 2.95)):
        for i, y in enumerate((-6.4, -3.2, 0, 3.2, 6.4)):
            _poner(col, arco, f"PASE_arco_{lado}_{i}", (x, y, 9.35 - ad.z * s), math.pi / 2, s)
    for i, y in enumerate((-4.8, -1.6, 1.6, 4.8)):
        ob = _poner(col, arco, f"PASE_fajon_{i}", (0, y, 0))
        ob.scale = (6.4 / ad.x, 6.4 / ad.x, 9.35 / ad.z)

    # 7/A · Mar de veladoras rojas en los escalones, con hueco al centro y en
    # los candelabros. Seis luces para el conjunto, no una por vela.
    veladora = _glb("veladora", 0.2 / 1.66)
    cera, flama = _cera_roja(), _mat("PASE_flama", (1, 0.5, 0.15), 0.5, (1, 0.45, 0.12), 7)
    for i, s_ in enumerate(veladora.material_slots):
        s_.material = flama if "flama" in (s_.material.name if s_.material else "") else cera
    reservado = [(x, 5.6, 0.5) for x in (-2.3, 2.3)] + [(x, y, 0.15) for x in (-1.5, -0.8, 0.8, 1.5) for y in (5.35,)]
    puestos = []
    while len(puestos) < 70:
        x = random.uniform(-2.5, 2.5)
        y, z = random.choice(((random.uniform(5.12, 5.9), 0.36), (random.uniform(4.66, 5.0), 0.18)))
        if abs(x) < 0.5 or any(abs(x - rx) < r and abs(y - ry) < r for rx, ry, r in reservado):
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 0.11 ** 2 for px, py, _ in puestos):
            continue
        puestos.append((x, y, z))
    for i, p in enumerate(puestos):
        _poner(col, veladora, f"PASE_veladora_{i:02d}", p, random.uniform(0, 6.28))
    # Las cuatro de la mesa del altar pasan a ser veladoras rojas también
    for i in range(4):
        v = esc.objects.get(f"VELADORA_{i}")
        if v:
            mn, mx = _bb(v)
            _poner(col, veladora, f"PASE_veladora_mesa_{i}", ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    for i, x in enumerate((-2.0, -1.2, -0.7, 0.7, 1.2, 2.0)):
        luz = bpy.data.lights.new(f"PASE_luz_veladoras_{i}", "POINT")
        luz.energy, luz.color, luz.shadow_soft_size = 30, (1, 0.55, 0.25), 0.3
        ob = bpy.data.objects.new(luz.name, luz)
        col.objects.link(ob)
        ob.location = (x, 5.3, 0.55)

    # H · Rosas rojas en botes de lata (entre las veladoras) y dos rosales al pie
    rosa = _glb("rosa-roja", 0.45 / 2.495)
    lata = _mat("PASE_lata", (0.55, 0.52, 0.48), 0.35, metal=1.0)
    for i, (x, y) in enumerate(((-1.5, 5.35), (-0.8, 5.35), (0.8, 5.35), (1.5, 5.35))):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.14, location=(x, y, 0.36 + 0.07))
        bote = bpy.context.active_object
        for c in bote.users_collection:
            c.objects.unlink(bote)
        col.objects.link(bote)
        bote.name = f"PASE_bote_{i}"
        _vestir(bote, lata)
        for k in range(5):
            r = _poner(col, rosa, f"PASE_rosa_{i}_{k}",
                       (x + random.uniform(-0.03, 0.03), y + random.uniform(-0.03, 0.03), 0.4),
                       random.uniform(0, 6.28))
            r.rotation_euler.x = random.uniform(-0.25, 0.25)
    rosal = _glb("rosal", 0.7 / 4.096)
    for i, x in enumerate((-2.1, 2.1)):
        _poner(col, rosal, f"PASE_rosal_{i}", (x, 6.9, 0), random.uniform(0, 6.28))

    # C · Velas derretidas: en una punta de la mesa y a los lados del escalón
    derretida = _glb("vela-derretida", lambda d: (0.35 / d.x,) * 3)
    for i, p in enumerate(((-1.5, 7.35, 1.13), (-1.1, 5.85, 0.36), (1.1, 5.85, 0.36))):
        _poner(col, derretida, f"PASE_derretida_{i}", p, random.uniform(0, 6.28))

    # 10/E · Retablo encima del neón y columnas salomónicas flanqueándolo
    retablo = _glb("retablo-pozalmuro", 1.0)
    _poner(col, retablo, "PASE_retablo", (0, 8.3, 5.35))
    salomonica = _glb("columna-salomonica", 2.6 / 1.385)
    for i, x in enumerate((-1.55, 1.55)):
        _poner(col, salomonica, f"PASE_salomonica_{i}", (x, 8.25, 2.85))

    # 17 · Vitrales: el redondo arriba del ventanal, Southwark en lo demás
    cupula = _glb("vitral-cupula", 1.0)
    southwark = _glb("vitral-southwark", 1.0)
    for lado, x in (("izq", -3.3), ("der", 3.3)):
        for i in range(4):
            v = esc.objects.get(f"VENTANA_vidrio_{lado}_lanceta_{i}")
            if v:
                _encajar(col, southwark, f"PASE_vitral_{lado}_{i}", _bb(v), "y")
        v = esc.objects.get(f"VENTANA_vidrio_{lado}_ventanal")
        if v:
            mn, mx = _bb(v)
            _encajar(col, cupula, f"PASE_vitral_{lado}_rosa", (Vector((mn.x, mn.y, 4.0)), mx), "y")
            _encajar(col, southwark, f"PASE_vitral_{lado}_bajo", (mn, Vector((mx.x, mx.y, 3.95))), "y")

    # I · Sahumerio colgado del techo con su cadena, junto al ventanal izquierdo
    sahumerio = _glb("sahumerio", 0.1)
    _poner(col, sahumerio, "PASE_sahumerio", (-2.2, 5.3, 2.3))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=9.35 - 3.26, location=(-2.2, 5.3, (9.35 + 3.26) / 2))
    cadena = bpy.context.active_object
    for c in cadena.users_collection:
        c.objects.unlink(cadena)
    col.objects.link(cadena)
    cadena.name = "PASE_sahumerio_cadena"
    _vestir(cadena, _mat("PASE_hierro", (0.05, 0.045, 0.04), 0.6, metal=1.0))

    # B · Reja de comulgatorio: dos tramos, con el pasillo abierto
    reja = _blend("reja-hierro", ("large_iron_gate", "large_iron_gate_left_door",
                                  "large_iron_gate_right_door", "large_iron_gate_bolt"),
                  lambda d: (1.7 / d.x, 1.7 / d.x, 1.1 / d.z))
    for i, x in enumerate((-1.75, 1.75)):
        _poner(col, reja, f"PASE_reja_{i}", (x, 4.4, 0))

    # 19 · Focos de la guirnalda: bombilla real donde estaban los cubitos
    foco = _blend("foco", ("lightbulb_01",), lambda d: (0.11 / d.z,) * 3)
    for i in range(11):
        f = esc.objects.get(f"FOCO_{i}")
        if f:
            mn, mx = _bb(f)
            _poner(col, foco, f"PASE_foco_{i}", ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z - 0.11))

    # 14 · Copa de latón y una botella, en la mesa del altar
    copa = _blend("copas-laton", ("brass_goblet_01",), 1.0, "copa")
    _poner(col, copa, "PASE_copa_0", (-1.38, 6.95, 1.13))
    _poner(col, copa, "PASE_copa_1", (1.3, 7.2, 1.13))
    botella = _blend("botellas-vino", ("wine_bottles_01_bordeaux",), 1.0, "botella")
    _poner(col, botella, "PASE_botella", (-1.55, 7.2, 1.13))

    # F · Óleos en marcos dorados, por encima de las lancetas
    oleos = (("villalpando-adan-eva", "marco-1", -3.13, 0.0, 1.7),
             ("villalpando-dolorosa", "marco-2", 3.13, -3.2, 1.3),
             ("villalpando-anunciacion", "marco-1", 3.13, 3.2, 1.3),
             ("echave-porciuncula", "marco-2", -3.13, -3.2, 1.3))
    for n, marco, x, y, alto in oleos:
        _oleo(col, n, marco, x, y, 4.5, alto)

    # G · Exvotos: el corazón enmarcado y una rejilla de placas en el muro izq.
    img = bpy.data.images.load(os.path.join(A, "oleos", "exvoto-corazon-cc0.jpg"), check_existing=True)
    m = _mat("PASE_exvoto", (1, 1, 1), 0.4, metal=0.3)
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = img
    m.node_tree.links.new(t.outputs["Color"], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    for k in range(9):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(-3.14, 2.1 + (k % 3) * 0.28, 1.3 + (k // 3) * 0.4))
        p = bpy.context.active_object
        for c in p.users_collection:
            c.objects.unlink(p)
        col.objects.link(p)
        p.name = f"PASE_exvoto_{k}"
        p.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        p.scale = (0.18 * img.size[0] / img.size[1], 0.18, 1)
        _vestir(p, m)

    bpy.context.view_layer.update()
    return {o.name: [round(c, 2) for c in o.location] for o in col.objects}


def _oleo(col, imagen, marco, x, y, z, alto):
    """Marco de Poly Haven con el lienzo sustituido por el óleo, cara a la nave."""
    base = marco.replace("marco-", "fancy_picture_frame_0")
    pl = _blend(marco, (base, base + "_canvas"), 1.0, f"{marco}_{imagen}")
    img = bpy.data.images.load(os.path.join(A, "oleos", imagen + ".jpg"), check_existing=True)
    m = bpy.data.materials.new("PASE_oleo_" + imagen)
    m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = img
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.35      # barniz
    m.node_tree.links.new(t.outputs["Color"], p.inputs["Base Color"])
    lienzo = [i for i, s in enumerate(pl.material_slots) if s.material and "_canvas" in s.material.name]
    for i in lienzo:
        pl.material_slots[i].material = m
    mn, mx = _caja([v.co for v in pl.data.vertices])
    d = mx - mn
    fino = "x" if d.x < d.y else "y"
    ancho = d.y if fino == "x" else d.x
    s = alto / d.z
    # El lienzo se estira al formato del óleo
    k = (img.size[0] / img.size[1]) / (ancho / d.z)
    ob = _poner(col, pl, "PASE_oleo_" + imagen, (x, y, z - alto / 2))
    ob.scale = (s * k, s, s) if fino == "y" else (s, s * k, s)
    # La cara del lienzo mira a la nave (hacia x = 0)
    normal = sum((pol.normal * pol.area for pol in pl.data.polygons if pol.material_index in lienzo), Vector())
    giro = 0.0
    if fino == "y":
        giro = math.pi / 2 if (normal.y < 0) == (x < 0) else -math.pi / 2
    elif (normal.x > 0) != (x < 0):
        giro = math.pi
    ob.rotation_euler.z = giro
    return ob

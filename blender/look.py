"""Santuario M⚡T — materiales, luz y atmósfera.

Fase 2. Se aplica sobre la escena que construye `altar.py`:

    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\altar.py").read(), ns); ns["build"]()
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\look.py").read(), ns2); ns2["aplicar()"]

Los colores salen de los tokens OKLCH de DESIGN.md, convertidos aquí mismo, para
que el oro del render y el oro del CSS sean el mismo oro.
"""

import bpy
import math

# ------------------------------------------------------- tokens de DESIGN.md
# (L en 0..1, C, H en grados) — mismos valores que src/styles.
TOKENS = {
    "bg":          (0.07, 0.000, 0.0),
    "bg_raised":   (0.11, 0.006, 60.0),
    "gold":        (0.78, 0.150, 85.0),
    "gold_peak":   (0.88, 0.140, 88.0),
    "gold_shadow": (0.50, 0.100, 78.0),
    "red":         (0.62, 0.220, 30.0),
    "red_glow":    (0.52, 0.200, 28.0),
    # Albedos de render, no colores de pantalla.
    "piedra":      (0.42, 0.008, 60.0),
    "piedra_honda": (0.24, 0.006, 60.0),
}

VELA_COLOR = (1.0, 0.50, 0.18)     # llama, ~1900 K
# Motor por defecto: Cycles. EEVEE deja el oro y el cromo negros porque un
# metal sólo refleja su entorno y aquí el entorno es negro; Cycles lo resuelve
# con rebotes reales. Ver docs/plans, resultado de la fase 2.
MOTOR = "CYCLES"
MUESTRAS = 128

# Potencias calibradas midiendo la luminancia del render, no estimadas.
# Están ajustadas a Cycles, que suma luz rebotada; en EEVEE se ven más bajas.
VELA_W = 140.0                      # potencia por veladora
NEON_W = 1400.0
CENITAL_W = 350.0
CONTRALUZ_W = 260.0                 # rim light frío; sin él, negro sobre negro
NIEBLA = 0.012                      # densidad; Cycles resuelve dispersion multiple y lava la escena con mas


def _oklch_a_lineal(L, C, H):
    """OKLCH -> sRGB lineal, que es el espacio en el que Blender quiere color."""
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(max(0.0, min(1.0, canal)) for canal in (r, g, bl))


def color(nombre):
    r, g, b = _oklch_a_lineal(*TOKENS[nombre])
    return (r, g, b, 1.0)


def _fijar(bsdf, nombre, valor):
    """Los nombres de socket cambian entre versiones de Blender; no reventar."""
    entrada = bsdf.inputs.get(nombre)
    if entrada is not None:
        entrada.default_value = valor


def _material(nombre, **props):
    mat = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    for clave, valor in props.items():
        _fijar(bsdf, clave.replace("_", " ").title().replace("Ior", "IOR"), valor)
    return mat


def _materiales():
    piedra = _material(
        "MTO_piedra", base_color=color("piedra"), roughness=0.92, metallic=0.0)
    piedra_oscura = _material(
        "MTO_piedra_oscura", base_color=color("piedra_honda"), roughness=0.95)
    oro = _material(
        "MTO_oro", base_color=color("gold"), metallic=1.0, roughness=0.33)
    oro_viejo = _material(
        "MTO_oro_viejo", base_color=color("gold_shadow"), metallic=1.0,
        roughness=0.45)
    neon = _material("MTO_neon", base_color=color("red"), roughness=0.4)
    _fijar(neon.node_tree.nodes["Principled BSDF"], "Emission Color", color("red"))
    _fijar(neon.node_tree.nodes["Principled BSDF"], "Emission Strength", 2.6)
    _tallar(neon, escala=60.0, fuerza=0.06)
    cera = _material(
        "MTO_cera", base_color=(0.85, 0.80, 0.70, 1.0), roughness=0.55,
        subsurface_weight=0.35, ior=1.45)
    llama = _material("MTO_llama", base_color=VELA_COLOR + (1.0,), roughness=1.0)
    _fijar(llama.node_tree.nodes["Principled BSDF"], "Emission Color",
           VELA_COLOR + (1.0,))
    _fijar(llama.node_tree.nodes["Principled BSDF"], "Emission Strength", 7.0)
    vinilo = _material(
        "MTO_vinilo", base_color=(0.012, 0.012, 0.014, 1.0), roughness=0.22)
    cromo = _material(
        "MTO_cromo", base_color=(0.78, 0.78, 0.80, 1.0), metallic=1.0,
        roughness=0.12)
    vidrio = _material(
        "MTO_vidrio", base_color=(0.86, 0.88, 0.86, 1.0), roughness=0.05,
        transmission_weight=0.97, ior=1.45)
    ceniza = _material(
        "MTO_ceniza", base_color=(0.16, 0.15, 0.14, 1.0), roughness=0.95)
    papel = _material(
        "MTO_papel", base_color=(0.055, 0.070, 0.045, 1.0), roughness=0.86)
    brasa = _material("MTO_brasa", base_color=(0.9, 0.25, 0.05, 1.0), roughness=0.9)
    _fijar(brasa.node_tree.nodes["Principled BSDF"], "Emission Color",
           (1.0, 0.28, 0.06, 1.0))
    _fijar(brasa.node_tree.nodes["Principled BSDF"], "Emission Strength", 4.0)
    madera = _material(
        "MTO_madera", base_color=(0.055, 0.032, 0.020, 1.0), roughness=0.62)
    fieltro = _material(
        "MTO_fieltro", base_color=(0.030, 0.026, 0.024, 1.0), roughness=0.95)
    hierro = _material(
        "MTO_hierro", base_color=(0.16, 0.15, 0.15, 1.0), metallic=1.0,
        roughness=0.55)
    terciopelo = _material(
        "MTO_terciopelo", base_color=(0.020, 0.010, 0.008, 1.0), roughness=0.98)
    _fijar(terciopelo.node_tree.nodes["Principled BSDF"], "Sheen Weight", 0.6)
    laton = _material(
        "MTO_laton", base_color=(0.62, 0.45, 0.18, 1.0), metallic=1.0,
        roughness=0.52)
    hueso = _material(
        "MTO_hueso", base_color=(0.62, 0.58, 0.50, 1.0), roughness=0.55)
    plata = _material(
        "MTO_plata", base_color=(0.42, 0.43, 0.45, 1.0), metallic=1.0,
        roughness=0.42)
    plastico = _material(
        "MTO_plastico", base_color=(0.015, 0.015, 0.017, 1.0), roughness=0.35)
    ceramica = _material(
        "MTO_ceramica", base_color=(0.030, 0.026, 0.024, 1.0), roughness=0.25)
    bombilla = _material("MTO_bombilla", base_color=(1.0, 0.72, 0.38, 1.0),
                         roughness=0.3)
    _fijar(bombilla.node_tree.nodes["Principled BSDF"], "Emission Color",
           (1.0, 0.64, 0.30, 1.0))
    _fijar(bombilla.node_tree.nodes["Principled BSDF"], "Emission Strength", 3.2)
    alfombra = _material(
        "MTO_alfombra", base_color=(0.085, 0.012, 0.010, 1.0), roughness=0.95)
    _fijar(alfombra.node_tree.nodes["Principled BSDF"], "Sheen Weight", 0.4)
    tequila = _material(
        "MTO_tequila", base_color=(0.72, 0.62, 0.42, 1.0), roughness=0.02,
        transmission_weight=0.96, ior=1.36)
    corcho = _material(
        "MTO_corcho", base_color=(0.045, 0.032, 0.026, 1.0), roughness=0.72)
    return {
        "alfombra": alfombra, "tequila": tequila, "corcho": corcho,
        "plata": plata, "plastico": plastico, "ceramica": ceramica,
        "bombilla": bombilla,
        "terciopelo": terciopelo, "laton": laton, "hueso": hueso,
        "madera": madera, "fieltro": fieltro, "hierro": hierro,
        "vidrio": vidrio, "ceniza": ceniza, "papel": papel, "brasa": brasa,
        "piedra": piedra, "piedra_oscura": piedra_oscura, "oro": oro,
        "oro_viejo": oro_viejo, "neon": neon, "cera": cera, "llama": llama,
        "vinilo": vinilo, "cromo": cromo,
    }


# Prefijo de nombre -> material. El primero que casa, gana.
ASIGNACION = (
    ("NAVE_", "piedra"),
    ("RETABLO_", "piedra"),
    ("COLUMNA_", "piedra"),
    ("ESCALON_", "piedra"),
    ("ALTAR_", "piedra"),
    ("HORNACINA_marco", "oro"),
    ("PROXY_hornacina", "piedra_oscura"),
    ("CRUZ_", "neon"),
    ("VELADORA_", "cera"),
    ("VINILO_pila", "vinilo"),
    ("VINILO_", "vinilo"),
    ("PROXY_vinilo", "vinilo"),
    ("PROXY_micro", "cromo"),
    ("MICRO_rejilla", "cromo"),
    ("PROXY_cadena", "oro"),
    ("PROXY_placa", "oro"),
    ("ETIQUETA_", "oro"),
    ("PROP_cenicero_hueco", "ceniza"),
    ("PROP_cenicero", "vidrio"),
    ("PROP_brasa", "brasa"),
    ("PROP_cigarro", "papel"),
    ("PROP_botella", "vidrio"),
    ("PROP_billete", "papel"),
    ("PROP_cera", "cera"),
    ("PROP_escapulario_cordon", "hueso"),
    ("PROP_escapulario", "fieltro"),
    ("PROP_rosario_nicho", "madera"),
    ("PROP_rosario_cruz", "madera"),
    ("PROP_cubana", "oro"),
    ("PROP_dije_rayo", "oro"),
    ("PROP_pitiado", "hueso"),
    ("PROP_cinturon", "fieltro"),
    ("PROP_hebilla_hueco", "piedra_oscura"),
    ("PROP_hebilla", "oro"),
    ("ALFOMBRA_franja", "oro"),
    ("ALFOMBRA_", "alfombra"),
    ("PROP_botella_liquido", "tequila"),
    ("PROP_botella_tapon", "corcho"),
    ("PROP_botella_cinta", "corcho"),
    ("PROP_botella_lazo", "corcho"),
    ("PROP_botella", "vidrio"),
    ("PROP_marcador", "plastico"),
    ("PROP_anillo", "plata"),
    ("PROP_pua", "hueso"),
    ("PROP_lentes", "plastico"),
    ("PROP_ceramica", "ceramica"),
    ("PROP_gorra", "fieltro"),
    ("PROP_tololoche", "madera"),
    ("FOCO_", "bombilla"),
    ("PROP_polaroid_img", "foto"),
    ("PROP_polaroid", "hueso"),
    ("PROP_tapete", "terciopelo"),
    ("PROP_frasco", "vidrio"),
    ("PROP_caja_forro", "terciopelo"),
    ("PROP_caja", "madera"),
    ("PROP_pluma_punta", "oro"),
    ("PROP_pluma", "hueso"),
    ("EXVOTO_repisa", "piedra"),
    ("EXVOTO_", "laton"),
    ("CONFETI_", "oro"),
    ("COLILLA_", "papel"),
    ("PROP_sombrero", "fieltro"),
    ("PROP_requinto", "madera"),
    ("PROP_rosario", "oro"),
    ("PROP_vaso", "vidrio"),
    ("PROP_cerillos", "papel"),
    ("BANCA_", "madera"),
    ("CANDELABRO_", "hierro"),
)


FOTOS = (
    r"E:\Cursor Projects\MTO\public\band\band-1.jpg",
    r"E:\Cursor Projects\MTO\public\band\band-2.jpg",
    r"E:\Cursor Projects\MTO\public\band\band-3.jpg",
)


def _materiales_foto():
    """Las polaroids llevan fotos reales de la banda, no siluetas inventadas."""
    hechos = []
    for indice, ruta in enumerate(FOTOS):
        nombre = "MTO_foto_%d" % indice
        mat = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        _fijar(bsdf, "Roughness", 0.32)
        try:
            imagen = bpy.data.images.load(ruta, check_existing=True)
        except RuntimeError:
            hechos.append(None)
            continue
        textura = mat.node_tree.nodes.new("ShaderNodeTexImage")
        textura.image = imagen
        mat.node_tree.links.new(textura.outputs["Color"], bsdf.inputs["Base Color"])
        hechos.append(mat)
    return hechos


def _tallar(mat, escala=14.0, fuerza=0.35):
    """Relieve procedural: la piedra lisa delata el render de inmediato."""
    arbol = mat.node_tree
    bsdf = arbol.nodes.get("Principled BSDF")
    if bsdf is None or bsdf.inputs["Normal"].is_linked:
        return mat
    ruido = arbol.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = escala
    ruido.inputs["Detail"].default_value = 8.0
    ruido.inputs["Roughness"].default_value = 0.62
    celdas = arbol.nodes.new("ShaderNodeTexVoronoi")
    celdas.inputs["Scale"].default_value = escala * 0.35
    mezcla = arbol.nodes.new("ShaderNodeMix")
    mezcla.data_type = "FLOAT"
    mezcla.inputs["Factor"].default_value = 0.45
    arbol.links.new(ruido.outputs["Fac"], mezcla.inputs[2])
    arbol.links.new(celdas.outputs["Distance"], mezcla.inputs[3])
    relieve = arbol.nodes.new("ShaderNodeBump")
    relieve.inputs["Strength"].default_value = fuerza
    arbol.links.new(mezcla.outputs[0], relieve.inputs["Height"])
    arbol.links.new(relieve.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _ensuciar(mat, escala=9.0, minimo=0.25, maximo=0.75):
    """Rugosidad variable con ruido: ninguna superficie real es uniforme."""
    arbol = mat.node_tree
    bsdf = arbol.nodes.get("Principled BSDF")
    if bsdf is None or bsdf.inputs["Roughness"].is_linked:
        return mat
    ruido = arbol.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = escala
    ruido.inputs["Detail"].default_value = 6.0
    rango = arbol.nodes.new("ShaderNodeMapRange")
    rango.inputs["To Min"].default_value = minimo
    rango.inputs["To Max"].default_value = maximo
    arbol.links.new(ruido.outputs["Fac"], rango.inputs["Value"])
    arbol.links.new(rango.outputs["Result"], bsdf.inputs["Roughness"])
    return mat


def _asignar(mats):
    aplicados = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        for prefijo, clave in ASIGNACION:
            if ob.name.startswith(prefijo):
                ob.data.materials.clear()
                ob.data.materials.append(mats[clave])
                aplicados[ob.name] = clave
                break
    return aplicados


def _velas(col, mats):
    """Cada veladora lleva su punto de luz: en EEVEE la emisión no ilumina."""
    for ob in [o for o in bpy.data.objects if o.name.startswith("VELADORA_")]:
        x, y, z = ob.matrix_world.translation
        bpy.ops.object.light_add(type="POINT", location=(x, y, z + 0.16))
        luz = bpy.context.object
        luz.name = "LUZ_" + ob.name
        luz.data.energy = VELA_W
        luz.data.color = VELA_COLOR
        luz.data.shadow_soft_size = 0.02
        for otra in list(luz.users_collection):
            otra.objects.unlink(luz)
        col.objects.link(luz)

        # mecha encendida, para que la llama se vea además de iluminar
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.022, segments=10, ring_count=6, location=(x, y, z + 0.14))
        flama = bpy.context.object
        flama.name = "LLAMA_" + ob.name
        flama.scale = (1.0, 1.0, 2.1)
        flama.data.materials.append(mats["llama"])
        for otra in list(flama.users_collection):
            otra.objects.unlink(flama)
        col.objects.link(flama)


def _luces(col):
    for ob in [o for o in bpy.data.objects if o.name.startswith("GREYBOX_")]:
        bpy.data.objects.remove(ob, do_unlink=True)

    cruz = bpy.data.objects.get("CRUZ_vertical")
    if cruz:
        x, y, z = cruz.matrix_world.translation
        bpy.ops.object.light_add(type="AREA", location=(x, y - 0.35, z + 0.2))
        neon = bpy.context.object
        neon.name = "LUZ_neon"
        neon.data.energy = NEON_W
        neon.data.color = _oklch_a_lineal(*TOKENS["red_glow"])
        neon.data.size = 2.2
        neon.rotation_euler = (math.radians(90), 0, 0)
        for otra in list(neon.users_collection):
            otra.objects.unlink(neon)
        col.objects.link(neon)

    # Contraluz frío lateral: sin él, el vinilo, el micro y el tololoche son
    # siluetas negras sobre fondo negro. Es luz de cámara, no color de marca:
    # define bordes sin teñir la escena.
    # La posición del altar se lee de la escena: las constantes viven en
    # altar.py y duplicarlas aquí sería garantizar que se desincronicen.
    altar = bpy.data.objects.get("ALTAR_bloque")
    altar_y = altar.matrix_world.translation.y if altar else 7.0
    for signo in (-1, 1):
        bpy.ops.object.light_add(
            type="AREA", location=(signo * 2.6, altar_y - 1.2, 2.6))
        rim = bpy.context.object
        rim.name = "LUZ_contraluz_%d" % signo
        rim.data.energy = CONTRALUZ_W
        rim.data.color = (0.38, 0.55, 0.85)
        rim.data.size = 2.4
        rim.rotation_euler = (math.radians(75), 0, math.radians(-95 * signo))
        for otra in list(rim.users_collection):
            otra.objects.unlink(rim)
        col.objects.link(rim)

    # Cenital fría: separa la arquitectura del negro sin iluminar el suelo.
    bpy.ops.object.light_add(type="AREA", location=(0, 2.0, 8.6))
    cenital = bpy.context.object
    cenital.name = "LUZ_cenital"
    cenital.data.energy = CENITAL_W
    cenital.data.color = (0.62, 0.66, 0.80)
    cenital.data.size = 3.0
    for otra in list(cenital.users_collection):
        otra.objects.unlink(cenital)
    col.objects.link(cenital)


def _mundo_y_niebla():
    mundo = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = mundo
    mundo.use_nodes = True
    arbol = mundo.node_tree
    for nodo in list(arbol.nodes):
        arbol.nodes.remove(nodo)
    salida = arbol.nodes.new("ShaderNodeOutputWorld")
    fondo = arbol.nodes.new("ShaderNodeBackground")
    fondo.inputs[0].default_value = color("bg")
    fondo.inputs[1].default_value = 0.04
    dispersion = arbol.nodes.new("ShaderNodeVolumeScatter")
    dispersion.inputs["Color"].default_value = (0.75, 0.68, 0.60, 1.0)
    dispersion.inputs["Density"].default_value = NIEBLA
    dispersion.inputs["Anisotropy"].default_value = 0.45
    arbol.links.new(fondo.outputs[0], salida.inputs["Surface"])
    arbol.links.new(dispersion.outputs[0], salida.inputs["Volume"])


def _render():
    escena = bpy.context.scene
    escena.render.engine = "BLENDER_EEVEE"
    escena.render.image_settings.color_mode = "RGB"
    eevee = escena.eevee
    for atributo, valor in (
        ("use_raytracing", True),
        ("use_volumetric_shadows", True),
        ("use_shadows", True),
        ("use_volume_custom_range", True),
        ("volumetric_start", 0.3),
        ("volumetric_end", 40.0),
        ("volumetric_samples", 96),
        ("taa_render_samples", 64),
    ):
        if hasattr(eevee, atributo):
            setattr(eevee, atributo, valor)
    escena.view_settings.view_transform = "AgX"
    # El enum de "look" depende del view transform ya fijado; puede no existir.
    disponibles = [i.identifier for i in
                   escena.view_settings.bl_rna.properties["look"].enum_items]
    for candidato in ("AgX - Medium High Contrast", "Medium High Contrast"):
        if candidato in disponibles:
            escena.view_settings.look = candidato
            break


def _compositor():
    """Blender 5 sacó el compositor a un node group con entrada y salida propias:
    ya no existen los nodos Render Layers ni Composite dentro del árbol."""
    escena = bpy.context.scene
    arbol = escena.compositing_node_group
    if arbol is None:
        arbol = bpy.data.node_groups.new("MTO_compositor", "CompositorNodeTree")
        escena.compositing_node_group = arbol
    escena.use_nodes = True
    for nodo in list(arbol.nodes):
        arbol.nodes.remove(nodo)

    nombres = [s.name for s in arbol.interface.items_tree]
    if "Image" not in nombres:
        arbol.interface.new_socket(
            "Image", in_out="INPUT", socket_type="NodeSocketColor")
        arbol.interface.new_socket(
            "Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    entrada = arbol.nodes.new("NodeGroupInput")
    salida = arbol.nodes.new("NodeGroupOutput")
    salida.location = (600, 0)
    brillo = arbol.nodes.new("CompositorNodeGlare")
    brillo.location = (300, 0)
    # El Glare se configura por sockets, no por propiedades.
    for socket, valor in (
        ("Type", "BLOOM"), ("Quality", "HIGH"), ("Threshold", 0.85),
        ("Strength", 0.35), ("Size", 7.0), ("Smoothness", 0.4),
    ):
        entrada_socket = brillo.inputs.get(socket)
        if entrada_socket is None:
            continue
        try:
            entrada_socket.default_value = valor
        except TypeError:
            pass  # socket de menú con otro juego de opciones

    arbol.links.new(entrada.outputs[0], brillo.inputs["Image"])
    arbol.links.new(brillo.outputs["Image"], salida.inputs[0])


def aplicar():
    col = bpy.data.collections.get("SANTUARIO")
    mats = _materiales()
    _ensuciar(mats["piedra"], escala=6.0, minimo=0.70, maximo=0.98)
    _tallar(mats["piedra"], escala=14.0, fuerza=0.4)
    _tallar(mats["oro"], escala=45.0, fuerza=0.12)
    _ensuciar(mats["alfombra"], escala=90.0, minimo=0.88, maximo=1.0)
    mats["foto"] = mats["hueso"]  # sustituido abajo por las fotos reales
    fotos = _materiales_foto()
    _ensuciar(mats["oro"], escala=22.0, minimo=0.22, maximo=0.52)
    _ensuciar(mats["cromo"], escala=30.0, minimo=0.06, maximo=0.20)
    aplicados = _asignar(mats)
    for indice, mat in enumerate(fotos):
        ob = bpy.data.objects.get("PROP_polaroid_img_%d" % indice)
        if ob is not None and mat is not None:
            ob.data.materials.clear()
            ob.data.materials.append(mat)
    _luces(col)
    _velas(col, mats)
    _mundo_y_niebla()
    _render()
    motor(MOTOR, MUESTRAS)
    # El compositor queda fuera a propósito: en Blender 5 el árbol vive en un
    # node group cuya entrada no recibe la imagen del render, y hasta un grupo
    # en passthrough devuelve negro. El glow del neón se hace en post con
    # ffmpeg en scripts/build-scene.sh, que además no obliga a re-renderizar
    # para ajustarlo.
    bpy.context.view_layer.update()
    return {"materiales": len(mats), "objetos_con_material": len(aplicados)}


def motor(nombre, samples=128):
    """Fija el motor de render. 'CYCLES' o 'BLENDER_EEVEE'.

    Cycles no aparece en el enum de `RenderSettings.bl_rna` aunque esté
    habilitado: los motores de add-on no se listan ahí. Se asigna directo.
    """
    escena = bpy.context.scene
    escena.render.engine = nombre
    if nombre == "CYCLES":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for tipo in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = tipo
                break
            except TypeError:
                continue
        prefs.get_devices()
        for dispositivo in prefs.devices:
            dispositivo.use = dispositivo.type in ("OPTIX", "CUDA")
        ciclos = escena.cycles
        ciclos.device = "GPU"
        ciclos.samples = samples
        ciclos.use_denoising = True
        if hasattr(ciclos, "denoiser"):
            try:
                ciclos.denoiser = "OPTIX"
            except TypeError:
                pass
        ciclos.max_bounces = 8
        ciclos.volume_bounces = 2
        ciclos.caustics_reflective = False
    else:
        escena.eevee.taa_render_samples = max(32, samples // 2)
    return escena.render.engine

"""Bruma baja que pasa DELANTE del titular en las estaciones sin capa de frente.

Sonido y reliquia son planos macro: entre la cámara y el sujeto no hay nada, así
que la capa de frente no existe y ningún objeto puede tapar las letras. Lo que
tapa aquí es aire: una caja de volumen colgada de la cámara, en la mitad baja
del cuadro, entre el objetivo y la mesa. Se renderiza sola y con alfa; el resto
de la escena queda invisible a cámara pero sigue iluminándola.

Procedural, sin simulación: no hay caché que hornear ni que versionar. El loop
cierra solo: la densidad es un fundido entre dos ruidos desfasados un periodo,
así que el cuadro N vale exactamente lo que el cuadro 0.

    h = {}
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\humo.py").read(), h)
    h["render_bruma"](r"E:\\Cursor Projects\\MTO\\tmp\\bruma", "sonido", cuadros=1)

No toca nada de altar.py: crea `FX_bruma` y lo borra al terminar.
"""

import os

import bpy

# estación -> frame de Blender, el mismo de blender/altar.py
ESTACIONES = {
    "sonido": 61,
    "reliquia": 121,
}
CUADROS = 90          # 3 s a 30 fps: humo lento, 60 seria 2.5x render y peso sin verse
DENSIDAD = 8.0
# Luz de vela dispersada. Sin esto, tras el velo de la web (x0.38) la bruma sale
# más oscura que el fondo y no se ve: la iluminación real de las velas no basta.
EMISION = 0.8
COLOR_EMISION = (1.0, 0.72, 0.45)
DERIVA = 0.35         # m que se desplaza la bruma en un loop, de izquierda a derecha
ESCALA_RUIDO = 0.9
COLOR = (0.62, 0.55, 0.48)  # gris cálido: la luz de las velas lo tiñe el resto


def _material():
    mat = bpy.data.materials.new("FX_bruma")
    mat.use_nodes = True
    nodos, enlaces = mat.node_tree.nodes, mat.node_tree.links
    nodos.clear()
    salida = nodos.new("ShaderNodeOutputMaterial")
    volumen = nodos.new("ShaderNodeVolumePrincipled")
    volumen.inputs["Color"].default_value = (*COLOR, 1.0)
    volumen.inputs["Anisotropy"].default_value = 0.3   # dispersa hacia delante: brilla a contraluz
    enlaces.new(volumen.outputs["Volume"], salida.inputs["Volume"])

    coords = nodos.new("ShaderNodeTexCoord")
    tiempo = nodos.new("ShaderNodeValue")
    tiempo.name = "tiempo"   # 0..1 a lo largo del loop

    def ruido(desfase):
        # W avanza con el tiempo y la textura deriva en X; `desfase` = -1
        # devuelve el mismo ruido un periodo antes.
        t = nodos.new("ShaderNodeMath")
        t.operation = "ADD"
        enlaces.new(tiempo.outputs[0], t.inputs[0])
        t.inputs[1].default_value = desfase
        deriva = nodos.new("ShaderNodeCombineXYZ")
        mult = nodos.new("ShaderNodeMath")
        mult.operation = "MULTIPLY"
        enlaces.new(t.outputs[0], mult.inputs[0])
        mult.inputs[1].default_value = -DERIVA
        enlaces.new(mult.outputs[0], deriva.inputs["X"])
        mover = nodos.new("ShaderNodeVectorMath")
        mover.operation = "ADD"
        enlaces.new(coords.outputs["Object"], mover.inputs[0])
        enlaces.new(deriva.outputs[0], mover.inputs[1])
        tex = nodos.new("ShaderNodeTexNoise")
        tex.noise_dimensions = "4D"
        tex.inputs["Scale"].default_value = ESCALA_RUIDO
        tex.inputs["Detail"].default_value = 3.0
        tex.inputs["Roughness"].default_value = 0.6
        enlaces.new(mover.outputs[0], tex.inputs["Vector"])
        w = nodos.new("ShaderNodeMath")
        w.operation = "MULTIPLY"
        enlaces.new(t.outputs[0], w.inputs[0])
        w.inputs[1].default_value = 0.6
        enlaces.new(w.outputs[0], tex.inputs["W"])
        return tex.outputs["Fac"]

    fundido = nodos.new("ShaderNodeMix")
    fundido.data_type = "FLOAT"
    enlaces.new(tiempo.outputs[0], fundido.inputs["Factor"])
    enlaces.new(ruido(0.0), fundido.inputs["A"])
    enlaces.new(ruido(-1.0), fundido.inputs["B"])

    # Ruido -> jirones: sólo lo que pasa de 0.5 es bruma, con borde corto.
    rango = nodos.new("ShaderNodeMapRange")
    rango.inputs["From Min"].default_value = 0.5
    rango.inputs["From Max"].default_value = 0.62
    enlaces.new(fundido.outputs["Result"], rango.inputs["Value"])

    # Pegada a la mesa: se desvanece hacia arriba del cuadro. La caja es hija de
    # la cámara sin girar, así que su Y local es el "arriba" del cuadro (-1 a 1).
    alto = nodos.new("ShaderNodeSeparateXYZ")
    enlaces.new(coords.outputs["Object"], alto.inputs[0])
    caida = nodos.new("ShaderNodeMapRange")
    caida.inputs["From Min"].default_value = 0.6
    caida.inputs["From Max"].default_value = -1.0
    enlaces.new(alto.outputs["Y"], caida.inputs["Value"])

    densidad = nodos.new("ShaderNodeMath")
    densidad.operation = "MULTIPLY"
    enlaces.new(rango.outputs["Result"], densidad.inputs[0])
    enlaces.new(caida.outputs["Result"], densidad.inputs[1])
    escala = nodos.new("ShaderNodeMath")
    escala.operation = "MULTIPLY"
    enlaces.new(densidad.outputs[0], escala.inputs[0])
    escala.inputs[1].default_value = DENSIDAD
    enlaces.new(escala.outputs[0], volumen.inputs["Density"])
    volumen.inputs["Emission Color"].default_value = (*COLOR_EMISION, 1.0)
    brillo = nodos.new("ShaderNodeMath")
    brillo.operation = "MULTIPLY"
    enlaces.new(densidad.outputs[0], brillo.inputs[0])
    brillo.inputs[1].default_value = EMISION
    enlaces.new(brillo.outputs[0], volumen.inputs["Emission Strength"])
    return mat, tiempo


def crear_bruma(estacion):
    """Caja de volumen en la mitad baja del cuadro, entre la cámara y el sujeto."""
    escena = bpy.context.scene
    escena.frame_set(ESTACIONES[estacion])
    camara = escena.camera
    datos = camara.data
    # Distancia de enfoque = distancia al sujeto: la bruma vive por delante.
    foco = datos.dof.focus_object
    grafo = bpy.context.evaluated_depsgraph_get()
    origen = camara.evaluated_get(grafo).matrix_world.translation
    distancia = (foco.matrix_world.translation - origen).length if foco else 3.0
    cerca, lejos = 0.35 * distancia, 0.85 * distancia
    profundidad = (cerca + lejos) / 2
    medio_ancho = profundidad * datos.sensor_width / (2 * datos.lens) * 1.3

    bpy.ops.mesh.primitive_cube_add(size=2)
    caja = bpy.context.active_object
    caja.name = "FX_bruma"
    # Hija de la cámara: coordenadas locales de cámara, que mira hacia -Z y
    # tiene Y hacia arriba del cuadro. Mitad baja: el centro, medio alto abajo.
    caja.parent = camara
    caja.matrix_parent_inverse.identity()
    caja.location = (0.0, -medio_ancho * 0.35, -profundidad)
    caja.scale = (medio_ancho, medio_ancho * 0.45, (lejos - cerca) / 2)
    mat, tiempo = _material()
    caja.data.materials.append(mat)
    return caja, tiempo


def render_bruma(out_dir, estacion, ancho=960, alto=540, cuadros=CUADROS, muestras=128,
                 desde=0, hasta=None):
    """Renderiza la bruma sola, con alfa. A media resolución: es niebla, no detalle.

    `desde`/`hasta` parten el loop en tandas: 90 cuadros no caben en una llamada MCP.
    """
    escena = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    previo = {
        "x": escena.render.resolution_x, "y": escena.render.resolution_y,
        "muestras": escena.cycles.samples, "denoise": escena.cycles.use_denoising,
        "transparente": escena.render.film_transparent,
        "modo": escena.render.image_settings.color_mode, "frame": escena.frame_current,
    }
    # Todo lo demás, invisible a cámara pero presente para la luz.
    visibles = {o.name: o.visible_camera for o in bpy.data.objects}
    # La niebla del mundo llenaría el alfa: se desconecta mientras dura (ver notas).
    mundo = escena.world
    enlaces_volumen = []
    if mundo and mundo.use_nodes:
        salida = mundo.node_tree.nodes.get("World Output")
        for enlace in list(mundo.node_tree.links):
            if salida and enlace.to_socket == salida.inputs["Volume"]:
                enlaces_volumen.append((enlace.from_socket, enlace.to_socket))
                mundo.node_tree.links.remove(enlace)

    caja, tiempo = crear_bruma(estacion)
    try:
        for ob in bpy.data.objects:
            if ob is not caja:
                ob.visible_camera = False
        escena.render.resolution_x, escena.render.resolution_y = ancho, alto
        escena.cycles.samples = muestras
        escena.cycles.use_denoising = True
        escena.render.film_transparent = True
        escena.render.image_settings.file_format = "PNG"
        escena.render.image_settings.color_mode = "RGBA"
        for i in range(desde, cuadros if hasta is None else hasta):
            # El frame de escena no se mueve: la cámara sigue en la estación.
            tiempo.outputs[0].default_value = i / cuadros
            escena.render.filepath = os.path.join(out_dir, "%s-%03d.png" % (estacion, i))
            bpy.ops.render.render(write_still=True)
    finally:
        mat = caja.data.materials[0]
        bpy.data.objects.remove(caja, do_unlink=True)
        bpy.data.materials.remove(mat)
        for nombre, visible in visibles.items():
            ob = bpy.data.objects.get(nombre)
            if ob:
                ob.visible_camera = visible
        for origen, hacia in enlaces_volumen:
            mundo.node_tree.links.new(origen, hacia)
        escena.render.resolution_x, escena.render.resolution_y = previo["x"], previo["y"]
        escena.cycles.samples = previo["muestras"]
        escena.cycles.use_denoising = previo["denoise"]
        escena.render.film_transparent = previo["transparente"]
        escena.render.image_settings.color_mode = previo["modo"]
        escena.frame_set(previo["frame"])
    return (cuadros if hasta is None else hasta) - desde


# Mitad de la resolución de cada formato de blender/render.py: es niebla.
FORMATOS = {"escritorio": (960, 540), "movil": (450, 800)}

if __name__ == "__main__":
    # Tanda larga en segundo plano, sin el límite de 60 s del MCP:
    #   "E:\Blender\blender.exe" -b -P "E:\Cursor Projects\MTO\blender\humo.py" -- sonido escritorio
    import sys
    argumentos = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argumentos:
        estacion, formato = argumentos[0], argumentos[1]
        raiz = r"E:\Cursor Projects\MTO"
        render = {"__name__": "render"}
        exec(open(os.path.join(raiz, "blender", "render.py")).read(), render)
        render["construir"]()
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles.device = "GPU"
        ancho, alto = FORMATOS[formato]
        destino = os.path.join(raiz, "tmp", "bruma", "%s-%s" % (estacion, formato))
        print("bruma: %d cuadros en %s" % (render_bruma(destino, estacion, ancho, alto), destino))

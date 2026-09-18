"""Render de los tramos y los loops de estación, en los dos formatos.

Se puede ejecutar dentro de Blender (MCP) o en segundo plano, que es lo suyo
para una tanda larga:

    "E:\\Blender\\blender.exe" -b -P "E:\\Cursor Projects\\MTO\\blender\\render.py" -- tramos movil

El último argumento elige formato: `movil` (900x1600) o `escritorio`
(1600x900). Sin argumentos no hace nada: importarlo es barato a propósito.

PNG de 16 bits porque el siguiente paso es comprimir a AVIF, y partir de 8 bits
hace bandas en los degradados de vela, que es lo que más ocupa esta escena.
"""

import os
import sys

import bpy

FORMATOS = {
    "movil": (900, 1600),
    "escritorio": (1920, 1080),
}

ESTACIONES = (1, 31, 61, 91, 121, 151)   # mismos frames que blender/altar.py
FRAMES_POR_TRAMO = 30   # 30 y no 20: a 20 el escalon del scrub se nota
OBTURADOR = 0.25                   # motion blur; ver DECISION en la spec
MUESTRAS = 128

RAIZ = r"E:\Cursor Projects\MTO"


def _escena(formato):
    ancho, alto = FORMATOS[formato]
    escena = bpy.context.scene
    escena.render.engine = "CYCLES"
    escena.cycles.device = "GPU"
    escena.cycles.samples = MUESTRAS
    escena.cycles.use_denoising = True
    escena.render.resolution_x = ancho
    escena.render.resolution_y = alto
    escena.render.resolution_percentage = 100
    escena.render.image_settings.file_format = "PNG"
    escena.render.image_settings.color_depth = "16"
    escena.render.image_settings.compression = 15
    return escena


def construir():
    """Levanta la escena desde el código, como en las notas."""
    espacio = {}
    exec(open(os.path.join(RAIZ, "blender", "altar.py")).read(), espacio)
    espacio["build"]()
    escena = bpy.context.scene
    escena.use_nodes = False
    escena.compositing_node_group = None
    look = {}
    exec(open(os.path.join(RAIZ, "blender", "look.py")).read(), look)
    look["aplicar"]()
    bpy.context.view_layer.update()
    return espacio


def tramos(formato, destino=None, desde=0, hasta=None):
    """Los cinco tramos entre estaciones, con motion blur.

    `desde`/`hasta` acotan qué tramos se hacen, para poder partir la tanda.
    """
    escena = _escena(formato)
    escena.render.use_motion_blur = True
    escena.render.motion_blur_shutter = OBTURADOR
    destino = destino or os.path.join(RAIZ, "tmp", "frames", formato)

    escritos = []
    tramos_ = list(zip(ESTACIONES, ESTACIONES[1:]))[desde:hasta]
    for indice, (inicio, _fin) in enumerate(tramos_, start=desde):
        carpeta = os.path.join(destino, "tramo-%d" % indice)
        os.makedirs(carpeta, exist_ok=True)
        for paso in range(FRAMES_POR_TRAMO):
            escena.frame_set(inicio + paso)
            escena.render.filepath = os.path.join(carpeta, "%03d" % paso)
            bpy.ops.render.render(write_still=True)
            escritos.append(escena.render.filepath + ".png")
    return escritos


def estaciones(formato, destino=None):
    """El frame quieto de cada estación, sin blur. El 0 es el LCP."""
    escena = _escena(formato)
    escena.render.use_motion_blur = False
    destino = destino or os.path.join(RAIZ, "tmp", "frames", formato)
    os.makedirs(destino, exist_ok=True)
    escritos = []
    for indice, frame in enumerate(ESTACIONES):
        escena.frame_set(frame)
        escena.render.filepath = os.path.join(destino, "estacion-%d" % indice)
        bpy.ops.render.render(write_still=True)
        escritos.append(escena.render.filepath + ".png")
    return escritos


def capas(formato, destino=None, espacio=None):
    """La capa con alfa de lo que va DELANTE del texto, una por estacion.

    Vive solo en las estaciones: durante los tramos se oculta. El PNG sale RGBA
    y lo encodea `scripts/build-scene.sh` a WebP, que es el unico formato de los
    dos que conserva el alfa con el ffmpeg de este equipo.
    """
    ancho, alto = FORMATOS[formato]
    destino = destino or os.path.join(RAIZ, "tmp", "frames", formato)
    espacio = espacio or construir()
    return espacio["render_capa_frontal"](destino, ancho, alto)


if __name__ == "__main__":
    argumentos = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if argumentos:
        que, formato = argumentos[0], argumentos[1]
        espacio = construir()
        if que == "tramos":
            hechos = tramos(formato)
        elif que == "capas":
            hechos = capas(formato, espacio=espacio)
        else:
            hechos = estaciones(formato)
        print("render: %d frames en %s" % (len(hechos), formato))

"""Puerta antes de una tanda de render: lo que se puede comprobar en la escena.

Sirve en la escena viva (MCP), antes de renderizar desde ahí:

    pt = {}
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\puerta.py").read(), pt)
    pt["revisar"](r"E:\\Cursor Projects\\MTO\\tmp\\poses-referencia.json")

y en segundo plano sobre la escena recién construida (`scripts/puerta-tanda.sh`).
Devuelve {"ok": bool, "problemas": [...]}; cada problema salió de un fallo real:

- Poses: lo que difiere del volcado aprobado. `build()` borra lo que el usuario
  movió a mano en el visor (docs/HANDOFF.md, "ya pasó una vez").
- Banderas de los pases (`hide_render`, `film_transparent`, `color_mode`,
  `view_transform`, `material_override`): si un pase no las restaura, el
  siguiente render sale negro (docs/handoffs/2026-10-05-movil-y-props.md).
"""

import os

import bpy

RAIZ = r"E:\Cursor Projects\MTO"


def revisar(volcado=None):
    escena = bpy.context.scene
    problemas = []
    if escena.render.film_transparent:
        problemas.append("film_transparent encendido (¿quedó de un pase de máscara o de capa?)")
    if escena.render.image_settings.color_mode != "RGB":
        problemas.append("color_mode %s, no RGB" % escena.render.image_settings.color_mode)
    if escena.view_settings.view_transform != "AgX":
        problemas.append("view_transform %s, no AgX (¿quedó del pase z?)" % escena.view_settings.view_transform)
    for capa in escena.view_layers:
        if capa.material_override is not None:
            problemas.append("material_override %s en %s" % (capa.material_override.name, capa.name))
    # Oculto en el render pero visible en el visor: lo que deja un pase sin restaurar.
    ocultos = sorted(o.name for o in escena.objects
                     if o.type in ("MESH", "LIGHT") and o.hide_render and not o.hide_viewport and o.visible_get())
    if ocultos:
        problemas.append("hide_render en %d objetos visibles en el visor: %s" % (len(ocultos), ", ".join(ocultos[:12])))

    if volcado:
        p = {}
        exec(open(os.path.join(RAIZ, "blender", "poses.py"), encoding="utf-8").read(), p)
        diferencias = p["comparar"](volcado)
        if diferencias["movidos"]:
            problemas.append("poses distintas del volcado: %s" % ", ".join(m["nombre"] for m in diferencias["movidos"][:12]))
        if diferencias["solo_en_volcado"]:
            problemas.append("en el volcado y no en la escena: %s" % ", ".join(diferencias["solo_en_volcado"][:12]))
    return {"ok": not problemas, "problemas": problemas}

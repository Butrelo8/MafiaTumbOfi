"""Atajos de navegacion para la escena, iguales en las dos maquinas.

Ejecutar una vez por maquina, desde el editor de texto de Blender o con:

    blender --python blender/keymap.py

Guarda las preferencias al final: el cambio persiste entre sesiones. Sin eso
los atajos viven solo en la sesion abierta.

    walk  ->  boton 4 del raton  |  Ctrl+Shift+W
    fly   ->  boton 5 del raton  |  Ctrl+Shift+F

Los botones laterales no existen en el trackpad del MacBook y las teclas no
estorban en el escritorio, asi que se asignan los dos juegos en ambas.
Blender ya trae `Shift + \\`` (view3d.navigate), pero esa tecla es incomoda en
teclado ES de Mac.
"""

import sys

import bpy

ATAJOS = [
    ("view3d.walk", "BUTTON4MOUSE", {}),
    ("view3d.fly", "BUTTON5MOUSE", {}),
    ("view3d.walk", "W", {"ctrl": True, "shift": True}),
    ("view3d.fly", "F", {"ctrl": True, "shift": True}),
]

vista = bpy.context.window_manager.keyconfigs.user.keymaps["3D View"]

for operador, tecla, mods in ATAJOS:
    for item in vista.keymap_items:
        mismo = all(getattr(item, m) == v for m, v in mods.items())
        # ponytail: desactivar, no borrar -> reversible desde Preferences > Keymap
        if item.type == tecla and mismo and item.idname != operador:
            item.active = False
    if not any(i.idname == operador and i.type == tecla for i in vista.keymap_items):
        vista.keymap_items.new(operador, tecla, "PRESS", **mods)

if sys.platform == "darwin":
    # En el MacBook no hay numpad ni boton central: se emulan.
    entradas = bpy.context.preferences.inputs
    entradas.use_mouse_emulate_3_button = True   # Alt + clic izquierdo orbita
    entradas.use_emulate_numpad = True           # 1..0 de la fila superior

bpy.ops.wm.save_userpref()
print("keymap: walk = boton 4 / Ctrl+Shift+W, fly = boton 5 / Ctrl+Shift+F")

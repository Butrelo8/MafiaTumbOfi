"""Preferencias y atajos para trabajar la escena en un portatil (MacBook).

Ejecutar una vez por maquina, desde el editor de texto de Blender o con:

    blender --python blender/keymap.py

Guarda las preferencias al final: el cambio persiste entre sesiones.
"""

import bpy

# En un MacBook no hay numpad ni botones laterales: se emulan.
prefs = bpy.context.preferences.inputs
prefs.use_mouse_emulate_3_button = True   # Alt + clic izquierdo = orbitar
prefs.use_emulate_numpad = True           # 1..0 de la fila superior = vistas

# Walk/Fly sin depender de la tecla ` (incomoda en teclado ES de Mac).
ATAJOS = [("view3d.walk", "W"), ("view3d.fly", "F")]

vista = bpy.context.window_manager.keyconfigs.user.keymaps["3D View"]

for operador, tecla in ATAJOS:
    for item in vista.keymap_items:
        # ponytail: desactivar, no borrar -> reversible desde Preferences > Keymap
        if item.type == tecla and item.ctrl and item.shift and item.idname != operador:
            item.active = False
    if not any(i.idname == operador and i.type == tecla for i in vista.keymap_items):
        vista.keymap_items.new(operador, tecla, "PRESS", ctrl=True, shift=True)

bpy.ops.wm.save_userpref()
print("keymap: Ctrl+Shift+W = walk, Ctrl+Shift+F = fly, preferencias guardadas")

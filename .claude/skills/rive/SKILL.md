---
name: rive
description: Anima personajes y UI interactiva con Rive (`.riv` + state machines) usando el MCP `rive-mcp` (sin editor ni suscripción) o el MCP oficial `rive` (editor de escritorio abierto). Dice cuándo Rive y cuándo Blender, el flujo probado PNG → `.riv` rigueado con `riv_rig_character`, sus trampas, precios y licencias. Úsala cuando el usuario diga "anima esta mascota", "personaje que reaccione al hover/clic", "haz un .riv", "Rive", "state machine", "convierte este Lottie/SVG a Rive".
---

# rive

Fuente: `/home/black/projects/visual-lab/web/visuales.md`, secciones
"Herramienta: Rive — precios y MCP" y "Prueba: animar personajes — Rive vs Blender" (probado 2026-09-22).
Si algo aquí contradice ese archivo, gana el archivo: léelo cuando dudes.

## ¿Rive o Blender?

| Qué se quiere | Herramienta | Entrega | Peso | Interactivo |
|---|---|---|---|---|
| Mascota o personaje caricaturesco que reacciona (hover, clic, trigger) | **Rive** (`rive-mcp`) | `.riv` en vivo en el navegador | ~75-100 KB | sí |
| Movimiento humano realista (baile, deporte, gesto) | **Blender** + Mixamo (skill `blender`) | video o frames | ~300 KB / 12 s | no |

Se pueden combinar (Blender renderiza, Rive o el scroll reproducen): **sin probar**.

## MCP: cuál usar

- **`rive-mcp`** (tercero, por defecto): escribe el `.riv` directo y valida con el runtime oficial en
  Chromium. No necesita editor ni plan pago. 32 tools `riv_*`: crear desde JSON, importar SVG y Lottie,
  PNG → personaje rigueado, lint de movimiento, crítica con filmstrip, Studio web local.
  Licencia freeware: uso comercial libre, lo generado es tuyo; **prohíbe analizar su código con IA**: úsalo
  solo por MCP, no leas su código.
- **`rive`** (oficial, 40 tools: `animation_editor`, `mesh_rigging_tool`, `viewmodel_editor`,
  `capture_artboard`, `export_file`…): controla el **editor de escritorio de Windows** (Early Access), que
  debe estar abierto. Desde WSL va por `cmd.exe /c npx -y mcp-remote http://127.0.0.1:9791/mcp`. Si sale
  "failed to connect", la app no está abierta: dilo, no reintentes. Exportar el resultado pide plan Cadet.

## Flujo probado: PNG → `.riv` rigueado (`riv_rig_character`)

Genera parpadeo vectorial, orejas y cola como piezas, cabeza que se ladea (malla de 2 huesos), respiración,
animación `happy` y state machine con trigger `happy`.

1. Personaje **de frente, sentado, cabeza arriba** (la herramienta supone la cabeza en la fracción superior:
   `headRatio`). Personajes echados o humanos no funcionan: eso es Blender.
2. PNG con **~60 px de margen transparente** alrededor (sin él, el lado derecho sale cortado).
   SVG → PNG sin instalar nada:
   `chrome --headless --default-background-color=00000000 --window-size=W,H --screenshot=out.png file.svg`.
3. Ojos, orejas y cola en coordenadas de píxel del PNG. Referencia (zorro 620x680):
   `headRatio 0.53`, `furColor #f07a2a`, ojos `{x:245,y:223,w:30,h:44}` y `{x:345,…}`, cola `behindBody: true`.
4. Preview: `riv_render_gif` con `animation: "happy"`.
5. Rayitas finas en la base de las orejas (corte del polígono): corregir con `riv_edit` o en el editor.

Resultados: dibujo original limpio al primer intento; personaje de caricatura con 3 intentos; **foto de
persona no sirve** (cortes visibles, animaciones de mascota). Usa personajes propios o con licencia.

## Costos y licencias

| Plan Rive | Precio | Importa |
|---|---|---|
| Free | 0 | **No exporta `.riv`** desde el editor |
| Cadet | 9 USD/mes por asiento | Exporta `.riv`, uso comercial |
| Voyager | 32 USD/mes | Librerías, hosting |

`rive-mcp` escribe el `.riv` sin editor, así que el plan Free alcanza para entregar. Archivos de la
comunidad de Rive: CC BY (crédito al autor).

## Trampas

- `rive-mcp` falla con `No Chromium-based browser found` → `RIVE_MCP_CHROME` en el `env` del servidor
  apuntando al Chromium de Playwright (`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`).
- MCP que la sesión no tiene cargado: `/home/black/projects/visual-lab/web/visuales-assets/mcp_stdio.py` lo lanza
  por stdio y llama la tool directo, sin reiniciar.
- Antes de escribir código con el runtime de Rive (`@rive-app/canvas`), consulta la doc actual (context7).

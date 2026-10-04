---
name: blender
description: Movimiento humano realista (baile, deporte, gesto) para web con Mixamo + Blender + ffmpeg, renderizado a video o frames, con el MCP oficial de Blender opcional. Flujo probado de ~10 min, escala 0.01 de Mixamo, render ortográfico, compresión WebM/MP4, y licencia de Mixamo (qué se puede entregar a un cliente). Úsala cuando el usuario diga "una persona bailando", "silueta animada", "animación 3D de un personaje humano", "Mixamo", "render de Blender para el hero".
---

# blender

Fuente: `/mnt/e/Cursor Projects/ProyectoInvestigación/research/visuales.md`, sección
"Prueba: animar personajes — Rive vs Blender" (probado 2026-09-22). Script completo:
`ProyectoInvestigación/research/visuales-assets/bailarina_blender.py`.

## ¿Blender o Rive?

Movimiento humano realista → **Blender** (video, ~300 KB por 12 s, no interactivo).
Mascota que reacciona al hover/clic → skill `rive`.

## Flujo: Mixamo → Blender → ffmpeg (~10 min; el render de 186 frames en EEVEE tardó 38 s)

1. **Mixamo** (mixamo.com, Adobe ID gratis): buscar la animación (p.ej. "Ballet Dance Variation One") en
   el personaje por defecto → Download: FBX Binary, With Skin, 30 fps.
2. **Blender**: importar el FBX; material negro mate (specular 0); fondo claro con
   `view_transform = 'Standard'` (con Filmic/AgX el fondo sale gris); cámara **ortográfica** si el personaje
   se desplaza.
3. **Objetos pegados a un hueso** (p.ej. un tutú en `mixamorig:Hips`): la armadura de Mixamo viene a
   **escala 0.01** → escalar lo emparentado ×100 o sale diminuto.
4. **Render** cada 2 frames → **ffmpeg**: WebM VP9 (264 KB) + MP4 (325 KB) para 12 s, 960x540, 15 fps.

Para enseñarlo a un cliente falta: ropa de verdad (capas, tela), personaje sin juntas visibles, cámara que
siga y un loop que cierre (Trim en Mixamo o fundido).

## MCP de Blender (opcional)

El preset `animacion-blender` agrega el MCP oficial (`projects.blender.org/lab/blender_mcp`, vía `uvx.exe`
de Windows). Controla un Blender abierto.
- Antes de ejecutar código: `get_blendfile_summary_path_info` dice qué archivo está abierto, para no pisar
  otra escena (p.ej. la de MTO).
- `bpy.ops.wm.read_homefile` rompe el contexto del import FBX: borrar los objetos a mano.
- Sin MCP también funciona: `blender -b -P script.py` con el script de la prueba.
- MCP que la sesión no tiene cargado: `ProyectoInvestigación/research/visuales-assets/mcp_stdio.py`.

## Licencia de Mixamo (verificado 2026-09-22)

- **Gratis**, solo Adobe ID (no sirve con IDs Enterprise/Federated). **Royalty free** para uso personal y
  comercial; sin crédito obligatorio.
- **Prohibido:** distribuir los archivos crudos (FBX del personaje o la animación): ni asset packs, ni
  plantillas, **ni entregarlos a clientes**; ni entrenar modelos de ML.
- **Entregar al cliente:** el **video renderizado**, sí. El `.blend` o el FBX, **no**. Un `.glb` animado en
  three.js es zona gris (el archivo se puede extraer): evitarlo o preguntar a Adobe.
- Riesgo: Adobe lo llama "technology preview"; bajar y guardar lo que se vaya a usar.

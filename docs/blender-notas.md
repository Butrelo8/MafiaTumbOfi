# Blender 5.2 — notas de campo

> Todo lo de aquí está verificado en esta máquina el 2026-09-16/17:
> Blender 5.2.2 en Windows, repo en WSL, RTX 4070 Ti, add-on MCP.
> Son las cosas que costaron tiempo. Si vuelves a tocar `blender/`, léelo antes.

## Si acabas de llegar, empieza aquí

**Qué se está construyendo.** El sitio se rehace como una página cuyo scroll
dirige una cámara por un santuario en 3D. La escena no se rinde en el navegador:
son frames pre-renderizados en Cycles que el scroll reproduce sobre un `<canvas>`,
con loops de vídeo cuando el scroll se detiene. Todo el texto sigue siendo HTML
encima.

**Dónde está todo.**

| Archivo | Qué es |
|---|---|
| `docs/specs/2026-09-16-santuario-3d-scroll-design.md` | El diseño aprobado. Manda sobre cualquier improvisación |
| `docs/plans/2026-09-16-santuario-3d-implementation-plan.md` | Fases, puertas y el resultado de cada una, con las correcciones sobre la marcha |
| `blender/altar.py` | Geometría, props y rig de cámara. `build()` levanta la escena entera |
| `blender/look.py` | Materiales, luces, niebla y motor. `aplicar()` la viste |
| `DESIGN.md` | Tokens de color y tipografía del sitio. La escena los consume |

El `.blend` **no** se versiona: la escena es código y se reconstruye en segundos.

**Cómo levantar la escena** (con Blender abierto y el add-on MCP conectado):

```python
ns = {}
exec(open(r"E:\Cursor Projects\MTO\blender\altar.py").read(), ns)
ns["build"]()

escena = bpy.context.scene          # imprescindible: build() no resetea esto
escena.use_nodes = False
escena.compositing_node_group = None

look = {}
exec(open(r"E:\Cursor Projects\MTO\blender\look.py").read(), look)
look["aplicar"]()

ns["render_stills"](r"E:\Cursor Projects\MTO\tmp\prueba", 800, 450)
ns["render_capa_frontal"](r"E:\Cursor Projects\MTO\tmp\prueba-frente", 800, 450)
```

**En qué punto está.** Fases 0, 1 y 2 cerradas: entorno verificado, encuadres
aprobados y look terminado con props. Lo siguiente es la fase 3: calibrar el CRF
contra un AVIF real y renderizar los frames de los cuatro tramos más los loops
de estación, en los dos formatos.

**Decisiones ya tomadas — no las vuelvas a abrir sin motivo nuevo:**

- **Cycles con OptiX**, no EEVEE. Se comparó midiendo: en EEVEE el oro y el
  cromo salen negros.
- **Frames pre-renderizados**, no three.js ni glTF en vivo.
- **El glow del neón va en post con ffmpeg**, no en el compositor de Blender.
- **La capa de primer plano sólo existe en las estaciones**, nunca por frame.
- **Sin sección de fechas** en el sitio (decisión de 2026-09-09).
- **Presupuesto**: 2 MB objetivo por visitante móvil, 3 MB de techo duro.

**La regla que más tiempo ahorra:** en esta escena, mide antes de opinar. La
mitad de las horas perdidas aquí vinieron de creer lo que parecía estar pasando
en vez de comprobarlo. Hay una sección entera sobre eso en las notas generales (abajo).


## Notas generales de Blender 5

Las trampas de API, rig de cámara, medición, render/look, alfa y entorno (no son de MTO) viven en
`/home/black/projects/visual-lab/blender/blender-notas.md` (movidas 2026-10-06). Léelas antes de tocar `blender/`.

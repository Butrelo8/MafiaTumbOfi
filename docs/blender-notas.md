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
en vez de comprobarlo. Hay una sección entera sobre eso más abajo.

## API que cambió en Blender 5

### El motor EEVEE ya no se llama "Next"

El identifier es `BLENDER_EEVEE` y **es** el motor reescrito. `BLENDER_EEVEE_NEXT`
no existe: comprobar por ese nombre da siempre falso.

### Cycles no aparece en el enum de motores, pero está

```python
[i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
# -> ["BLENDER_EEVEE"]   ...y aun así:
bpy.context.scene.render.engine = "CYCLES"   # funciona
```

El enum de `bl_rna` no lista los motores registrados por add-on. Comprobar la
disponibilidad de Cycles por ahí da un falso negativo — nos costó escribir en el
plan que "Cycles no estaba disponible" cuando lo estaba. Para saberlo de verdad,
asigna y mira si lanza excepción.

### El compositor vive en un node group

`scene.node_tree` ya no existe. Ahora es `scene.compositing_node_group`, un
`CompositorNodeTree` con `NodeGroupInput` / `NodeGroupOutput`. Dentro **no**
existen `CompositorNodeRLayers` ni `CompositorNodeComposite`.

Y el aviso importante: montamos un grupo en **passthrough** —entrada conectada
directo a la salida, sin un solo nodo de efecto— y el render salió **negro**. No
conseguimos que la entrada del grupo reciba la imagen del render, y la
documentación del manual no cubre el caso. Por eso el glow del neón se hace en
post con ffmpeg y no en el compositor.

### El nodo Glare se configura por sockets

Ya no tiene `glare_type`, `quality` ni `mix` como propiedades. Todo son entradas:
`Type`, `Quality`, `Threshold`, `Strength`, `Size`, `Smoothness`… Acceder a
`node.glare_type` lanza `KeyError`.

### `view_settings.look` depende del view transform ya fijado

Si consultas el enum antes de fijar `view_transform`, sólo ves `NONE`. Fija
primero el transform, luego lee las opciones y elige entre las que existan.

### Los volumétricos necesitan rango explícito

`volumetric_start` y `volumetric_end` no hacen nada sin
`eevee.use_volume_custom_range = True`.

### `use_raytracing` y `use_volumetric_shadows` vienen apagados

Son justamente lo que da reflejo creíble al metal y haces a la niebla en EEVEE.
Hay que encenderlos a mano.

## Trampas del rig de cámara

### Una curva creada por API no es un camino

`bpy.data.curves.new()` deja `use_path = False`. Con eso, un constraint
`Follow Path` no mueve absolutamente nada y la cámara se queda en el origen, sin
error ni aviso.

```python
curva.use_path = True
curva.path_duration = 100
```

### `Follow Path` es aditivo, no sustitutivo

La posición final es la del objeto **más** la del camino. Suena a detalle
menor y resultó ser un regalo: animando `camara.location.z` se obtiene un canal
de grúa por encima del riel, que es de donde salen el picado de la estación del
sonido y la retirada.

### Los offsets del recorrido se miden, no se estiman

`offset_factor` no se corresponde linealmente con la geometría de la curva.
Estimarlo a ojo dio encuadres muy lejos de lo buscado. Lo que funciona: barrer
`offset_factor` en 41 muestras, anotar la posición real de la cámara en cada una
y quedarse con la más cercana al punto de observación deseado. Si cambia el
recorrido, hay que rehacer la medición.

## Medición y método

### `image.pixels` dentro de Blender no fue fiable

Cargar el PNG recién escrito y leer `.pixels` devolvió **el mismo resultado en
todas las pruebas**, y apuntó al problema equivocado durante un buen rato: nos
hizo creer que la escena estaba sobreexpuesta cuando estaba negra.

Lo que sí funciona, desde fuera:

```bash
ffmpeg -i frame.png -vf "scale=8:5" -f rawvideo -pix_fmt gray - | od -An -tu1
```

Da la luminancia real en 40 puntos. Con eso se calibra exposición con números en
vez de impresiones.

### Compara los md5 antes de sacar conclusiones

Cinco pruebas A/B distintas resultaron ser **byte-idénticas**. Un `md5sum` lo
habría dicho en un segundo, y habría ahorrado media hora de teorías sobre
materiales y luces.

```bash
md5sum tmp/ab/*.png
```

### `build()` no resetea los ajustes de escena

Reconstruir la escena borra objetos, pero `view_settings`, `scene.eevee`,
`use_nodes`, el volumen del World y el motor **persisten** de una pasada a otra.
Cualquier comparación A/B tiene que limpiarlos explícitamente o estará midiendo
los restos de la prueba anterior. Fue la causa de que las cinco pruebas salieran
idénticas.

### El visor pinta el vacío de blanco

Un render negro con alfa se ve **blanco** al abrirlo. No confíes en el ojo para
decidir si algo está quemado o apagado: mide.

## Render y look

### Los tokens de CSS no son albedos

Los colores de `DESIGN.md` están en OKLCH y describen **píxeles ya iluminados**.
Usados como color base de un material dejaron la escena en cero absoluto: negro
en todos los canales. La piedra necesita un albedo propio de render; la
oscuridad la tiene que poner la luz, no el material.

El oro y el rojo sí salen de los tokens, convertidos de OKLCH a sRGB lineal
dentro del script, para que el oro del render sea el mismo del navegador.

### En EEVEE los metales salen negros

Un metal sólo refleja su entorno. En un interior negro, el oro y el cromo se ven
**negros** en EEVEE. Cycles lo resuelve con rebotes reales. Fue el argumento que
decidió el motor: en esta escena el oro es identidad de marca, no decoración.

Paliativos si te quedas en EEVEE: subir la intensidad del World para dar algo
que reflejar, y ensuciar el `roughness`. Ninguno sustituye a la GI.

### En EEVEE la emisión de un material no ilumina

Una vela con material emisivo se ve encendida pero no alumbra nada. Hay que
poner una luz real dentro de cada veladora. En Cycles la emisión sí ilumina,
pero mantuvimos las luces porque convergen mucho más rápido.

### La niebla se comporta al revés de lo esperado entre motores

La densidad que en EEVEE **apenas se notaba** (0.05), en Cycles lavaba la escena
entera y mataba los negros, porque Cycles resuelve la dispersión múltiple. La
densidad final es 0.012, cuatro veces menor.

Corolario: no transfieras valores de volumen entre motores sin volver a mirar.

### Con AgX, emisión por encima de ~8 quema a blanco

La cruz de neón con `Emission Strength` 18 salía blanca con un halo rosa: se
perdía el rojo, que es medio concepto. A 2.6 conserva el color y sigue
leyéndose como neón. Las velas, a 7.

### Las potencias se calibran midiendo

Los valores que acabaron funcionando (veladora 140 W, neón 2400 W, cenital
700 W) no se parecen a nada "físicamente razonable" y no se habrían adivinado.
Salieron de renderizar, medir la luminancia con ffmpeg y repetir. Además hubo
que recalibrarlos al pasar a Cycles, porque la GI suma luz rebotada.

### Coste real medido

| Motor | Ajustes | Por frame a 640×360 |
|---|---|---|
| EEVEE | 64 muestras | 0.2 – 0.4 s |
| Cycles | 128 muestras, OptiX, denoise | 1.2 – 1.5 s |

Las cinco estaciones a 800×450 en Cycles: 9.5 s. Los dos formatos: 19 s.

## Capa con alfa

### El volumen del World llena el alfa

Con `film_transparent = True`, la niebla del mundo se renderiza igual y el
resultado es una imagen lechosa en vez de un recorte limpio. Hay que desconectar
el enlace de Volume del World mientras dura ese render, y volver a conectarlo
después.

### La distancia al origen no dice si un objeto tapa

Para decidir qué es "primer plano" usamos la distancia del origen del objeto a la
cámara. Para una columna o una vela funciona; para el piso, los muros o el techo
es absurdo, porque su origen está en el centro de una malla de veinte metros. Se
resuelve con una lista blanca de prefijos que pueden ser primer plano, más el
criterio de distancia.

## Entorno

### Rutas WSL ↔ Windows

Blender corre en Windows y escribe en `E:\Cursor Projects\MTO\...`; WSL lee lo
mismo en `/mnt/e/Cursor Projects/MTO/...`. No hace falta traducir nada, pero los
scripts que ejecuta Blender tienen que usar rutas Windows.

### Un visor abierto bloquea el render

Si tienes un PNG abierto en el visor de fotos de Windows, el render falla con
`cannot save: 'E:\...\0-nave.png'`. Renderiza a otra carpeta o cierra el visor.

### AVIF sin avifenc

`avifenc` no está instalado y no hace falta: ffmpeg 6.1 trae `libaom-av1`,
`libsvtav1`, `av1_nvenc` y `libvpx-vp9`.

```bash
ffmpeg -i frame.png -c:v libaom-av1 -still-picture 1 -crf 38 -cpu-used 6 frame.avif
```

### El namespace no persiste entre llamadas MCP

Cada `execute_blender_code` arranca limpio. Por eso el patrón en esta sesión es
`exec(open(ruta).read(), ns)` al principio de cada bloque: los scripts viven en
el repo y Blender los relee. Sale gratis y además obliga a que la escena sea
código versionado en vez de un `.blend` opaco.

## Detalles menores que hacen perder tiempo

- `bpy.ops.object.modifier_apply` necesita que el objeto sea el **activo**, no
  basta con que esté seleccionado.
- Los nombres de socket del Principled BSDF cambian entre versiones
  (`Subsurface Weight`, `Transmission Weight`, `Emission Strength`). Conviene
  asignarlos de forma defensiva y no reventar si uno no existe.
- `bpy.ops.object.light_add` y compañía enlazan a la colección activa: hay que
  desenlazar y reenlazar a mano si quieres controlar dónde caen.
- Tras mover objetos o cambiar constraints, `bpy.context.view_layer.update()`
  antes de leer `matrix_world`, o lees la posición vieja.

## Importar assets de terceros

Tres trampas, las tres costaron un render cada una:

**Escalar cada pieza por separado no encoge el conjunto.** Cada objeto se escala
respecto de su propio origen, así que la distancia entre orígenes no cambia y el
grupo mantiene su tamaño. Hay que emparentar las piezas a un empty que haga de
ancla y escalar el ancla.

**`ob.scale = (f, f, f)` sobrescribe, no multiplica.** Si el asset viene ya
escalado, se pierde su escala original y el resultado no tiene el tamaño
calculado. Correcto: `ob.scale = tuple(c * f for c in ob.scale)`.

**El origen de un objeto no está ni en su centro ni en su base.** Calcular dónde
apoyarlo con `location` y `dimensions` lo deja flotando o hundido. Hay que medir
la caja envolvente real recorriendo `bound_box` y pasando cada esquina por
`matrix_world`.

Además: un `.glb` puede venir sin materiales ni UV, sólo geometría — que suele
ser justo lo que interesa, porque los materiales se ponen con los tokens del
proyecto. Y conviene decimar: 92.000 polígonos para un objeto que ocupa unos
píxeles en el render final no aportan nada.

**Licencias.** Revisar siempre el archivo de licencia que acompaña al asset, no
sólo la etiqueta de la web: en Blend Swap un blend puede ser CC-0 y estar además
marcado como *Fan Art*, lo que prohíbe todo uso comercial.

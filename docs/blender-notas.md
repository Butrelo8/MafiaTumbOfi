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

### CRF calibrado contra AVIF real (2026-09-17)

Medido, no estimado: dos frames a 900×1600 (`f001` estación nave, `f011` en
mitad del tramo) codificados con
`ffmpeg -c:v libaom-av1 -still-picture 1 -cpu-used 6`:

| CRF | frame nave | frame tramo | 80 frames |
|---|---|---|---|
| 30 | 18.6 KB | 22.3 KB | 1.78 MB |
| 34 | 15.3 KB | 18.4 KB | 1.47 MB |
| **38** | **12.6 KB** | **14.7 KB** | **1.18 MB** |
| 42 | 10.6 KB | 12.2 KB | 0.98 MB |
| 46 | 9.0 KB | 10.0 KB | 0.80 MB |

**CRF 38 para los frames de tramo.** Es el primero que cabe en la línea de
1.2 MB del presupuesto. El SSIM no sirve para elegir aquí (0.99 → 0.98 en todo
el rango: la escena es casi negra y el índice apenas se mueve); se decidió
mirando recortes con el brillo subido, que es donde aparece el banding. A 38 el
grano del muro y los degradados de las velas aguantan; a 46 se posterizan.

El frame 0 (LCP) puede ir a CRF 30: 18.6 KB contra los 45 KB que le da el
presupuesto.

El set de escritorio es 1600×900 = los mismos 1.44 Mpx, así que los pesos valen
igual para los dos formatos.

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

### Atajos de navegacion: hay que guardarlos

`blender/keymap.py` asigna walk y fly al boton 4/5 del raton y a
`Ctrl+Shift+W` / `Ctrl+Shift+F`, y en macOS activa la emulacion de raton de 3
botones y de numpad (el MacBook no tiene ninguno de los dos). Se ejecuta una
vez por maquina, desde el editor de texto de Blender o con
`blender --python blender/keymap.py`.

Un `keymap_items.new()` suelto **se pierde al cerrar Blender**: el script
termina en `bpy.ops.wm.save_userpref()` justo por eso. Si un atajo "no agarra"
despues de reiniciar, es que se asigno sin guardar.

Blender ya trae `Shift + \`` (`view3d.navigate`), pero esa tecla es incomoda en
teclado ES de Mac.

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

## Saber qué se movió a mano, sin preguntarlo

`blender/poses.py` compara la escena del visor con la que produce el script.
Hay un orden obligatorio, porque `build()` borra la escena y con ella lo que se
haya colocado a mano:

```python
p = {}
exec(open(r"E:\Cursor Projects\MTO\blender\poses.py").read(), p)
p["volcar"](r"E:\Cursor Projects\MTO\tmp\poses-visor.json")   # 1. ANTES de nada
# 2. build() + aplicar()
p["comparar"](r"E:\Cursor Projects\MTO\tmp\poses-visor.json")  # 3. lista de movidos
```

Devuelve, por objeto, la pose del visor, la del script y el delta. Mide por el
centro de la caja envolvente y no por `location`, por lo mismo que se explica
en la sección de congelar poses.

Si se reconstruye antes de volcar, lo movido ya no existe y no hay nada que
comparar.

## Comprobar intersecciones con datos, no a ojo

Colocar props a ojo y mirar el render es lento y engañoso: un instrumento puede
parecer apoyado y estar atravesando un escalón. Sale mucho más barato comparar
cajas envolventes en coordenadas de mundo antes de renderizar:

```python
def solapan(a, b, holgura=0.01):
    (a_min, a_max), (b_min, b_max) = a, b
    return all(a_min[i] < b_max[i] - holgura and b_min[i] < a_max[i] - holgura
               for i in range(3))
```

Con eso, cada intento devuelve la lista exacta de objetos que se están tocando
en vez de una impresión. Y cuando la lista no se vacía tras varios intentos,
conviene medir el hueco real: si el prop ocupa 1,52 m y el espacio libre es
1,49, ninguna posición lo va a resolver. En ese caso se cambia la escena —
quitar una banca y dejar que el instrumento ocupe el claro — en vez de seguir
empujando el objeto de sitio en sitio.

## `rotation_euler` no hace nada en modo quaternion

Los assets generados (`.glb`, y los `.blend` de generadores) llegan con
`rotation_mode = "QUATERNION"`. Asignar `ob.rotation_euler` entonces **no rota
nada y no avisa**: el objeto se queda como estaba y la depuración se va por el
camino equivocado, porque `ob.rotation_euler` sí devuelve los valores que
acabas de escribir mientras `matrix_world` sigue sin rotación.

```python
ob.rotation_mode = "XYZ"      # primero esto
ob.rotation_euler = (x, y, z)
```

Para detectarlo: comparar `ob.rotation_euler` con la rotación que sale de
`ob.matrix_world.decompose()`. Si la primera tiene valores y la segunda es
cero, es esto.

## Congelar en el script una pose hecha a mano

Colocar props a ojo en el visor funciona mucho mejor que calcular coordenadas,
pero el script reconstruye la escena desde cero y borra cualquier ajuste
manual. El flujo que funciona: el usuario coloca, se lee la transformación y se
escribe en el script como constante.

Dos avisos al hacerlo:

- **Anclar por el centro de la caja envolvente, no por `location`.** El origen
  de una malla reimportada no tiene por qué caer donde cayó en la sesión en que
  se colocó a mano; el centro de la caja sí es comparable.
- **Verificar con la caja, no con el ojo.** Se guarda la caja que tenía la pose
  original y, tras reconstruir, se comprueba que coincide dentro de una
  tolerancia. Así se sabe que la pose quedó realmente congelada.

## Navegar la escena en primera persona

Para revisar encuadres es mucho más rápido moverse por la nave que orbitar.
Blender lo trae de serie: **Walk Navigation** (`View > Navigation > Walk
Navigation`, por defecto `Shift + \``).

Dentro de ese modo: `W A S D` para moverse, `Q` baja, `E` sube, `Shift` acelera,
`Alt` va despacio, la rueda cambia la velocidad base, clic izquierdo confirma y
`Esc` cancela y vuelve a donde estabas.

Se puede lanzar desde un botón lateral del ratón:

```python
teclas = bpy.context.window_manager.keyconfigs.user.keymaps["3D View"]
teclas.keymap_items.new("view3d.walk", "BUTTON4MOUSE", "PRESS")
teclas.keymap_items.new("view3d.fly", "BUTTON5MOUSE", "PRESS")
```

Si ese botón ya tenía algo asignado, conviene desactivar la asignación anterior
(`item.active = False`) en vez de borrarla: queda reversible desde
`Preferences > Keymap`. El cambio vive en la sesión hasta que se guarde con
`bpy.ops.wm.save_userpref()`.

## Dónde cae el sujeto en cada estación, medido

Esta tabla no existía y por eso el encuadre de hornacinas se descubrió mirando
capturas en vez de leyendo un número. Sale de proyectar las esquinas de la caja
envolvente de cada sujeto con `world_to_camera_view`, sin renderizar nada:

```python
from bpy_extras.object_utils import world_to_camera_view
p = world_to_camera_view(escena, cam, ob.matrix_world @ Vector(esquina))
# p.x, p.y en 0..1 sobre el cuadro; p.z <= 0 significa detrás de la cámara
```

Coordenadas normalizadas del cuadro renderizado. `u` de izquierda a derecha,
`v` de abajo a arriba. Medido el 2026-09-17.

| Estación | Frame Blender | Frame web | Sujeto | Escritorio `u` | Escritorio `v` | Móvil `u` | Móvil `v` |
|---|---|---|---|---|---|---|---|
| nave | 1 | 0 | Cruz + retablo | 0.413–0.587 | 0.450–0.790 | 0.345–0.655 | 0.472–0.663 |
| sonido | 21 | 20 | Vinilos y mesa | 0.163–1.001 | 0.064–0.833 | −0.098–1.391 | 0.255–0.687 |
| hornacinas | 41 | 40 | Los tres marcos | **0.034–0.994** | 0.164–0.815 | **−0.328–1.379** | 0.311–0.677 |
| reliquia | 61 | 60 | Micro de bala | 0.363–0.629 | 0.250–0.902 | 0.257–0.729 | 0.360–0.726 |
| retirada | 81 | 79 | Placa M⚡T | 0.405–0.609 | 0.323–0.914 | 0.330–0.694 | 0.401–0.733 |

**El cuadro renderizado no es el cuadro que se ve.** El canvas va con
`object-fit: cover`, así que el navegador recorta el eje que sobra. En una
ventana de 1425×900 contra un frame de 1600×900 el recorte es del **10.9 %:
88 px por lado**, y sólo se ve de `u` 0.055 a 0.945. Cualquier cosa fuera de ese
rango se pierde en esa ventana, y en una más estrecha se pierde más.

La cuenta, para no repetirla a ojo:

```
escala   = max(ancho_ventana / ancho_frame, alto_ventana / alto_frame)
visible_u = [ (1 - ancho_ventana / (ancho_frame * escala)) / 2 , 1 - eso ]
```

Consecuencias que hay que respetar al mover la cámara o al maquetar:

- **Hornacinas se sale.** Los marcos llegan a 0.994 y el navegador corta en
  0.945: los dos de fuera se ven cortados. Bajar la lente de 34 a 28 mm los
  deja en 0.117–0.907, con aire. En móvil los marcos laterales quedan fuera de
  cuadro y hace falta 16 mm para meterlos, lo que los deja diminutos: decisión
  del usuario del 2026-09-17, **móvil se queda con el nicho central solo**.
- **En sonido y hornacinas no hay zona libre**: el sujeto ocupa el ancho
  completo y el texto va forzosamente encima. La legibilidad la sostiene el
  velo de 0.62, no el hueco.
- **En nave, reliquia y retirada el sujeto vive en la franja central** (entre
  0.36 y 0.63 en escritorio). Ahí sí hay columna libre a los dos lados, y es
  donde debe caer el texto.

## Loops de estación: dónde van

Los loops son los frames de estación, no otros: **1, 21, 41, 61 y 81** en
Blender, que `framesDeEstacion()` traduce a **0, 20, 40, 60 y 79** en la web.
Un loop entra cuando el scroll se detiene en una estación y tiene que empalmar
consigo mismo, cerrado con `ffmpeg xfade`.

Qué hay en cada estación que merezca animarse, según la spec:

| Estación | Qué se mueve |
|---|---|
| nave | Parpadeo de la cruz de neón; velas del altar al fondo |
| sonido | Llama de las veladoras de la mesa; humo del cigarro del cenicero |
| hornacinas | Velas de la repisa; polvo en los haces de los focos |
| reliquia | Llama muy cerca; polvo; reflejo moviéndose en el cromo |
| retirada | Velas apagándose; parpadeo del neón |

**Hoy la escena no tiene nada de eso animado.** Las llamas son mallas quietas y
el neón es un material emisivo constante: los cinco loops son trabajo de
animación en Blender, no de encode. Es lo único que queda abierto de la fase 3.

## Bruma delante del titular (2026-09-23) — DESCARTADA

Se probó y se quitó el mismo día: **leía como caricatura** (emisión propia,
ruido grande y suave, sin fuente que la produjera: una manta, no humo). En su
lugar van los cirios de latón (`CIRIOS` en `altar.py`), objetos reales en la
capa de frente. `blender/humo.py` se borró; está en el historial (`30ad3b1`).
Lo medido, por si se vuelve a intentar con humo simulado de verdad:

- **Volumen procedural, no Mantaflow.** Ruido 4D en una caja hija de la cámara,
  mitad baja del cuadro. Nada que hornear. El loop cierra solo: la densidad
  funde dos ruidos desfasados un periodo, y el cuadro N vale lo que el 0.
- **Se renderiza sola**: todo lo demás `visible_camera = False`, que sigue
  iluminando. La niebla del mundo se desconecta, como en la capa de frente.
- **Necesita emisión propia.** Sólo con la luz de las velas la bruma salía más
  oscura que la mesa una vez compuesta: invisible. La emisión va multiplicada
  por la misma densidad, así que no brilla donde no hay bruma.
- **No lleva el velo** (`brightness(0.38)`) en la web, a diferencia de la capa
  de frente: atenuada así quedaba igual de clara que el fondo.
- **Coste**: ~2 s por cuadro en GPU a 960×540, 128 muestras con denoise. 90
  cuadros (3 s a 30 fps) ≈ 3 min por estación y formato. El MCP corta a 60 s:
  las tandas van con `blender -b -P blender/humo.py -- <estacion> <formato>`.
- **Encode**: VP9 con alfa, CRF 45, 640 px de ancho: 55 KB/s. A 960 px pesa 3.4×
  más y no se distingue. WebP animado: 3.9 MB/s, descartado.
- **Safari ignora el alfa de VP9** y pinta negro. Necesita HEVC con alfa, que
  sólo se encodea en macOS (Finder → Encode Selected Video Files → Preserve
  Transparency, desde un ProRes 4444). Hasta tenerlo, WebKit no recibe bruma.
- **Probarla con `python3 -m http.server` no deja saltar** en el vídeo (responde
  200, no 206): se reproduce, pero `currentTime` no se mueve. Ver la ficha
  `video-que-avanza` de la galería.

## Lo que se ve desde el pasillo, medido con rayos (2026-10-05, ticket 13)

Antes de poner utilería en la maqueta, preguntar a la escena qué se ve: `scene.ray_cast(depsgraph, cámara,
dirección, distance=largo − 0.05)` sobre una rejilla de puntos, más `world_to_camera_view` para el píxel. En la
nave, desde el pasillo central, hacia el muro del fondo de las naves laterales sólo hay una rendija de ~30 px: lo
que se ve son los arcos entre pilares. Para validar una pieza ya puesta: contar cuántas esquinas de su
`bound_box` llegan sin chocar (el Cristo en y 11 daba 17/64: lo tapaba el pilar 1; en y 12, 35/64).

Otros que costaron una vuelta:
- **BVH cuenta como cruce el contacto coplanar.** Una veladora con la base a z 0.9 sobre un remate cuyo tope es
  0.9 sale en `overlap()`. No es un cruce: es apoyo. Leer qué par cruza antes de mover nada.
- **Cilindro de un punto a otro:** `(b − a).to_track_quat("Z", "Y").to_euler()` en un `primitive_cylinder_add`
  centrado en `(a + b) / 2`. Para apuntar un spot: `to_track_quat("-Z", "Y")` (los spots alumbran hacia −Z).
- **Piezas en coordenadas locales:** crearlas con el empty en el origen y luego hacer `parent` → mover/girar el
  empty. Con el padre en identidad, `matrix_parent_inverse` queda en identidad y no hay que compensar nada.
- **Desde atrás una banca también es casi un tablero.** Lo que la hace leer como banca (y no como caja, que es lo
  que Klein copiaba) es el remate delgado, los costados con perfil y el hueco entre filas. Lo que apoyes "en la
  banca" va sobre el remate (0.9 m) o en el asiento (0.45 m, casi siempre tapado por el respaldo).

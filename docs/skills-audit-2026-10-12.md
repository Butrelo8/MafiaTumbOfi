# Auditoría: qué convertir en skills, scripts o flujos (MTO, 2026-10-12)

Propuesta solamente: este documento no crea ni edita ninguna skill. Revisa cómo se
trabajó de verdad en MTO entre el 2026-09-16 y el 2026-10-12, para decidir qué
convertir en script, skill, flujo o línea de `CLAUDE.md`.

Cada afirmación lleva su fuente y una etiqueta: **medido** (sale de contar o
cronometrar los transcripts o el disco), **doc** (lo dice un archivo del repo; se
cita la ruta) u **opinión** (juicio mío, sin medición detrás).

## Método

- **Fuente principal:** los 27 transcripts de Claude Code en
  `~/.claude/projects/-mnt-e-Cursor-Projects-MTO*/*.jsonl` (unos 390 MB). Excluí
  esta misma sesión (`b94292b2`). Nunca leí un archivo entero: extraje con `jq`
  los prompts del usuario, cada `tool_use` (nombre, id, primer argumento hasta
  4000 caracteres, si iba en segundo plano), cada `tool_result` (marca de tiempo
  y `is_error`) y las notificaciones de tareas en segundo plano.
- **Sesiones:** se citan por los primeros 8 caracteres de su id (por ejemplo,
  `cc4f90b1`).
- **Duplicados:** `64d1fcbf` y `6c621476` comparten historia (una es fork de la
  otra). Por eso deduplico por id de `tool_use` y por marca de tiempo de evento.
- **Cómo se calculan los tiempos:**
  - Duración de una herramienta: del `tool_use` a su `tool_result`.
  - Trabajo en segundo plano: del lanzamiento a la `<task-notification>` que lo
    cierra.
  - Turno del usuario: el hueco entre el último mensaje del asistente y el
    siguiente prompt real, cuando dura menos de 1 h.
  - Modelo: los huecos de un resultado o prompt al siguiente mensaje del
    asistente.
- **Suma de duraciones:** cada sesión cuenta su propia duración. Hubo sesiones
  en paralelo (la familia de `drones` del 10-09 y el 10-11), así que 51.9 h no
  es tiempo de reloj del calendario.
- **Lo que no pude medir:**
  - La duración real de la mayoría de los trabajos de ComfyUI: su informe
    (`OK en ~Ns`) quedó en archivos de salida de tareas que ya no existen. Solo
    aparece en 10 trabajos.
  - Si una llamada lenta fue espera de permiso o el usuario ausente: el
    transcript no los distingue.
  - Qué salidas de ComfyUI llegaron al sitio.

## Dónde se fue el tiempo

| Bloque | Horas | % de 51.9 h | Etiqueta y fuente |
|---|---|---|---|
| Turno del usuario: revisar, mover props en Blender, decidir | ~19.9 (14.45 entre mensajes + 5.42 en `AskUserQuestion`) | 38 % | medido |
| …de eso, preguntas para revisar algo visual (hoja, lado a lado, `.mp4`) | 3.82 (n=40) | 7 % | medido |
| …de eso, preguntas de decisión, alcance o permiso | 1.60 (n=47) | 3 % | medido |
| Herramientas en primer plano (sin `AskUserQuestion`) | 16.1 | 31 % | medido |
| …de eso, bucles `until`/`while`/`sleep` que bloquean el hilo esperando un trabajo | 2.17 (87 llamadas, 21 sesiones) | 4 % | medido |
| …de eso, comandos triviales (`cat >`, `sed -i`, `git`) que tardaron más de 60 s | ≤1.69 (37 llamadas) | ≤3 % | **inferido**: probablemente esperas de permiso; no se distinguen de un usuario ausente |
| Modelo pensando y escribiendo | 7.55 | 15 % | medido |
| Orientarse al arrancar sesión (del primer prompt a la primera acción que no es leer) | mediana 0.4 min por sesión | <1 % | medido |

**En segundo plano** (corre en paralelo, así que no suma con lo de arriba):

| Trabajo | Horas | n | Fuente |
|---|---|---|---|
| Renders de Blender | 4.89 | 6 | medido. Tres renders completos de 77, 82 y 85 min en `18a906bb` y `cc4f90b1`. Uno de 29 min en `64d1fcbf` murió con exit −1 |
| ComfyUI (H3 y Klein) | 3.46 | 19 | medido. La media de H3 `preset_posevideo_ff` es ~645 s (n=3) |
| Montaje y encode con ffmpeg | 0.35 | 6 | medido |
| **Repeticiones tras un rechazo o un cambio** (re-render, regenerar, reintentar, relanzar, reconstruir) | **4.43** | 11 | medido. 2.77 h son los dos renders completos de `cc4f90b1`: uno es "Full scene re-render with moved cirio"; el otro siguió a "equilibra la velocidad de cámara" |

### Los mayores sumideros, en orden

1. **El ciclo de revisión visual.** Claude arma la comparación, el usuario la
   mira y decide, y se rehace. Es el bloque más grande que se puede atacar:
   - 3.82 h en 40 preguntas visuales (medido).
   - 238 llamadas que arman un lado a lado (`hstack`/`vstack`/`xstack`) en 11
     sesiones (medido).
   - 125 hojas de contacto en 14 sesiones y 136 extracciones de cuadro en 12
     sesiones (medido).
   - El usuario pidió revisar 14 veces en 9 sesiones ("otra vez", "arregla", "no
     me gustó", "se deforma", "caricaturesco", "no encajan"; medido en sus
     prompts).
2. **Repeticiones de trabajo pesado:** 4.43 h (medido). La peor es el render
   completo de 82 min por mover un cirio (`cc4f90b1`). Ya existe
   `blender/render.py` con `tramos(formato, desde, hasta)` y `estaciones()`, así
   que bastaba con volver a renderizar los tramos donde se ve el cirio (doc:
   `blender/render.py:65`, `:88`; lo de que alcanzaba con eso es opinión).
3. **Esperas que bloquean el hilo:** 2.17 h en primer plano (medido). Monitor
   solo se usó 14 veces, y el `sleep` en primer plano fue bloqueado por el
   arnés en 6 sesiones (`90d9750d`, `85d043ac`, `69270c65`, `64d1fcbf`,
   `40defb47`, `10602c56`; medido), aunque la regla 6 de `~/.claude/CLAUDE.md`
   ya lo prohíbe.
4. **Iteración de generación:**
   - `E:\ComfyUI\ComfyUI\output\mto` tiene 214 salidas (150 PNG y 60 MP4)
     entre el 10-04 y el 10-11 (medido en disco).
   - `tmp/contrabajo-12/` tiene `h3`, `klein` y `montar` en versiones v1 a v4
     (medido en disco).
   - Klein se desvía: al quitar el rosario quitó también la texana (doc:
     `docs/handoffs/2026-10-11-gente-reproyeccion.md:37-38`).
5. **Esperas de permiso (inferido, ≤1.69 h).** Ejemplos: `cat >>` de un
   ticket que tardó 6.4 min en `ca646a3a`, y un `cat >` del reporte que tardó
   5.7 min.

**Lo que contradice la hipótesis de partida.** Reconstruir el contexto al
reiniciar sesión no es un sumidero de tiempo:

- La mediana es de 0.4 min hasta la primera acción. Ninguna sesión pasó de
  6 min, salvo el fork `6c621476` (medido).
- 8 de las 26 sesiones con prompt propio arrancan desde un handoff o un
  "continúa" (medido sobre el primer prompt de cada sesión). No hubo ninguna
  compactación: 0 registros `isCompactSummary` o `type:"summary"` en los 27
  `.jsonl` (medido).

Lo que sí cuesta es perder estado *dentro* del trabajo. `build()` borra las
poses que el usuario movió, y eso "ya pasó una vez" (doc: `docs/HANDOFF.md:35`,
`docs/handoffs/2026-09-18-profundidad.md:52-55`).

## Tandas en vez de render→revisar→ajustar: cuándo sí y cuándo no

La idea del usuario es fijar primero props, gente y escena, y luego renderizar
en tanda (de noche o en cola), en vez de render→revisar→ajustar por toma.

**Cuándo ayuda:**

- En los renders de Blender, una vez que el look y las poses están aprobados.
  Los tres renders completos de 77 a 85 min ya funcionan así (medido), y una
  tanda de noche convierte ese tiempo en tiempo muerto (opinión).
- En los barridos de semillas de Klein (`s11/s22/s33/s44`, el patrón que ya se
  ve en `output/mto`; medido). Son independientes entre sí: se lanzan juntos y
  se revisan en una sola hoja.

**Cuándo sale caro:**

- Con un look que todavía no está aprobado. En `cc4f90b1` hubo un render
  completo, luego un cambio (cirio, velocidad de cámara) y otro render completo:
  2.77 h (medido).
- Con una tanda que nadie comprobó antes de lanzarla: los 29 min de
  `64d1fcbf` murieron con exit −1 (medido). En esa misma sesión, un `grep`
  devolvió la sección de notas "Un visor abierto bloquea el render": un PNG
  abierto en el visor de fotos de Windows hace fallar el render con
  `cannot save` (medido en el transcript). Esa sección ya no aparece en
  `docs/` ni en `visual-lab/blender/blender-notas.md` (medido con `grep`): es
  un quirk que se perdió.
- Con cadenas de Klein: cada edición encadenada se desvía más (doc: handoff
  10-11:37-38). Klein va en barridos paralelos desde una misma placa, nunca en
  cadena.
- Con H3 (unos 10 min por trabajo) antes de aprobar la placa: cada placa
  rechazada tira la tanda entera (opinión, basada en la versión v1 a v4 de
  `contrabajo-12`).

**Puerta antes de lanzar una tanda.** Cada punto sale de un fallo real:

1. `poses.comparar(ruta)` sin diferencias contra el volcado aprobado (doc:
   `blender/poses.py:46`). Si no, `build()` se come lo que movió el usuario
   (doc: `docs/HANDOFF.md:35`).
2. `hide_render` y demás banderas restaurados después de los pases (doc:
   `docs/handoffs/2026-10-05-movil-y-props.md:68`). Si no, el siguiente render
   sale negro. `hide_render` aparece en 39 llamadas de 12 sesiones (medido).
3. Una hoja de contacto con **un cuadro Cycles por estación** a muestras
   finales, aprobada por el usuario. **La vista previa en Eevee no sirve de
   puerta aquí:** en Eevee el oro y el cromo salen negros y el humo no se ve
   (doc: `docs/blender-notas.md:53-54`; el prompt de `ba6882d0` lo menciona).
   Lo barato válido es Cycles a media resolución o con pocas muestras. Hubo
   intentos así en 4 sesiones (`64d1fcbf`, `0ed2c9a0`, `0542fe41`, `1007097a`;
   medido), pero ninguno quedó como paso fijo.
4. Ningún PNG de destino abierto en un visor de Windows (quirk visto en
   `64d1fcbf` y hoy perdido de las notas; ver arriba).
5. Disco y presupuesto: `scripts/check-budget.sh` y espacio libre. Un pase en
   PNG de 16 bits ocupó 933 MB (doc: `docs/HANDOFF.md:79-80`).
6. En ComfyUI, que la cola responda y no esté colgada en "Model Initializing".
   Eso pasó 4 veces (doc: `docs/handoffs/2026-10-10-micro-colgado.md:76-80`).

## Secuencias que se repiten entre sesiones

| Secuencia | Llamadas | Sesiones | Ejemplos | Ya existe como código |
|---|---|---|---|---|
| `exec()` de `altar.py`/`transicion.py`/`look.py` y luego `build()` | 200 | 14 | `ba6882d0` (82), `64d1fcbf` (25), `18a906bb` (21) | Sí (`blender/*.py`); la invocación se escribe a mano cada vez |
| Medir en Blender (`world_to_camera_view`, `ray_cast`, BVH, `bound_box`) | 147 | 14 | `64d1fcbf` (40), `ba6882d0` (30), `0542fe41` (20) | No hay un módulo de medición en el repo |
| Volcar y comparar poses / guardar posiciones | 47 | 8 | `64d1fcbf` (14), `18a906bb` (13), `10602c56` (9) | Sí: `blender/poses.py`, que llegó después de las primeras sesiones |
| Lado a lado con `hstack`/`vstack`/`xstack` | 238 | 11 | `0ed2c9a0` (51), `1007097a` (41), `57ebe5be` (40) | No; solo `tmp/hero/hoja.py`, en un `tmp/` ignorado por git |
| Hoja de contacto (`tile=`, `hoja*.py`) | 125 | 14 | `0542fe41` (23), `a2960099` (19), `272c7e29` (17) | Igual que la anterior |
| Extraer un cuadro (`-vframes`, `select=eq`) | 136 | 12 | `a2960099` (23), `4bc959ab` (19), `ca646a3a` (18) | No |
| Medir costura o parecido (SSIM, PSNR, "costura") | 100 | 11 | `1007097a` (18), `a2960099` (15), `0ed2c9a0` (14) | No. Ojo: SSIM "no sirve" para esto (doc: `docs/HANDOFF.md:162-163`) |
| Armar un loop (`xfade`, `tmix`, `reverse`, fundido) | 126 | 16 | `a2960099` (27), `ca646a3a` (23), `0542fe41` (12) | Copias de `montar*.sh` en `tmp/` |
| Look de cine (halación, `dof.py`, grano) | 76 | 7 | `1007097a` (20), `0ed2c9a0` (20), `ca646a3a` (16) | `tmp/cine-look/{halacion.sh,dof.py,montar_r7.sh}`, ignorados por git |
| Klein (edición Flux) | 288 | 10 | `57ebe5be` (73), `0542fe41` (62) | `~/.claude/skills/comfy-local/scripts/gen.sh` más un `klein*.sh` por carpeta |
| H3 (video) | 205 | 9 | `ca646a3a` (45), `a2960099` (30) | `gen.sh` más un `h3*.sh` por carpeta |
| Encode final (x264, x265, AV1, VP9) | 96 | 15 | `ca646a3a` (16), `4bc959ab` (12) | La escalera de códecs vive solo en `tmp/micro/*/cod/ladder.sh` (doc: `docs/scope-terminado-2026-10-12.md:77`) |
| Render headless `blender.exe -b` | 50 | 8 | `57ebe5be` (13), `cc4f90b1` (9) | `scripts/build-scene.sh` |

En disco hay 12 copias de `h3*.sh` en 9 carpetas, 18 de `klein*.sh` en 8 y 18 de
`montar*.sh` en 13. Ninguna de las `h3.sh` es idéntica a otra (medido con
`md5sum`): cada ticket clona y retoca el anterior. El orden real de la tubería
está escrito en `docs/handoffs/2026-10-10-micro-colgado.md:45-57`:
`atenuar.py` → `ajustar_mascara.py` → `micro_viva.py` → `montar_r7.sh` → `dof.py`
→ `halacion.sh`, unos 4 min (doc).

## Errores que se volvieron a aprender

| Error | Veces o sesiones | Ejemplos | Fuente |
|---|---|---|---|
| `sleep` en primer plano bloqueado por el arnés | 6 sesiones | `90d9750d`, `85d043ac`, `64d1fcbf` | medido; ya está prohibido en `~/.claude/CLAUDE.md` (regla 6) |
| El MCP de Blender no conecta (puerto 9876/9877, WSL en modo *mirrored*, `0.0.0.0`) | 3 sesiones más 1 timeout; el usuario lo explicó 3 veces | `db8aab27`, `64d1fcbf`, `a2960099`, `90d9750d` | medido |
| Filtergraph de ffmpeg roto (alturas que no casan en `hstack`, etiquetas de más) | 4 | `a2960099`, `57ebe5be` ×2, `272c7e29` | medido |
| `numpy` o `PIL` ausentes en el `python3` del sistema | 3 sesiones; se usó `uv run --with …` 88 veces | `cc4f90b1`, `a2960099`, `0542fe41` | medido |
| H3 `SamplerCustomAdvanced shape … is invalid` | 2 | `272c7e29`, `1007097a` (se reintentó a 928×512) | medido; la causa exacta (dimensiones o número de cuadros) no está verificada |
| Salida de ComfyUI ausente después de esperar | 3 | `0ed2c9a0` ×2, `ca646a3a` | medido |
| ComfyUI colgado en "Model Initializing" | 4 veces | — | doc: `docs/handoffs/2026-10-10-micro-colgado.md:77` |
| `build()` pierde las poses movidas | "ya pasó una vez" en dos documentos | — | doc: `docs/HANDOFF.md:35`, `docs/handoffs/2026-09-18-profundidad.md:55` |
| Afirmar sin medir ("s44 se había corrido y era falso") | — | — | doc: `docs/handoffs/2026-10-11-gente-reproyeccion.md:41-42`; regla en `docs/blender-notas.md:61-63` |

## Instrucciones que el usuario tuvo que repetir

| Instrucción | Sesiones | Ejemplos |
|---|---|---|
| "Haz el handoff con matt-handoff y ponlo dentro del repo" | pedido explícito en 3 (`ba6882d0`, `18a906bb`, `6c621476`); la skill `matt-handoff` o `handoff` se cargó en 7 | En `10602c56` Claude contesta "como ya pediste la vez pasada" sobre guardarlo en el repo |
| "Commit de todo, también lo de otros agentes u otra sesión" | commit pedido en 5 sesiones; "todo, incluso lo de otros" en 3 | `4bc959ab`, `0542fe41`, `85d043ac`; commit simple en `a603460c` y `cc4f90b1` (×2) |
| "Anota quirks, hallazgos y técnicas" (en ProyectoInvestigación, visual-lab o ComfyUI) | 6 | `ba6882d0` (×2), `a2960099`, `85d043ac`, `0542fe41`, `1007097a` |
| "Ya moví cosas, guarda posiciones" | 5 | `64d1fcbf` (×4), `6c621476`, `10602c56`, `18a906bb`, `ba6882d0` |
| "¿Cómo va?" (preguntar por el avance de un render largo) | 4 sesiones, 7 veces | `cc4f90b1` (×4) |
| "Verifica con screenshots o recorre la página" | 3 | `cc4f90b1`, `10602c56`, `ba6882d0` |
| "Blender ya está en 0.0.0.0 / mirrored" | 2 sesiones, 3 veces | `64d1fcbf` (×2), `a2960099` |

Las notas se escriben en tres repos: ProyectoInvestigación (38 escrituras en 6
sesiones), visual-lab (31 en 4) y los `docs/` de MTO. Además, `blender-notas.md`
aparece en 82 llamadas de 14 sesiones (medido). Quedan sin cubrir dos cosas:
qué hallazgo va a qué repo, y que el cierre de sesión (hallazgos, commit,
handoff, reporte) siempre es el mismo.

## Skills: usadas, sin usar y solapadas

**Uso medido**, contando llamadas a la herramienta Skill más
`mcp__mpaf__get_skill_instructions`:

- `matt-handoff` 6, `handoff` 2, `matt-wayfinder` 4 y `brainstorm` 3.
- `resa` 2, `comfy-local` 2, `matt-grilling` 2.
- `director`, `frameref`, `matt-prototype`, `matt-domain-modeling` y
  `diseccion` (mpaf), una vez cada una.

**Uso de `comfy-local`:** se usa sobre todo llamando a su `gen.sh` por ruta
directa: aparece en 80 comandos, contra 2 cargas como skill (medido). El script *es* la skill.

**Nunca cargadas en 27 sesiones (medido):**

- `blender`, `kiln-prop` y `rive`.
- `diseccion-video` y `diseccion-voz`.
- `animation-vocabulary` y `review-animations`.
- Toda la familia `figma-*`. En `a603460c` el usuario preguntó "¿no usaste
  figma-mcp?".

**Choque de nombres con `blender` (doc).** Tres handoffs y el MAP mandan a
cargar `blender` antes de tocar `blender/`:

- `docs/handoffs/2026-10-05-movil-y-props.md:86`
- `docs/handoffs/2026-10-10-micro-colgado.md:87`
- `docs/handoffs/2026-10-11-gente-reproyeccion.md:56`
- `.wayfinder/santuario/MAP.md:17`

Pero esa skill es el flujo Mixamo → baile (`.claude/skills/blender/SKILL.md`),
no la tubería de la escena. Por suerte nunca se cargó.

**Copias y archivos sin seguimiento (medido, `git status` y `ls -la`):**

- En MTO, `director`, `diseccion-voz`, `kiln-prop` y `rive` están sin
  seguimiento en `.claude/skills/`.
- En visual-lab, casi todas son enlaces simbólicos a su carpeta de origen. Las
  de MTO son copias.
- `blender` y `rive` de MTO tienen el mismo `SKILL.md` que visual-lab, pero sin
  sus 5 archivos auxiliares. Si una cambia, la otra se queda atrás.

## Propuestas, en orden

El orden pondera el ahorro esperado contra el esfuerzo. Se sigue la regla del
usuario: lo que un script puede comprobar va en código, no en un prompt.

### 1. `scripts/comparar.sh` — script

- **Qué automatiza:** con una sola orden se arma el lado a lado (alinea alturas
  y fps solo), la hoja de contacto con etiquetas, la extracción de cuadros por
  índice y la medición de costura de loop (diferencia del último cuadro con el
  primero, más saltos entre cuadros). La salida va a una ruta fija que se le
  entrega al usuario. Va al repo; hoy `tmp/hero/hoja.py` está en un `tmp/`
  ignorado por git.
- **Evidencia (medido):**
  - 238 lado a lado en 11 sesiones (`0ed2c9a0`, `1007097a`, `57ebe5be`).
  - 125 hojas en 14 sesiones; 136 extracciones de cuadro en 12; 100 medidas de
    costura en 11.
  - 4 filtergraphs rotos (`a2960099`, `57ebe5be`, `272c7e29`).
  - 3.82 h de revisión visual en 40 preguntas.
- **Esfuerzo:** 2–3 h (opinión).
- **Ahorro esperado (opinión):** quita la mayoría de los filtergraphs escritos a
  mano en cada sesión y sus errores. La revisión se acelera porque toda hoja sale
  con el mismo formato y etiquetas. No reduce el tiempo de decisión del usuario.

### 2. Flujo «fijar → puerta → tanda» con `scripts/puerta-tanda.sh` — flujo más script

- **Qué automatiza:** el script comprueba lo que se puede comprobar:
  - `poses.comparar` sin diferencias;
  - `hide_render` restaurado;
  - ningún PNG de destino abierto (intentar abrirlo en escritura);
  - disco libre y `check-budget.sh`;
  - la cola de ComfyUI viva.

  El flujo deja al usuario solo lo que es suyo: aprobar la hoja de Cycles por
  estación. Después lanza la tanda en segundo plano y vuelve a renderizar solo
  los tramos afectados (`render.tramos(desde, hasta)`). Así se evita el render
  completo.
- **Evidencia (medido):**
  - 4.43 h de repeticiones en 11 trabajos. De eso, 2.77 h son dos renders
    completos en `cc4f90b1`.
  - 29 min perdidos en `64d1fcbf` (exit −1).
  - "Guardar posiciones" repetido en 5 sesiones.
  - `hide_render` en 39 llamadas de 12 sesiones.
  - Doc: `docs/HANDOFF.md:35`, `docs/handoffs/2026-10-05-movil-y-props.md:68`.
- **Esfuerzo:** 3–4 h (opinión).
- **Ahorro esperado (opinión):** del orden de 1–3 h por cada cambio tardío de un
  prop, más las tandas muertas. Las tandas de noche convierten el render en
  tiempo muerto, pero solo si la puerta pasa.

### 3. `scripts/loop-vivo.sh`: la tubería placa → H3 → máscara → montaje → DOF → halación → escalera de códecs, con parámetros — script

- **Qué automatiza:** reemplaza las copias por carpeta (`h3.sh`, `klein.sh`,
  `montar.sh`) con un solo script que recibe placa, máscara, formato (escritorio
  o vertical), duración (5, 10 o 15 s) y semilla. Sube al repo
  `tmp/cine-look/*` y `ladder.sh`. Los prompts de H3 y Klein se quedan como
  archivos de datos por ticket.
- **Evidencia (medido):**
  - 48 copias en disco: `h3*` 12 en 9 carpetas, `klein*` 18 en 8 y `montar*` 18
    en 13. Todas distintas.
  - Klein en 288 llamadas de 10 sesiones; H3 en 205 de 9.
  - 126 armados de loop en 16 sesiones; 76 llamadas de halación o DOF en 7.
  - Doc: el orden de la tubería está en
    `docs/handoffs/2026-10-10-micro-colgado.md:45-57`, y `ladder.sh` existe
    solo en `tmp/`.
- **Esfuerzo:** 4–6 h (opinión). Es el más caro, porque hay que unificar
  variantes.
- **Ahorro esperado (opinión):** menos tiempo de modelo leyendo y retocando
  scripts viejos, y resultados repetibles. Además, la tubería sobrevive a una
  limpieza de `tmp/`.

### 4. `scripts/esperar.sh` más un preflight de entorno — script

- **Qué automatiza:**
  - `esperar.sh` espera N archivos, o a que la cola de ComfyUI se vacíe, o un
    `ERROR` en el log, siempre con tope de tiempo. Está pensado para usarse
    desde Monitor o en segundo plano. Reemplaza las 23 variantes de `until …`
    escritas a mano.
  - `preflight.sh` comprueba al arrancar: el puerto del MCP de Blender (la
    explicación de `0.0.0.0` y *mirrored* va en el mensaje de error), que
    ComfyUI responda, y que `uv run --with numpy,pillow` funcione.
- **Evidencia (medido):**
  - 2.17 h en esperas que bloquean, en 21 sesiones.
  - `sleep` bloqueado en 6 sesiones.
  - Fallos de conexión de Blender en 3 sesiones, explicados por el usuario 3
    veces.
  - `numpy` ausente en 3 sesiones; 3 salidas de ComfyUI ausentes.
  - Doc: el cuelgue en "Model Initializing" pasó 4 veces
    (`docs/handoffs/2026-10-10-micro-colgado.md:77`).
- **Esfuerzo:** 1–2 h (opinión).
- **Ahorro esperado (opinión):** el hilo deja de bloquearse en las esperas, y
  el usuario deja de repetir el diagnóstico de red. Los preflights fallan rápido
  en vez de a mitad de una tanda.

### 5. Skill de proyecto `santuario-escena`, en lugar de `blender` en los handoffs — skill nueva más una corrección en los docs

- **Qué automatiza:** una skill corta, de procedimiento, para la escena de MTO:
  - cómo cargar `altar.py`/`transicion.py` (200 llamadas a mano);
  - el módulo de medición: `world_to_camera_view`, rayos y BVH, que hoy se
    reescribe en 147 llamadas de 14 sesiones (lo convertiría en
    `blender/medir.py`);
  - `poses.py`, `render.py` por tramos y `blender.exe -b`;
  - un puntero a `docs/blender-notas.md` y la puerta de la propuesta 2.

  Los cuatro docs que hoy dicen `blender` pasarían a apuntar a ella. Va
  registrada en git; hoy cuatro skills de `.claude/skills/` no lo están.
- **Evidencia:**
  - Choque de nombres en los cuatro docs citados arriba (doc).
  - `blender` cargada 0 veces (medido).
  - Medición reescrita 147 veces (medido).
- **Esfuerzo:** 2 h la skill y 1–2 h `blender/medir.py` (opinión).
- **Ahorro esperado (opinión):** menos reescritura de código de medición, y que
  la próxima sesión no cargue la skill de Mixamo.

### 6. Cierre de sesión: extender `handoff` con «hallazgos → destino» y commit — extender la skill existente `handoff`

- **Qué automatiza:** el cierre que el usuario pide a mano: anotar quirks,
  commit de todo y handoff. Añade una tabla de enrutado de hallazgos:
  - lo específico del sitio va a `docs/` de MTO;
  - el método general va a visual-lab;
  - lo de cliente o ventas va a ProyectoInvestigación (solo a través de su
    propia sesión).

  Lleva también una lista de lo que se commitea, incluidos los cambios de otros
  agentes cuando el usuario lo autoriza en esa sesión.
- **Evidencia (medido):**
  - Handoff pedido explícitamente en 3 sesiones y escrito con la skill en 7;
    commit pedido en 5 (en 3, "todo, incluso lo de otros"); anotar hallazgos
    en 6.
  - Escrituras repartidas: ProyectoInvestigación 38 en 6 sesiones, visual-lab
    31 en 4.
- **Esfuerzo:** 1 h (opinión).
- **Ahorro esperado (opinión):** menos instrucciones repetidas al cerrar, y
  hallazgos que no se pierden entre los tres repos.

### 7. Líneas de `CLAUDE.md` y un hook para lo que se re-aprende — línea de `CLAUDE.md` más hook

- **Qué automatiza:**
  - En el `CLAUDE.md` de MTO, tres líneas:
    - «Python con numpy/PIL: `uv run --with numpy,pillow python`».
    - «Antes de lanzar una tanda: `scripts/puerta-tanda.sh`».
    - «La skill de escena es `santuario-escena`, no `blender`».
  - Las reglas que ya están escritas y aun así se rompen (el `sleep`) piden un
    hook o un alias, no otra línea de texto: un `python3` que apunte al entorno
    con numpy, y la skill `fewer-permission-prompts` para las esperas de
    permiso de comandos triviales.
- **Evidencia:**
  - `sleep` en 6 sesiones pese a la regla 6 (medido).
  - `numpy` en 3 sesiones, con 88 llamadas a `uv run` (medido).
  - Hasta 1.69 h de comandos triviales lentos (inferido).
- **Esfuerzo:** 30–60 min (opinión).
- **Ahorro esperado:** pequeño por vez y constante (opinión).

### 8. Limpiar el catálogo de skills de MTO — tarea de higiene, no una skill nueva

- **Qué automatiza:** cambiar las copias de `blender` y `rive` en MTO por
  enlaces o por el preset de mpaf (`animacion-blender`, que ya se intentó
  instalar en `c2ca8794`). Decidir si `director`, `diseccion-voz`, `kiln-prop` y
  `rive` se registran en git o se quitan.
- **Evidencia (medido):**
  - 7 skills sin uso en 27 sesiones.
  - 4 carpetas sin seguimiento en git.
  - `SKILL.md` idénticos en dos sitios, con archivos auxiliares solo en uno.
- **Esfuerzo:** 30 min (opinión).
- **Ahorro esperado (opinión):** menos ruido al elegir skill y ninguna copia
  desfasada. Es el de menor impacto en tiempo.

## Lo que no encontré o queda abierto

- **Tiempo real de cada trabajo de ComfyUI:** solo 10 informes `OK en ~Ns`
  sobrevivieron en los transcripts.
- **Cuántas de las 214 salidas de ComfyUI llegaron al sitio:** sin ese dato no
  se puede calcular el ratio de desperdicio de la generación.
- **Separar las esperas de permiso del usuario ausente:** el 1.69 h queda como
  inferido.
- **Una fuente externa que contradiga estas propuestas:** no busqué ninguna;
  todo lo de arriba sale de datos internos. Dentro de los datos, lo que
  contradice el planteamiento es el tiempo de orientación (no es un sumidero) y
  que la vista previa en Eevee no vale como puerta en esta escena.
- **Si el preset `animacion-blender` de mpaf terminó de instalarse en
  `c2ca8794`:** no lo verifiqué (el dry-run avisó de un conflicto en
  `.mcp.json`).

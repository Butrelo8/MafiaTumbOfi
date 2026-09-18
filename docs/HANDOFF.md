# Handoff — Santuario M⚡T

> Escrito 2026-09-17, 02:30 CST. Reescrito 14:00 CST. Rama `dev`, 41 commits
> por delante de `main`.
> Formato según la skill `matt-handoff` de mpaf, guardado en el repo (y no en el
> temporal del sistema, como sugiere la skill) para que sobreviva entre
> sesiones.

## Lo primero que te van a pedir

**El usuario está moviendo props en el visor de Blender ahora mismo.** Su
siguiente instrucción será que revises qué movió y lo guardes. El flujo exacto,
y el orden importa:

```python
p = {}
exec(open(r"E:\Cursor Projects\MTO\blender\poses.py").read(), p)
p["comparar"](r"E:\Cursor Projects\MTO\tmp\poses-referencia.json")
```

`comparar()` devuelve, por objeto, la pose de referencia, la actual y el delta.
Con eso se escriben las constantes en `blender/altar.py`, se reconstruye y se
vuelve a comparar: el residuo tiene que quedar por debajo del milímetro.

**No reconstruyas la escena antes de comparar.** `build()` borra todo y con ello
lo que el usuario movió; ya pasó una vez esta sesión. Si tienes que tocar la
escena por cualquier otro motivo, primero `volcar()` a un JSON nuevo.

Después de congelar, vuelve a volcar la referencia:

```python
p["volcar"](r"E:\Cursor Projects\MTO\tmp\poses-referencia.json")
```

Y ojo: si cambia la geometría de la mesa hay que **re-renderizar los frames**,
porque los 170 AVIF que sirve la web salieron de la escena de las 13:26 CST.
Mover un prop pequeño no lo justifica; mover la gorra dos metros, sí.

## Qué se está haciendo

Rehacer mafiatumbada.com como una página cuyo scroll dirige una cámara por un
santuario en 3D. La escena **no** se renderiza en el navegador: son frames
pre-renderizados en Cycles que el scroll reproduce sobre un `<canvas>`, con
loops de vídeo cuando el scroll se detiene y todo el texto en HTML encima.

Cinco estaciones: nave, sonido, hornacinas, reliquia, retirada.

## No dupliques esto, léelo

| Documento | Qué contiene |
|---|---|
| `docs/specs/2026-09-16-santuario-3d-scroll-design.md` | El diseño aprobado: storyboard, presupuesto de peso, ajustes de render, capa web, accesibilidad. Manda sobre cualquier improvisación |
| `docs/plans/2026-09-16-santuario-3d-implementation-plan.md` | Fases, puertas y el resultado real de cada una |
| `docs/blender-notas.md` | **Léelo antes de tocar `blender/`.** Quirks de Blender 5.2, importación de assets, método de medición, congelar poses, detectar lo movido, atajos de navegación |
| `public/scene/CREDITOS.md` | Licencias de todo lo que no es nuestro |
| `DESIGN.md` | Tokens de color y tipografía; la escena los consume |

`git log main..dev` cuenta el resto: cada commit explica **por qué**.

## Estado

**Fases 0, 1 y 2 cerradas.** Escena de 343 objetos, Cycles con OptiX, 128
muestras. Se levanta en 14 s desde código; el `.blend` no se versiona.

**Fase 3 casi cerrada.** Falta sólo el punto 3:

1. ~~Calibrar CRF~~ — 38 tramos, 30 estaciones. Tabla y método en las notas.
2. ~~Renderizar 4 tramos × 20 frames~~ — 170 PNG de 16 bits en `tmp/frames`
   (933 MB, ignorados), obturador **0.25**, 10 s por frame, 33 min la tanda.
3. **Pendiente: los 5 loops de estación** a 24 fps con llama, humo de cigarro,
   polvo en los haces y parpadeo del neón, cerrados con `ffmpeg xfade`. Hoy la
   escena no tiene nada de eso animado: es trabajo de animación, no de encode.
4. ~~`scripts/build-scene.sh`~~ — AVIF + `src/data/scene.json`. Le falta la
   rama de WebM, que depende del punto 3.
5. ~~`scripts/check-budget.sh`~~ — mide el formato más pesado, no la suma.

**Fase 4 en marcha y funcionando en el navegador.** `src/components/AltarScene.astro`
y `src/lib/scrollScene.ts`; las cinco secciones de `index.astro` llevan
`data-estacion` y el frame se interpola entre sus centros. Verificado con
Chrome DevTools: centrar cada sección da los frames 0, 20, 40, 60 y 79.

**Fase 5 sin empezar.**

## Números medidos, no estimados

| Qué | Valor |
|---|---|
| Peso por visitante | **0.85 MB** (objetivo 2 MB, techo 3 MB) |
| Frames de tramo | 160–219 KB los 20 de cada tramo |
| Estaciones | 14–28 KB cada una |
| Velocidad de cámara | 84 / 105 / 80 / 84 px de scroll por frame |
| Recorrido total | ~820vh |
| Velo sobre la escena | `rgba(0,0,0,0.62)`, el mínimo para 4.5:1 |

El velo salió de medir el percentil 95 de luminancia de cada estación contra
`--text`. La reliquia es la que manda por el cromo del micro. Si cambias la
iluminación de la escena, **ese 0.62 hay que recalcularlo**.

## Decisiones cerradas — no las reabras sin motivo nuevo

- **Cycles con OptiX**, no EEVEE: en EEVEE el oro y el cromo salen negros.
- **Frames pre-renderizados**, no three.js ni glTF en vivo.
- **Obturador 0.25**, no 0.5 como decía la spec: a 0.5 el retablo y la guitarra
  quedaban ilegibles a media carrera. Corregido en la spec con el motivo.
- **El glow del neón va en post con ffmpeg**: el compositor de Blender 5
  devuelve negro incluso en passthrough.
- **El vídeo del hero y sus dos velos están apagados** por CSS desde
  `AltarScene.astro`. El marcado sigue: no se borró nada.
- **Sin sección de fechas** (2026-09-09). **Sin arma en la escena**.
- **Sin marcas reales**: `MARCA` y `MARCA_MONOGRAMA` en `blender/altar.py`
  llevan SANTO VICIO, inventada. La botella de tequila es sólo silueta, sin
  etiqueta ni logo.
- **Los cigarros sueltos de terceros se usan igual**: vienen de un foro de
  videojuegos, sin licencia escrita, y es decisión explícita del usuario del
  2026-09-17. Anotado en `CREDITOS.md`.

## Pendientes y bloqueos

- ~~Licencia de `blender/assets/guitarra.blend`~~ — **CC0**, verificada el
  2026-09-17: https://blendswap.com/blend/31078. No obliga a acreditar en el
  sitio. Era el único bloqueo para publicar; ya no hay ninguno.
- **La tabla de contraste de `DESIGN.md` está calculada contra negro plano** y
  ya no vale: hay texto sobre la escena. Se recalcula en la fase 5; el 0.62 del
  velo es el dato de partida.
- ~~Los retratos de las hornacinas~~ — ya no son huecos negros: los tres se ven
  en los renders del 2026-09-17.
- **Deuda preexistente en `look.py`**: la fila `("PROP_botella", "vidrio")` gana
  antes que las de `liquido`, `tapon`, `cinta` y `lazo`, que nunca se aplicaron.
  No la toqué porque es anterior a esta sesión.
- **La página mide 820vh.** Es el precio de igualar la velocidad de cámara. Si
  el usuario lo ve largo, bajar `.tramo-espacio` de `50svh` a `25svh`.
- **Los 9 platos del candelabro están vacíos** y con el cenicero nuevo
  desaparecieron las dos `PROP_brasa` emisivas: ya no hay brasa encendida en la
  mesa.

## Cómo trabajar con este repo

**Colocar props.** El usuario coloca a ojo en el visor —es mucho mejor que
calcular coordenadas— y el agente lee la transformación y la escribe como
constante en `blender/altar.py`. Lo que no pase al script se pierde.
`blender/poses.py` detecta qué se movió sin preguntar; lee la rotación **del
mundo**, porque la local no ve el ancla del padre.

**Medir antes de opinar.** Casi todas las decisiones buenas de esta sesión
salieron de medir: el CRF contra AVIF reales, el obturador renderizando el
tramo entero, el velo con luminancias, la colocación de props proyectando a
cámara (los prerrollos ocupaban 8 px en el escalón y estaban fuera de cuadro en
cuatro de cinco estaciones), y los huecos de scroll con `getBoundingClientRect`.
El SSIM **no** sirve en esta escena: va de 0.99 a 0.98 en todo el rango de CRF
porque casi todo es negro.

**Comprobar intersecciones con cajas envolventes**, nunca a ojo. El candelabro
sólo cabe en un sitio y se supo probando 18 combinaciones, no mirando renders.

## Trampas que ya costaron tiempo

Todas en `docs/blender-notas.md`. Las que se repiten:

1. **`build()` borra la escena.** Volcar poses antes de reconstruir.
2. **`rotation_euler` no rota nada en modo quaternion**, que es como llegan los
   assets generados, y Blender no avisa.
3. **Los assets generados llegan soldados a su peana.** El micro traía un disco
   de escenario de 1.9 m y el candelabro y la botella venían a 1.9 de lado: se
   cortan por geometría o se escalan por el ancho, no por el alto. Unos lentes
   tumbados miden 4 cm de alto y 14 de ancho: escalarlos por altura los deja del
   tamaño de la mesa.
4. **Los atajos de teclado de Blender no sobreviven sin `save_userpref()`.**
   `blender/keymap.py` los deja fijos: botón 4/5 del ratón y `Ctrl+Shift+W/F`
   para walk y fly.
5. **El MCP de Blender corre como `uvx.exe` en Windows**, así que habla al
   `localhost` de Windows y el NAT de WSL no le afecta. Si "no agarra", casi
   siempre es que el servidor del add-on no está arrancado (`N` → BlenderMCP →
   Start).

## Cómo hablar con el usuario

Español. Prefiere que se le contradiga con datos antes que complacencia: esta
sesión mejoró porque se le dijo que la gorra del nicho era basura flotante, que
los prerrollos no se veían, y que partir la sección de Música no iba a arreglar
la velocidad de cámara. Quiere ver renders, no descripciones: se los manda con
`SendUserFile` o los abre desde Windows en `E:\Cursor Projects\MTO\tmp\ref\`.

Decide rápido y delega la decisión técnica ("lo que tú me digas"), pero quiere
saber el coste de lo que se elige.

## Skills sugeridas para la próxima sesión

- `caveman` / `ponytail` — **apagadas a petición del usuario**. No las
  reactives sin que lo pida.
- `cloudflare:web-perf` — para la fase 5: Lighthouse móvil y los Core Web
  Vitals del scrub con 80 AVIF.
- `design:accessibility-review` — recalcular la tabla de contraste de
  `DESIGN.md` con el texto sobre la escena.
- `code-review` — antes de mezclar `dev` en `main`, que lleva 41 commits.
- `brainstorm` — sólo si se replantea una estación o entra contenido nuevo.

# Santuario M⚡T — escena 3D dirigida por scroll

> Diseño aprobado 2026-09-16. Rama `dev`. Reemplaza la presentación de la
> página única; no cambia su contenido ni su arquitectura de información.
> Reconciliar con [`DESIGN.md`](../../DESIGN.md) al implementar: los tokens
> mandan, esta escena los consume.

## Problema

El sitio actual presenta ocho secciones apiladas sobre negro plano con un video
de hero. Funciona, pero no tiene profundidad ni progresión: el scroll solo
desplaza bloques. Queremos que el scroll dirija una escena con profundidad
real — cámara, encuadre y enfoque cambiando — sin sacrificar peso,
accesibilidad ni el contenido que ya existe.

## Principio rector

**El navegador no rinde 3D.** Blender rinde todo por adelantado; la web solo
reproduce frames. Todo el texto sigue siendo HTML real posicionado encima de la
escena. SEO, lectores de pantalla, selección de texto y enlaces no se tocan. Si
la escena no carga, queda un sitio estático correcto.

Decisiones descartadas y por qué:

- **three.js + glTF en vivo** — +150 KB de librería, sin calidad de render
  offline, y riesgo real de rendimiento en el móvil de gama media que usa la
  audiencia de la banda.
- **Solo capas 2D con paralaje** — no da motion blur ni cambio de enfoque
  creíbles, que son justo el efecto buscado.
- **Video único con seek por scroll** — el seek cuadro a cuadro no es fiable en
  Safari ni en móviles.

## Storyboard

Cinco estaciones, cuatro tramos de viaje entre ellas.

| # | Estación | Encuadre | Contenido HTML encima |
|---|---|---|---|
| 0 | Nave | Altar completo, lejos, velado en niebla; cruz de neón rojo al fondo | Logo, eyebrow, lede, chips, CTA WhatsApp |
| 1 | Nicho del sonido | Dolly adelante; foco cae en vinilos y carátulas apiladas | Música: cards de releases, Apple Music, fila de videos |
| 2 | Hornacinas | Lateral; tres marcos dorados vacíos labrados en la piedra | El grupo: los 3 retratos reales dentro de los marcos |
| 3 | La reliquia | Macro: micro de bala, cadena de oro, veladoras muy cerca | Contratación: copy, teléfono, CTA WhatsApp |
| 4 | Retirada | La cámara retrocede; M⚡T en oro sobre el altar, velas apagándose | Footer: socials, legal |

La bio ("El sonido de Xalapa") no tiene estación propia: vive durante el tramo
0→1, avanzando mientras la cámara viaja. Le da al viaje un motivo para durar.

El marquee rojo se conserva, una sola vez, fijo sobre la escena entre las
estaciones 0 y 1.

No se añade sección de fechas — decisión de 2026-09-09, sigue vigente.

## Dos materiales distintos

**Tramos (scroll en movimiento).** Secuencia de frames atada a `scrollY`, con
motion blur horneado por el obturador de la cámara de Blender. 20 frames por
tramo como base; el blur hace que se lean como muchos más. Se dibujan en un
`<canvas>`, no en `<img>`, para que no parpadee el salto de frame.

**Estaciones (scroll detenido).** Tras ~150 ms sin cambio de `scrollY` arranca
un loop de video de ~2.5 s con la cámara quieta: la llama respirando, polvo
cruzando el haz de luz, el brillo del oro desplazándose. El último frame del
tramo es idéntico al frame 0 del loop, así que el empalme es invisible. Al
reanudar el scroll, el video se pausa y el canvas retoma.

## Capa de primer plano

Cada estación tiene además una imagen con alfa de lo que queda **delante** del
sujeto enfocado: columnas, bancas, el borde de la mesa, las velas del macro. Se
compone por encima del texto HTML, de modo que la tipografía queda dentro de la
escena en vez de flotar sobre ella — una columna pasa frente al título, una vela
desenfocada cruza por delante del párrafo.

Sólo existe en las cinco estaciones, nunca en los tramos: por frame duplicaría
el peso del proyecto, y en movimiento no se aprecia. Durante el scrub se oculta
y reaparece con el loop al detenerse.

Qué cuenta como primer plano lo decide el render: es todo objeto candidato
(columnas, bancas, candelabros, props, veladonas, vinilos, el micro) que esté
más cerca de la cámara que el objeto enfocado, con un margen de 0.78. La
arquitectura queda excluida por nombre, porque el origen de una malla enorme no
dice nada sobre si tapa a la cámara. La niebla del mundo se desconecta mientras
se renderiza, o llenaría el alfa entero.

El texto que quede bajo esta capa necesita comprobación de contraste propia
(check 5).

## Presupuesto de peso

**Objetivo 2 MB por visitante móvil. Techo duro 3 MB**, ampliado desde
el objetivo inicial para dar sitio a la capa de primer plano. El margen entre ambos se
gasta en más frames de tramo — nunca en subir resolución.

| Recurso | Cálculo | Peso |
|---|---|---|
| Frame 0 estático (LCP) | AVIF 900×1600 | ~45 KB |
| 4 tramos × 20 frames | AVIF; la escena casi negra comprime muy bien | ~1.2 MB |
| 5 loops idle | WebM/AV1, 2.5 s, 900×1600 | ~550 KB |
| 5 capas de primer plano | AVIF con alfa, sólo estaciones | ~200 KB |
| Total objetivo | | **~2.0 MB** |

Escritorio descarga su propio set 16:9 a 1600×900. Cada visitante baja un solo
set. La carga es progresiva: el hero pinta con el frame 0 y los tramos
siguientes se precargan mientras el visitante lee.

Si una estación pide más frames, salen del margen hasta 3 MB. Pasado ese techo,
se recortan frames de otro tramo.

## La escena en Blender

La escena se construye por script (`blender/altar.py`), no a mano. Queda
diffeable, reproducible y ajustable por parámetros. El `.blend` es un artefacto
de build y no se versiona.

### Geometría

Deliberadamente barata; el peso visual lo cargan la luz y la niebla.

| Elemento | Cómo se hace | Polígonos aprox. |
|---|---|---|
| Altar y nave | Cubos biselados; tres hornacinas restadas con boolean | 2k |
| Cruz de neón | Curva con bevel redondo, material emisivo rojo | 1k |
| Veladoras (7–9) | Cilindros + llama emisiva con blackbody | 3k |
| Vinilos y carátulas | Cilindros apilados con las carátulas reales del catálogo | 1k |
| Micro de bala | Cilindro + rejilla; el héroe de la estación 3 | 4k |
| Cadena de oro | Array sobre curva | 5k |
| M⚡T | Placa dorada extruida usando `/icon/mafiatumbada.webp` como alfa | 1k |

### Materiales

Cinco, no más: piedra oscura, oro (`metallic 1`, `roughness 0.25`, tintado a
`--gold`), neón rojo (emisión a `--red`), cera con llama, y un volumen de niebla
que atraviesa la nave. Los tokens de `DESIGN.md` entran como valores de
material, de modo que la escena y el CSS comparten el mismo color.

### Rig de cámara

Cámara con `Follow Path` sobre una curva que recorre la nave, apuntando a un
empty con `Track To`. El DOF enfoca un segundo empty. Las estaciones son
keyframes de esos tres valores: **encuadre, cámara y enfoque son tres canales
animables independientes**. Mover dónde cae el foco en una estación es mover un
empty, no rehacer la escena.

### Ajustes de render

**Cycles con OptiX**, 128 muestras y denoise. Decidido comparando ambos motores
sobre el mismo still el 2026-09-17: en EEVEE el oro de las hornacinas y el cromo
del micro salen **negros**, porque un metal sólo refleja su entorno y aquí el
entorno es negro. Cycles lo resuelve con rebotes reales, y el oro es media
identidad de la banda. Cuesta 1.2–1.5 s por frame a 640×360, lo que proyecta
unos 5 s a 1600×900: los dos juegos completos de frames caben en menos de una
hora. EEVEE queda como motor de vista previa rápida.
Motion blur con obturador **0.25** (era 0.5; corregido el 2026-09-17 tras
renderizar el tramo 0 completo: a 0.5, a media carrera entre estaciones el
retablo y la guitarra quedaban ilegibles. A 0.25 el arrastre sigue ahí y la
escena se lee. Cuesta 0.5 KB más por frame en AVIF, que cabe de sobra). Glare en el compositor para el neón
(EEVEE Next ya no expone panel de bloom). Dos pasadas sobre el mismo `.blend`,
cambiando solo el sensor de cámara: 1600×900 escritorio, 900×1600 móvil.

### Loops en bucle perfecto

Los idle se renderizan con la cámara quieta y se cierran con `ffmpeg xfade`: la
cola hace crossfade contra la cabeza. Con polvo y llama, que no tienen forma
fija, el empalme es invisible; no hace falta una animación matemáticamente
cíclica.

## Cadena de build

```
blender/altar.py        construye la escena (vía MCP, o blender -b -P)
blender/render.py       tramos + loops, ambos aspect ratios, PNG 16-bit
scripts/build-scene.sh  avifenc + ffmpeg -> public/scene/{mobile,desktop}/
                        escribe src/data/scene.json
```

`src/data/scene.json` es el contrato entre Blender y la web: estaciones, rango
de frames de cada tramo, rutas, y duración de cada loop. La capa web no sabe
nada de la escena salvo lo que lea de ahí, así que re-renderizar con otro número
de frames no toca una línea de TypeScript.

**Entorno:** Blender corre en Windows; el repo vive en `/mnt/e/…`, que allá es
`E:\`. Los scripts de render escriben rutas Windows. Se verifica en la fase 1,
antes de construir nada encima.

## Capa web

Dos archivos nuevos:

- `src/components/AltarScene.astro` — el `<canvas>` fijo de fondo, los
  `<video>` de cada estación con `preload="metadata"`, y el frame 0 como `<img>`
  estático debajo, que es a la vez el LCP y el fallback.
- `src/lib/scrollScene.ts` — aproximadamente 150 líneas: mapea `scrollY` a
  índice de frame, dibuja tras `decode()` para no parpadear, precarga el tramo
  siguiente, y detecta la detención del scroll para hacer crossfade al loop de
  la estación.

El contenido actual de `src/pages/index.astro` se conserva íntegro y se
reposiciona encima. Las secciones definen la altura de scroll. Cada sección de estación pide
`100svh` de mínimo y entre las dos últimas parejas hay un `.tramo-espacio` de
`50svh`, porque con las alturas naturales la cámara recorría veinte frames en
900 px de scroll en unos tramos y en 2005 en otros —el doble de velocidad en la
segunda mitad de la página—. Con eso el recorrido queda en ~820vh y los cuatro
tramos van a 80–105 px por frame. No se añade ni se pierde contenido: el
espacio de viaje está vacío y es `aria-hidden`.

## Accesibilidad

- La escena entera es `aria-hidden`. Ningún contenido vive solo dentro de ella.
- Con `prefers-reduced-motion: reduce`: sin scrub y sin loops. Cada sección
  muestra su frame clave fijo, con fade.
- Los retratos de la estación 2 son `<img>` HTML con su enlace a Instagram, no
  textura horneada: conservan `alt`, foco y click.
- Se mantienen las reglas vigentes de `DESIGN.md`: jerarquía `h1`→`h2`→`h3`,
  foco visible, objetivos táctiles ≥44px, contenido en español.

## Verificación

| # | Check | Cómo |
|---|---|---|
| 1 | Peso móvil ≤ 3 MB (objetivo 2 MB) | `scripts/check-budget.sh` suma `public/scene/mobile/` y falla si se pasa; corre en el build |
| 2 | LCP < 2.5s, CLS < 0.1, TBT < 200ms | Lighthouse móvil vía chrome-devtools MCP |
| 3 | Sin movimiento con `prefers-reduced-motion` | Toggle en DevTools: ni scrub ni video, frames fijos con fade |
| 4 | Escena caída = sitio usable | Bloquear `/scene/*` en DevTools; todo el texto y los CTA siguen presentes |
| 5 | Contraste AA sobre la escena | Recomputar cada texto contra el frame más claro de su estación, no contra `--bg` |
| 6 | Teclado y touch | Tab completo, foco visible, retratos clicables a 320/768/1280/1920 |
| 7 | Empalme tramo→loop invisible | Revisión visual en las cinco estaciones |

El check 5 es el más delicado: hoy el texto va sobre negro plano y `DESIGN.md`
trae una tabla de contraste medida contra `--bg`. Sobre una escena con velas
encendidas esa tabla deja de valer, y cada estación necesita su propio scrim
calculado contra su frame más claro. La tabla de `DESIGN.md` se actualiza como
parte de la fase 5.

## Fases

| Fase | Entrega | Puerta |
|---|---|---|
| 1 | Greybox sin materiales + rig de cámara, 5 stills a 480px; rutas Windows verificadas | Aprobación de encuadres |
| 2 | Materiales, luces, niebla; 5 stills finales | Aprobación del look |
| 3 | Render completo, conversión, `scene.json` | Peso dentro de presupuesto |
| 4 | Capa web y contenido migrado encima | Coincide con el storyboard |
| 5 | Reduced-motion, fallbacks, contraste, Lighthouse | Los siete checks pasan |

Las puertas 1 y 2 existen porque un encuadre malo renderizado a máxima calidad
son horas tiradas. Stills feos y rápidos primero.

## Riesgos

- **Texto sobre la escena.** Mitigación: scrim por estación, calculado contra su
  propio frame más claro (check 5).
- **Peso.** El objetivo deja poco margen. Si una estación pide más frames, salen
  del margen a 3 MB; pasado eso, se recortan de otro tramo.
- **Safari y AVIF.** Cubierto desde Safari 16. Si falla el decode, el canvas se
  queda en el frame estático y el sitio sigue leyéndose.
- **Tiempo de render.** EEVEE Next sobre NVIDIA dedicada mantiene el render en
  minutos, no horas. Si algún efecto obligara a Cycles, se reevalúa antes de
  la fase 3.

## Fuera de alcance

- Sección de fechas o tour.
- Comercio o merch.
- Contenido nuevo: el copy, las canciones, los videos y los integrantes son los
  que ya están en `src/data/`.
- Cualquier interacción 3D en vivo (orbitar, arrastrar, hover sobre objetos).

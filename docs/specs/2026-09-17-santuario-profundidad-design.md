# Santuario M⚡T — profundidad, pop-in y estación *altar*

> Diseño aprobado 2026-09-17. Rama `dev`. Extiende
> [`2026-09-16-santuario-3d-scroll-design.md`](./2026-09-16-santuario-3d-scroll-design.md),
> no lo reemplaza: el scrub de frames pre-renderizados sigue siendo el
> mecanismo. Lo que cambia es que el texto deja de flotar **sobre** la escena y
> pasa a vivir **dentro** de ella.

## Problema

La escena ya funciona: el scroll mueve la cámara por seis paradas y el texto se
lee encima. Pero el texto es una capa plana pegada sobre una imagen plana. No
hay profundidad, no hay entrada ni salida de los bloques, y el contenido largo
compite con la escena en vez de turnarse con ella.

## Principio rector

**Dos registros, frontera dura.** La escena es para contemplar; el panel es
para leer. Lo que se toca o se lee con detenimiento —listas, tarjetas,
formularios, enlaces— va en un panel opaco por encima de todo. Lo que se
contempla —un titular, una línea— va incrustado en la profundidad de la escena.
Un formulario detrás de una vela es mal UX y no se va a construir.

## Decisiones cerradas

| Decisión | Motivo |
|---|---|
| Capas con alfa, **no** PNG | Un frame 1920×1080 en PNG pesa ~2 MB. AVIF/WebP con alfa: ~20-60 KB |
| **Dos** capas, no tres | El frame plano ya contiene fondo y medio. Solo falta el frente |
| Capa de frente **solo en estaciones** | Ya era decisión cerrada en `docs/blender-notas.md`. Por frame sería 170×2 capas |
| Se mantiene el **scrub** continuo | Lo que hace fade y pop-in es el texto y la capa, no la cámara |
| Sexta estación: **altar** | Resuelve que `bio-section` fuera la única sección con titular sin parada de cámara |
| `Marquee.astro` **se borra** | Su texto duplica `hero-meta`, y es un movimiento horizontal peleando con el viaje de cámara |
| `avifenc`, **no** `ffmpeg` | libaom vía ffmpeg descarta el canal alfa. Alternativa: `cwebp` |

## 1. Render y capas

Pila por estación:

```
z:0  canvas                 frame plano del scrub          (existe)
z:1  TITULAR HTML           pop-in
z:2  <img data-capa-frente> alfa, solo en las 6 estaciones (por renderizar)
```

`blender/altar.py:1132` `render_capa_frontal()` **ya está escrita**: renderiza
por estación lo que esté más cerca que `distancia_cámara→sujeto × margen`
(0.78), con `film_transparent`, desconectando el volumen del mundo para que la
niebla no llene el alfa. Nunca se ha ejecutado a resolución real, ni encodeado,
ni servido.

Trabajo:

1. Ejecutar `render_capa_frontal()` en los dos formatos → 12 PNG RGBA.
2. Revisar `margen` estación por estación. Es un factor de distancia, no una
   verdad: si en hornacinas mete la banca entera, baja para esa estación.
3. Encodear con `avifenc` (alfa) o `cwebp` si no está disponible. CRF más
   agresivo que el 30 de las estaciones: la capa es casi toda transparente.
4. `scripts/scene-json.py` añade `capaFrente: { imagen, bytes }` por estación.

**Verificación:** componer `frente` sobre el frame plano de la misma estación y
comparar contra el frame plano original. Deben ser idénticos. Si difieren, hay
un objeto renderizado dos veces con bordes distintos.

## 2. Estación nueva: *altar*

Segunda fila de `ESTACIONES` en `blender/altar.py:43`. Las columnas son
`(nombre, frame, offset_en_curva, aim, foco, focal_mm, altura, dist_foco)`.

```python
("nave",    1,   0.000, "AIM_altar", "AIM_altar", 28.0, 0.00, 4.0),
("altar",   21,  ?,     "AIM_altar", "AIM_altar", 24.0, ?,    ?  ),   # nueva
("sonido",  41,  0.825, "PROXY_vinilo", ...
```

- **24 mm.** Mete el retablo entero y las columnas laterales en cuadro —que es
  lo que alimenta la capa de frente— sin llegar al 18 mm, donde las rectas del
  muro se curvan y se delata el CG. Al renderizar se comparan 24, 28 y 20, y el
  usuario elige mirando.
- **Los `?` se miden.** Offset en curva, altura y distancia de foco salen de
  renderizar 3-4 candidatos a 800×450, igual que salieron los otros cinco
  encuadres. No se estiman en este documento.
- **Riesgo conocido:** la cámara es la misma para los dos formatos; solo cambia
  la resolución. Un 24 mm frontal en 9:16 mete mucho techo y mucho piso. Si en
  móvil sale vacío, la salida es un offset distinto en la curva para ese
  formato, **no** otra lente.

Arrastra:

| | antes | después |
|---|---|---|
| estaciones | 5 | 6 |
| tramos | 4 × 20 | 5 × 20 |
| frames | 80 | 100 |
| `data-estacion` | 0-4 | 0-5 (`#musica` pasa de 1 a 2) |
| altura de página | 820vh | ~970vh |

**Una sola tanda de render, o se paga dos veces:**

1. Tramos nave→altar y altar→sonido (sustituyen al tramo-0 actual).
2. Tramos 1 y 2: los toca el cambio de lente de hornacinas, **34 → 28 mm**, que
   venía pendiente de la sesión anterior.
3. Las 6 estaciones y sus 6 capas de frente.

≈100 frames × 2 formatos × 10 s ≈ **35 min**, solo escritorio. Los tramos
reliquia→retirada no se tocan.

## 3. Capa web

Una sola señal manda sobre la capa de frente y sobre el pop-in del texto: la
distancia en frames entre el frame actual y el frame de la estación.

```
cercania = 1 - min(|frameActual - frameDeEstacion| / VENTANA, 1)
```

`cercania = 1` → capa opaca, titular dentro de la escena.
`cercania = 0` → capa invisible, scrub plano de siempre.

Esto no es decoración. La capa de frente es **una imagen fija** y el fondo se
mueve: fuera de la estación las dos cosas no encajan. La ventana de fundido
existe para que nadie vea ese desencaje.

**`VENTANA` arranca en 4 frames y se mide.** Se sube hasta que el fundido se
sienta suave y se baja en cuanto la vela empiece a flotar sobre un fondo que ya
se movió. Es el único número de esta sección que no se puede decidir en un
documento.

Código nuevo, y es poco:

- `src/lib/scrollScene.ts`: un callback opcional `alCambiarFrame`, llamado donde
  ya se escribe `canvas.dataset.frame`. Una línea. Nada más se toca.
- `src/lib/capasEstacion.ts`: la función pura `cercania()` más el montaje que
  aplica opacidades y escribe `data-cerca` en cada sección. Con test, al lado de
  `scrollScene.test.ts`.
- `src/components/AltarScene.astro`: renderiza los `<img>` de frente leyendo
  `capaFrente` de `scene.json`.

**Pop-in del texto:** el módulo escribe `data-cerca` en la sección y el CSS hace
la transición (`opacity` + `translateY` corto). Se descarta
`animation-timeline: view()`, que sería lo nativo: se dispara con el **borde**
de la sección y la estación vive en el **centro** — el mismo error que ya está
documentado en `scrollScene.ts` para los enlaces `#hash`.

**Degradación:** si `capaFrente` no existe en `scene.json`, no se pinta nada y
la página queda exactamente como hoy. Sirve de interruptor durante la
implementación.

**`prefers-reduced-motion`:** sin scrub hay un still por estación, así que la
capa de frente va opaca y fija, sin transición, y el pop-in aparece sin animar.
La profundidad se conserva; el movimiento no.

## 4. Contenido y ritmo

Patrón, igual en las seis:

```
┌ 100svh ─────────────┐
│  TITULAR incrustado │  entre canvas y capa de frente. Titular + eyebrow.
│  (nada más)         │  Sin párrafos: aquí se lee una línea.
└─────────────────────┘
┌ panel de cuerpo ────┐  z:3, --bg-raised opaco. Sube tapando la capa de
│  lista, tarjetas,   │  frente. Aquí se lee, no se contempla.
│  formulario         │
└─────────────────────┘
   .tramo-espacio        viaje de cámara, nada que leer
```

| # | estación | titular incrustado | panel |
|---|---|---|---|
| 0 | nave | logo MTO + metadatos + CTA WhatsApp | — |
| 1 | altar | El sonido de *Xalapa* | bio |
| 2 | sonido | Música | videos y catálogo |
| 3 | hornacinas | El grupo | 5 integrantes |
| 4 | reliquia | ¿Tienes una *fecha disponible?* | contacto |
| 5 | retirada | monograma MTO | socials y copyright |

**Cambia el orden de lectura.** Hoy `bio-section` va después de Música en el
DOM; su estación es la 1, así que sube por delante: logo → quiénes son → música
→ integrantes → contratar. Es mejor orden narrativo, pero es un cambio, no un
efecto secundario.

**La nave es la única sin panel.** La retirada sí lleva: seis enlaces de redes
son interactivos, y lo que se toca no va detrás de una vela.

**Altura.** La perilla ya está documentada: `.tramo-espacio` de `50svh` a
`25svh` devuelve los ~970vh a ~820. No se toca en la implementación inicial:
con seis paradas primero se mira, porque acortar el tramo acelera la cámara.

**Lo que NO cambia:** tokens, tipografía, `FilmStrip`, `ArtworkShelf`,
`MemberCard` y el menú de cabecera. Los componentes de contenido entran en el
panel tal cual están.

### Hero y footer

Hero (estación 0):

```
incrustado:  logo MTO
             Xalapa, Veracruz · Corridos Tumbados · Desde 2021
             [Escríbenos por WhatsApp]
```

- `hero-blurb` **se muda** al panel de la estación 1. Ya era la bio: hoy ese
  párrafo y `bio-section` dicen lo mismo en dos sitios. Se muda, no se reescribe.
- `hero-meta` pasa de cuatro chips a una línea. "Regional Mexicano" se cae por
  redundante con "Corridos Tumbados".
- El CTA de WhatsApp se queda: es un enlace, no un formulario, y es la
  conversión principal.

Footer (estación 5): monograma incrustado, y socials más copyright en panel.

**Muerto que este rediseño deja sin excusa:**

- `hero-video` y `src/lib/heroVideo.ts` — en `display: none` desde que entró la
  escena. Se borran.
- `.hero::before` / `::after` — ya neutralizados desde `AltarScene.astro` con
  `background-image: none` y `box-shadow: none`. Se borran de su propia hoja en
  vez de anularse desde otro archivo.
- `Marquee.astro` y su uso en `index.astro`.

`hero-grain` se queda, con reserva: el render de Cycles ya trae grano propio. Si
al verlos juntos se nota doble, se quita. Es mirar, no decidir aquí.

## 4b. Presupuesto de peso y calidad

**El techo de 3 MB se levanta** (decisión del usuario, 2026-09-17: un hero de
10 MB carga bien en 5G en otro proyecto suyo). Hoy la escena pesa **1.06 MB por
formato**; con 100 frames, ~1.3 MB. No estamos recortando calidad por peso:
sobra margen sin usar.

Dónde gastarlo, **en este orden**, parando en cuanto se vea bien y no hasta
llenar el presupuesto:

| # | Dónde | Qué compra | Coste |
|---|---|---|---|
| 1 | Frames por tramo, 20 → 30 | Suavidad del scrub. Hoy son 20 frames por ~1000 px de scroll y los escalones se ven | ~+0.6 MB, +50% de render |
| 2 | Resolución desktop, 1600×900 → 1920×1080 | Nitidez: hoy se estira hasta 2560 px | +40% píxeles, poco en AVIF, solo desktop |
| 3 | CRF de tramos, 38 → 32 | Menos banding en los degradados oscuros, que es *el* artefacto de esta escena | Por medir; el 38 se calibró mirando y puede estar bien |

Los tres se deciden mirando el resultado, no en este documento. `scripts/check-budget.sh`
mide el formato más pesado y sigue siendo la referencia.

## 5. Contraste y accesibilidad

**Error real detectado al diseñar la capa web.** `.altar-escena__velo` es negro
al 0.62 sobre el canvas, y el texto se lee encima. La capa de frente va por
encima del texto, o sea **por encima del velo**: saldría a brillo completo sobre
una escena atenuada al 38%, como un recorte pegado. Y el ajuste de la sección 1
—componer el frente sobre el plano devuelve el frame original— dejaría de ser
cierto en el navegador.

Tapar con negro al 0.62 equivale a multiplicar el color por 0.38:

```css
[data-capa-frente] { filter: brightness(0.38); }  /* mismo velo, respeta el alfa */
```

El 0.62 y el 0.38 salen del mismo sitio y se atan con una variable CSS, no con
dos literales: si el velo cambia, cambian juntos.

**La tabla de contraste de `DESIGN.md` se recalcula** — ya estaba marcada como
rota por estar medida contra negro plano. Lo que cambia respecto a lo previsto:

- Se mide contra la **composición final** (velo + frente atenuado), no contra el
  frame plano.
- Se mide **por estación y en la zona donde cae el texto**, no en el cuadro
  entero. Mismo método de percentil 95 que ya usa el repo.
- *altar* es candidata a ser la más brillante de las seis: un 24 mm frontal del
  retablo iluminado. Si obliga a subir el velo por encima de 0.62, sube para
  todas: un velo por estación no vale lo que cuesta.

**Oclusión del titular.** WCAG no cubre que una vela tape una letra, pero la
legibilidad sí. Regla: la capa de frente **rodea** el titular, no lo cruza. Se
verifica mirando las seis; si en alguna cae encima, el titular cambia de
columna. El layout ya es asimétrico, hay sitio.

**El texto es visible sin JS.** El CSS base deja el titular visible; solo cuando
el módulo ha escrito `data-cerca` se hace cargo de la animación. Si el script
falla o tarda, se lee la página entera. Mismo criterio que el `<img>` de LCP.

**Sin cambios:** orden de lectura del DOM (el titular sigue siendo `h1`/`h2`
real), foco visible, 44 px de área táctil, `aria-hidden` y `pointer-events:
none` en toda la escena.

## Criterios de aceptación

1. Componer capa de frente sobre frame plano reproduce el frame plano original.
2. Las seis secciones centradas dan sus seis frames de estación exactos.
3. Con el scrub en marcha, en ningún punto se ve la capa de frente desencajada
   del fondo.
4. Peso medido y anotado por formato; sin techo duro, pero ningún gasto
   sin mejora visible que lo justifique.
5. Contraste AA en las seis estaciones, medido sobre la composición final en la
   zona del texto.
6. Con JS desactivado se lee la página entera, con su orden y sus enlaces.
7. Con `prefers-reduced-motion` no hay scrub, ni fundido, ni pop-in animado.

## Fuera de alcance

- Parallax por `translateZ` entre capas. Se añade encima de esto sin rehacer
  nada, y trae un problema propio: detrás de la vela no hay píxeles renderizados.
- Botones de navegación por estación. El marcado ya está listo (`data-estacion`,
  `id` estable) y el aviso de que no pueden ser enlaces `#hash` está en
  `scrollScene.ts`. Es una decisión de diseño pendiente, no de esta spec.
- Los 5 loops de vídeo de estación (punto 3 de la fase 3). Con seis estaciones
  ahora serían 6.
(La licencia de `blender/assets/guitarra.blend` **no** está fuera de alcance:
es la puerta del paso 1, más abajo.)

## Puerta previa: la guitarra

`blender/assets/guitarra.blend` viene de Blend Swap sin archivo de licencia. Es
geometría de la escena, así que **se resuelve antes de lanzar el render**: si se
cambia el asset después, hay que re-renderizar los 100 frames y las 6 capas
(35 min) y volver a medir el velo.

Tres salidas, en orden de preferencia:

1. Licencia verificada y compatible → seguir, acreditar donde toque. Si resulta
   CC-BY hay que acreditar **en el sitio**, no solo en `CREDITOS.md`.
2. Sustituirla por un asset con licencia clara → una línea en `blender/assets.py`,
   y el render que íbamos a hacer de todos modos. Ojo: el contrabajo
   (`blender/altar.py:494`) es el mismo asset escalado a 1.85 m, así que la
   sustitución afecta a dos objetos, no a uno.
3. Modelarla → solo si 1 y 2 fallan.

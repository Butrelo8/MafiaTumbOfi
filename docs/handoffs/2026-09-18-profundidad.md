# Handoff — Mafia Tumbada, santuario 3D

Sesión del 2026-09-17 (21:00 → 00:00). Rama `dev`, árbol limpio, último commit
`64da4f4`. 18 commits nuevos sobre `main`, todos con el porqué en su mensaje:
`git log main..dev`.

## Qué es esto

`mafiatumbada.com` es una página única de Astro cuyo scroll dirige una cámara
por un santuario en 3D. La escena **no** se renderiza en el navegador: son
frames pre-renderizados en Cycles que el scroll reproduce sobre un `<canvas>`,
con todo el texto en HTML encima.

## Lee esto antes de tocar nada

| Documento | Qué manda |
|---|---|
| `docs/HANDOFF.md` | Estado general del repo. **Desactualizado en dos puntos**, ver abajo |
| `docs/specs/2026-09-17-santuario-profundidad-design.md` | El diseño aprobado de esta sesión |
| `docs/plans/2026-09-17-profundidad-implementation-plan.md` | Las 7 fases con sus puertas |
| `docs/blender-notas.md` | Obligatorio antes de tocar `blender/` |
| `DESIGN.md` | Tokens; la tabla de contraste sigue rota, se recalcula en la fase 6 |

## Dónde se quedó

Fases **0 a 4 cerradas**, fase **5 sin empezar**.

- **0** — Licencias resueltas. Ningún asset queda sin licencia escrita: todo CC0,
  verificado contra Blend Swap y anotado en `public/scene/CREDITOS.md`.
- **1** — Encuadres. Entra una sexta estación (`altar`), hornacinas cambia de
  lente, ventanas góticas con tormenta detrás del cristal, el rayo M⚡T sustituye
  a la cruz de neón, y una fiel sentada de espaldas en una banca.
- **2** — Render: 336 imágenes en 77 minutos, sin fallos.
- **3** — Encode y `src/data/scene.json`.
- **4** — Capa web: `src/lib/capasEstacion.ts` + callback en `scrollScene.ts` +
  los `<img>` en `AltarScene.astro`. **Escrita y con test, pero sin verificar en
  el navegador**, porque la fase 5 la bloquea.

## Lo siguiente, y por qué está bloqueado

**La página tiene 5 secciones `data-estacion` (0-4) y la escena ya tiene 6.**
Hasta que la fase 5 renumere, las capas se montan contra índices que no
corresponden y el scrub nunca pasa del frame 120 de 149.

La fase 5 está detallada en el plan. En resumen: subir `bio-section` por delante
de Música y darle `data-estacion="1"`, renumerar las seis, aplicar el patrón de
titular incrustado + panel opaco, rehacer hero y footer, y borrar
`Marquee.astro`, `src/lib/heroVideo.ts` y las reglas `.hero::before/::after`.

## Trampas que ya costaron tiempo

1. **No reconstruyas la escena mientras el usuario coloca cosas en el visor.**
   `build()` borra todo y levanta desde el código. El flujo correcto está en
   `blender/poses.py`: volcar ANTES, reconstruir, comparar, y escribir las
   diferencias como constantes. Ya pasó una vez: se perdió una pose.
2. **El servidor de desarrollo es inservible para juzgar rendimiento.** Astro dev
   tarda 1.6–2.4 s por archivo de 15 KB cruzando WSL↔Windows; el mismo archivo
   servido desde `dist/` tarda 14 ms. Medir siempre sobre el build.
3. **`scroll-behavior: smooth` está activo.** Un `scrollTo` tarda ~1.3 s en
   llegar, así que cualquier medición programada del scrub tiene que
   desactivarlo o mide la página en pleno vuelo.
4. **Los assets de Blend Swap llegan con `scale` ya aplicada.** Hay que
   multiplicar la escala, nunca sustituirla. Una ventana salió de 2 cm.
5. **Para apoyar un asset en una superficie se usa `_plantar`**, que crea un
   ancla en la base de la caja envolvente. Restar el mínimo de la caja a la
   ubicación no vale porque el origen del asset no está en cero.

## Medidas que no hay que repetir

- **Decode por frame** (medido en Chrome, frame real de tramo a 1920):
  AVIF 45.3 ms · WebP 1920 17.4 ms · WebP 1600 11.3 ms · WebP 1280 6.5 ms.
  Por eso los tramos son WebP y las estaciones AVIF.
- **Coste por frame de scroll**: leer el layout 0.01 ms, `drawImage` 0.01 ms.
  Ninguno de los dos es el problema. Quedan ~19 ms de pintado de la página que
  **también ocurren con la escena oculta**: es el CSS actual, y la fase 5 lo
  reescribe entero.
- **Peso**: desktop 4.56 MB, móvil 4.48 MB. El usuario levantó el techo de 3 MB
  el 2026-09-17 (un hero de 10 MB le carga bien en 5G).

## Abierto, sin decidir

- **Material del cinturón**: usa `MTO_fieltro` desde que era una caja; ahora es
  cuero de verdad en primer plano. Añadir un material de cuero son cuatro líneas
  en `blender/look.py`.
- **El monograma dice "SV"** (SANTO VICIO, marca inventada, `MARCA_MONOGRAMA`).
  Si el retablo ya lleva el rayo M⚡T, quizá el cinturón también.
- **Derrame abocinado en las ventanas**: haría que el relámpago pinte una cuña de
  luz en el muro. Es lujo, no bloquea.
- **`docs/HANDOFF.md` desactualizado**: los retratos de las hornacinas ya no son
  huecos negros, y la licencia de la guitarra ya está resuelta. Lo segundo ya se
  corrigió; el fichero necesita un repaso completo en la fase 6.
- **Las 44 puntadas de pitiado** se fueron con la correa vieja. Era un prop del
  usuario; él lo sabe y no pidió recuperarlas.

## Cómo mirar la página

Con el build, nunca con `bun dev`, por el punto 2 de arriba:

```bash
bun run build && (cd dist && python3 -m http.server 4399)
```

`tmp/frames` ocupa 2.3 GB de PNG de 16 bits; está en `.gitignore` y se puede
borrar, pero re-encodear sin volver a renderizar exige conservarlo.

## Suggested skills

- `brainstorm` — si hay que rediseñar algo antes de escribir código. Fue el que
  produjo la spec de esta sesión.
- `code-review` — sobre el diff de `dev` antes de fusionar a `main`.
- `design:accessibility-review` — para la fase 6, que recalcula el velo y la
  tabla de contraste de `DESIGN.md`.
- Skills de Cloudflare (`cloudflare:wrangler`) — sólo cuando toque desplegar;
  el sitio va en Workers Static Assets.

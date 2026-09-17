# Handoff — Santuario M⚡T

> Escrito 2026-09-17, 02:30 CST. Rama `dev`, 18 commits por delante de `main`.
> Formato según la skill `matt-handoff` de mpaf, guardado en el repo (y no en
> el temporal del sistema, como sugiere la skill) para que sobreviva entre
> sesiones.

## Qué se está haciendo

Rehacer mafiatumbada.com como una página cuyo scroll dirige una cámara por un
santuario en 3D. La escena **no** se renderiza en el navegador: son frames
pre-renderizados en Cycles que el scroll reproduce sobre un `<canvas>`, con
loops de vídeo cuando el scroll se detiene y todo el texto en HTML encima.

Cinco estaciones: nave, sonido, hornacinas, reliquia, retirada.

## No dupliques esto, léelo

| Documento | Qué contiene |
|---|---|
| `docs/specs/2026-09-16-santuario-3d-scroll-design.md` | El diseño aprobado: storyboard, presupuesto de peso, capa de primer plano, accesibilidad, verificación. Manda sobre cualquier improvisación |
| `docs/plans/2026-09-16-santuario-3d-implementation-plan.md` | Fases, puertas y el resultado real de cada una, con las correcciones sobre la marcha y las decisiones de dirección de arte |
| `docs/blender-notas.md` | **Léelo antes de tocar `blender/`.** Quirks de Blender 5.2, trampas al importar assets, método de medición, y una sección de arranque con el bloque de código que levanta la escena |
| `public/scene/CREDITOS.md` | Licencias de todo lo que no es nuestro |
| `DESIGN.md` | Tokens de color y tipografía del sitio; la escena 3D los consume |

El historial de `git log main..dev` cuenta el resto: cada commit explica **por
qué**, no sólo qué.

## Estado

**Fases 0, 1 y 2 cerradas** — entorno verificado, encuadres aprobados, look
terminado con props y assets externos. La escena son 380 objetos, unas 85.000
caras en render, y los cinco encuadres en los dos formatos salen en 28 s.

**Lo siguiente es la fase 3**, que ya es producción y no diseño:

1. Calibrar CRF convirtiendo un still final a AVIF y midiendo el peso real
   (tarea heredada de la fase 0; sin esto no se sabe cuántos frames caben).
2. Renderizar 4 tramos × 20 frames con motion blur, en los dos formatos.
3. Renderizar los 5 loops de estación a 24 fps con llama, humo de cigarro,
   polvo en los haces y parpadeo del neón; cerrarlos en bucle con `ffmpeg xfade`.
4. `scripts/build-scene.sh` → AVIF + WebM + `src/data/scene.json`.
5. `scripts/check-budget.sh` → falla por encima de 3 MB en móvil.

Después, fase 4 (capa web) y fase 5 (accesibilidad y verificación).

## Decisiones cerradas — no las reabras sin motivo nuevo

- **Cycles con OptiX**, no EEVEE: en EEVEE el oro y el cromo salen negros.
- **Frames pre-renderizados**, no three.js ni glTF en vivo.
- **El glow del neón va en post con ffmpeg**: el compositor de Blender 5 devuelve
  negro incluso en passthrough.
- **Capa de primer plano sólo en las estaciones**, nunca por frame.
- **Sin sección de fechas** en el sitio (decisión de 2026-09-09).
- **Presupuesto**: 2 MB objetivo por visitante móvil, 3 MB de techo duro.
- **Sin marcas reales**: la gorra y la hebilla llevan una marca ficticia propia,
  SANTO VICIO (constantes `MARCA` y `MARCA_MONOGRAMA` en `blender/altar.py`).
- **Sin arma en la escena**: decisión de negocio documentada en el plan,
  reversible si la banda la pide.

## Pendientes y bloqueos

- **Licencia de `blender/assets/guitarra.blend` sin verificar.** Se descargó de
  Blend Swap sin su archivo de licencia. Está marcado en `CREDITOS.md`. Si
  resulta CC-BY, hay que acreditar al autor **en el sitio**, no sólo en el repo.
  Es lo único que puede obligar a cambiar la página antes de publicar.
- **Los detalles que Gemini atribuyó a los videos de la banda** (gorra de
  parches, marca de tequila, vapes) no están verificados por nadie que conozca
  su material. Se adoptaron porque funcionan como dirección de arte, no como
  identidad documentada. Ver el plan.
- **La tabla de contraste de `DESIGN.md` sigue calculada contra negro plano** y
  deja de valer en cuanto haya texto sobre la escena. Se recalcula en la fase 5.
- **Los retratos de las hornacinas** son huecos negros hasta que la capa web
  ponga encima las fotos reales con su enlace a Instagram.

## Trampas que ya costaron tiempo

Están todas en `docs/blender-notas.md`, pero estas tres se repiten:

1. **Mide, no mires.** `image.pixels` dentro de Blender dio el mismo resultado
   en todas las pruebas y mandó la investigación por el camino equivocado. Lo
   fiable es ffmpeg desde fuera, más `md5sum` para descubrir que dos renders
   "distintos" son idénticos.
2. **`build()` no resetea los ajustes de escena.** Cualquier A/B tiene que
   limpiar `view_settings`, `scene.eevee`, `use_nodes` y el volumen del World, o
   estará midiendo los restos de la prueba anterior.
3. **Al importar assets**: escalar cada pieza por separado no encoge el grupo,
   `ob.scale =` sobrescribe en vez de multiplicar, el origen no está en la base,
   y un Subsurf heredado convierte 2.000 caras en 55.000 al renderizar.

## Cómo hablar con el usuario

Escribe en español. Prefiere que se le contradiga con datos antes que
complacencia: varias decisiones buenas de esta sesión salieron de decirle que
algo no funcionaba (la gorra a la tercera, el tololoche que no cabía, las
licencias). Quiere ver resultados renderizados, no descripciones.

Las hojas de contactos se generan con `ffmpeg xstack` a `tmp/`, que está
ignorado por git; él las abre desde Windows en `E:\Cursor Projects\MTO\tmp\`.

## Skills sugeridas para la próxima sesión

- `brainstorm` — si se replantea alguna estación o entra contenido nuevo; fue el
  flujo que produjo el spec y el plan.
- `caveman` / `ponytail` — **apagadas a petición del usuario** para este trabajo.
  No las reactives sin que lo pida.
- `cloudflare:web-perf` — en la fase 5, para el Lighthouse móvil y los Core Web
  Vitals del scrub.
- `code-review` — antes de mezclar `dev` en `main`.

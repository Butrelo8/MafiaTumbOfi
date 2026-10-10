# 10 — Acabado visual de la UI
Type: prototype · Status: open · Blocks: — · Blocked by: 03, 07 · Assignee: —

## Question
Con las escenas ya dirigidas: ¿la tipografía, el color y los componentes actuales (Gótico Tumbado,
`DESIGN.md`) siguen casando con el santuario fotográfico, o algo se rehace? Prueba sobre los cuadros de
estilo de los cinco espacios.

> Nota (2026-10-05, ticket 05): diseñar el aviso de "cargando" del gesto que espera la precarga (hoy placeholder:
> la línea roja bajo el número del menú se llena); se resuelve con Figma.

## Avance (2026-10-10): herramientas de gusto para la UI y primera pasada

Investigación en visual-lab: `/home/black/projects/visual-lab/cross-tool/ui-taste-skills-eval-2026-10-10.md`
(skills instaladas vs. externas, veredictos para MTO). La conclusión de todas las fuentes: el gusto no lo pone una
skill. Lo ponen las referencias, `DESIGN.md` y revisar la captura antes de dar algo por bueno. Una skill de diseño
por sesión, invocada por su nombre.

- **Auditoría con impeccable** (`npx -y impeccable@4.5.2 detect --json --no-config <ruta>`, sin instalar nada en el repo):
  - **Sitio actual, `dist/index.html`: 59 hallazgos.**
    - Reales:
      - enlaces de streaming a 9.92 px y del menú a 10.88 px (mínimo 11);
      - texto rojo `#9b4333` sobre `#060403` a 3.2:1;
      - hijos pegados al borde en `estacion-panel` y `mobile-menu`.
    - De marca, se quedan: el degradado dorado del texto y el brillo dorado.
    - Falsos: Pirata One leído como serif itálica; el `src` vacío del diálogo de zoom (lo llena JS); contrastes medidos
      sobre el video, que el detector no ve.
  - **Prototipo del rediseño `tmp/movil-06/web/`: 1 hallazgo**, crema `#e8e2d8` sobre rojo `#d4202a` a 4.0:1 (pide 4.5:1).
  - El hook de impeccable no se instaló: se corre `detect` a mano por prototipo.
- **Skills instaladas** en `.claude/skills/` (sin commit): `review-animations` (revisión estricta de movimiento:
  transiciones, paneles D/E) y `animation-vocabulary` (el nombre exacto de cada efecto, para pedirlo bien).
- **Gusto de las referencias del ticket 03** (travisscott, white-desert, igloo; método `/taste`):
  `/home/black/projects/visual-lab/web/taste-dna-mto-refs-2026-10-10.md`. Propone cinco reglas con su porqué para
  `DESIGN.md`. **Pendiente: decidir cuáles entran.**
  1. La interfaz no lleva color de marca: el oro sólo en la única acción y en el titular.
  2. Una fuente de interfaz a dos tamaños, mínimo 14 px; la gótica sólo en el titular de la sección.
  3. Contraste por salto de tamaño, no por añadir elementos.
  4. Velo, no tarjeta: sin relleno, sin sombra, radio ≤ 2 px o píldora.
  5. Escala de tiempos con una sola curva (p. ej. 0.22 / 0.44 / 0.9 s).
- **Variantes de la pieza E de Música** sobre el cuadro real de la sacristía, con portadas reales y los tokens de
  `DESIGN.md`, en un lienzo de Claude Design: https://claude.ai/artifact/14tvkoVv8GH2oo1r7iqg6F (privado).
  A paso con texto, B portada grande, C tira con vecinos, y A en móvil 390. **Pendiente: elegir.** Sólo 4 de las 9
  portadas están cargadas.
- **Figma, decidido por el usuario el 2026-10-10:** fuera del camino de MTO. Las variantes de UI y el aviso de
  "cargando" de la nota de arriba se prueban en el lienzo de Claude Design o directo en código. Figma queda para
  clientes que lo pidan y para práctica.

# Context

Glosario del santuario en movimiento. Sólo términos; las decisiones viven en `.wayfinder/santuario/`.

- **Santuario**: el lugar ficticio por el que el scroll lleva al visitante. Una iglesia colonial mexicana de noche.
- **Espacio**: un lugar distinto del santuario, uno por sección (nave, sacristía, camarín de las hornacinas,
  cripta, atrio). Se genera por separado de los demás.
- **Estación**: término viejo (spec del 2026-09-16) para una parada de la cámara dentro de la *misma* capilla.
  Sobrevive en el código (`data-estacion`, `capaFrente`); en conversación se dice *espacio*.
- **Transición**: el paso de un espacio al siguiente, avanzado con el scroll. Nunca un fundido.
- **Oclusor**: el objeto oscuro (pilar, jambaje, banca) que tapa todo el cuadro mientras cae el corte entre dos
  espacios.
- **Loop**: el video del espacio que corre cuando el scroll se detiene.
- **Reliquia**: el instrumento protagonista de un espacio (requinto, tololoche, micrófono de bala). Uno por
  espacio.
- **Titular**: el título HTML de la sección, compuesto sobre la escena en el hueco que la toma le deja.
- **Ruta M / Ruta D**: cómo se hace el loop de un espacio. M = MiniMax H3 con ControlNet de profundidad;
  D = DepthFlow sobre un cuadro fijo.
- **Cuadro de estilo**: la imagen de Klein que fija el look de un espacio; MiniMax la toma como primer cuadro.

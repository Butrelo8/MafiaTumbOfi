# Handoff — ticket 06 (móvil) y prueba de props en las bancas (2026-10-05)

Formato `matt-handoff` (mpaf). Guardado en el repo y no en el temporal del sistema, como los handoffs anteriores, para
que sobreviva entre sesiones.

## Qué sigue (lo que pidió el usuario)

**Prueba "all out" de props y gente en las bancas vacías**, en stills de escritorio y vertical, **antes** de correr H3.
El usuario eligió las cuatro opciones a la vez:

1. **Señora con rebozo**, sentada de espaldas, cabeza cubierta con rebozo oscuro, rezando, en la **4.ª banca derecha**.
2. **Nardos blancos con listón** en las cabeceras del pasillo, filas 2–6.
3. **Texana negra con un rosario encima**, dejados en la **6.ª banca derecha**.
4. **Joven de gorra y sudadera, de espaldas**, sentado atrás, como fan escuchando. No hay asiento medido para él: buscar
   uno con el mismo método.

Lo que se midió (rayo desde la cámara + `world_to_camera_view`; cabeza sentada a z 1.15; fila i → y = 6 + 1.2·i + 0.3):

| Lugar | Escritorio u, v | Vertical u, v | Nota |
|---|---|---|---|
| Banca derecha x 1.9, filas 3–4 | 0.70–0.73, 0.40–0.41 | 0.67–0.70, 0.71 | **libre en los dos y fuera del hueco del texto** |
| Banca derecha x 1.9, fila 6 | 0.66, 0.43 | 0.64, 0.72 | libre (texana) |
| Banca izquierda x −1.4, filas 2–7 | 0.30–0.39, 0.38–0.44 | 0.04–0.26, 0.70–0.72 | en escritorio cae **dentro** del hueco de la esquina inferior izquierda (ticket 03): evitar |
| Junto al pasillo x 0.9 | filas 2, 5, 7 tapadas por bocina/requinto/veladora | libre | |

Reglas para la prueba:
- Gente **de espaldas, sin cara** y lejos (~8 m): una cara de 40 px se deforma, y en H3 la gente se mueve.
- Nada más brillante que los instrumentos. Paleta del DESIGN.md (negro/oro, rojo sólo de acento): **nada de papel picado
  de colores**, armas ni botellas protagonistas.
- Ponerlo en la **maqueta** (`blender/transicion.py`, como `capillas()`), comprobar cruces con BVH **en el mundo** (ver
  `docs/blender-notas.md`, al final) y que se vea con rayos. Luego Klein de escritorio (sin referencia, 3 semillas) y la
  vertical con la escritorio elegida como referencia (`klein_pila.sh`, `ESC=<semilla>`), cada una en lienzo alto.
- Klein copia los **tonos** de la maqueta: dale a las figuras un gris que se lea (no negro sobre negro).
- Enseñar los stills al usuario **antes** de H3.

Después de que apruebe (lo que quedó en pausa):
1. **Escritorio r8:** zonas a mano sobre la placa nueva, H3 del loop (canny de la placa, 40 pasos), RTX ×1.5, `velas.py`,
   `polvo.py`, montaje como `tmp/movil-06/polvo/montar_r7.sh`. Página: `tmp/placa-13/index.html` (añadir r8).
2. **Vertical:** lo mismo en `tmp/movil-06/viva/` (`zonas.py`, `h3.sh`, `velas.py`, `montar.sh`) y las dos mitades de la
   transición (`tmp/movil-06/h3.sh` con `V=e`, `NAVE_PLACA`/`SAC_PLACA`; `montar.sh` con `CUT=28`). Primero rendir de nuevo
   los pases `z` y `mascara` del tramo T con `build(movil=True)`: la nave cambió.
3. Cerrar el ticket 06: escribir su **Answer** y moverlo a "Decisions so far" en `.wayfinder/santuario/MAP.md`.

## Dónde está todo (no lo dupliques: léelo)

- **Ticket 06 completo:** `.wayfinder/santuario/tickets/06-movil.md` (Prueba, v2, v3, v4): cámara vertical propia,
  Klein ignora el `shift_y` (lienzo alto + recorte), Klein con referencia, polvo en la luna, zona segura 19.5:9
  (sacristía en x 45.4), nave vertical viva, bocina en el piso.
- **Mapa:** `.wayfinder/santuario/MAP.md`. Método de loops: ticket 13.
- **Quirks:** `docs/blender-notas.md` (al final: shift de Klein, estado que deja `render()`, BVH en local) y
  `ProyectoInvestigación/research/escenas-ia-transiciones-2026-10-04.md` (secciones del ticket 06).
- **Escena:** `blender/transicion.py`: `MOVIL` (28 mm, shift −0.25, nave x 0.8, sacristía x 45.4), `build(movil=True)`,
  `instrumentos()` con sub + bocina en el piso y requinto de madera clara.
- **Prototipos** (`tmp/`, ignorado): `tmp/movil-06/` (`web/` = página móvil; `klein_*.sh`, `h3.sh`, `montar.sh`,
  `polvo.py`, `medir.py`, `viva/`, hojas `.jpg`), `tmp/placa-13/` (escritorio, r7 = r6 + polvo).
- **Placas vigentes:** escritorio `tmp/movil-06/klein/nave13pila3_s22_00001_.png`; vertical
  `tmp/movil-06/klein/nave06pc3_s33.png`; sacristía vertical `tmp/movil-06/klein/sac06a45_s33.png`. La referencia de
  escritorio aprobada antes de la pila: `tmp/placa-13/capillas/placa.png` (r6).

Para ver: `python3 -m http.server 8806` desde `tmp/movil-06/web/` (móvil, DevTools 390×844) y `8813` desde
`tmp/placa-13/` (escritorio, tecla 8 = r7).

## Trampas de esta sesión que ahorran tiempo

- **Lienzo alto:** la maqueta vertical se rinde **sin** shift, `sensor_fit` vertical, `sensor_height` 54, 704×1920, y la
  placa se recorta en sus 2/3 de abajo. Snippet en cualquier bloque de la sesión: `cam.data.shift_y=0;
  cam.data.sensor_fit='VERTICAL'; cam.data.sensor_height=54`, luego restaurar `AUTO` y −0.25.
- **Después de `render()` por pases**, restaurar `hide_render`, `film_transparent`, `color_mode`, `view_transform` y
  `material_override`, o el siguiente render sale negro.
- **ComfyUI cachea `LoadImage` por nombre:** cada intento con un nombre nuevo (`…pila3`, `V=e`).
- **`preset_edit_ref`** (en `E:\ComfyUI\workflows`) = `preset_edit` con el nodo 92 (2 imágenes) activo: slots `92.text`,
  `92.noise_seed`, `92/111.megapixels`, `92/85.megapixels`, `122.filename_prefix`; `76.image` = maqueta, `121.image` =
  referencia. La referencia **también arrastra la composición**: siempre superponer la maqueta al 50 % para comprobarlo.
- **`velas.py`**: la copia de `tmp/movil-06/viva/` trae `max(1, …)`; aun así, revisa que el pico de cada caja quede lejos
  del borde (si no, la caja está corrida).
- La GPU es una sola (12 GB): no rindas EEVEE en Blender mientras corre H3.

## Sin commit

`blender/transicion.py`, `docs/blender-notas.md`, el ticket 06 y este handoff, más
`ProyectoInvestigación/research/escenas-ia-transiciones-2026-10-04.md`. `CLAUDE.md` también aparece modificado, pero no
es de esta sesión: es del usuario y no va en estos commits. El usuario commitea cuando lo pide (un cambio por commit).

## Skills sugeridas

- `blender` (proyecto) + leer `docs/blender-notas.md` antes de tocar `blender/`.
- `frameref` si hace falta referencia de cómo se ve una señora con rebozo rezando o un fan en una iglesia de noche.
- `director` para decidir pose y peso visual de las figuras dentro del encuadre.
- mpaf `matt-wayfinder` para cerrar el ticket 06 en el mapa.

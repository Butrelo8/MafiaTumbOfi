# Santuario — micrófono colgado en la nave (sujeto al centro para el bokeh)

> Diseño aprobado por el usuario el 2026-10-10, con las correcciones de Fable incluidas. Rama `dev`. Extiende el
> ticket 14 v5 (placa real + foco de lente T2.8, `.wayfinder/santuario/tickets/14-look-de-cine.md`) y el método de
> placa fija + capas del ticket 13. No reabre ninguno de los dos.

## Problema

El foco de lente de v5 se lee, pero no tiene protagonista: enfoca la guitarra en la orilla derecha y el bokeh queda
de fondo. El usuario quiere un sujeto al centro del cuadro para que la profundidad de campo cuente más.

## Decisiones cerradas

| Decisión | Motivo |
|---|---|
| **Micrófono tipo Shure 55** ("Elvis"), el del hero (`public/video/hero.mp4`, ~2.6 s) | El usuario lo eligió sobre un SM58 de bola (el que Chalino usó en Culiacán en 1992, visto en el VHS; marca sin confirmar) |
| **Colgado de la bóveda por su cable**, no en pie | Referencia del usuario: lámpara colgante de micrófono (Etsy). Hace de lámpara del Santísimo: reliquia de la voz. Sin base ni cable en el piso que choquen con bancas, sub o rayo de luna |
| **Oro viejo, deslustrado** | Oro es el color de la paleta (monograma, CTA); oro rosa brillante compite con el dorado de los CTA |
| **Brasa tenue dentro**, a nivel de veladora | La luz de la lámpara del Santísimo; nunca más brillante que los instrumentos |
| **Una rosa roja oscura en el capuchón, sostenida por un moño de listón negro** atado al cable | Fable: a la altura de la cruz peleaba con el neón rojo. El moño lo pidió el usuario al elegir la semilla 1 (2026-10-10): "como si la sostuviera" |
| **Quieto**, sin vaivén | Los loops son de cámara quieta (ticket 13); un vaivén pediría H3 propio |
| **A 1.8 m de la lente**, a la altura de la boca (1.62 m) | El usuario lo eligió entre 1.3 / 1.8 / 2.4 m (`tmp/micro/dist_cmp.jpg`). "El micrófono del cantante ausente, no una lámpara" (Fable) |
| **Foco en el micrófono** | El usuario eligió "micro nítido, a media nave": el retablo, la cruz y las veladoras se vuelven bokeh grande; los instrumentos quedan apenas suaves |
| **Posición propia por formato** | Medido: un solo punto no sirve. Donde funciona en escritorio cae en el borde izquierdo de la vertical (u ≈ 0.08, fuera del recorte del teléfono); un punto común cae dentro del bloque sub/bocina. Escritorio y vertical son renders separados que nunca se ven juntos |
| **Pegar y refinar** sobre la placa aprobada, no regenerarla | Fuera de la máscara del sujeto la placa queda idéntica: zonas a mano, llamas H3 y humo H3 (~18 min) no se rehacen |

## 1. El sujeto

- Rejilla de Shure 55 colgada **hacia abajo**, cable negro que **sale del capuchón superior** (como la lámpara de la
  referencia) y sube recto hasta la bóveda (z 15 m; medido con rayo: libre en los dos puntos). En cuadro sólo se ve
  ~1 m de cable que se pierde en el negro de la bóveda; no cruza la cruz de neón.
- La cámara está a la altura de la rejilla: ve el capuchón y las costillas laterales, no la cara. **Nada de rejilla
  de frente** ni inclinada hacia la lente (un micrófono colgado no puede).
- Brasa: Klein la pinta fija en la placa, "luz cálida tenue que se escapa por las costillas laterales y deja una mancha
  cálida en el escalón de abajo" (este prompt es lo que evita que dibuje la rejilla de frente). En post sólo se modula
  su brillo (paso 4).
- Rosa: roja oscura (más oscura que el vidrio de las veladoras), en el capuchón, con un solo filo de luz,
  sostenida por un moño de listón negro satinado atado al cable, con dos colas.
- Escala: la rejilla del bloqueo mide 13 cm de alto × 8 de ancho × 6 de fondo (un 55 real es más chico, ~7.5 cm de
  ancho). Se acepta, igual en los dos formatos: el micro es el sujeto y a escala real saldría ~78 px de alto a 1920 y
  ~40 px a 704.

## 2. Posición

| Formato | Cámara | Micro (mundo) | En cuadro (u, v desde arriba) |
|---|---|---|---|
| Escritorio | `cam` (0, 2, 1.6), 35 mm | (~0.14, 3.8, 1.62) | u ≈ 0.575, v ≈ 0.48 |
| Vertical | `cam_movil` (0.8, 2, 1.6), 28 mm, shift_y −0.25 | (0.609, 3.8, 1.62) | u 0.35, v 0.24 |

- Escritorio: u 0.575 y no 0.55 (Fable): a 0.55 tocaba el halo de la cruz y el borde del panel de texto abierto
  (columna izquierda ~50 %, ticket 03). Micro, guitarra y bajo quedan en 0.58 / 0.68 / 0.85. La x exacta se vuelve
  a medir con `world_to_camera_view` al implementar.
- Vertical: mitad de arriba (ticket 03), dentro del recorte 19.5:9 (u 0.08–0.92), sobre el retablo, sin tapar la
  guitarra (u 0.43, v 0.39).

## 3. Producción

Escritorio primero; luego la vertical con la misma secuencia.

1. **Maqueta.** `micro()` en `blender/transicion.py`, del estilo de `capillas()`. Posiciones en constantes: `MICRO`
   (escritorio) y `MOVIL["micro"]` (vertical); `build(movil)` pone la que toca. Comprobación BVH en espacio de mundo
   (`docs/blender-notas.md`) y rayo del capuchón a la bóveda.
2. **Render gris iluminado + alfa.** Render de la maqueta con la luz que de verdad llega al micro (veladoras cálidas
   desde abajo; comprobar en Blender si el rayo de luna alcanza los 1.8 m: probablemente no) y un pase de alfa del
   sujeto (micro + cable + rosa). Interior oscuro: en el render gris no hay brasa (la pinta Klein, paso 3).
3. **Pegar y refinar.** El gris iluminado se pega sobre la placa aprobada con el alfa; Klein (`preset_edit`, 4 MP,
   nombre de imagen nuevo por variante) lo convierte en un micrófono real de oro viejo colgado de su cable con la rosa
   en el capuchón. 3 semillas → stills → el usuario elige **antes** de seguir. El resultado de Klein se compone de
   vuelta sobre la placa aprobada **sólo dentro de la máscara del sujeto dilatada y suavizada**: fuera queda idéntica
   por construcción y no hace falta el flujo de `alinear_flujo.py`.
   **Deriva dentro de la máscara:** Klein movió objetos 25–47 px en la vertical aun con "no cambies nada". Por cada
   semilla se mide el corrimiento del micro entre lo pegado y lo que dibujó Klein (flujo DIS sobre la zona de la
   máscara, como `registro.py`); sólo vale una semilla con ≤ 3 px, si no, la siguiente. La **máscara de producción del
   sujeto** (composición, `FOCO_MASK`, recorte de polvo y humo) se saca del micro que dibujó Klein en la semilla
   elegida, no del alfa de Blender, que sólo sirve para pegar.
4. **Capas vivas.**
   - Brasa: el brillo que pintó Klein se modula en post dentro de la máscara (multiplicar, como el parpadeo de las
     velas en `velas.py`); no se suma una segunda luz. La medida de luma (brasa y brillos de la rejilla ≤ guitarra) se
     hace sobre la salida de Klein, en el pico del parpadeo.
   - Polvo de luna (`polvo.py`) y humo H3: la máscara del sujeto va encima como recorte, así pasan por detrás.
   - DLSS NR de la placa nueva: lo corre el usuario (el modo auto bloquea los binarios; se le da el `! cmd.exe /c …`).
5. **Cadena v5.** `placa_real.py` (placa real cerca, tono de la placa NR) + MoGe nuevo + `dof.py`:
   - `FOCO_MASK` = la máscara del sujeto (dilatada ~4 px, suavizada): MoGe pierde un cable de 6 px y probablemente
     pega la cabeza al retablo.
   - **Arreglo previo en `dof.py`:** hoy toma la profundidad de foco (`df`) del MoGe crudo en (foco_x, foco_y) *antes*
     de aplicar `FOCO_MASK` (línea 22, máscara en 26–28). Si MoGe pone el micro a la profundidad del retablo, nada queda
     "detrás del foco" y el efecto desaparece. Comprobar que la disparidad del micro es mayor que la de la bocina, o
     pasar `df` explícito.
   - Foco: escritorio (0.575, 0.48), vertical (0.35, 0.24).
   - Desenfoque: escritorio 12–13 px a 1920 (35 mm T2.8 enfocando a 1.8 m; guitarra ~4–5 px, bajo ~3.5 px). Vertical:
     probar primero ~10 px reales (argumento ≈ 27) antes de ~13 px (≈ 36); 13 px es igualar a escritorio en pantalla,
     no física de lente. Still al 100 % (trastes de la guitarra) para el usuario antes de renderizar los loops.
   - `halacion.sh` al final.

## Criterios de aceptación

- El micro se lee como un Shure 55 de oro viejo colgado de su cable, con la rosa, nítido al 100 %; el retablo, la cruz
  y las veladoras detrás son bokeh.
- Brasa y brillos de la rejilla ≤ luma de la guitarra (medido).
- Escritorio: nada del sujeto en la columna izquierda del 50 %. Vertical: sujeto en la mitad de arriba y dentro del
  recorte 19.5:9.
- Fuera de la máscara del sujeto, la placa es idéntica a la aprobada; el micro de Klein está a ≤ 3 px de lo pegado.
- Humo y polvo pasan por detrás del micro.
- Costura del loop y peso no peores que v5 (r7_v5 287 KB, nave_v5 197 KB; costura medida igual que en `NOTAS.md`).

## Fuera de alcance

- **Transiciones.** Pero hay una condición dura: el loop de la nave gana un micro que las transiciones de entrada y
  salida no tienen; saltaría en el corte. Las transiciones vecinas de la nave se rehacen con `micro()` **antes de
  cualquier deploy**: el loop no se publica solo. Van con el pendiente v5 de transiciones (profundidad por cuadro).
- Vaivén del micro, otros espacios, el merge a `main` y el deploy.

## Material

- Bloqueo en la escena de Blender abierta (empties `micro` y `micro_movil`, cámara `cam_movil`); no está en
  `transicion.py` todavía. Renders: `tmp/micro/` (`final_*.png`, `dist_cmp.jpg`).
- Revisión de Fable y sus imágenes: `tmp/micro/fable/`.

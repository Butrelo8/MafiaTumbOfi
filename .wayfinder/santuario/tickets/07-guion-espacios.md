# 07 — Guion de camarín, cripta y atrio
Type: grilling · Status: closed · Blocks: 10 · Blocked by: 02, 03 · Assignee: —

## Question
Con la skill `director`: por espacio restante, qué muestra, su reliquia, su luz y su referencia
(`frameref`), y su transición (qué oclusor; dónde va el único "atravesar un umbral" y el "empujar hacia un
retrato que se abre"). Incluye decidir el atrio (¿la calle con la troca?) y cómo entran los retratos de
El grupo.

## Answer
Decidido por el usuario el 2026-10-13, en una pasada sobre los tableros de `tmp/07/tablero/` (detalle de cada opción
en la propuesta de abajo):

| Espacio | Elegido | Reliquia | Luz | Referencias |
|---|---|---|---|---|
| Camarín (El grupo, E) | **B · El vestidor**: ropero abierto con la ropa de escenario colgada como ornamentos, texana, espejo grande de marco dorado, tocador con tres veladoras | La guitarra de Diego recargada en el tocador | Dos arbotantes de 2200 K y las veladoras | `silence 007`, `jessejames 015` |
| Cripta (Contratación, D) | **B · La línea directa**: altar de piedra bajo la bóveda de tezontle | Teléfono de disco de oro (excepción aceptada: no es un instrumento) | Un haz frío de luna por la reja de la clave, con polvo; dos veladoras | `silence 002`, `jessejames 008` |
| Atrio (Cierre, D esquina) | **C · La fachada desde la calle**, con la troca: sí | La troca: **pickup negra estilo Lobo**, doble cabina, cromo, calaveras verticales rojas, sin emblemas | Luz cálida del portal abierto, sodio, calaveras, neblina | `sicario 034`, `sicario 015` |

- **Transiciones, plan 1.** Sacristía → camarín: empujar hacia el cuadro que cuelga sobre el tocadiscos en s11, que se
  abre como puerta (vuelta: se cierra). Camarín → cripta: oclusor con la puerta del ropero y bajar la escalera.
  Cripta → atrio: el único umbral, subir y salir por el portal a la neblina, el mismo portal que el atrio ve desde la
  calle. Ninguna toca placas de la nave ni de la sacristía.
- **Retratos de El grupo:** HTML en el hueco de E, uno a la vez; la escena del vestidor no cambia por integrante.
- **La troca la eligió Claude a pedido del usuario** ("que se vea más real, saca alguna que se vea con la estética"):
  tres variantes sobre una maqueta con proporciones de pickup real (`blockout.py › troca2`, 5.9 × 2.0 × 2.0 m,
  estacionada junto a la banqueta, vista de tres cuartos por detrás), `tmp/07/tablero/tablero_troca.jpg`. La negra
  porque mantiene el negro sobre negro, el cromo toma el oro del sodio y las calaveras son el rojo de la paleta; la
  blanca es lo más claro del cuadro y le quita el ojo al portal; la gris estilo Raptor repite la firma de calaveras de
  Ford y se lee fría. Placa elegida: `tmp/07/tablero/atrio_C2_lobo_elegida.png` (semilla 22).
- **Para la producción** (cuando el espacio entre a la cola): las previas son de una semilla y sirven de dirección,
  no de placa. Corregir el muro verde menta del vestidor a cal/almagre en el prompt; modelar la guitarra y el
  teléfono en Blender con su silueta real (lección del 12); la troca con un asset o la maqueta `troca2` mejorada,
  nunca la caja del primer tablero. Prompts: `prompts/07-guion-espacios/`.
- **Placas de escritorio (E3, 2026-10-13).** Tres semillas por espacio desde las maquetas de producción de
  `blender/espacios07.py` (`tmp/07/tablero/tablero_e3.jpg`, el hueco medido en luma media): el usuario eligió
  **cripta s22** (hueco 10.5, el haz cae entero sobre el teléfono), **atrio s22** (esquina 22.5, la más oscura) y
  **vestidor s11** (hueco 42.5), éste con una corrección: la guitarra recargada en el tocador queda en una postura
  imposible. Con la misma semilla se probaron cinco soportes en la maqueta: atril de piso y gancho en el muro
  (descartados: el gancho quedó sobre el clavijero y la guitarra parecía recargada) y luego silla, dentro del ropero y
  estuche abierto (`tmp/07/tablero/tablero_guitarra2.jpg`). **El usuario eligió la silla**: una silla de madera junto
  al tocador, el cuerpo en el asiento de tule y el cuello en el respaldo, a la luz de las velas. Placa:
  `tmp/07/e3/out/e3_vestidor_silla_s11_00001_.png`; prompt `prompts/07-guion-espacios/e3_vestidor_silla.txt`. El muro
  blanco del vestidor todavía aclara el hueco (luma media 47): lo baja la placa real (Klein 4 MP + tono NR).
- **Verticales (E4), primer intento rechazado por el usuario (2026-10-13 05:20):** "pixeleado donde Klein rellenó",
  la cripta "se ve horrible", el teléfono no se lee, la guitarra se ve rota; el atrio, el menos malo. Causa, medida en
  `tmp/07/e4/lado_*.jpg` y `detalle_*.jpg`: **la cámara vertical de `espacios07.py` (28 mm, más atrás, shift −0.25) es
  demasiado abierta**: todo sale a ~40–50 % del tamaño de escritorio (el teléfono en ~25 px) y el 53–56 % del cuadro cae
  fuera de lo que vio la placa de escritorio, así que lo inventa Klein. Además, Klein con una sola imagen vertical
  **reencuadra** (base y pase: bajó el contenido 150–300 px y lo escaló): la correlación de fase de `pegar_huecos.py`
  no lo alinea (respuesta 0.05); `tmp/07/e4/pegar_alineado.py` (SIFT + RANSAC, semejanza) sí. Las placas de escritorio
  sí coinciden con su maqueta (superpuestas al 50 %). Siguiente: cámara vertical medida, con lente más larga desde la
  posición de escritorio, el sujeto arriba y entero dentro del cuadro de escritorio (prueba gris → gris de
  `reproyectar.py`, que imprime `fuera del cuadro`), un tablero de 2–3 encuadres para que el usuario elija; la banda de
  abajo (el hueco vertical, que el escritorio nunca vio) como extensión oscura y no con Klein; si pide contenido real,
  el método de dos imágenes del 17 (maqueta + placa aprobada como referencia, `prompts/17-transiciones-micro-v5/sac17.txt`).
- **Verticales (E4) re-encuadradas, elegidas por el usuario (2026-10-13 05:45).** La cámara vertical ahora comparte
  posición y rotación con la de escritorio y sólo cambia lente y shift, así que la vertical es un **recorte exacto** de
  la placa aprobada (afín, sin Klein) más una banda abajo que la placa no vio. Nueve candidatos medidos (48–63 mm;
  `tmp/07/e4/encuadre/medidas.txt`: gris → gris dif. 0.8–2.5, ningún hueco fuera de la banda salvo los bordes de la
  prueba de profundidad en la reja del atrio) y tableros `tmp/07/tablero/e4_encuadre_*.jpg`. Elegidos: **vestidor
  amplio 48 mm** (el único con el sujeto entero: espejo, arbotantes, tocador y guitarra en la silla; ×1.04, banda 24 %),
  **cripta cerrado 63 mm** (sin banda, nada inventado; teléfono ×1.36; el frente oscuro del altar es la zona de la UI,
  luma 7) y **atrio amplio 48 mm** (portal con reja y las calaveras rojas de la troca; ×1.04, banda 24 %). Valores en
  `CAMARAS[...]["movil"]` de `blender/espacios07.py`. La banda es extensión oscura (media de las últimas filas que cae a
  negro, con el grano medido): `tmp/07/e4/encuadre/verticales.py` → `tmp/07/e4/v2/out/vertical_*.png` (720×1280), pares
  al mismo alto en `tmp/07/tablero/e4_vertical_*.jpg`. Con la placa de producción (Klein 4 MP) la escala ×1.36 de la
  cripta deja de ser ampliación.
- **El atrio elegido todavía no deja limpia la esquina** (`tmp/07/tablero/atrio_C2_lobo_hueco.jpg`: luma media 24 en
  el hueco contra 46 en el cuadro): el poste, el muro que alumbra el sodio y el canto izquierdo del portal caen dentro.
  En la placa de producción el poste se mueve a la derecha del portal o el muro bajo la lámpara cae a negro, para que
  el monograma y las redes queden sobre oscuro. Klein además dibujó un emblema en el costado de la troca: se quita.

## Propuesta (2026-10-13)
Vuelve en la versión 1 a pedido del usuario. Tres opciones por espacio, cada una con dos fotogramas de referencia,
su maqueta gris (Blender workbench, `tmp/07/blockout.py`) y una previa de Klein de **una sola semilla** (s22,
orientativa: sirve para elegir dirección, no es placa). El hueco del ticket 03 va marcado en rojo sobre cada maqueta y
cada previa. Tableros: `tmp/07/tablero/tablero_{camarin,cripta,atrio,transiciones}.jpg`; prompts en `tmp/07/prompts/`.

**Idea que manda.** Después de la sacristía el visitante entra más hondo y más abajo en el santuario (camarín, cripta)
y el único umbral es la salida a la noche de Xalapa: cuatro interiores cerrados y oscuros sostienen la afinidad y el
exterior con neblina es el contraste del final. El atrio mira hacia atrás, a la iglesia que se deja, y cierra el
círculo con la plaza del hero.

**Reglas que respetan todas las opciones.** Sujeto a la derecha o al centro y el hueco oscuro (03); la reliquia con su
silueta real desde Blender, nunca inventada por Klein (12); un loop por espacio con placa fija y sólo las zonas vivas
(13, 16); el retrato de cada integrante es HTML en el hueco de E, uno a la vez, y la escena no cambia por integrante.
El camarín no puede ser otro retablo de tres nichos: la nave ya lo tiene (`prompts/13-placa-y-capas/nave13c.txt`).

### Camarín (El grupo, layout E)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias: qué se iguala / qué cambia a propósito |
|---|---|---|---|---|
| A · Camarín octagonal dorado | El cuarto detrás del retablo donde se viste la imagen (modelo: Tepotzotlán); paneles tallados y dorados, columnas salomónicas, repisa corrida de veladoras, linternilla | La docerola de pie en la peana, vestida con un manto de terciopelo rojo bordado y un resplandor dorado | 1900 K de las veladoras subiendo por el oro; un hilo frío de la linternilla | `silence 039` (el oro sólo vive donde lo toca la vela) / arquitectura tallada en vez de tela; `jessejames 036` (la fila de luces chicas abajo) / sin figura |
| **B · El vestidor (recomendada)** | El vestidor de la imagen convertido en el de la banda: ropero abierto con la ropa de escenario colgada como ornamentos, texana en la repisa, espejo grande con marco dorado | La guitarra de Diego recargada en el tocador; tres veladoras; el espejo refleja el ropero | Dos arbotantes de 2200 K y las veladoras; el ropero cae a sombra | `silence 007` (un retrato flotando en negro) / es un espejo, y lo que se ve es la ropa de ellos; `jessejames 015` (una puerta que se abre a la luz) / la abre el espejo |
| C · Muro de exvotos | Pared cubierta de retablitos de lámina, milagros en listón rojo y fotos; tres marcos dorados mayores vacíos | Guitarra colgada con milagros atados al mástil; banco de veladoras | Vela rasante de 1900 K desde abajo | `silence 023` (relieve de metal en muro de cal, luz rasante) / cientos de piezas y vela en vez de día; `amoresperros 010` (interior mexicano con crucifijo y lámparas) / sin gente |

Por qué B: es el único que no vuelve a ser un interior de iglesia dorado (A repite el oro del retablo de la nave en otra
forma) y su función real, vestir la imagen, se vuelve la de la sección: la gente de la banda. El espejo es el retrato
que se abre. C es la imagen más mexicana, pero llena la pared de caras de desconocidos inventadas por la IA en la
sección de los integrantes reales y compite con el retrato HTML. Defectos de la semilla: B y C salen con muros verde
menta (el LOOK y el prompt los llevan a cal/almagre); A da guitarra de seis cuerdas, no docerola; C inventa caras.

### Cripta (Contratación, layout D con el CTA de WhatsApp siempre a la vista)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias |
|---|---|---|---|---|
| A · Estuche-relicario | Bóveda baja de tezontle y cantera con nichos de entierro; losa de piedra | Estuche negro abierto forrado de terciopelo rojo con una trompeta de oro (la trompeta sale en el hero); veladoras en el piso | Veladoras de piso, 1900 K desde abajo | `silence 015` (luz de vela baja, desde el piso) / sin gente; `sicario 029` (lámpara ámbar en bóveda de roca) / piedra labrada |
| **B · La línea directa (recomendada)** | La misma bóveda; un altar de piedra al centro-derecha | Teléfono de disco de oro con su cordón; dos veladoras | Un solo haz frío de luna por una reja de la clave, con polvo; el resto negro | `silence 002` (un haz de ventana en una nave abovedada) / cripta baja y reja; `jessejames 008` (contraluz en niebla) / sin figura |
| C · Bodega de gira | La bóveda como bodega: estuches de gira negros con cantos de aluminio | Un estuche abierto con la cadena de oro; foco desnudo al fondo | Foco de 2400 K y dos veladoras | `sicario 029` / igual; `sicario 015` (unidades repetidas bajo un techo bajo) / estuches en vez de trocas |

Por qué B: es la imagen más fuerte de las nueve y la más literal a la sección ("¿Tienes una fecha disponible?": el
teléfono es la línea; el CTA de WhatsApp es contestarlo), y ya deja la mitad izquierda negra que pide D abierto.
**Se aparta de la definición de reliquia** (`CONTEXT.md`: un instrumento): el teléfono no es un instrumento. A la
cumple (la trompeta, que necesita su asset de Blender: Klein la dibujó sin pistones) y C tampoco la cumple. El foco
de C cae dentro del hueco.

### Atrio (Cierre, layout D en la esquina)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias |
|---|---|---|---|---|
| A · La reja y la troca | Desde dentro del atrio, a través de la reja de hierro, la troca estacionada en la calle empedrada | La troca, oscura, con las calaveras rojas encendidas; fachadas de enfrente | Lámpara de sodio, calaveras rojas, ventanas cálidas, neblina | `nocountry 022` (reja en primer plano, luces de noche detrás) / reja colonial; `sicario 032` (calaveras rojas en el negro) / calle de Xalapa |
| B · Cruz atrial en la neblina | La cruz atrial de piedra (s. XVI) con veladoras y una rosa roja al pie, la fachada perdida en la niebla. **Sin troca** | La cruz; la rosa repite la del micro | Veladoras al pie, 1900 K; la niebla iluminada de lejos | `silence 019` (la niebla que se traga todo) / piedra en vez de figuras; `jessejames 008` (contraluz en niebla) |
| **C · La fachada desde la calle (recomendada)** | La retirada: desde la calle se ve la iglesia que se deja, con el portal abierto y la luz de las velas saliendo; la troca estacionada a la derecha | La troca vista de atrás, calaveras rojas; reja abierta; poste con lámpara de sodio | Luz cálida del portal, sodio, calaveras, neblina de Xalapa | `sicario 034` (pórtico cálido de noche enmarcado en negro) / fachada colonial y portal abierto; `sicario 015` (calaveras de una troca bajo luz cenital) |

Por qué C: es la retirada de la spec original contada en una imagen: el portal abierto es el lugar del que se sale, la
troca es la banda que se va, y el monograma M⚡T y las redes caben en la esquina libre. Repite la plaza del hero de noche
(fachada iluminada, Xalapa) y cierra el recorrido. **La troca sale en A y en C**: si se elige, falta saber cuál es
(modelo y color del videoclip); las maquetas usan una pickup genérica. La troca tampoco es un instrumento.

### Transiciones (las dos de la sacristía salen de lo que ya está en la placa s11; todas se leen de ida y de vuelta)
| Plan | Sacristía → camarín | Camarín → cripta | Cripta → atrio |
|---|---|---|---|
| **1 (recomendado)** | **Empujar hacia un retrato que se abre**: la cámara empuja hacia el cuadro que cuelga sobre el tocadiscos y el cuadro se abre como puerta (los camarines se alcanzan por una puerta detrás del altar); su revés oscuro tapa el cuadro y del negro sale el camarín. Vuelta: el cuadro se cierra | Oclusor: la puerta del ropero (B), una pilastra (A) o el muro oscuro (C) barre el cuadro y la cámara baja por la escalera | **El único umbral**: sube la escalera y sale por el portal a la neblina; en C es el mismo portal que se ve desde la calle. Vuelta: se entra de la noche a lo oscuro |
| 2 | Oclusor: el muro negro de la izquierda de s11 | Empujar hacia el espejo (B) o el marco central (C), que se abre a la escalera | Umbral, como en el 1 |
| 3 | Retrato que se abre, como en el 1 | Umbral de humo de copal bajo un arco al bajar a la cripta | Oclusor: la hoja del portal o la reja |

Por qué el 1: el cuadro ya está en la placa aprobada (se planta en el loop de la sacristía y paga en el gesto
siguiente), el umbral queda al final como contraste mayor, y nada obliga a tocar las placas de la nave ni de la
sacristía. Anotado sobre s11: `tmp/07/tablero/s11_salidas.jpg`.

### Qué se mueve en cada loop (placa fija, zonas vivas)
Camarín B: las llamas de los arbotantes y las veladoras, su reflejo en el espejo. Cripta B: el polvo dentro del haz
y las dos velas. Atrio C: la neblina que corre, la lámpara de sodio, las velas del portal. Ninguno pide cámara.

### Abierto
- Integrantes: `members.ts` tiene 3 (Héctor, Alexandro, Diego); la spec del 2026-09-17 hablaba de 5 y
  `public/members/` tiene también `dimora`. La escena de B no depende del número.

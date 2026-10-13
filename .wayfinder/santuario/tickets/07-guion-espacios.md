# 07 — Guion de camarín, cripta y atrio
Type: grilling · Status: open · Blocks: 10 · Blocked by: 02, 03 · Assignee: —

## Question
Con la skill `director`: por espacio restante, qué muestra, su reliquia, su luz y su referencia
(`frameref`), y su transición (qué oclusor; dónde va el único "atravesar un umbral" y el "empujar hacia un
retrato que se abre"). Incluye decidir el atrio (¿la calle con la troca?) y cómo entran los retratos de
El grupo.

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

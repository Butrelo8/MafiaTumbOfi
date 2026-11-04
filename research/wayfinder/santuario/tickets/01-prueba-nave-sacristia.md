# 01 — Prueba nave → sacristía
Type: prototype · Status: resolved · Blocks: 02, 03, 04 · Blocked by: — · Assignee: claude

## Question
¿Se sostiene una transición sin fundido (corte escondido tras un oclusor) entre dos espacios generados por
separado? ¿Qué ruta hace mejor el loop del espacio: DepthFlow (D) o MiniMax H3 + profundidad (M)?

## Answer
Resuelto el 2026-10-04 con el usuario ("quedó bien, mejor de lo esperado").

- **El corte escondido funciona.** Travelling lateral a la derecha, 35 mm a ambos lados del negro; el pilar
  y luego el jambaje tapan 5 cuadros de negro puro (forzado en el montaje). Cada mitad se genera aparte, la de
  la sacristía al revés, para que cada una arranque de su cuadro de estilo y acabe en negro.
- **MiniMax (M) sobre DepthFlow (D).** M sigue la cámara de Blender cuadro a cuadro y anima lo que vive en
  la escena (el vinilo gira). D no coincide con el encuadre de la transición (salto al cambiar de video) y no
  se mueve nada.
- **Look:** Klein lleva la maqueta gris a foto real; una segunda pasada de "relight" oscurece lo que sale de
  clave alta. El LOOK del hero sin retoques deja la luma media cerca del hero (37.8): nave 39, sacristía 30.
- **Pendiente que abre:** 864×480 se ve bajo de resolución (lo dijo el usuario) → ticket 04. La primera mitad
  del travelling se lee lenta porque todo lo cercano está lejos → un objeto en primer plano (ticket 02).
- Tiempos: Klein ~20 s por cuadro; H3 a 864×480, 20 pasos: ~3 min el loop de 124 cuadros, 1 min la mitad de
  la transición.

Assets (en `tmp/`, ignorado): `tmp/transicion-1/` — `web/index.html` (página de prueba con selector D/M),
`montar.sh`, `h3.sh`, `loop_df.py`. Escena: `blender/transicion.py`. Ficha de planos y referencias:
`E:\ComfyUI\storyboards\mto-santuario\shotspec.md`.

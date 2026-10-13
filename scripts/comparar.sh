#!/usr/bin/env bash
# Material de revisión visual con una sola orden, siempre con el mismo formato (reemplaza los hstack/vstack,
# hojas, extracciones de cuadro y medidas de costura escritos a mano en cada sesión, y tmp/hero/hoja.py).
#
#   comparar.sh lado <salida.mp4|.jpg> <a> <b> [c ...]   lado a lado con etiquetas (nombre de archivo). Alinea alturas
#        (ALTO, por omisión la menor) y renumera cada entrada a 24 fps (bases de tiempo distintas = cuadros repetidos).
#        Salida .jpg/.png = un solo cuadro (CUADRO, por omisión 0). FILAS=2 parte las entradas en dos filas.
#   comparar.sh hoja <prefijo> <carpeta|video> [N]         hoja de contacto 8×6 de 240×135, con etiqueta.
#        Carpeta de .jpg/.png: etiqueta = tiempo (t.txt de la carpeta, o el número del archivo / 24), como hoja.py.
#        Video: N cuadros repartidos (por omisión 48), etiqueta = índice de cuadro. Escribe <prefijo>-00.jpg, -01…
#   comparar.sh cuadro <carpeta> <video> <i> [j ...]       extrae los cuadros i, j… (índice desde 0) a <carpeta>/f_NNNN.png
#   comparar.sh costura <video> [...]                      costura del loop: diferencia media último→primero contra la
#        mediana y el máximo de los saltos entre cuadros (BGR 0–255, la medida de tmp/micro/NOTAS.md; GRIS=1 en luma).
#        Se compara entre versiones (r7_micro 0.48, nave_v5 0.56). SSIM no sirve aquí: la escena es casi toda negra.
set -euo pipefail
PY="uv run -q --with numpy --with opencv-python-headless --with pillow python -I"
FUENTE=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf
que=${1:?uso: comparar.sh lado|hoja|cuadro|costura ...}; shift

case $que in
lado)
  out=$1; shift; n=$#; [ "$n" -ge 2 ] || { echo "lado: hacen falta 2 entradas o más"; exit 1; }
  alto=${ALTO:-$(for f in "$@"; do ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f"; done | sort -n | head -1)}
  ins=(); g=""; i=0
  for f in "$@"; do
    case $f in *.png|*.jpg) ins+=(-loop 1 -framerate 24 -i "$f") ;; *) ins+=(-i "$f") ;; esac
    et=$(basename "${f%.*}" | sed "s/[':\\]/_/g")
    g+="[$i:v]fps=24,settb=1/24,setpts=N,scale=-2:$alto,format=yuv420p,drawtext=fontfile=$FUENTE:text='$et':x=8:y=8:fontsize=$((alto / 30 + 8)):fontcolor=yellow:box=1:boxcolor=black@0.6[v$i];"
    i=$((i + 1))
  done
  if [ "${FILAS:-1}" = 2 ] && [ "$n" -ge 4 ]; then
    a=$(( (n + 1) / 2 )); arr=""; abj=""
    for k in $(seq 0 $((a - 1))); do arr+="[v$k]"; done
    for k in $(seq $a $((n - 1))); do abj+="[v$k]"; done
    # una fila con menos entradas se rellena con negro para que las dos midan lo mismo
    [ $((n - a)) -lt "$a" ] && { g+="color=black:s=16x16:r=24,scale=-2:$alto[relleno];"; abj+="[relleno]"; }
    g+="${arr}hstack=$a[fa];${abj}hstack=$a[fb];[fa][fb]xstack=inputs=2:layout=0_0|0_h0:fill=black[o]"
  else
    for k in $(seq 0 $((n - 1))); do g+="[v$k]"; done; g+="hstack=$n[o]"
  fi
  case $out in
    *.jpg|*.png) ffmpeg -v error -y "${ins[@]}" -filter_complex "$g;[o]select=eq(n\,${CUADRO:-0})[s]" -map "[s]" -frames:v 1 "$out" ;;
    *) ffmpeg -v error -y "${ins[@]}" -filter_complex "$g" -map "[o]" -shortest -c:v libx264 -crf 16 -pix_fmt yuv420p -an "$out" ;;
  esac
  echo "$out" ;;
hoja)
  $PY - "$@" <<'EOF'
import sys, glob, os, cv2
from PIL import Image, ImageDraw
pref, ent = sys.argv[1], sys.argv[2]
W, H, C, R = 240, 135, 8, 6
if os.path.isdir(ent):
    fs = sorted(glob.glob(f"{ent}/*.jpg") + glob.glob(f"{ent}/*.png"))
    tt = f"{ent}/t.txt"
    ts = [float(x) for x in open(tt)] if os.path.exists(tt) else [int(os.path.basename(f)[:-4]) / 24 for f in fs]
    ims = [Image.open(f).convert("RGB") for f in fs]
    ets = [f"{int(t // 60):02d}:{t % 60:04.1f}" for t in ts]
else:
    cap = cv2.VideoCapture(ent); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = min(int(sys.argv[3]) if len(sys.argv) > 3 else 48, total)
    idx = sorted({round(i * (total - 1) / max(n - 1, 1)) for i in range(n)})
    ims, ets = [], []
    for i in idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read()
        if ok: ims.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))); ets.append(f"#{i}")
for p in range(0, len(ims), C * R):
    hoja = Image.new("RGB", (W * C, H * R))
    for i, (im, et) in enumerate(zip(ims[p:p + C * R], ets[p:p + C * R])):
        im = im.resize((W, H))
        ImageDraw.Draw(im).text((4, 4), et, fill="yellow")
        hoja.paste(im, ((i % C) * W, (i // C) * H))
    hoja.save(f"{pref}-{p // (C * R):02d}.jpg", quality=85)
    print(f"{pref}-{p // (C * R):02d}.jpg")
EOF
  ;;
cuadro)
  dir=$1 vid=$2; shift 2; mkdir -p "$dir"
  for i in "$@"; do
    ffmpeg -v error -y -i "$vid" -vf "select=eq(n\,$i)" -frames:v 1 -fps_mode passthrough "$dir/$(printf 'f_%04d' "$i").png"
    echo "$dir/$(printf 'f_%04d' "$i").png"
  done ;;
costura)
  GRIS=${GRIS:-} $PY - "$@" <<'EOF'
import sys, os, cv2, numpy as np
gris = bool(os.environ.get("GRIS"))
for v in sys.argv[1:]:
    c = cv2.VideoCapture(v); fs = []
    while True:
        ok, f = c.read()
        if not ok: break
        fs.append((cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if gris else f).astype(np.float32))
    d = [np.abs(fs[i + 1] - fs[i]).mean() for i in range(len(fs) - 1)]
    cost = float(np.abs(fs[-1] - fs[0]).mean())
    print(f"{v}: {len(fs)} cuadros  costura {cost:.2f}  mediana {np.median(d):.2f}  máx {max(d):.2f}")
EOF
  ;;
*) echo "no conozco '$que': lado|hoja|cuadro|costura"; exit 1 ;;
esac

# Profundidad de campo de lente real sobre la placa (o sobre cada cuadro del loop): círculo de confusión ∝ |d − d_foco|,
# con d = disparidad normalizada de MoGe (cerca = blanco). Desenfoque de disco en luz lineal, así las velas lejanas
# salen como bokeh redondo y brillante. Sólo el fondo se desenfoca por capas pesadas por "detrás del foco", para que
# lo enfocado (instrumentos) no se derrame como halo sobre lo desenfocado.
# Uso: python dof.py <entrada.png|mp4> <disparidad.png> <salida.png|mkv> <foco_x> <foco_y> <coc_lejos_px>
#   foco_x/y en fracción del cuadro (0–1); coc_lejos_px = diámetro del desenfoque en el fondo más lejano, a 1920 de ancho
#   (32 mm a T2 en Super 35 enfocando a ~2.5 m da ~10–13 px a 1920 en el infinito).
import sys, subprocess, numpy as np, cv2

src, dsp, out, fx, fy, coc_far = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])


def disco(r):
    k = np.zeros((2 * r + 1, 2 * r + 1), np.float32)
    cv2.circle(k, (r, r), r, 1.0, -1, cv2.LINE_AA)
    return k / k.sum()


def preparar(W, H):
    d = cv2.imread(dsp, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    d = cv2.resize(d, (W, H), interpolation=cv2.INTER_LINEAR)
    df = np.median(d[int(fy * H) - 4:int(fy * H) + 5, int(fx * W) - 4:int(fx * W) + 5])
    import os
    # FOCO_D: disparidad del plano de foco explícita. Un sujeto fino (micrófono colgado, 2026-10-10) MoGe lo pega al
    # retablo: el df muestreado en el foco sería el del fondo y nada quedaría detrás del foco (Fable).
    if os.environ.get("FOCO_D"):
        df = float(os.environ["FOCO_D"])
    # FOCO_MASK: zonas que van en el plano de foco aunque el mapa vea el fondo detrás (humo de copal sobre la bocina:
    # MoGe ve el muro a través del humo y lo desenfocaba).
    if os.environ.get("FOCO_MASK"):
        m = cv2.resize(cv2.imread(os.environ["FOCO_MASK"], cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255, (W, H))
        d = d * (1 - m) + np.maximum(d, df) * m
    lejos = np.percentile(d, 1)
    radio = np.clip((df - d) / max(df - lejos, 1e-3), 0, None) * coc_far / 2 * W / 1920  # sólo detrás del foco
    niveles = [0, 1, 2, 3, 4, 6, 8, 11, 15]
    niveles = [r for r in niveles if r <= max(1, radio.max()) + 1]
    peso_atras = cv2.GaussianBlur((d <= df + 0.02).astype(np.float32), (0, 0), 2)  # no mezclar lo enfocado en el fondo
    return radio, niveles, peso_atras, df


def aplicar(img, radio, niveles, peso):
    lin = (img.astype(np.float32) / 255) ** 2.2
    capas = []
    for r in niveles:
        if r == 0:
            capas.append(lin)
            continue
        k = disco(r)
        num = cv2.filter2D(lin * peso[..., None], -1, k)
        den = cv2.filter2D(peso, -1, k)[..., None]
        capas.append(np.where(den > 1e-3, num / np.maximum(den, 1e-3), lin))
    res = np.zeros_like(lin)
    rr = np.array(niveles, np.float32)
    idx = np.clip(np.searchsorted(rr, radio) , 1, len(rr) - 1)
    lo, hi = rr[idx - 1], rr[idx]
    t = np.clip((radio - lo) / np.maximum(hi - lo, 1e-3), 0, 1)
    for i in range(len(rr)):
        w = np.where(idx == i, t, 0) + np.where(idx - 1 == i, 1 - t, 0)
        res += capas[i] * w[..., None]
    return (np.clip(res, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)


if src.endswith(".png"):
    img = cv2.imread(src)
    H, W = img.shape[:2]
    radio, niveles, peso, df = preparar(W, H)
    cv2.imwrite(out, aplicar(img, radio, niveles, peso))
    print(out, W, H, "d_foco", round(float(df), 3), "radio max", round(float(radio.max()), 1))
else:
    cap = cv2.VideoCapture(src)
    W, H = int(cap.get(3)), int(cap.get(4))
    radio, niveles, peso, df = preparar(W, H)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24",
                           "-i", "-", "-c:v", "ffv1", out], stdin=subprocess.PIPE)
    n = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        ff.stdin.write(aplicar(f, radio, niveles, peso).tobytes())
        n += 1
    ff.stdin.close(); ff.wait()
    print(out, W, H, n, "cuadros", "d_foco", round(float(df), 3))

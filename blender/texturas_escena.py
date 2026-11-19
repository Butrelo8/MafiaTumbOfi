"""Scene textures from the asset audit (2026-11-18): CC0 scans re-coloured to a palette, 512 px, written to
blender/texturas/<group>/<name>_{color,rough,nor}.jpg. Cab interior (defects 1, 7, 9: escena.py's cabina()), the far hills (21) and
the guardrail (22). Cycles and the live GLB read the same files.

  uv run -q --with numpy --with pillow python -I blender/texturas_escena.py [<dir of the 1k scans>]

The scans come from visual-lab's fetch_texture.py (credits in texturas/<group>/SOURCES.txt). Colour: the scan's luminance stretched
to 0-1 and mapped onto a dark / mid / light palette (kiln-prop § Materials: never multiply a scan by a tint). The palette levels are
linear and taken from the reference (refs r01-r04, CEFIC's photos of the real 6x6): black nappa, carbon trim, brushed aluminium;
the headliner is the one change on purpose (charcoal, not the photo's light grey: escena.py CABINA_TECHO picks).
"""
import os, sys
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/cc-out/mto-asset-fixes/tex/1k")
DEST = os.path.join(AQUI, "texturas")
LADO = 512
# (group, name): (scan, palette dark/mid/light (linear RGB), roughness remap (lo, hi))
LAMINAS = {
    ("cabina", "piel"): ("Leather026", [(0.004, 0.004, 0.0045), (0.010, 0.0095, 0.0095), (0.024, 0.022, 0.021)], (0.38, 0.62)),
    ("cabina", "alcantara"): ("velour_velvet", [(0.010, 0.010, 0.011), (0.020, 0.020, 0.021), (0.036, 0.035, 0.036)], (0.82, 0.98)),
    ("cabina", "alcantara_clara"): ("velour_velvet", [(0.16, 0.155, 0.15), (0.26, 0.25, 0.24), (0.36, 0.35, 0.33)], (0.82, 0.98)),
    ("cabina", "carbono"): ("Fabric004", [(0.003, 0.003, 0.0035), (0.012, 0.012, 0.014), (0.045, 0.045, 0.05)], (0.30, 0.45)),
    ("cabina", "aluminio"): ("Metal009", [(0.40, 0.40, 0.41), (0.55, 0.55, 0.56), (0.68, 0.68, 0.69)], (0.22, 0.38)),
    # the far hills at night: a drone scan of rocky scrub, mottled near-black (the old flat cerro was 0.012, 0.011, 0.01)
    ("mundo", "cerro"): ("rocky_terrain_02", [(0.004, 0.0045, 0.0035), (0.011, 0.012, 0.009), (0.024, 0.025, 0.019)], (0.85, 1.0)),
    # galvanised W-beam: zinc spangle from a galvanised sheet scan (its corrugation stays out: escena.py uses no normal map for it)
    ("mundo", "galvanizado"): ("corrugated_iron_02", [(0.30, 0.31, 0.32), (0.46, 0.47, 0.48), (0.60, 0.61, 0.62)], (0.30, 0.55)),
}


def srgb(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def lum_lineal(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float64) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return a @ np.array([0.2126, 0.7152, 0.0722])


def color(scan, paleta):
    y = lum_lineal(scan)
    lo, hi = np.percentile(y, 2), np.percentile(y, 98)
    t = np.clip((y - lo) / max(hi - lo, 1e-6), 0, 1)[..., None]
    p = np.array(paleta)
    out = np.where(t < 0.5, p[0] + (p[1] - p[0]) * (t / 0.5), p[1] + (p[2] - p[1]) * ((t - 0.5) / 0.5))
    return Image.fromarray((srgb(out) * 255 + 0.5).astype(np.uint8))


def rugosidad(scan, lo, hi):
    y = np.asarray(scan.convert("L"), dtype=np.float64) / 255.0
    a, b = np.percentile(y, 2), np.percentile(y, 98)
    return Image.fromarray(((lo + (hi - lo) * np.clip((y - a) / max(b - a, 1e-6), 0, 1)) * 255 + 0.5).astype(np.uint8))


for (grupo, nombre), (scan, paleta, (r0, r1)) in LAMINAS.items():
    dest = os.path.join(DEST, grupo)
    os.makedirs(dest, exist_ok=True)
    abre = lambda m: Image.open(os.path.join(FUENTE, f"{scan}_{m}_1k.jpg")).resize((LADO, LADO), Image.LANCZOS)
    color(abre("diff"), paleta).save(os.path.join(dest, f"{nombre}_color.jpg"), quality=88)
    rugosidad(abre("rough"), r0, r1).save(os.path.join(dest, f"{nombre}_rough.jpg"), quality=88)
    abre("nor_gl").convert("RGB").save(os.path.join(dest, f"{nombre}_nor.jpg"), quality=92)
    print("TEXTURA", grupo, nombre, scan)
fuentes = open(os.path.join(FUENTE, "SOURCES.txt"), encoding="utf8").read().splitlines()
for grupo in {g for g, _ in LAMINAS}:
    scans = {s for (g, _), (s, *_r) in LAMINAS.items() if g == grupo}
    with open(os.path.join(DEST, grupo, "SOURCES.txt"), "w", encoding="utf8") as f:
        f.write("Scans re-coloured by blender/texturas_escena.py (512 px). Sources:\n"
                + "\n".join(l for l in fuentes if l.split(" ")[0] in scans) + "\n")

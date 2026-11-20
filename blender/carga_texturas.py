"""Roof load, step 0 (2026-11-20): the two bags' textures to web size, from the owner's downloads. Run with PIL and numpy:

  uv run -q --with pillow --with numpy python -I blender/carga_texturas.py <dir with the unzipped downloads> <out dir>

  bolsa   (Bag_FBX.zip, Substance TGAs 4096)             <- <in>/bag/Texture/T_Bag_*.tga
  mochila (the BackPack_Blend.blend mesh has no textures in its zip; the same backpack's maps ship in max_physical.zip)
                                                         <- <in>/max/textures/backpack_*.png

Each comes out at 1024 px: <pieza>_base.jpg, <pieza>_rm.jpg (glTF packing: G roughness, B metallic; R white, no AO) and <pieza>_n.png.
The page's optimizer (scripts/vivo-optimizar.mjs) takes them to 512 WebP. Nothing here is committed: the sources are third-party.
"""
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ENT, SAL = sys.argv[1], sys.argv[2]
N = 1024


def gris(p):
    im = Image.open(p)
    a = np.asarray(im.convert("L").resize((N, N), Image.LANCZOS))
    return a


def hacer(pieza, base, rough, metal, normal):
    Image.open(base).convert("RGB").resize((N, N), Image.LANCZOS).save(f"{SAL}/{pieza}_base.jpg", quality=90)
    r, m = gris(rough), gris(metal)
    rm = np.stack([np.full_like(r, 255), r, m], axis=-1)
    Image.fromarray(rm).save(f"{SAL}/{pieza}_rm.jpg", quality=92)
    Image.open(normal).convert("RGB").resize((N, N), Image.LANCZOS).save(f"{SAL}/{pieza}_n.png")
    print("TEXTURAS", pieza, "rough mean", r.mean().round(1), "metal mean", m.mean().round(1), flush=True)


hacer("bolsa", f"{ENT}/bag/Texture/T_Bag_BaseColor.tga", f"{ENT}/bag/Texture/T_Bag_Roughness.tga",
      f"{ENT}/bag/Texture/T_Bag_Metalic.tga", f"{ENT}/bag/Texture/T_Bag_Normal.tga")
hacer("mochila", f"{ENT}/max/textures/backpack_basecolor.png", f"{ENT}/max/textures/backpack_rough.png",
      f"{ENT}/max/textures/backpack_metal.png", f"{ENT}/max/textures/backpack_norm.png")

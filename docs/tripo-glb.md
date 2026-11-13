# Tripo GLBs: what comes out wrong and how it was fixed (2026-11-12)

The four figures (manager, Héctor, Diego, Alejandro) come from Tripo, the owner's account, with the inputs in
`comfy-out/para-subir/`. The originals stay in `C:\Users\black\Downloads`. The fixed copies are in
`blender/assets/reparto/{manager,hector,diego,alejandro}.glb` (git-ignored).

## What a Tripo export brings
- The files are structurally fine: one mesh (~364k tris), one material, 4096² base colour, rm and normal maps. The
  colour spaces are correct and no images are missing.
- **False metal.** The B channel (metallic) of `*_rm.jpg` is ≈1 on surfaces seen at a grazing angle (arm and shoe
  edges, cap brim) and on white areas (Alejandro's whole T-shirt). That makes them render dark and chrome-like.
- **Wet gloss.** The G channel (roughness) has a median of 0.15–0.31.
- **Paint smears from projection:** the navy smudge on the back of the manager's cap, a white wash around his eyes,
  grey fringes on hands and inner arms, a grey band under Héctor's and Diego's chins, skin strips at the back hems.

## What was applied (owner's choices)
- All four: roughness remapped so the median is 0.5 (finish "B, satin"; the owner chose it out of 0.5 and 0.7).
  Metal is zeroed, plus `metallicFactor: 0`.
- Héctor: metal is kept only on small pieces (glasses, chain, earrings, cap snap): components of B>0.6 with an area
  under 6000 px. That mask failed on Diego and Alejandro, so their chains are non-metal.
- Manager: the navy on the cap crown is repainted white and the eye wash is partly repainted to skin. The ghost arcs
  above the lids and a faint patch line on the crown remain.
- Pending: a manual texture-paint pass for the rest of the smears (owner's choice); a colour rule changed nothing.
- Héctor (2026-11-12, after the owner saw "artifacts on the hat" in the transition clip): the normal map has thin
  bake lines on the back of the head (a triangle on the turned-back brim, arcs on another island). They rendered as dark
  cracks; the colour texture is clean there. `normales.py` inpaints texels on the back of the head that differ from their
  15-px median by more than 0.12 (18k texels, 1.6 % of that zone). In the shot's frame 0 crop the dark-line pixels go
  699 → 154 (146 with the normal map off). Before: `blender/assets/reparto/hector-v1.glb`.

## Re-run on a new export
```bash
cd blender/tripo            # scripts use the cwd for glbio.py and pos_<name>.npy
uv run -q --with numpy --with opencv-python-headless --with pillow python -I patch.py in.glb out.glb 0.5 zero
uv run -q --with numpy --with opencv-python-headless --with pillow python -I patch.py in.glb out.glb 0.5 jewel 6000 0.6
uv run -q --with numpy --with opencv-python-headless python -I posmap.py in.glb pos_<name>.npy 2048   # repaint.py needs it
uv run -q --with numpy --with opencv-python-headless --with pillow python -I normales.py in.glb out.glb pos_<name>.npy  # bake lines, back of head
./batch.sh <prefix> lit|flat|metal|rough <px> file.glb ...     # 4 views in Blender (Cycles OptiX), r/<prefix><name>_<mode>_*.png
```
`patch.py` rewrites only the rm image and the bufferView offsets: the mesh bytes are untouched, with no round trip
through Blender's exporter. Numbers: `blender/render/reparto/tripo-fix/numeros.txt`; sheet: `antes-despues.png`.

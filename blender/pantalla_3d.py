"""Pantalla móvil 3D (oopdrone, 2026-11-15; docs/design/pantalla-3d.md): the screen truck as a found 3D model, in place of
utileria.py's box stand-in `pantalla_c`, wearing livery A (Renta), B (Gira) or C (Marquesina) from docs/design/pantalla-movil.md.

Runs inside montaje.py's namespace: its hook execs this file when MONTAJE_PANTALLA is set (pass it from WSL with WSLENV):
  MONTAJE_PANTALLA=b WSLENV=MONTAJE_PANTALLA /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 \
    --python "$(wslpath -w blender/montaje.py)" -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 16 \
    p3-a-led-esc3,p3-b-led-esc5,... 960x540 [wb]

What it changes: `pantalla_c` (utileria's namespace `_g` and this one) becomes `pantalla_3d` with MONTAJE_PANTALLA's livery and
MONTAJE_PANTALLA_LUZ's box light: same (x, y) signature and anchor (the box's back face at y - 3.42, centred on x), so the
montaje-esc* holds that call pantalla_c get the truck unchanged. It adds one option per livery x box light x view (the p3-* names
at the bottom), so one run renders any set of them.

The base mesh is blender/pantalla_3d_prep.py's output (the Fuso Canter by Raed Almaharmah, CC-BY-4.0, its box removed);
everything above its chassis floor is built here: the LED box, the screens and the livery.
"""
import math
import os

import bpy
from mathutils import Vector

P3_LIBREA = os.environ.get("MONTAJE_PANTALLA", "b").lower()[:1]
P3_LUZ = os.environ.get("MONTAJE_PANTALLA_LUZ", "led")  # led | tira | ancha (luz_caja)
P3_BASE = os.path.join(AQUI, "assets", "pantalla3d", "canter-base.blend")
if not os.path.exists(P3_BASE):  # untracked: other worktrees use the shared copy
    P3_BASE = r"\\wsl.localhost\Ubuntu\home\black\cc-out\mto-integracion\assets\pantalla3d\canter-base.blend"
P3_MINI = r"\\wsl.localhost\Ubuntu\home\black\cc-out\mto-pantalla\thumb-XxhXFo-hm-I.jpg"  # "EN VIVO PLAZA LERDO" (rizzdrone)
P3_FUENTE = os.path.join(REPO, "tmp", "fuentes", "saira-condensed-latin-800-normal.ttf")  # DESIGN.md display type
# box (m): the base's old box spanned y 0..5.26 behind the cab, 2.31 wide; its floor tops out at z 0.91. Top 3.40 as rizzdrone's
# blockout (LED boxes sit well above the cab). Side screen 3.6 x 2.025 (16:9, the videos' shape): 4.0 x 2.25 left no room for
# B's name over it and overfilled the scene 3 frame (544 px of 540, pantalla-movil.md). Rear screen 2.0 x 2.05: the top band
# carries B's name at 0.20 m cap (rizzdrone: 0.12 m is 10 px at scene 5, too small).
P3_L, P3_W, P3_Z0, P3_Z1 = 5.26, 2.31, 0.92, 3.40
P3_LADO = (3.6, 2.025, 2.06)  # w, h, centre z
P3_ATRAS = (2.0, 2.05, 2.0)
P3_CACHE = {}


def _p3_base():
    if "me" not in P3_CACHE:
        with bpy.data.libraries.load(P3_BASE, link=False) as (s, d):
            d.meshes = ["pantalla3d_base"]
        P3_CACHE["me"] = d.meshes[0]
    return P3_CACHE["me"]


def _p3_rotulo(s, cap, loc, rot, m, ancho_max=None):
    """Saira Condensed 800 lettering, cap height ~cap m, centred."""
    cu = bpy.data.curves.new("p3_txt", "FONT")
    cu.body = s
    cu.font = bpy.data.fonts.load(P3_FUENTE, check_existing=True)
    cu.size, cu.align_x, cu.align_y = cap / 0.70, "CENTER", "CENTER"
    o = bpy.data.objects.new("p3_txt", cu)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    o.data.materials.append(m)
    if ancho_max:
        bpy.context.view_layer.update()
        if o.dimensions.x > ancho_max:
            o.scale = (ancho_max / o.dimensions.x,) * 3
    GRUPO.append(o)
    return o


LADO_ROT = (math.pi / 2, 0, math.pi / 2)  # a plano facing +X (the right side, toward the band's lane)
ATRAS_ROT = (math.pi / 2, 0, 0)            # facing -Y (toward the band behind)


def pantalla_3d(x=PM_X, y=PM_Y, librea=None, luz_=None):
    lib, modo = librea or P3_LIBREA, luz_ or P3_LUZ
    yb = y - 3.42  # the box's back face, where pantalla_c had it
    o = bpy.data.objects.new("p3_camion", _p3_base())
    sc.collection.objects.link(o)
    o.location = (x, yb, 0)
    pintura = mat("p3_cab_blanca", (0.80, 0.81, 0.82), 0.35) if lib == "a" else mat("p3_cab_negra", (0.015, 0.015, 0.017), 0.3)
    for i, m in enumerate((pintura, NEGRO_MATE, mat("p3_chasis", (0.03, 0.03, 0.032), 0.6),
                           mat("p3_calavera", (0.6, 0.02, 0.01), 0.3, emit=8.0, ecolor=(1.0, 0.05, 0.02)),
                           mat("p3_faro", (1.0, 0.95, 0.85), 0.2, emit=12.0))):
        o.material_slots[i].link = "OBJECT"
        o.material_slots[i].material = m
    GRUPO.append(o)
    # the LED box: black (DESIGN.md --cap), on the chassis floor
    yc = yb + P3_L / 2
    # matte: at scene 5 the G63's headlights sit beside the lens, and a glossy black back face (CAP, rough 0.4) came out washed white
    caja((P3_W, P3_L, P3_Z1 - P3_Z0), (x, yc, (P3_Z0 + P3_Z1) / 2), mat("p3_caja", (0.0056, 0.0048, 0.0031), 0.9), bevel=0.02, parent=False)
    xs = x + P3_W / 2 + 0.006
    w, h, zc = P3_LADO
    panel_led(w, h, (xs, yc, zc), LADO_ROT, P3_MINI, 320)  # ~11 mm pitch (outdoor truck panels: P6-P10); 96 read as coarse dots
    wa, ha, za = P3_ATRAS
    ya = yb - 0.008
    # the empty state (plan §5, no invented dates), as utileria's pantalla_vacia but fitted to the screen's width: its h-scaled
    # lettering ran past a 2.0 m screen. Cap heights from pantalla-movil.md (0.20 m reads 16 px at scene 5)
    plano(wa, ha, (x, yb - 0.006, za), mat("p3_led_negro", (0.008, 0.008, 0.008), 0.9), rot=ATRAS_ROT, parent=False)
    _p3_rotulo("PRÓXIMAS FECHAS", 0.20, (x, ya - 0.002, za + 0.35), ATRAS_ROT, mat("u_led_oro", (1.0, 0.7, 0.25), emit=6), wa - 0.2)
    _p3_rotulo("MUY PRONTO", 0.14, (x, ya - 0.002, za - 0.05), ATRAS_ROT, mat("u_led_blanco", (1, 1, 1), emit=4), wa - 0.4)
    if lib == "a":  # Renta: the band only on the screens; amber beacon bar on the cab roof (tile 09)
        caja((1.2, 0.22, 0.10), (x, yb + 6.3, 2.42), AMBAR, parent=False)
    elif lib == "b":  # Gira: gold band framing each screen (tile 16), the name over the side screen and on the rear (tile 04)
        for dz in (-1, 1):
            plano(w + 0.2, 0.10, (xs + 0.002, yc, zc + dz * (h / 2 + 0.05)), ORO, rot=LADO_ROT, parent=False)
            plano(wa + 0.2, 0.10, (x, ya, za + dz * (ha / 2 + 0.05)), ORO, rot=ATRAS_ROT, parent=False)
        for dy in (-1, 1):
            plano(0.10, h + 0.3, (xs + 0.002, yc + dy * (w / 2 + 0.05), zc), ORO, rot=LADO_ROT, parent=False)
            plano(0.10, ha + 0.3, (x + dy * (wa / 2 + 0.05), ya, za), ORO, rot=ATRAS_ROT, parent=False)
        _p3_rotulo("MAFIA TUMBADA", 0.20, (xs + 0.004, yc, zc + h / 2 + 0.22), LADO_ROT, ORO, ancho_max=w)
        _p3_rotulo("MAFIA TUMBADA", 0.20, (x, ya - 0.002, za + ha / 2 + 0.22), ATRAS_ROT, ORO, ancho_max=P3_W - 0.2)
    elif lib == "c":  # Marquesina (the owner's round-2 pick): warm bulbs above and below the side screen, round the rear one
        foco = mat("p3_foco", (1.0, 0.75, 0.4), 0.3, emit=12)
        n = int((w + 0.2) / 0.2) + 1
        for i in range(n):
            for zz in (zc - h / 2 - 0.07, zc + h / 2 + 0.07):
                esfera(0.045, (xs + 0.03, yc - (n - 1) * 0.1 + i * 0.2, zz), foco, parent=False)
        n = int((wa + 0.2) / 0.2) + 1
        for i in range(n):
            for zz in (za - ha / 2 - 0.07, za + ha / 2 + 0.07):
                esfera(0.045, (x - (n - 1) * 0.1 + i * 0.2, ya - 0.03, zz), foco, parent=False)
        for dx in (-1, 1):
            for i in range(1, int(ha / 0.2) + 1):
                esfera(0.045, (x + dx * (wa / 2 + 0.07), ya - 0.03, za - ha / 2 - 0.07 + i * 0.2), foco, parent=False)
    luz_caja(x, yb, xs, modo)
    print(f"PANTALLA3D librea {lib} luz {modo} x {x:.2f} caja y {yb:.2f}..{yb + P3_L:.2f}", flush=True)


def luz_caja(x, yb, xs, modo):
    """The box's own light (owner 23:18, via the mothership): 'led' = the screens are the only light; 'tira' = one minimal cool-white
    strip outlining the whole box (top and bottom edges of the side and the rear); 'ancha' = a wide lamp bar along the top of the
    side and the rear, washing the box face and the road beside it."""
    if modo == "led":
        return
    yc, ya = yb + P3_L / 2, yb - 0.012
    if modo == "tira":
        m = mat("p3_tira", (0.9, 0.95, 1.0), 0.3, emit=10.0)
        for z in (P3_Z0 + 0.03, P3_Z1 - 0.03):
            caja((0.02, P3_L, 0.025), (xs + 0.008, yc, z), m, parent=False)
            caja((P3_W, 0.02, 0.025), (x, ya, z), m, parent=False)
        for yy in (yb + 0.03, yb + P3_L - 0.03):
            caja((0.02, 0.025, P3_Z1 - P3_Z0), (xs + 0.008, yy, (P3_Z0 + P3_Z1) / 2), m, parent=False)
        return
    m = mat("p3_lampara", (1.0, 0.88, 0.68), 0.3, emit=3.456)  # owner 2026-11-16: 'ancha' too bright, all three values x0.8 twice then x0.9 (6.0, 900 W, 400 W -> x0.576); colour warmed a little (tungsten-ish)
    caja((0.30, P3_L - 0.2, 0.12), (xs + 0.15, yc, P3_Z1 + 0.04), NEGRO, parent=False)  # the lamp housing over the side
    caja((0.22, P3_L - 0.3, 0.02), (xs + 0.15, yc, P3_Z1 - 0.025), m, parent=False)  # its face, looking down
    caja((P3_W - 0.2, 0.30, 0.12), (x, yb - 0.15, P3_Z1 + 0.04), NEGRO, parent=False)
    caja((P3_W - 0.3, 0.22, 0.02), (x, yb - 0.15, P3_Z1 - 0.025), m, parent=False)
    for pos, mira_, largo, w_ in (((xs + 0.25, yc, P3_Z1 - 0.05), (xs + 1.2, yc, 0.0), P3_L - 0.3, 518),
                                  ((x, yb - 0.25, P3_Z1 - 0.05), (x, yb - 1.2, 0.0), P3_W - 0.3, 230)):
        o = luz("AREA", pos, w_, (1.0, 0.86, 0.66), mira=mira_, parent=False)
        o.data.shape, o.data.size, o.data.size_y = "RECTANGLE", largo, 0.25  # aimed in a vertical plane: local X is horizontal


_g["pantalla_c"] = pantalla_3d
pantalla_c = pantalla_3d


# one option per livery x box light x view, "p3-<a|b|c>-<led|tira|ancha>-<esc3|esc3-adelante|esc5>"; esc3-adelante is scene 3's
# hold with the truck 3.5 m further ahead, rizzdrone's stand-in for the start of the 3→4 move
P3_VISTAS = {"esc3": (m_esc3, 0.0), "esc3-adelante": (m_esc3, 3.5), "esc5": (m_esc5, 0.0)}
for _lib in "abc":
    for _luz in ("led", "tira", "ancha"):
        for _vista, (_f, _dy) in P3_VISTAS.items():
            def _p3_op(f=_f, dy=_dy, lib=_lib, luz_=_luz):
                _g["pantalla_c"] = lambda x=PM_X, y=PM_Y: pantalla_3d(x, y + dy, lib, luz_)
                try:
                    r = f()
                finally:
                    _g["pantalla_c"] = pantalla_3d
                viejo_diego()
                if WB:
                    pase_wb()
                return r
            opcion(f"p3-{_lib}-{_luz}-{_vista}")(_p3_op)

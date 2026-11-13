"""Cab shot (frame 0 of the transicion move) as layered passes with alpha, for compositing in EffectCraft.

The scene code is not on this branch: it is the uncommitted work in the main checkout (/mnt/e/Cursor Projects/MTO,
blender/escena.py + transicion.py + src/lib/escena.json + blender/assets/reparto). This script loads it from there
without changing it (escena.py ends in an unconditional main(), so its source is exec'd without that last line).

Run (Blender on Windows, from WSL; effectcraft/render-capas.sh wraps this):
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w effectcraft/capas.py)" \
    -- <w> <h> <out_dir (Windows path)> <samples> <pass:first-last> [<pass:first-last> ...]
Frames go to <out_dir>/<pass>/f_####.png (RGBA). Passes:
  bg     everything but the band and the two front seat backs (opaque plate)
  fig    the band only, cut where a non-seat truck part (cushion, console, dash) is in front of them
  fg     the two front seat backs only, cut where a head is in front of a seat-back top
  beauty plain render, for the difference check
The split is a box around the front seat backs (ASIENTOS, world coords), applied on camera rays only (Light Path ›
Is Camera Ray), so shadows and bounce light are the same in every pass. A distance split (camera clipping) was tried
first: the roof and the door pillars cross any split distance, and on a 2.5D push the seam opened onto the sky.
The camera is frozen at the f0 pose of transicion.CAMINO; the move happens in EffectCraft.
60 frames loop: road tile 8 m, ground 4 m, tramo 48 m = 60 f at 0.8 m/f; nod/bob 20 f; steering sin(2pi f/120) is 0 at 0 and 60.
"""
import bpy, os, sys, time, hashlib, math

MTO = r"E:\Cursor Projects\MTO"
ESCENA = os.path.join(MTO, "blender", "escena.py")
# front seat backs (both seats, the console between them), world metres: truck centre x 1.72, seat-back front face
# y ~0.29, cushion z ~1.08 (docs/escena-transicion.md "Measured"); roof inside z 2.19 and doors stay out
ASIENTOS = ((0.97, 2.47), (-0.30, 0.40), (0.85, 2.10))

for f in (ESCENA, os.path.join(MTO, "blender", "transicion.py"), os.path.join(MTO, "src", "lib", "escena.json")):
    print("SHA256", hashlib.sha256(open(f, "rb").read()).hexdigest()[:16], f)

src = open(ESCENA, encoding="utf8").read().rstrip()
assert src.endswith("main()"), "escena.py no longer ends in main(); update capas.py"
E = {"__file__": ESCENA, "__name__": "escena"}
exec(compile(src[: -len("main()")], ESCENA, "exec"), E)
sys.path.insert(0, os.path.dirname(ESCENA))
import transicion as T

argv = sys.argv[sys.argv.index("--") + 1:]
w, h, out, samples = int(argv[0]), int(argv[1]), argv[2], int(argv[3])
pases = []
for p in argv[4:]:
    nombre, r = p.split(":")
    a, b = (r.split("-") + [r])[:2]
    pases.append((nombre, int(a), int(b)))

t0 = time.time()
s = E["build"]()
E["mundo_render"](s, "noche")
E["motor"](samples, "noche")
T.preparar(s, w, h, E["islas"])
sc = bpy.context.scene
co = sc.camera
for ob in (co, co.data):
    ob.animation_data_clear()
p, m, lens = T.muestra(0, 1), T.muestra(0, 2), T.muestra(0, 3)
co.location = p
co.rotation_euler = (m - p).to_track_quat("-Z", "Y").to_euler()
co.data.lens = 18 / math.tan(0.75 * math.atan(18 / lens)) if h > w else lens
print("CAMARA", tuple(round(x, 3) for x in p), "lens %.2f" % co.data.lens, "build %.1fs" % (time.time() - t0))


def es_figura(o):
    while o is not None:
        if o.type == "ARMATURE":
            return True
        o = o.parent
    return False


figs = [o for o in bpy.data.objects if es_figura(o)]
print("FIGURAS", sorted(o.name for o in figs if o.type == "MESH"))

# every non-figure material: camera rays see  orig | Transparent (inside the box, VIN=1) | Holdout (outside, VOUT=1)
VIN, VOUT = [], []


def mascaras():
    propios = {sl.material for o in figs for sl in o.material_slots if sl.material}
    n = 0
    for mt in bpy.data.materials:
        if mt in propios or not mt.node_tree:
            continue
        nt = mt.node_tree
        salida = next((x for x in nt.nodes if x.type == "OUTPUT_MATERIAL" and x.is_active_output), None)
        if salida is None or not salida.inputs["Surface"].links:
            continue
        orig = salida.inputs["Surface"].links[0].from_socket
        N = lambda t: nt.nodes.new(t)
        L = nt.links.new
        geo, sep, lp = N("ShaderNodeNewGeometry"), N("ShaderNodeSeparateXYZ"), N("ShaderNodeLightPath")
        L(geo.outputs["Position"], sep.inputs[0])
        dentro = None
        for eje, (lo, hi) in zip("XYZ", ASIENTOS):  # inside = product of (lo < v) (v < hi) on each axis
            for op, lim in (("GREATER_THAN", lo), ("LESS_THAN", hi)):
                c = N("ShaderNodeMath"); c.operation = op; c.inputs[1].default_value = lim
                L(sep.outputs[eje], c.inputs[0])
                if dentro is None:
                    dentro = c
                else:
                    mu = N("ShaderNodeMath"); mu.operation = "MULTIPLY"
                    L(dentro.outputs[0], mu.inputs[0]); L(c.outputs[0], mu.inputs[1])
                    dentro = mu
        vin, vout = N("ShaderNodeValue"), N("ShaderNodeValue")
        vin.outputs[0].default_value = vout.outputs[0].default_value = 0.0
        VIN.append(vin); VOUT.append(vout)
        tr, ho = N("ShaderNodeBsdfTransparent"), N("ShaderNodeHoldout")
        a_in, a_out, caja, cam = (N("ShaderNodeMixShader") for _ in range(4))
        L(vin.outputs[0], a_in.inputs[0]); L(orig, a_in.inputs[1]); L(tr.outputs[0], a_in.inputs[2])
        L(vout.outputs[0], a_out.inputs[0]); L(orig, a_out.inputs[1]); L(ho.outputs[0], a_out.inputs[2])
        L(dentro.outputs[0], caja.inputs[0]); L(a_out.outputs[0], caja.inputs[1]); L(a_in.outputs[0], caja.inputs[2])
        L(lp.outputs["Is Camera Ray"], cam.inputs[0]); L(orig, cam.inputs[1]); L(caja.outputs[0], cam.inputs[2])
        L(cam.outputs[0], salida.inputs["Surface"])
        n += 1
    print("MASCARAS", n)


mascaras()
sc.render.use_persistent_data = True  # keep the static BVH between frames
sc.render.image_settings.color_mode = "RGBA"
t_frame = []
bpy.app.handlers.render_pre.append(lambda *a: t_frame.append(time.time()))
bpy.app.handlers.render_post.append(lambda *a: print("FRAME %d %.1fs" % (sc.frame_current, time.time() - t_frame[-1])))

#          figures visible, figures holdout, VIN (seat backs transparent), VOUT (rest holdout), film transparent
MODO = {"bg": (False, False, 1, 0, False), "fig": (True, False, 1, 1, True),
        "fg": (True, True, 0, 1, True), "beauty": (True, False, 0, 0, False)}
for nombre, a, b in pases:
    vis, hold, vi, vo, transp = MODO[nombre]
    for o in figs:
        o.visible_camera, o.is_holdout = vis, hold
    for v in VIN:
        v.outputs[0].default_value = vi
    for v in VOUT:
        v.outputs[0].default_value = vo
    sc.render.film_transparent = transp
    sc.frame_start, sc.frame_end, sc.frame_step = a, b, 1
    sc.render.filepath = os.path.join(out, nombre, "f_####")
    t1 = time.time()
    bpy.ops.render.render(animation=True)
    print("PASE %s %d-%d %dx%d %.1fs" % (nombre, a, b, w, h, time.time() - t1))
print("TOTAL %.1fs" % (time.time() - t0))

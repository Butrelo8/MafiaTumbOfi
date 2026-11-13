"""Render variants of the transicion clip's render settings on a short stretch, to compare the trembling (2026-11-12).
Same scene, camera, light as `escena.py transicion`; only the render engine/denoiser/seed settings change.
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/temblor.py)" \
    -- <variant> <out_dir> <w> <h> <first> <last>
Variants: see VAR. `act` reproduces the v2 clips' settings. Frames go to <out_dir>/f_####.png; the log prints the effective
settings and the seconds per frame.
"""
import bpy, os, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(AQUI, "escena.py"), encoding="utf8").read()
assert src.rstrip().endswith("main()")
ns = {"__file__": os.path.join(AQUI, "escena.py"), "__name__": "escena"}
exec(compile(src.rstrip()[:-len("main()")], os.path.join(AQUI, "escena.py"), "exec"), ns)

# name: (cycles samples, denoiser, animated seed, extra)
VAR = {
    "act": dict(samples=24),                                              # the v2 clips
    "seed": dict(samples=24, animated_seed=True),                         # same, new noise pattern every frame
    "nodn24": dict(samples=24, denoise=False),                            # no denoiser: the raw noise
    "s128": dict(samples=128),                                            # default denoiser (OIDN)
    "s128o": dict(samples=128, denoiser="OPTIX"),
    "s128seed": dict(samples=128, animated_seed=True),
    "s256": dict(samples=256),
    "s256o": dict(samples=256, denoiser="OPTIX"),
    "s512o": dict(samples=512, denoiser="OPTIX"),
    "s512": dict(samples=512),
    "tex1k": dict(samples=24, tex=1024),                                  # diagnostic: every texture over 1024 px prefiltered to 1024
    "nomb": dict(samples=24, motion_blur=False),                          # diagnostic: no motion blur
    # reference: many samples, best denoise, only the figures crop (x560 y230 w260 h200 of 1280x720) so it stays cheap
    "ref": dict(samples=1024, adaptive=False, quality="HIGH", border=(560, 230, 260, 200)),
    "eevee": dict(engine="BLENDER_EEVEE", taa=64),
}


def aplicar(v):
    sc = bpy.context.scene
    c = sc.cycles
    if v.get("engine"):
        sc.render.engine = v["engine"]
        sc.eevee.taa_render_samples = v["taa"]
        return
    if v.get("tex"):
        hechas = []
        for im in bpy.data.images:
            if im.type != "IMAGE":
                continue
            im.pixels[0]  # an image of a .glb is not decoded until something reads it: size is 0x0 before
            if im.size[0] > v["tex"] and im.size[1] > v["tex"]:
                hechas.append((im.name, tuple(im.size)))
                im.scale(v["tex"], v["tex"])
                im.pack()  # without this Cycles keeps reading the packed 4096 original
        print("TEX_ESCALADAS", len(hechas), hechas[:6])
    if "motion_blur" in v:
        sc.render.use_motion_blur = v["motion_blur"]
    if v.get("border"):  # pixel box; the file keeps the full size (crop off), y counts from the bottom in Blender
        x, y, w, h = v["border"]
        W, H = sc.render.resolution_x, sc.render.resolution_y
        sc.render.use_border, sc.render.use_crop_to_border = True, False
        sc.render.border_min_x, sc.render.border_max_x = x / W, (x + w) / W
        sc.render.border_min_y, sc.render.border_max_y = (H - y - h) / H, (H - y) / H
    c.samples = v["samples"]
    c.use_denoising = v.get("denoise", True)
    if v.get("denoiser"):
        c.denoiser = v["denoiser"]
    c.use_animated_seed = v.get("animated_seed", False)
    if "adaptive" in v:
        c.use_adaptive_sampling = v["adaptive"]
    if v.get("quality"):
        c.denoising_quality = v["quality"]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    nombre, out, w, h, first, last = argv[0], argv[1], int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])
    s = ns["build"]()
    sys.path.insert(0, AQUI)
    import transicion
    ns["mundo_render"](s, "noche")
    ns["motor"](24, "noche")
    transicion.preparar(s, w, h, ns["islas"])
    sc = bpy.context.scene
    aplicar(VAR[nombre])
    c = sc.cycles
    print("AJUSTES", nombre, sc.render.engine, "samples", c.samples, "denoise", c.use_denoising, c.denoiser,
          getattr(c, "denoising_input_passes", None), getattr(c, "denoising_prefilter", None), getattr(c, "denoising_quality", None),
          "adaptive", c.use_adaptive_sampling, c.adaptive_threshold, c.adaptive_min_samples, "animated_seed", c.use_animated_seed,
          "seed", c.seed, "filter", c.filter_width, "motion_blur", sc.render.use_motion_blur, sc.render.motion_blur_shutter)
    sc.frame_start, sc.frame_end, sc.frame_step = first, last, 1
    sc.render.filepath = os.path.join(out, "f_####")
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    print("SEGUNDOS_POR_FRAME", nombre, round((time.time() - t0) / (last - first + 1), 1))


main()

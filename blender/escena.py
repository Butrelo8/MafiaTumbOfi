"""Truck on an endless highway: one scene for the live page (GLB export) and the Cycles loop.

Values (stops, presets, world sizes) come from src/lib/escena.json, shared with the page.
Run headless from WSL (Blender on Windows):
  /mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- glb
  ... -- still <preset> <stop> <w> <h> <out.png> [samples]
  ... -- loop  <preset> <stop> <w> <h> <out_dir> [samples] [first] [last]
The world moves -Y (Blender) by `recorrido_loop` metres per loop; everything periodic divides it, so frame N == frame 0.
"""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(REPO, "src", "lib", "escena.json"), encoding="utf8"))
ASSETS = os.path.join(REPO, "blender", "assets", "camion")
MUNDO = CFG["mundo"]
FPS, LOOP_S, RECORRIDO, TRAMO = MUNDO["loop_fps"], MUNDO["loop_s"], MUNDO["recorrido_loop"], MUNDO["tramo"]
NFR = FPS * LOOP_S
# Light power conversions from the preset's page units to Cycles watts (calibrated by measuring renders).
W_FARO, W_POSTE, W_CALAVERA = 40.0, 2200.0, 6.0


def b(v):  # three.js (Y up, -Z forward) -> Blender (Z up, +Y forward)
    return Vector((v[0], -v[2], v[1]))


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, color, rough, metal=0.0, coat=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    p = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
    if p is None:
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.04
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = estr
    return m


def caja(name, size, loc, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cil(name, r, h, loc, m, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    return o


def plano(name, w, l, y0, z, m, tile):
    """Plane x in [-w/2, w/2], y in [y0, y0 + l]; UV in metres / tile so textures repeat every `tile` m."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y0 + l / 2, z))
    o = bpy.context.object
    o.name = name
    o.scale = (w, l, 1)
    bpy.ops.object.transform_apply(scale=True)
    uv = o.data.uv_layers.active.data
    for loop in o.data.loops:
        co = o.data.vertices[loop.vertex_index].co
        uv[loop.index].uv = ((co.x + w / 2) / tile if tile != w else (co.x + w / 2) / w, (co.y + o.location.y) / tile)
    o.data.materials.append(m)
    return o


def tex_mat(name, stem, tile_dim=1.0, oscurecer=1.0, tinte=(1, 1, 1)):
    """Principled with ambientCG Color/Normal/Roughness images (exportable to glTF)."""
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    d = os.path.join(ASSETS, stem)
    def img(kind, non_color):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(os.path.join(d, f"{stem}_1K-JPG_{kind}.jpg"))
        if non_color:
            n.image.colorspace_settings.name = "Non-Color"
        return n
    c = img("Color", False)
    if oscurecer != 1.0 or tinte != (1, 1, 1):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(c.outputs["Color"], mix.inputs[6])
        mix.inputs[7].default_value = (tinte[0] * oscurecer, tinte[1] * oscurecer, tinte[2] * oscurecer, 1)
        nt.links.new(mix.outputs[2], p.inputs["Base Color"])
    else:
        nt.links.new(c.outputs["Color"], p.inputs["Base Color"])
    r = img("Roughness", True)
    nt.links.new(r.outputs["Color"], p.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    n = img("NormalGL", True)
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m


# ---------------------------------------------------------------- truck

# Atlas swatches of the Quaternius pickup (measured, see SWATCH print) -> our materials.
SWATCHES = [((0.31, 0.54, 0.67), "pintura"), ((1.0, 1.0, 1.0), "pintura"), ((0.68, 0.68, 0.68), "cromo"),
            ((0.48, 0.48, 0.48), "cromo"), ((0.35, 0.35, 0.35), "vidrio"), ((0.27, 0.27, 0.27), "goma"),
            ((0.16, 0.16, 0.16), "goma"), ((0.12, 0.12, 0.12), "goma"), ((0.35, 0.29, 0.24), "goma")]


def clasificar(rgb):
    return min(SWATCHES, key=lambda sw: sum((a - b_) ** 2 for a, b_ in zip(sw[0], rgb)))[1]


def camion():
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, "pickup-quaternius.glb"))
    imported = list(bpy.context.selected_objects)
    meshes = [o for o in imported if o.type == "MESH"]
    for o in meshes:  # bake the importer's hierarchy into the mesh data
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(mw)
        o.matrix_world = Matrix.Identity(4)
    for o in imported:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
    body = next(o for o in meshes if o.name.startswith("Pickup"))

    def centro_mat(nombre):
        idx = next(i for i, m in enumerate(body.data.materials) if m and m.name.startswith(nombre))
        ps = [p.center for p in body.data.polygons if p.material_index == idx]
        return sum(ps, Vector()) / len(ps)
    fwd = centro_mat("Headlights") - centro_mat("BrakeLight")
    ang = math.atan2(fwd.x, fwd.y)  # rotate so forward -> +Y
    R = Matrix.Rotation(ang, 4, "Z")
    pts = [R @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    f = MUNDO["largo_camion"] / (hi.y - lo.y)
    c = (lo + hi) / 2
    M = Matrix.Translation((MUNDO["carril_x"], 0, 0)) @ Matrix.Scale(0.82, 4, (1, 0, 0)) @ Matrix.Scale(f, 4) @ Matrix.Translation((-c.x, -c.y, -lo.z)) @ R
    for o in meshes:
        o.data.transform(M)

    # repaint: classify each atlas face by its swatch colour
    atlas_m = next(m for m in body.data.materials if m.name.startswith("Atlas"))
    tex = next(n for n in atlas_m.node_tree.nodes if n.type == "TEX_IMAGE").image
    W, H = tex.size
    px = list(tex.pixels)
    mats = {
        "pintura": mat("pintura", (0.012, 0.012, 0.014), 0.32, metal=0.2, coat=1.0),
        "cromo": mat("cromo", (0.92, 0.92, 0.93), 0.12, metal=1.0),
        "goma": mat("goma", (0.018, 0.018, 0.018), 0.85),
        "vidrio": mat("vidrio", (0.01, 0.012, 0.015), 0.03, coat=1.0),
        "ambar": mat("ambar", (0.9, 0.45, 0.05), 0.3, emit=(1.0, 0.45, 0.05), estr=1.5),
    }
    faros = mat("faros", (1, 0.95, 0.85), 0.2, emit=(1.0, 0.9, 0.72), estr=6.0)
    pre = CFG["presets"]["noche"]
    calav = mat("calaveras", (0.6, 0.02, 0.01), 0.3, emit=lin(pre["calaveras"]["color"]), estr=4.0)
    cuenta, hist = {}, {}
    for o in meshes:
        me = o.data
        old = list(me.materials)
        me.materials.clear()
        orden = list(mats.values()) + [faros, calav]
        for m in orden:
            me.materials.append(m)
        uv = me.uv_layers.active.data if me.uv_layers else None
        for p in me.polygons:
            om = old[p.material_index] if p.material_index < len(old) else None
            if om and om.name.startswith("Headlights"):
                p.material_index = orden.index(faros); continue
            if om and om.name.startswith("BrakeLight"):
                p.material_index = orden.index(calav); continue
            u = sum((uv[i].uv for i in p.loop_indices), Vector((0, 0))) / len(p.loop_indices)
            x = min(W - 1, max(0, int(u.x % 1 * W))); y = min(H - 1, max(0, int(u.y % 1 * H)))
            k = (y * W + x) * 4
            cls = clasificar(px[k:k + 3])
            cuenta[cls] = cuenta.get(cls, 0) + 1
            q = (o.name[:5], cls) + tuple(round(c, 2) for c in px[k:k + 3])
            hist[q] = hist.get(q, 0) + 1
            p.material_index = orden.index(mats[cls])
    print("CLASES", cuenta)
    for q, n in sorted(hist.items(), key=lambda kv: -kv[1])[:30]:
        print("SWATCH", q, n)
    camion_e = bpy.data.objects.new("camion", None)
    bpy.context.scene.collection.objects.link(camion_e)
    ruedas = []
    for o in meshes:
        if "Wheel" in o.name:
            bpy.ops.object.select_all(action="DESELECT")
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
            ruedas.append(o)
        o.parent = camion_e
    radio = max(o.dimensions.z for o in ruedas) / 2
    print("RADIO", radio, "DIM", body.dimensions[:])
    return camion_e, body, ruedas, radio


# ---------------------------------------------------------------- road, props, hills

def tramo_props():
    """One `tramo` of roadside props at y in [0, TRAMO). Exported once, recycled on the page."""
    col = bpy.data.collections.new("tramo")
    bpy.context.scene.collection.children.link(col)
    galv = mat("galvanizado", (0.55, 0.56, 0.58), 0.38, metal=1.0)
    blanco = mat("poste_blanco", (0.7, 0.7, 0.68), 0.6)
    lampara = mat("lampara", (1, 0.8, 0.5), 0.3, emit=lin(CFG["presets"]["noche"]["postes"]["color"]), estr=6.0)
    refl = mat("reflejante", (0.5, 0.03, 0.02), 0.3, emit=lin(CFG["presets"]["noche"]["fantasmas"]["color"]), estr=0.8)
    objs = []
    # light pole, right shoulder
    objs.append(cil("poste", 0.11, 9.0, (6.4, 8, 4.5), galv))
    objs.append(cil("brazo", 0.06, 2.6, (5.15, 8, 8.95), galv, rot=(0, math.pi / 2, 0)))
    objs.append(caja("lampara", (0.75, 0.32, 0.14), (3.95, 8, 8.9), lampara))
    # guardrail, right side: a continuous beam and a post every 4 m
    objs.append(caja("riel", (0.06, TRAMO, 0.32), (5.0, TRAMO / 2, 0.62), galv))
    for i in range(TRAMO // 4):
        objs.append(caja(f"poste_riel_{i}", (0.14, 0.14, 0.8), (5.1, i * 4 + 2, 0.4), galv))
    # delineators ("fantasmas"), left shoulder every 16 m, with a red reflector
    for i in range(TRAMO // 16):
        objs.append(caja(f"fantasma_{i}", (0.12, 0.12, 1.05), (-4.7, i * 16 + 6, 0.52), blanco))
        objs.append(caja(f"reflejante_{i}", (0.13, 0.03, 0.18), (-4.7, i * 16 + 6 - 0.06, 0.88), refl))
    for i in range(TRAMO // 16):  # reflectors on the guardrail
        objs.append(caja(f"reflejante_riel_{i}", (0.03, 0.12, 0.1), (4.96, i * 16 + 2, 0.66), refl))
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    luz = bpy.data.lights.new("luz_poste", "SPOT")
    luz.spot_size = math.radians(120)
    luz.spot_blend = 0.6
    luz.color = lin(CFG["presets"]["noche"]["postes"]["color"])
    lo = bpy.data.objects.new("luz_poste", luz)
    lo.location = (3.95, 8, 8.75)
    col.objects.link(lo)
    return col, objs, lo


def cerros():
    """A ring of low hills far away: silhouette against the sky. Static (at infinity parallax is nil)."""
    import bmesh
    bm = bmesh.new()
    n, rings = 180, 4
    radios = [700, 820, 950, 1100]
    verts = []
    for j, rr in enumerate(radios):
        fila = []
        for i in range(n):
            a = 2 * math.pi * i / n
            h = 0 if j in (0, rings - 1) else (38 + 26 * math.sin(3 * a + 1.3) + 18 * math.sin(7 * a + 0.4) + 9 * math.sin(17 * a + 2.1)) * (1.0 if j == 1 else 0.75)
            fila.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, max(h, 0) - 2)))
        verts.append(fila)
    for j in range(rings - 1):
        for i in range(n):
            bm.faces.new((verts[j][i], verts[j][(i + 1) % n], verts[j + 1][(i + 1) % n], verts[j + 1][i]))
    me = bpy.data.meshes.new("cerros")
    bm.to_mesh(me)
    o = bpy.data.objects.new("cerros", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat("cerro", (0.012, 0.011, 0.01), 0.95))
    return o


# ---------------------------------------------------------------- build

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    cam_e, body, ruedas, radio = camion()
    col, props, luz_poste = tramo_props()
    hills = cerros()
    return dict(camion=cam_e, body=body, ruedas=ruedas, radio=radio, tramo=col, props=props, luz_poste=luz_poste, cerros=hills)


def exportar_glb(s):
    out = os.path.join(REPO, "public", "escena", "escena.glb")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [s["camion"], s["body"], *s["ruedas"], *s["props"], s["cerros"]]:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_lights=False, export_cameras=False,
                              export_draco_mesh_compression_enable=False)
    print("GLB", out, os.path.getsize(out))


def mundo_render(s, preset):
    """Road, ground, instances of the tramo, lights, world; animated over one loop."""
    sc = bpy.context.scene
    P = CFG["presets"][preset]
    largo_total = 760
    mundo = bpy.data.objects.new("mundo", None)
    sc.collection.objects.link(mundo)
    losa = MUNDO["losa"]
    road = plano("carretera", 8.0, largo_total, -120, 0.015, tex_mat("asfalto_carril", "Road007"), 8.0)
    ground = plano("terreno", 3000, largo_total + 1400, -820, 0.0, tex_mat("terreno", "Asphalt031", oscurecer=0.22, tinte=(1.0, 0.86, 0.72)), 4.0)
    road.parent = mundo; ground.parent = mundo
    # instances of the tramo every TRAMO m, enough to cover the view during the whole loop
    for k in range(-2, (largo_total - 120) // TRAMO):
        inst = bpy.data.objects.new(f"tramo_{k}", None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = s["tramo"]
        inst.location = (0, k * TRAMO, 0)
        inst.parent = mundo
        sc.collection.objects.link(inst)
    sc.view_layers[0].layer_collection.children["tramo"].exclude = True
    # lights from the preset
    s["luz_poste"].data.energy = W_POSTE * P["postes"]["intensidad"]
    if not P["postes"]["encendidos"]:
        for m in ("lampara",):
            bpy.data.materials[m].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
    sol = bpy.data.lights.new("luna", "SUN")
    sol.energy = P["luna"]["intensidad"]
    sol.color = lin(P["luna"]["color"])
    sol.angle = math.radians(1.5)
    so = bpy.data.objects.new("luna", sol)
    so.rotation_euler = (-b(P["luna"]["dir"])).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(so)
    for lado in (-0.62, 0.62):
        sp = bpy.data.lights.new(f"faro_{lado}", "SPOT")
        sp.energy = W_FARO * P["faros"]["intensidad"]
        sp.color = lin(P["faros"]["color"])
        sp.spot_size = math.radians(55)
        sp.spot_blend = 0.5
        sp.shadow_soft_size = 0.08
        o = bpy.data.objects.new(f"faro_{lado}", sp)
        o.location = (MUNDO["carril_x"] + lado, MUNDO["largo_camion"] / 2 + 0.05, 0.85)
        o.rotation_euler = Vector((0, 1, -0.06)).to_track_quat("-Z", "Y").to_euler()
        o.parent = s["camion"]
        sc.collection.objects.link(o)
    cl = bpy.data.lights.new("calaveras", "POINT")
    cl.energy = W_CALAVERA * P["calaveras"]["intensidad"]
    cl.color = lin(P["calaveras"]["color"])
    co = bpy.data.objects.new("calaveras", cl)
    co.location = (MUNDO["carril_x"], -MUNDO["largo_camion"] / 2 - 0.3, 0.9)
    sc.collection.objects.link(co)
    # world HDRI
    w = bpy.data.worlds.new("cielo")
    sc.world = w
    if not w.node_tree:
        w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(ASSETS, f"{P['hdri']}_2k.hdr"))
    bg = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = P["cielo_intensidad"]
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    # animation: world moves -Y by RECORRIDO over NFR frames; wheels turn a whole number of times
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, NFR - 1
    def lineal(ob, path, idx, v0, v1):
        ob.keyframe_insert(path, index=idx, frame=0)
        fc = ob.animation_data.action
        setattr_path(ob, path, idx, v1)
        ob.keyframe_insert(path, index=idx, frame=NFR)
        setattr_path(ob, path, idx, v0)
    def setattr_path(ob, path, idx, v):
        getattr(ob, path)[idx] = v
    mundo.location.y = 0
    lineal(mundo, "location", 1, 0.0, -float(RECORRIDO))
    vueltas = round(RECORRIDO / (2 * math.pi * s["radio"]))
    print("VUELTAS", vueltas, "radio", s["radio"])
    for r in s["ruedas"]:
        r.rotation_euler.x = 0
        lineal(r, "rotation_euler", 0, 0.0, -2 * math.pi * vueltas)
    for ob in [mundo, *s["ruedas"]]:
        for fc in iter_fcurves(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
            fc.extrapolation = "LINEAR"


def iter_fcurves(ob):
    act = ob.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:  # Blender 5 layered actions
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
        return out


def camara(parada, w, h):
    sc = bpy.context.scene
    st = next(p for p in CFG["paradas"] if p["id"] == parada)
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    asp = w / h
    vfov = math.radians(st["fov"])
    if asp < 1:  # same rule as the page: hold the horizontal angle of a square frame
        vfov = 2 * math.atan(math.tan(vfov / 2) / asp)
    cd.angle_y = vfov
    cd.clip_end = 3000
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    co.location = b(st["pos"])
    co.rotation_euler = (b(st["mira"]) - b(st["pos"])).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100


def motor(samples, preset):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = math.log2(CFG["presets"][preset]["exposicion"])
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5  # 180 degrees
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["glb"]
    s = build()
    if argv[0] == "glb":
        exportar_glb(s)
        return
    preset, parada, w, h, out = argv[1], argv[2], int(argv[3]), int(argv[4]), argv[5]
    samples = int(argv[6]) if len(argv) > 6 else 64
    mundo_render(s, preset)
    camara(parada, w, h)
    motor(samples, preset)
    sc = bpy.context.scene
    if argv[0] == "still":
        sc.frame_set(0)
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    else:
        sc.frame_start = int(argv[7]) if len(argv) > 7 else 0
        sc.frame_end = int(argv[8]) if len(argv) > 8 else NFR - 1
        sc.render.filepath = os.path.join(out, "f_####")
        bpy.ops.render.render(animation=True)


main()

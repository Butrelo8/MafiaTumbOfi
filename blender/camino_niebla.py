"""road3's fog: denser ("Xalapa is foggy") and with the warm 'ancha' lamp's glow back, without road2's blotches.
Exec'd by camino_mx140.py in its namespace (MONTAJE_CAMINO=road3). Every value can be overridden for one still with
NIEBLA_PRUEBA="clave=valor;clave=valor" (WSLENV must carry it); the defaults below are the kept result.

  dens      fog density (Principled Volume, mundo.niebla's own 0.0028 before)
  scatter   1 = the 'ancha' areas light the fog (luz_caja reads NIEBLA_CFG)      0 = road2's fix, no glow
  muestreo  fog material volume sampling: DISTANCE | EQUIANGULAR | MULTIPLE_IMPORTANCE
  clamp     sample_clamp_indirect (0 = off)         arbol  1/0 light tree         spp  samples (default: the command line's)
  pasadas   denoiser input passes RGB | RGB_ALBEDO | RGB_ALBEDO_NORMAL   pre  prefilter NONE|FAST|ACCURATE   cdirecto  clamp direct   dn  1/0 denoise
  paso      scene volume_step_rate                  adapt  1/0 adaptive sampling  vol_rebotes  volume bounces
"""
import os

NIEBLA_CFG = dict(dens=0.005, scatter=1, muestreo="EQUIANGULAR", clamp=0.0, arbol=1, spp=0, paso=0.0, adapt=1, vol_rebotes=-1, pasadas="RGB", pre="", cdirecto=0.0, dn=1, dnr="")
for _kv in filter(None, os.environ.get("NIEBLA_PRUEBA", "").split(";")):
    _k, _v = _kv.split("=")
    NIEBLA_CFG[_k] = type(NIEBLA_CFG[_k])(float(_v)) if isinstance(NIEBLA_CFG[_k], (int, float)) else _v


def niebla_ajustes():
    c = NIEBLA_CFG
    sc_ = bpy.context.scene
    mat_f = bpy.data.objects["w_niebla"].data.materials[0]
    pv = next(n for n in mat_f.node_tree.nodes if n.type == "PRINCIPLED_VOLUME")
    pv.inputs["Density"].default_value = c["dens"]
    mat_f.cycles.volume_sampling = c["muestreo"]
    sc_.cycles.sample_clamp_indirect = c["clamp"]
    sc_.cycles.use_light_tree = bool(c["arbol"])
    sc_.cycles.use_adaptive_sampling = bool(c["adapt"])
    if c["spp"]:
        sc_.cycles.samples = int(c["spp"])
    if c["paso"]:
        sc_.cycles.volume_step_rate = c["paso"]
    cy_ = sc_.cycles
    if c["pasadas"]:
        cy_.denoising_input_passes = c["pasadas"]
    if c["pre"]:
        cy_.denoising_prefilter = c["pre"]
    if c["dnr"]:
        cy_.denoiser = c["dnr"]
    cy_.sample_clamp_direct = c["cdirecto"]
    cy_.use_denoising = bool(c["dn"])
    if c["vol_rebotes"] >= 0:
        sc_.cycles.volume_bounces = int(c["vol_rebotes"])

    def antes_de_render(*_):
        cy = bpy.context.scene.cycles
        print("CAMINO render: spp", cy.samples, "adaptivo", cy.use_adaptive_sampling, "clamp_indirecto", cy.sample_clamp_indirect,
              "arbol", cy.use_light_tree, "paso_vol", cy.volume_step_rate, "rebotes_vol", cy.volume_bounces,
              "muestreo", mat_f.cycles.volume_sampling, "denoiser", cy.denoiser, "pasadas", cy.denoising_input_passes, "prefiltro", cy.denoising_prefilter, "clamp_directo", cy.sample_clamp_direct, "denoise", cy.use_denoising, "densidad", pv.inputs["Density"].default_value,
              "areas", [(o.name, o.visible_volume_scatter) for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "AREA" and o.data.energy in (518, 230)],
              flush=True)
    bpy.app.handlers.render_pre.append(antes_de_render)
    print("CAMINO niebla:", c, flush=True)


niebla_ajustes()

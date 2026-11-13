// Cab shot, 2.5D: three Blender layers (bg, fig, fg; 60-frame loops with alpha) on 3D planes, a slow camera push with
// depth of field focused on the band, an idle wiggle on the figures, glow on the lights, motion blur.
// Injected before this file by componer.sh: W, H, CAPAS (dir with bg/ fig/ fg/ f_0000.png..), PUSH (fraction of the
// figures' distance the camera travels), APERTURA (px), DERIVA (px of sideways drift), DUR (s).
//
// Geometry: the camera starts Z px in front of the figure plane (Z = its zoom, so z = 0 is the 100 % plane). Each plane
// sits at its real distance from the Blender camera (fg seat backs ~1.0 m, figures ~1.25 m, bg ~2.6 m: dash at 1.8 m,
// road beyond) scaled so 1.25 m = Z px, and is scaled by d / Z so every plate frames exactly as rendered at t = 0.
var M = { fg: 1.0, fig: 1.25, bg: 2.6 };
var c = app.project.items.addComp("Cabina", W, H, 1, DUR, 24);
var cam = c.layers.addCamera("Camara", [W / 2, H / 2]);
var zoom = cam.property("Camera Options").property("Zoom").value;

function capa(nombre) {
    var io = new ImportOptions(File(CAPAS + "/" + nombre + "/f_0000.png"));
    io.sequence = true;
    var ft = app.project.importFile(io);
    ft.mainSource.conformFrameRate = 24;
    var L = c.layers.add(ft);
    L.name = nombre;
    L.threeDLayer = true;
    var d = zoom * M[nombre] / M.fig;
    L.property("Transform").property("Position").setValue([W / 2, H / 2, d - zoom]);
    L.property("Transform").property("Scale").setValue([100 * d / zoom, 100 * d / zoom, 100]);
    L.timeRemapEnabled = true;               // 60-frame seamless loop (road 48 m, nod 20 f) cycled over the shot
    L.property("Time Remap").expression = "loopOut('cycle')";
    L.outPoint = DUR;
    L.motionBlur = true;
    writeLn(nombre + " " + ft.name + " " + ft.duration.toFixed(3) + " s, plane at " + (d - zoom).toFixed(1) + " px, scale " + (100 * d / zoom).toFixed(1));
    return L;
}
var bg = capa("bg"), fig = capa("fig"), fg = capa("fg");   // added in this order: fg ends on top of the stack

// idle: the band sways a hair with the road (2 px, 0.6 Hz) on top of its own nod
fig.property("Transform").property("Position").expression = "value + [wiggle(0.6, 2)[0] - value[0], wiggle(0.6, 2, 1, 0.5, time + 7)[1] - value[1], 0]";

// glow on the lights (dash screen, road lamps, headlight pool): only what is near white
var g = bg.Effects.addProperty("Glow");
g.property("Glow Threshold").setValue(78);
g.property("Glow Radius").setValue(H / 40);
g.property("Glow Intensity").setValue(0.8);

// camera: eased push along its axis plus an optional sideways drift; focus follows the figure plane
var cp = cam.property("Transform").property("Position");
var p0 = cp.value;
cp.setValueAtTime(0, p0);
cp.setValueAtTime(DUR, [p0[0] + DERIVA, p0[1], p0[2] + PUSH * zoom]);
var e = new KeyframeEase(0, 60);
for (var k = 1; k <= cp.numKeys; k++) cp.setTemporalEaseAtKey(k, [e], [e]);
var co = cam.property("Camera Options");
co.property("Depth of Field").setValue(1);
co.property("Aperture").setValue(APERTURA);
co.property("Focus Distance").expression = "thisComp.layer('fig').transform.position[2] - transform.position[2]";
// point of interest moves with the camera so the push stays straight
cam.property("Transform").property("Point of Interest").expression = "transform.position + [0, 0, 1000]";

c.motionBlur = true;
writeLn("zoom " + zoom.toFixed(1) + " push " + (PUSH * zoom).toFixed(1) + " px, aperture " + APERTURA + ", drift " + DERIVA);

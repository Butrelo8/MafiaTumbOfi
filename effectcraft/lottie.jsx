// Small Lottie test: a gold title that rises and fades in, holds, fades out. 800x240, 3 s at 24 fps.
// effectcraft-cli --empty script effectcraft/lottie.jsx --save-as <dir>/titulo.ecproj
// effectcraft-cli --project <dir>/titulo.ecproj exec file.exportLottie '{"comp":"Titulo","path":"<dir>/titulo.json","textAsShapes":true}'
var c = app.project.items.addComp("Titulo", 800, 240, 1, 3, 24);
var t = c.layers.addText("MAFIA TUMBADA");
var d = t.property("Source Text").value;
d.font = "Inter-Bold";
d.fontSize = 72;
d.fillColor = [0.79, 0.64, 0.27];
d.justification = ParagraphJustification.CENTER_JUSTIFY;
d.tracking = 60;
t.property("Source Text").setValue(d);
var p = t.property("Position");
p.setValueAtTime(0, [400, 170]);
p.setValueAtTime(0.8, [400, 145]);
var o = t.property("Opacity");
o.setValueAtTime(0, 0);
o.setValueAtTime(0.8, 100);
o.setValueAtTime(2.4, 100);
o.setValueAtTime(3, 0);
var e = new KeyframeEase(0, 75);
for (var k = 1; k <= p.numKeys; k++) p.setTemporalEaseAtKey(k, [e], [e]);
var r = c.layers.addShape();
r.name = "linea";
var g = r.property("Contents").addProperty("ADBE Vector Group");
g.property("Contents").addProperty("ADBE Vector Shape - Rect").property("Size").setValue([520, 3]);
g.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("Color").setValue([0.79, 0.64, 0.27]);
// EffectCraft 0.24.1: on a shape layer r.property("Position"|"Scale"|"Opacity") binds the first group's transform, not the
// layer's (After Effects binds the layer). Go through "Transform" explicitly.
var tr = r.property("Transform");
tr.property("Position").setValue([400, 190]);
var s = tr.property("Scale");
s.setValueAtTime(0.3, [0, 100]);
s.setValueAtTime(1.2, [100, 100]);
tr.property("Opacity").setValueAtTime(2.4, 100);
tr.property("Opacity").setValueAtTime(3, 0);
writeLn("layers " + c.numLayers + " font " + t.property("Source Text").value.font);

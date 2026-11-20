#!/usr/bin/env bun
// Live scene with the new G63 (2026-11-20), step 3: swaps the 6x6 for the new car in the exporter's crudo files.
//   GT=<dir whose node_modules has @gltf-transform/*, draco3dgltf> bun scripts/vivo-g63-unir.mjs <crudo dir (old)> <coche.glb> <vivo-g63-datos.json> <out crudo dir>
// escena.glb: everything under `camion` goes except the cast (the four _v5 rigs) and Héctor's bottle; coche.glb's `camion` children
// (car, rack, load, net, dressing) take their place; the cast rigs, the bottle and their clips move by blender/props/g63_paradas.json
// `cast` {dy, dz} (Blender axes) until the owner places them in the new car (docs/g63-nuevo-dueno.md). pantalla_camion and cerros stay.
// vivo.json: stop cameras / cab boxes from g63_paradas.json, the headlamps, the wheel radius, the truck box from Blender's numbers.
// mundo.glb is copied as is.
import { createRequire } from 'node:module'
import { join, dirname } from 'node:path'
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const req = createRequire(join(process.env.GT ?? '.', 'node_modules', 'x.js'))
const { NodeIO } = req('@gltf-transform/core')
const { ALL_EXTENSIONS } = req('@gltf-transform/extensions')
const { mergeDocuments, unpartition } = req('@gltf-transform/functions')
const draco3d = req('draco3dgltf')
const [viejo, coche, datosJ, sal] = process.argv.slice(2)
const AQUI = dirname(fileURLToPath(import.meta.url))
const P = JSON.parse(readFileSync(join(AQUI, '..', 'blender', 'props', 'g63_paradas.json'), 'utf8'))
const D = JSON.parse(readFileSync(datosJ, 'utf8'))
mkdirSync(sal, { recursive: true })
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() })

const A = await io.read(join(viejo, 'escena.glb'))
const B = await io.read(coche)
const camA = A.getRoot().listNodes().find((n) => n.getName() === 'camion')
const camB = B.getRoot().listNodes().find((n) => n.getName() === 'camion')
if (!camA || !camB) throw new Error('no camion node')
const CAST = /^(alejandro|hector|manager|diego)_v5_rig$/
const BOTELLA = /^k5_bebida_mano/
// the cast's old stand-in rigs (alejandro_rig ...) parent nothing the page keeps; the optimizer drops them. Keep the chain it expects.
const guardar = new Set()
for (const n of camA.listChildren()) {
  if (CAST.test(n.getName()) || BOTELLA.test(n.getName()) || /^(alejandro|hector|manager|diego)_rig$|^diego_raiz$|^asiento_/.test(n.getName())) guardar.add(n)
}
let quitados = 0
for (const n of camA.listChildren()) if (!guardar.has(n)) { n.traverse((x) => x.dispose()); quitados++ }
console.log('escena vieja: camion hijos quitados', quitados, 'guardados', [...guardar].map((n) => n.getName()).join(' '))

const mapa = mergeDocuments(A, B)
const camB2 = mapa.get(camB)
for (const h of [...camB2.listChildren()]) { camB2.removeChild(h); camA.addChild(h) }
// the merged source scene: drop its root node `camion` (now empty) and the extra scene
for (const s of A.getRoot().listScenes().slice(1)) s.dispose()
camB2.dispose()

// the cast and the bottle onto the new seats
const [dy, dz] = [P.cast.dy, P.cast.dz]
const mover = (n) => {
  const t = n.getTranslation()
  n.setTranslation([t[0], t[1] + dz, t[2] - dy]) // glTF axes: x, y = Blender z, z = -Blender y
}
const movidos = new Set()
for (const n of camA.listChildren()) if (CAST.test(n.getName()) || BOTELLA.test(n.getName())) { mover(n); movidos.add(n) }
for (const a of A.getRoot().listAnimations()) {
  for (const c of a.listChannels()) {
    if (c.getTargetPath() !== 'translation' || !movidos.has(c.getTargetNode())) continue
    const acc = c.getSampler().getOutput()
    for (let i = 0; i < acc.getCount(); i++) { const v = acc.getElement(i, []); acc.setElement(i, [v[0], v[1] + dz, v[2] - dy]) }
  }
}
console.log('cast movido', dy, dz, 'nodos', movidos.size)
await A.transform(unpartition()) // the merge adds a second buffer; a GLB takes one
for (const e of A.getRoot().listExtensionsUsed()) if (/draco/i.test(e.extensionName)) e.dispose() // written plain: vivo-optimizar re-encodes
await io.write(join(sal, 'escena.glb'), A)
copyFileSync(join(viejo, 'mundo.glb'), join(sal, 'mundo.glb'))

// ---- vivo.json
const J = JSON.parse(readFileSync(join(viejo, 'vivo.json'), 'utf8'))
const cam = P.camaras.map((c) => c)
cam[3] = P.banda[0]
J.camaras = cam
J.banda = P.banda
J.cabina = P.cabina
J.parabrisas = P.parabrisas
const alto = D.cuerpo.max[2] // the body only, as for the 6x6: the load hangs on the roof and is not part of the box vivoRuta orbits (its tests walk the paths against it)
J.camion = { min: [D.cuerpo.min[0], D.cuerpo.min[1], 0], max: [D.cuerpo.max[0], D.cuerpo.max[1], alto] }
J.camion.min[0] = 2 * 1.72 - J.camion.max[0] // symmetric about the lane, as the old exporter did
J.domoZ = P.domoZ
J.lamparasZ = P.lamparasZ
J.oclusion = P.oclusion
J.faros = D.faros
J.ruedas = D.ruedas_nombres
J.radio = D.radio_rueda
writeFileSync(join(sal, 'vivo.json'), JSON.stringify(J, null, 1))
console.log('vivo.json: camion', JSON.stringify(J.camion), 'radio', J.radio, 'ruedas', J.ruedas.join(','))

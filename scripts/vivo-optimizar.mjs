#!/usr/bin/env bun
// /vivo-secciones step 2b: the exporter's escena.glb + mundo.glb -> the page's lighter files (2026-11-18, "make it swift").
//   GT=<dir whose node_modules has @gltf-transform/{core,extensions,functions}, draco3dgltf, meshoptimizer, sharp> \
//     bun scripts/vivo-optimizar.mjs tmp/vivo/crudo public/vivo
// escena.glb: drops the old stand-ins (alejandro|hector|diego|manager and their rigs; the _v5 rigs hang from them, so the
//   v5 rigs move up to `camion` first), strips transmission (three re-renders every opaque object for it) and clearcoat,
//   simplifies the two meshes the exporter never decimated (the screen truck's cab, the strawberry), textures to 512.
// reparto.glb: the four _v5 rigs and their clips, loaded after the first frame. The rigs riding the truck hang from an
//   empty named `camion` that the page empties into the real one.
// mundo.glb: textures to 512.
import { createRequire } from 'node:module'
import { join } from 'node:path'

const req = createRequire(join(process.env.GT ?? '.', 'node_modules', 'x.js'))
const { NodeIO } = req('@gltf-transform/core')
const { ALL_EXTENSIONS } = req('@gltf-transform/extensions')
const { prune, dedup, weld, simplifyPrimitive, textureCompress, draco } = req('@gltf-transform/functions')
const draco3d = req('draco3dgltf')
const { MeshoptSimplifier } = req('meshoptimizer')
const sharp = req('sharp')

const [ent, sal] = process.argv.slice(2)
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule(),
})
await MeshoptSimplifier.ready
const VIEJOS = /^(alejandro|hector|diego|manager)(_rig)?$/ // exact: a prefix would take the _v5 cast and the asiento_* seats
const REPARTO = /^(alejandro|hector|manager|diego)_v5_rig$/
const SIMPLIFICAR = { p3_camion: 0.12, 'pp_fresa.001': 0.06 } // node name -> ratio (124 k and 50 k tris in the export)
const nodo = (doc, n) => doc.getRoot().listNodes().find((x) => x.getName() === n)
const tris = (doc) => doc.getRoot().listMeshes().flatMap((m) => m.listPrimitives()).reduce((a, p) => a + (p.getIndices()?.getCount() ?? 0) / 3, 0)

async function terminar(doc, nombre) {
  await doc.transform(prune(), dedup(), textureCompress({ encoder: sharp, targetFormat: 'webp', resize: [512, 512] }), draco({ method: 'edgebreaker' }))
  await io.write(join(sal, nombre), doc)
  const r = doc.getRoot()
  console.log(nombre, `tris ${tris(doc) | 0}, nodes ${r.listNodes().length}, materials ${r.listMaterials().length}, clips ${r.listAnimations().map((a) => `${a.getName()}:${a.listChannels().length}`).join(' ')}`)
}

// ---- escena: one read per output (the cast file and the rest)
const leer = async () => {
  const doc = await io.read(join(ent, 'escena.glb'))
  const camion = nodo(doc, 'camion')
  // the export left each _v5 rig with a local translation that cancels its parent's: the cast sat at the world origin (the
  // figure on the road at stop 2) and only the old stand-ins filled the seats. Zeroed, each rig sits on its old rig's origin.
  for (const n of doc.getRoot().listNodes()) if (REPARTO.test(n.getName())) n.setTranslation([0, 0, 0])
  for (const n of doc.getRoot().listNodes()) if (REPARTO.test(n.getName()) && n.getParentNode() !== camion && VIEJOS.test(n.getParentNode()?.getName() ?? '')) {
    // child of an old rig that itself sits under camion: fold the old rig's local transform in, then hang it from camion
    const viejo = n.getParentNode()
    if (viejo.getParentNode() !== camion) throw new Error(`${n.getName()}: old rig not under camion`)
    const m = multiplicar(viejo.getMatrix(), n.getMatrix())
    viejo.removeChild(n); camion.addChild(n); n.setMatrix(m)
  }
  for (const n of doc.getRoot().listNodes()) if (VIEJOS.test(n.getName())) n.traverse((x) => x.dispose())
  return doc
}

const esc = await leer()
for (const n of esc.getRoot().listNodes()) if (REPARTO.test(n.getName())) n.traverse((x) => x.dispose())
for (const a of esc.getRoot().listAnimations()) a.dispose()
for (const e of esc.getRoot().listExtensionsUsed()) if (/transmission|clearcoat/.test(e.extensionName)) e.dispose()
for (const [n, ratio] of Object.entries(SIMPLIFICAR)) {
  const x = nodo(esc, n)
  if (!x?.getMesh()) throw new Error(`no mesh node ${n}`)
  const antes = x.getMesh().listPrimitives().reduce((a, p) => a + p.getIndices().getCount() / 3, 0)
  // Draco-decoded, every face has its own normals: no weld, no simplify (124 k -> 61 k at any error). Drop the normals
  // (GLTFLoader then shades these two flat, fine at their size on screen), weld, simplify.
  for (const p of x.getMesh().listPrimitives()) p.setAttribute('NORMAL', null)
  await esc.transform(weld())
  for (const p of x.getMesh().listPrimitives()) simplifyPrimitive(p, { simplifier: MeshoptSimplifier, ratio, error: 0.01 })
  console.log('simplify', n, antes, '->', x.getMesh().listPrimitives().reduce((a, p) => a + p.getIndices().getCount() / 3, 0))
}
await esc.transform(weld())
await terminar(esc, 'escena.glb')

const rep = await leer()
const camionR = nodo(rep, 'camion')
const quedan = new Set([camionR, ...rep.getRoot().listNodes().filter((n) => REPARTO.test(n.getName()))])
for (const n of rep.getRoot().listNodes()) {
  if (quedan.has(n) || [...quedan].some((q) => q !== camionR && esAncestro(q, n))) continue
  if (esAncestro(n, nodo(rep, 'diego_v5_rig'))) continue // diego_raiz < mx < diego_v5_rig: keep the chain
  if (n === camionR) continue
  n.dispose()
}
camionR.setMesh(null)
await terminar(rep, 'reparto.glb')

const mun = await io.read(join(ent, 'mundo.glb'))
await terminar(mun, 'mundo.glb')

function esAncestro(a, n) { for (let p = n?.getParentNode(); p; p = p.getParentNode()) if (p === a) return true; return false }
function multiplicar(a, b) { // column-major 4x4
  const o = new Array(16).fill(0)
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]
  return o
}

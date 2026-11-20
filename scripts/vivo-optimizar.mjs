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
  // glass as the page draws it (vivoSecciones.ts vidrios(): same names, opacity 0.15), set here so dedup() can't merge it with an
  // opaque twin: vidrio_falso exports as plain white like k3_alu, and the merge kept k3_alu's name (windows opaque, 2026-11-19)
  for (const m of doc.getRoot().listMaterials()) if (/vidrio|mica|glass|pet/i.test(m.getName())) m.setAlphaMode('BLEND').setBaseColorFactor([...m.getBaseColorFactor().slice(0, 3), 0.15])
  if (nombre === 'escena.glb') await aplanar(doc) // the truck's props only: the road's dark textures stay
  if (nombre === 'escena.glb') await calcas256(doc)
  await doc.transform(prune(), dedup(), textureCompress({ encoder: sharp, targetFormat: 'webp', resize: [512, 512] }), draco({ method: 'edgebreaker' }))
  await io.write(join(sal, nombre), doc)
  const r = doc.getRoot()
  console.log(nombre, `tris ${tris(doc) | 0}, nodes ${r.listNodes().length}, materials ${r.listMaterials().length}, clips ${r.listAnimations().map((a) => `${a.getName()}:${a.listChannels().length}`).join(' ')}`)
}

// ---- escena: one read per output (the cast file and the rest)
const leer = async () => {
  const doc = await io.read(join(ent, 'escena.glb'))
  const camion = nodo(doc, 'camion')
  // the v5 rigs hang straight from camion with their Cycles world matrix (vivo_secciones_exportar.asentar_reparto): no zeroing
  // here any more (it hid the old parent-relative transform and left the heads 0.06-0.22 m low, Diego out of his seat)
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
sinGigantes(esc)
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

/** Near-black, near-uniform colour textures (mean < 20/255 and spread <= 8 on every channel: the kiln props' leather and padding,
 * piel_Baked*, acolchado_Baked) become flat materials: their mean colour, roughness and metalness, no maps. Live they read as flat
 * black anyway, and a flat material joins the page's one merged mesh (vivoSecciones.ts fusionar) instead of costing a draw
 * call each: 5 calls, which the 2026-11-19 truck needed to stay under the cap of 90. */
async function aplanar(doc) {
  const lin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  for (const m of doc.getRoot().listMaterials()) {
    const t = m.getBaseColorTexture()
    if (!t || m.getAlphaMode() !== 'OPAQUE' || m.getEmissiveTexture()) continue
    const s = (await sharp(Buffer.from(t.getImage())).stats()).channels.slice(0, 3)
    if (!s.every((c) => c.mean < 20 && c.stdev <= 8)) continue
    const f = m.getBaseColorFactor()
    m.setBaseColorFactor([0, 1, 2].map((i) => lin(s[i].mean / 255) * f[i]).concat(f[3]))
    const mr = m.getMetallicRoughnessTexture()
    if (mr) {
      const q = (await sharp(Buffer.from(mr.getImage())).stats()).channels
      m.setRoughnessFactor(m.getRoughnessFactor() * q[1].mean / 255).setMetallicFactor(m.getMetallicFactor() * q[2].mean / 255)
    }
    m.setBaseColorTexture(null).setNormalTexture(null).setMetallicRoughnessTexture(null).setOcclusionTexture(null)
    console.log('aplanar', m.getName(), s.map((c) => c.mean.toFixed(0)).join(','))
  }
}

/** The stickers' art (c3_* materials, 22 textures, 214 KB at 512) to fit 256: they sat 136 KB on escena.glb, the first-frame file,
 * and TTFF reached 3.99 s against the 4 s cap (2026-11-19). PNG keeps the alpha; textureCompress then makes it webp. */
async function calcas256(doc) {
  const ts = new Set(doc.getRoot().listMaterials().filter((m) => /^c3_/.test(m.getName())).map((m) => m.getBaseColorTexture()).filter(Boolean))
  for (const t of ts) {
    const ajenos = t.listParents().filter((p) => p.propertyType === 'Material' && !/^c3_/.test(p.getName()))
    if (ajenos.length) { console.log('calcas256 skip (shared)', t.getName(), ajenos.map((m) => m.getName()).join(',')); continue }
    t.setImage(new Uint8Array(await sharp(Buffer.from(t.getImage())).resize(256, 256, { fit: 'inside', withoutEnlargement: true }).png().toBuffer())).setMimeType('image/png')
  }
  console.log('calcas256', ts.size)
}

/** The decimate leaves 1.15-1.5 m plastico triangles lying in the headliner's plane (z 2.165-2.19, cab_techo at 2.189): which
 * of the two wins the depth test flips between exports (2026-11-19: a pale wedge at the top of stop 1). Rule, in Blender axes:
 * a soup node (Material*), not the headliner or the paint, all three corners at z 2.16-2.20, centre in the cab ahead of the
 * visors (x 1.0-2.45, y -0.3-0.75), an edge over 0.4 m. On the 2026-11-19 export: 8 faces, the headliner within 1.5 cm over
 * 6-7 of 7 sample points of each (/mnt/e/tmp/mto-cabina-restos/scripts/gigantes.py).
 * Also the old headrests' faces in the headliner material, which cabina_tripo.CABECERA_NO kept: cab_techo with all corners at
 * z 1.90-2.03 inside the cabecera boxes (x 1.11-2.33, y 0.05-0.60); 3 faces, a pale line behind Diego at banda-hector
 * (the real headliner sits at 2.19, its sides at 2.05+ by the doors: techo_bajo.py). */
function sinGigantes(doc) {
  const quitadas = []
  for (const n of doc.getRoot().listNodes()) {
    if (!n.getMesh() || !/^Material/.test(n.getName())) continue
    const M = n.getWorldMatrix()
    const blender = (a) => { const w = [0, 1, 2].map((r) => M[r] * a[0] + M[4 + r] * a[1] + M[8 + r] * a[2] + M[12 + r]); return [w[0], -w[2], w[1]] }
    for (const p of n.getMesh().listPrimitives()) {
      const ind = p.getIndices(), pos = p.getAttribute('POSITION')
      const mat = p.getMaterial()?.getName() ?? '', techo = /cab_techo/.test(mat)
      if (!ind || /pintura/.test(mat)) continue
      const quedan = []
      for (let t = 0; t < ind.getCount(); t += 3) {
        const ix = [0, 1, 2].map((k) => ind.getScalar(t + k))
        const P = ix.map((i) => blender(pos.getElement(i, [])))
        const c = [0, 1, 2].map((k) => (P[0][k] + P[1][k] + P[2][k]) / 3)
        const borde = Math.max(...[0, 1, 2].map((k) => Math.hypot(...[0, 1, 2].map((j) => P[k][j] - P[(k + 1) % 3][j]))))
        const gigante = !techo && P.every((v) => v[2] >= 2.16 && v[2] <= 2.2) && c[0] >= 1.0 && c[0] <= 2.45 && c[1] >= -0.3 && c[1] <= 0.75 && borde > 0.4
        const cabecera = techo && P.every((v) => v[2] >= 1.9 && v[2] <= 2.03) && c[0] >= 1.11 && c[0] <= 2.33 && c[1] >= 0.05 && c[1] <= 0.6
        if (gigante || cabecera) {
          quitadas.push(`${n.getName()} ${techo ? 'cab_techo ' : ''}${c.map((x) => x.toFixed(3)).join(',')} ${borde.toFixed(2)}`)
          continue
        }
        quedan.push(...ix)
      }
      if (quedan.length < ind.getCount()) ind.setArray(new (ind.getArray().constructor)(quedan))
    }
  }
  console.log('sinGigantes', quitadas.length, quitadas.join(' | '))
}

function esAncestro(a, n) { for (let p = n?.getParentNode(); p; p = p.getParentNode()) if (p === a) return true; return false }
function multiplicar(a, b) { // column-major 4x4
  const o = new Array(16).fill(0)
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]
  return o
}

import { createRequire } from 'node:module'
import { join } from 'node:path'
import { statSync } from 'node:fs'
const req = createRequire(join(process.env.GT, 'node_modules', 'x.js'))
const { NodeIO } = req('@gltf-transform/core')
const { ALL_EXTENSIONS } = req('@gltf-transform/extensions')
const { prune, dedup, weld, textureCompress, draco } = req('@gltf-transform/functions')
const draco3d = req('draco3dgltf'); const sharp = req('sharp')
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule() })
const tris = (doc) => doc.getRoot().listMeshes().flatMap((m) => m.listPrimitives()).reduce((a, p) => a + (p.getIndices()?.getCount() ?? 0) / 3, 0)
for (const [nombre, quitar] of [['solo ruedas', /^(g63_|rack_|k3_|carga_|vest_|Cube|Cylinder|Cone|Sphere|Plane|txt|pp_|placa|u_)/], ['interior+exterior sin ruedas ni carga', /^(rueda|rack_|k3_|carga_|vest_|Cube|Cylinder|Cone|Sphere|Plane|txt|pp_|placa|u_)/]]) {
  const doc = await io.read(process.argv[2])
  for (const n of doc.getRoot().listNodes()) if (quitar.test(n.getName()) && n.getName() !== 'camion') n.dispose()
  await doc.transform(prune(), dedup(), weld(), textureCompress({ encoder: sharp, targetFormat: 'webp', resize: [512, 512] }), draco({ method: 'edgebreaker' }))
  const f = `/tmp/claude-1001/pesos-${nombre.replace(/\W/g, '_')}.glb`
  await io.write(f, doc)
  console.log(nombre.padEnd(22), 'tris', Math.round(tris(doc)), 'bytes', statSync(f).size)
}

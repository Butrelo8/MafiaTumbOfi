#!/usr/bin/env node
// Cast pose inside a GLB, no Blender and no browser: forward kinematics of every joint of the four v5 rigs at the clip's time T (default 0),
// in Blender axes, against the owner's dump (blender/props/reparto_pose_dueno.json). Expect 0.0000 for all four. DZ lowers his side
// (the G63 cast shift is -0.28; the d7f18f1c / old crudo files use 0).
//   GT=<dir whose node_modules has @gltf-transform/{core,extensions}, draco3dgltf> node scripts/g63/pose_en_glb.mjs <reparto.glb | escena.glb> <dueno.json> [T=0] [DZ=0]
import { createRequire } from 'node:module'
import { join } from 'node:path'
import { readFileSync } from 'node:fs'
const req = createRequire(join(process.env.GT, 'node_modules', 'x.js'))
const { NodeIO } = req('@gltf-transform/core')
const { ALL_EXTENSIONS } = req('@gltf-transform/extensions')
const draco3d = req('draco3dgltf')
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule() })
const [glb, duenoPath, tiempo = '0', dz = '0'] = process.argv.slice(2)
const t = Number(tiempo)
const dueno = JSON.parse(readFileSync(duenoPath, 'utf8'))
const doc = await io.read(glb)
const mul = (a, b) => { const o = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o }
function compose(T, Q, S) {
  const [x, y, z, w] = Q
  const m = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0, 2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0, 2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0, 0, 0, 0, 1]
  for (let c = 0; c < 3; c++) for (let r = 0; r < 3; r++) m[c * 4 + r] *= S[c]
  m[12] = T[0]; m[13] = T[1]; m[14] = T[2]
  return m
}
const anim = new Map() // node -> {translation, rotation, scale} sampled at t, per animation name
function muestrear(a, canal) {
  const s = canal.getSampler(), ti = s.getInput().getArray(), v = s.getOutput().getArray(), n = canal.getTargetPath() === 'rotation' ? 4 : 3
  let i = 0
  while (i + 1 < ti.length && ti[i + 1] <= t) i++
  return Array.from(v.slice(i * n, i * n + n))
}
const animDe = {}
for (const a of doc.getRoot().listAnimations()) {
  const m = new Map()
  for (const c of a.listChannels()) { const nd = c.getTargetNode(); if (!m.has(nd)) m.set(nd, {}); m.get(nd)[c.getTargetPath()] = muestrear(a, c) }
  animDe[a.getName()] = m
}
const mundoDe = (n, m) => {
  const a = m.get(n) ?? {}
  const loc = compose(a.translation ?? n.getTranslation(), a.rotation ?? n.getRotation(), a.scale ?? n.getScale())
  const p = n.getParentNode()
  return p ? mul(mundoDe(p, m), loc) : loc
}
const aBlender = (p) => [p[0], -p[2], p[1]] // glTF y-up -> Blender z-up
const mulM = (M, p) => [0, 1, 2].map((r) => M[r][0] * p[0] + M[r][1] * p[1] + M[r][2] * p[2] + M[r][3])
for (const q of ['manager', 'hector', 'alejandro', 'diego']) {
  const rig = doc.getRoot().listNodes().find((n) => n.getName() === `${q}_v5_rig`)
  const clip = animDe[q] ?? new Map()
  const d = []
  rig.traverse((n) => {
    const nom = n.getName()
    if (!dueno.rigs[q].huesos[nom]) return
    const W = mundoDe(n, clip)
    const pg = aBlender([W[12], W[13], W[14]])
    const B = dueno.rigs[q].huesos[nom]
    const po = mulM(dueno.rigs[q].mundo, [B[0][3], B[1][3], B[2][3]])
    d.push([Math.hypot(...pg.map((v, i) => v - po[i] - (i === 2 ? Number(dz) : 0))), nom])
  })
  d.sort((a, b) => b[0] - a[0])
  const head = d.find((x) => /HeadTop/.test(x[1]))
  console.log(q, 'joints', d.length, 'max', d[0][0].toFixed(4), d[0][1], 'median', d[d.length >> 1][0].toFixed(4), 'HeadTop', head?.[0].toFixed(4), 'clipNodes', clip.size)
}

#!/usr/bin/env node
// (GLTFLoader names the rigs' same-named bones Hips, Hips_1, ...: the suffix is stripped to match.)
// The cast as the live page poses it against the owner's dump: every bone of each v5 rig in world space (three.js), converted to
// Blender axes, against his world matrix x bone matrix (+DZ). Truck sway is off (?f=0).
//   PW=E:\tmp\pw-vivo\node_modules\playwright-core CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe" WSLENV=PW:CHROME \
//     node.exe scripts/g63/pose_en_pagina.mjs <url> <dueno.json (Windows)> [DZ=-0.28]
import { createRequire } from 'node:module'
import { readFileSync } from 'node:fs'
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url, duenoPath, dz = '-0.28'] = process.argv.slice(2)
const dueno = JSON.parse(readFileSync(duenoPath, 'utf8'))
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist'] })
const page = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage()
await page.goto(`${url}?f=0&parada=0&sinpantalla`, { waitUntil: 'load' })
await page.waitForFunction(() => window.__vivo?.cargado, null, { timeout: 120000 })
await page.waitForTimeout(1500)
const mundo = await page.evaluate(() => {
  const esc = window.__vivo.escena, out = {}
  esc.updateMatrixWorld(true)
  for (const q of ['manager', 'hector', 'alejandro', 'diego']) {
    const rig = esc.getObjectByName(`${q}_v5_rig`)
    out[q] = {}
    rig?.traverse((o) => { if (o.isBone) { const p = o.getWorldPosition(new o.position.constructor()); out[q][o.name.replace(/_\d+$/, '')] = [p.x, p.y, p.z] } })
  }
  return out
})
const mul = (M, p) => [0, 1, 2].map((r) => M[r][0] * p[0] + M[r][1] * p[1] + M[r][2] * p[2] + M[r][3])
for (const q of Object.keys(dueno.rigs)) {
  const d = []
  for (const [nom, B] of Object.entries(dueno.rigs[q].huesos)) {
    const p = mundo[q][nom.replace(':', '')]
    if (!p) continue
    const bl = [p[0], -p[2], p[1]] // three (x, y up, z) -> Blender (x, -z, y)
    const po = mul(dueno.rigs[q].mundo, [B[0][3], B[1][3], B[2][3]])
    d.push([Math.hypot(bl[0] - po[0], bl[1] - po[1], bl[2] - po[2] - Number(dz)), nom])
  }
  d.sort((a, b) => b[0] - a[0])
  console.log(q, 'bones matched', d.length, '/', Object.keys(dueno.rigs[q].huesos).length, 'max', d[0]?.[0].toFixed(4), d[0]?.[1], 'median', d[d.length >> 1]?.[0].toFixed(4))
}
await browser.close()

import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist'] })
const page = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage()
await page.goto(process.argv[2] + '?f=0&parada=0&sinpantalla', { waitUntil: 'load' })
await page.waitForFunction(() => window.__vivo?.cargado, null, { timeout: 120000 })
await page.waitForTimeout(9000)
const r = await page.evaluate(() => {
  const out = {}
  const esc = window.__vivo.escena
  esc.updateMatrixWorld(true)
  esc.traverse((o) => {
    if (/HeadTop_End$|mixamorig.?Head$|LeftHandIndex4$|RightHandIndex4$/.test(o.name) && o.isBone !== false) {
      const v = o.getWorldPosition(new o.position.constructor())
      out[o.name + '#' + Object.keys(out).length] = [+v.x.toFixed(4), +(-v.z).toFixed(4), +v.y.toFixed(4)] // back to Blender axes
    }
  })
  return out
})
console.log(JSON.stringify(r, null, 0))
await browser.close()

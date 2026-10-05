#!/usr/bin/env node
// Mide en un navegador real lo que baja el santuario. Entrada: hasta que la página marca el arranque de la
// cascada (`<html data-precarga="cascada">`) o, si nunca lo marca, hasta que la red se calma. Cascada: lo que
// baja después sin tocar nada. Gestos: cada PageDown hasta que la red se calma otra vez. Presupuesto del
// ticket 05: en móvil, entrada ≤ 3 MB y gesto ≤ 1 MB; cascada y escritorio sólo informan.
//
//   node scripts/medir-peso.mjs <url> [gestos=5]
//
// Usa el playwright global (npm i -g playwright). Mide la ruta de Chromium (AV1); la de Safari (HEVC) no se
// puede emular en Linux: se cuenta sumando archivos.
import { createRequire } from 'node:module'
import { execSync } from 'node:child_process'

const require = createRequire(import.meta.url)
const { chromium } = require(`${execSync('npm root -g').toString().trim()}/playwright`)

const [url, gestos = '5'] = process.argv.slice(2)
if (!url) { console.error('uso: node scripts/medir-peso.mjs <url> [gestos]'); process.exit(2) }
const MB = 1024 * 1024
const TECHO = { entrada: 3 * MB, gesto: 1 * MB }
const PERFILES = {
  movil: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 3 },
  escritorio: { viewport: { width: 1440, height: 900 } },
}

const navegador = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] })
let falla = false
for (const [nombre, perfil] of Object.entries(PERFILES)) {
  const pagina = await (await navegador.newContext(perfil)).newPage()
  const cdp = await pagina.context().newCDPSession(pagina)
  await cdp.send('Network.enable')
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true })
  // 4G de teléfono (9 Mbps, 40 ms): los bytes no cambian, pero sí cuándo llegan respecto a la marca de cascada.
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 40, downloadThroughput: 9e6 / 8, uploadThroughput: 2e6 / 8 })
  let bytes = 0, ultimo = Date.now()
  cdp.on('Network.dataReceived', (e) => { bytes += e.encodedDataLength; ultimo = Date.now() })
  cdp.on('Network.loadingFinished', () => { ultimo = Date.now() })

  // La red está calmada cuando pasan 3 s sin datos, contados desde el gesto: la precarga puede arrancar al acabar
  // la transición (2.5 s). Máximo 30 s: un video en streaming no se calma nunca.
  const cascada = () => pagina.evaluate(() => document.documentElement.dataset.precarga === 'cascada')
  const calma = async (hasta = async () => false, max = 30000) => {
    const t0 = ultimo = Date.now()
    while (Date.now() - ultimo < 3000 && Date.now() - t0 < max && !(await hasta())) await pagina.waitForTimeout(50)
    const antes = bytes; bytes = 0; return antes
  }

  await pagina.goto(url)
  const filas = [['entrada', await calma(cascada), TECHO.entrada]]
  if (await cascada()) filas.push(['cascada', await calma(undefined, 180000), Infinity])
  for (let i = 1; i <= +gestos; i++) {
    await pagina.keyboard.press('PageDown')
    filas.push([`gesto ${i}`, await calma(), TECHO.gesto])
  }

  console.log(`\n${nombre} ${perfil.viewport.width}×${perfil.viewport.height}`)
  for (const [que, b, techo] of filas) {
    const pasa = b <= techo
    if (nombre === 'movil' && !pasa) falla = true
    const juicio = nombre !== 'movil' || techo === Infinity ? '' : pasa ? 'OK' : `PASADO (techo ${techo / MB} MB)`
    console.log(`  ${que.padEnd(9)} ${(b / MB).toFixed(2).padStart(6)} MB  ${juicio}`)
  }
}
await navegador.close()
process.exit(falla ? 1 : 0)

import { expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { Glob } from 'bun'

// Workers Static Assets ignores Range and iOS Safari refuses a <video> without a 206 (worker.js header), so every .mp4 under
// public/ must be on a run_worker_first route, where worker.js answers the range itself.
test('cada .mp4 de public/ pasa por el Worker (rango)', () => {
  const config = JSON.parse(readFileSync(`${import.meta.dir}/../../wrangler.jsonc`, 'utf8').replace(/^\s*\/\/.*$/gm, ''))
  const rutas: string[] = config.assets.run_worker_first
  const raiz = `${import.meta.dir}/../../public`
  const fuera = [...new Glob('**/*.mp4').scanSync(raiz)]
    .map((f) => `/${f}`)
    .filter((f) => !rutas.some((r) => f.startsWith(r.replace(/\*$/, ''))))
  expect(fuera).toEqual([])
})

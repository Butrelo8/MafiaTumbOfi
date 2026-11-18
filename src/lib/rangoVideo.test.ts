import { expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { Glob } from 'bun'

// Workers Static Assets ignores Range and iOS Safari refuses a <video> without a 206 (worker.js header), so every .mp4 under
// public/ must be on a run_worker_first route, where worker.js answers the range itself.
const config = JSON.parse(readFileSync(`${import.meta.dir}/../../wrangler.jsonc`, 'utf8').replace(/^\s*\/\/.*$/gm, ''))
const rutas: RegExp[] = (config.assets.run_worker_first as string[])
  .filter((r) => !r.startsWith('!'))
  .map((r) => new RegExp(`^${r.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*')}$`)) // `*` matches deep, as Cloudflare's
const fuera = (urls: string[]) => urls.filter((u) => !rutas.some((r) => r.test(u)))

test('cada .mp4 de public/ pasa por el Worker (rango)', () => {
  const raiz = `${import.meta.dir}/../../public`
  expect(fuera([...new Glob('**/*.mp4').scanSync(raiz)].map((f) => `/${f}`))).toEqual([])
})

// public/vivo/ is git-ignored (2026-11-18: /vivo/pantalla.mp4 answered a Range with 200 on the preview), so also check every
// .mp4 URL the source asks for
test('cada .mp4 que pide src/ pasa por el Worker (rango)', () => {
  const urls = [...new Glob('**/*.{ts,astro}').scanSync(`${import.meta.dir}/..`)]
    .flatMap((f) => [...readFileSync(`${import.meta.dir}/../${f}`, 'utf8').matchAll(/['"`](\/[\w./-]+\.mp4)['"`]/g)].map((m) => m[1]))
  expect(urls).toContain('/vivo/pantalla.mp4')
  expect(fuera(urls)).toEqual([])
})

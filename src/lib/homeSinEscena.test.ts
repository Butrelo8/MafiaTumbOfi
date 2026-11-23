import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

// 2026-11-23: production's `/` is the Gótico home (was /anterior); the video cab is the hidden /cabina and the three.js scene the hidden /escena. `/` must never pull either.
describe('home `/`', () => {
  const home = readFileSync(new URL('../pages/index.astro', import.meta.url), 'utf8')
  const escena = readFileSync(new URL('../pages/escena.astro', import.meta.url), 'utf8')
  const cabina = readFileSync(new URL('../pages/cabina.astro', import.meta.url), 'utf8')

  test('does not import the scene, the cab, three.js or any GLB', () => {
    expect(home).not.toMatch(/vivoSecciones|escena\.ts|prototipo|three|\.glb|\/vivo\//)
  })
  test('is indexable; the scene and the cab are not', () => {
    expect(home).not.toMatch(/robots/)
    expect(escena).toMatch(/name="robots" content="noindex"/)
    expect(cabina).toMatch(/robots="noindex,nofollow"/)
  })
})

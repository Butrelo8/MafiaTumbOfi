import { describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'

// 2026-11-23: production's `/` is the video home; the three.js scene lives at the hidden /escena. `/` must never pull the scene.
describe('home `/`', () => {
  const home = readFileSync(new URL('../pages/index.astro', import.meta.url), 'utf8')
  const escena = readFileSync(new URL('../pages/escena.astro', import.meta.url), 'utf8')

  test('does not import the scene, three.js or any GLB', () => {
    expect(home).not.toMatch(/vivoSecciones|escena\.ts|three|\.glb|\/vivo\//)
  })
  test('is indexable; the scene is not', () => {
    expect(home).not.toMatch(/name="robots"/)
    expect(escena).toMatch(/name="robots" content="noindex"/)
  })
})

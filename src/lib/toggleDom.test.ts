import { expect, test } from 'bun:test'

// Needs the built page: `bun run build` first. Reproduces the bug where the hidden loop toggle stayed on screen
// (a scoped `display: inline-flex` beat the UA [hidden] rule), with the loop source failing and with JavaScript off.
test('el interruptor del loop está oculto sin JavaScript y cuando el video falla', () => {
  const r = Bun.spawnSync(['node', `${import.meta.dir}/../../scripts/toggle-dom-test.mjs`], { timeout: 90000 })
  const salida = r.stdout.toString() + r.stderr.toString()
  expect(salida).not.toContain('FAIL')
  expect(r.exitCode).toBe(0)
}, 100000)

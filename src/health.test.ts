import { afterEach, beforeEach, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { app } from './index'

const pkgPath = join(dirname(fileURLToPath(import.meta.url)), '..', 'package.json')
const expectedPkgVersion = (
  JSON.parse(readFileSync(pkgPath, 'utf-8')) as { version: string }
).version.trim()

let savedAppVersion: string | undefined
let savedReleaseVersion: string | undefined

beforeEach(() => {
  savedAppVersion = process.env.APP_VERSION
  savedReleaseVersion = process.env.RELEASE_VERSION
  delete process.env.APP_VERSION
  delete process.env.RELEASE_VERSION
})

afterEach(() => {
  if (savedAppVersion === undefined) delete process.env.APP_VERSION
  else process.env.APP_VERSION = savedAppVersion
  if (savedReleaseVersion === undefined) delete process.env.RELEASE_VERSION
  else process.env.RELEASE_VERSION = savedReleaseVersion
})

test('GET /health returns 200, status ok, and package.json version', async () => {
  const res = await app.request('/health')
  expect(res.status).toBe(200)
  const data = (await res.json()) as { status: string; version: string }
  expect(data.status).toBe('ok')
  expect(data.version).toBe(expectedPkgVersion)
})

test('GET /health uses APP_VERSION when set', async () => {
  process.env.APP_VERSION = 'deploy-sha'
  const res = await app.request('/health')
  const data = (await res.json()) as { version: string }
  expect(data.version).toBe('deploy-sha')
})

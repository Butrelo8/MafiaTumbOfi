import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { getAppVersion } from './appVersion'

const pkgPath = join(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  'package.json',
)
const expectedPkgVersion = (
  JSON.parse(readFileSync(pkgPath, 'utf-8')) as { version: string }
).version.trim()

describe('getAppVersion', () => {
  let savedApp: string | undefined
  let savedRelease: string | undefined

  beforeEach(() => {
    savedApp = process.env.APP_VERSION
    savedRelease = process.env.RELEASE_VERSION
    delete process.env.APP_VERSION
    delete process.env.RELEASE_VERSION
  })

  afterEach(() => {
    if (savedApp === undefined) delete process.env.APP_VERSION
    else process.env.APP_VERSION = savedApp
    if (savedRelease === undefined) delete process.env.RELEASE_VERSION
    else process.env.RELEASE_VERSION = savedRelease
  })

  test('returns package.json version when overrides unset', () => {
    expect(getAppVersion()).toBe(expectedPkgVersion)
  })

  test('prefers APP_VERSION when set', () => {
    process.env.APP_VERSION = 'ci-abc123'
    expect(getAppVersion()).toBe('ci-abc123')
  })

  test('prefers APP_VERSION over RELEASE_VERSION when both set', () => {
    process.env.APP_VERSION = 'from-app'
    process.env.RELEASE_VERSION = 'from-release'
    expect(getAppVersion()).toBe('from-app')
  })

  test('uses RELEASE_VERSION when APP_VERSION unset', () => {
    process.env.RELEASE_VERSION = 'rel-only'
    expect(getAppVersion()).toBe('rel-only')
  })

  test('trims whitespace on override vars', () => {
    process.env.APP_VERSION = '  trimmed  '
    expect(getAppVersion()).toBe('trimmed')
  })
})

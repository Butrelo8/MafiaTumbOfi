import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { getWebAppVersion } from './webAppVersion'

const webPkgPath = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'package.json')
const expectedWebPkgVersion = (
  JSON.parse(readFileSync(webPkgPath, 'utf-8')) as { version: string }
).version.trim()

describe('getWebAppVersion', () => {
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

  test('returns web/package.json version when overrides unset', () => {
    expect(getWebAppVersion()).toBe(expectedWebPkgVersion)
  })

  test('prefers APP_VERSION when set', () => {
    process.env.APP_VERSION = 'web-ci-abc'
    expect(getWebAppVersion()).toBe('web-ci-abc')
  })

  test('prefers APP_VERSION over RELEASE_VERSION when both set', () => {
    process.env.APP_VERSION = 'from-app'
    process.env.RELEASE_VERSION = 'from-release'
    expect(getWebAppVersion()).toBe('from-app')
  })

  test('uses RELEASE_VERSION when APP_VERSION unset', () => {
    process.env.RELEASE_VERSION = 'rel-only'
    expect(getWebAppVersion()).toBe('rel-only')
  })

  test('trims whitespace on override vars', () => {
    process.env.APP_VERSION = '  trimmed  '
    expect(getWebAppVersion()).toBe('trimmed')
  })
})

import { afterEach, describe, expect, test } from 'bun:test'
import { defaultBunSqlitePath, detectDbMode } from './detect'

describe('detectDbMode', () => {
  const base = { ...process.env }

  afterEach(() => {
    process.env = { ...base }
  })

  test('libsql remote when Turso env set and DB_PATH unset', () => {
    process.env = {
      ...base,
      TURSO_DATABASE_URL: 'libsql://db-org.turso.io',
      TURSO_AUTH_TOKEN: 'tok',
      DB_PATH: '',
    }
    delete process.env.DB_PATH
    expect(detectDbMode()).toEqual({
      mode: 'libsql',
      url: 'libsql://db-org.turso.io',
      authToken: 'tok',
    })
  })

  test('libsql embedded replica when Turso env and DB_PATH set', () => {
    process.env = {
      ...base,
      TURSO_DATABASE_URL: 'libsql://db-org.turso.io',
      TURSO_AUTH_TOKEN: 'tok',
      DB_PATH: './data/local.db',
    }
    expect(detectDbMode()).toEqual({
      mode: 'libsql',
      url: 'libsql://db-org.turso.io',
      authToken: 'tok',
      replicaLocalPath: './data/local.db',
    })
  })

  test('trims Turso env values', () => {
    process.env = {
      ...base,
      TURSO_DATABASE_URL: '  libsql://x.turso.io  ',
      TURSO_AUTH_TOKEN: '  secret  ',
    }
    delete process.env.DB_PATH
    expect(detectDbMode()).toEqual({
      mode: 'libsql',
      url: 'libsql://x.turso.io',
      authToken: 'secret',
    })
  })

  test('bun-sqlite when Turso URL missing', () => {
    process.env = { ...base, TURSO_AUTH_TOKEN: 'only-token' }
    delete process.env.TURSO_DATABASE_URL
    delete process.env.DB_PATH
    expect(detectDbMode()).toEqual({ mode: 'bun-sqlite', path: defaultBunSqlitePath() })
  })

  test('bun-sqlite when Turso token missing', () => {
    process.env = { ...base, TURSO_DATABASE_URL: 'libsql://x.turso.io' }
    delete process.env.TURSO_AUTH_TOKEN
    delete process.env.DB_PATH
    expect(detectDbMode()).toEqual({ mode: 'bun-sqlite', path: defaultBunSqlitePath() })
  })

  test('bun-sqlite uses DB_PATH when Turso unset', () => {
    process.env = { ...base, DB_PATH: '/tmp/test.db' }
    delete process.env.TURSO_DATABASE_URL
    delete process.env.TURSO_AUTH_TOKEN
    expect(detectDbMode()).toEqual({ mode: 'bun-sqlite', path: '/tmp/test.db' })
  })

  test('explicit env object does not read process.env', () => {
    const missing = detectDbMode({})
    expect(missing).toEqual({ mode: 'bun-sqlite', path: defaultBunSqlitePath() })
  })
})

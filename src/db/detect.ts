import { join, resolve } from 'node:path'

function trimEnv(env: NodeJS.ProcessEnv, key: string): string | undefined {
  const raw = env[key]
  if (raw == null) return undefined
  const t = raw.trim()
  return t === '' ? undefined : t
}

export type DbMode =
  | { mode: 'libsql'; url: string; authToken: string; replicaLocalPath?: string }
  | { mode: 'bun-sqlite'; path: string }

/**
 * Default SQLite file path (project `data/sqlite.db`), stable regardless of `process.cwd()`.
 */
export function defaultBunSqlitePath(): string {
  return resolve(join(import.meta.dir, '..', '..', 'data', 'sqlite.db'))
}

/**
 * Resolves how the app connects to SQLite / libsql:
 * - **libsql remote:** `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN`, no `DB_PATH` (e.g. Render).
 * - **libsql embedded replica:** same Turso env + `DB_PATH` → local file syncs from remote (local dev).
 * - **bun:sqlite file:** no Turso env → `DB_PATH` or default `data/sqlite.db` (tests, offline dev).
 */
export function detectDbMode(env: NodeJS.ProcessEnv = process.env): DbMode {
  const url = trimEnv(env, 'TURSO_DATABASE_URL')
  const authToken = trimEnv(env, 'TURSO_AUTH_TOKEN')
  const dbPath = trimEnv(env, 'DB_PATH')

  if (url && authToken) {
    if (dbPath) {
      return { mode: 'libsql', url, authToken, replicaLocalPath: dbPath }
    }
    return { mode: 'libsql', url, authToken }
  }

  return { mode: 'bun-sqlite', path: dbPath ?? defaultBunSqlitePath() }
}

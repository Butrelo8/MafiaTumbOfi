/**
 * Exits with code 1 if the DB is missing required tables (users, bookings).
 * Use after migrate in startCommand so the app never starts with an empty DB.
 */

import { Database } from 'bun:sqlite'
import { existsSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createClient } from '@libsql/client'
import { detectDbMode } from '../src/db/detect'
import { findMissingTables } from '../src/lib/findMissingTables'

const REQUIRED_TABLES = ['users', 'bookings'] as const

async function main(): Promise<void> {
  const mode = detectDbMode()

  if (mode.mode === 'libsql') {
    const client =
      mode.replicaLocalPath != null
        ? (() => {
            const p = mode.replicaLocalPath
            const dir = dirname(p)
            if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
            return createClient({
              url: pathToFileURL(p).href,
              syncUrl: mode.url,
              authToken: mode.authToken,
            })
          })()
        : createClient({
            url: mode.url,
            authToken: mode.authToken,
          })

    try {
      const missing = await findMissingTables(async (sql, args) => {
        const r = await client.execute({
          sql,
          args: args as (string | number | bigint | boolean | null)[],
        })
        return r.rows[0] as unknown | undefined
      }, REQUIRED_TABLES)

      if (missing.length) {
        console.error(
          `[check-db] Required tables missing: ${missing.map((t) => `"${t}"`).join(', ')}.\n` +
            'Ensure the Start Command is "bun run migrate && bun run check-db && bun run start" ' +
            'and Turso env vars are set (or DB_PATH for file SQLite), then redeploy.',
        )
        process.exit(1)
      }
    } finally {
      client.close()
    }

    console.log('[check-db] OK — all required tables present.')
    return
  }

  const dbPath = mode.path
  const db = new Database(dbPath)
  try {
    const missing = await findMissingTables(async (sql, args) => {
      const stmt = db.query(sql)
      return stmt.get(args[0] as string) as unknown | undefined
    }, REQUIRED_TABLES)

    if (missing.length) {
      console.error(
        `[check-db] Required tables missing: ${missing.map((t) => `"${t}"`).join(', ')}.\n` +
          'Ensure the Start Command is "bun run migrate && bun run check-db && bun run start" ' +
          'and DB_PATH is set (e.g. /data/sqlite.db on Render with file SQLite), then redeploy.',
      )
      process.exit(1)
    }
  } finally {
    db.close()
  }

  console.log('[check-db] OK — all required tables present.')
}

await main()

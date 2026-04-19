import { Database } from 'bun:sqlite'
import { existsSync, mkdirSync, readdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createClient } from '@libsql/client'
import { detectDbMode } from '../src/db/detect'

function isIdempotentSqliteError(msg: string): boolean {
  return msg.includes('already exists') || msg.includes('duplicate column name')
}

async function main(): Promise<void> {
  const root = join(import.meta.dir, '..')
  const drizzleDir = join(root, 'drizzle')
  const files = readdirSync(drizzleDir)
    .filter((f) => f.endsWith('.sql'))
    .sort()

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

    const label = mode.replicaLocalPath != null ? `replica ${mode.replicaLocalPath}` : 'remote'
    console.log('[migrate] libsql:', label)

    try {
      for (const file of files) {
        const sql = readFileSync(join(drizzleDir, file), 'utf8')
        const statements = sql
          .split('--> statement-breakpoint')
          .map((s) => s.trim())
          .filter(Boolean)
        for (const st of statements) {
          try {
            await client.execute(st)
          } catch (e: unknown) {
            const err = e as { message?: string }
            const msg = err.message ?? ''
            if (!isIdempotentSqliteError(msg)) throw e
          }
        }
        console.log(`Applied ${file}`)
      }
    } finally {
      client.close()
    }
    console.log('Migrations complete.')
    return
  }

  const dbPath = mode.path
  console.log('[migrate] DB_PATH:', dbPath)
  const dir = dirname(dbPath)
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }

  const db = new Database(dbPath)
  try {
    for (const file of files) {
      const sql = readFileSync(join(drizzleDir, file), 'utf8')
      const statements = sql
        .split('--> statement-breakpoint')
        .map((s) => s.trim())
        .filter(Boolean)
      for (const st of statements) {
        try {
          db.run(st)
        } catch (e: unknown) {
          const err = e as { message?: string }
          const msg = err.message ?? ''
          if (!isIdempotentSqliteError(msg)) throw e
        }
      }
      console.log(`Applied ${file}`)
    }
  } finally {
    db.close()
  }
  console.log('Migrations complete.')
}

await main()

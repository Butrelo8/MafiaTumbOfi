import { Database } from 'bun:sqlite'
import { existsSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createClient } from '@libsql/client'
import { drizzle as drizzleBun } from 'drizzle-orm/bun-sqlite'
import { drizzle as drizzleLibsql } from 'drizzle-orm/libsql'
import { detectDbMode } from './detect'
import * as schema from './schema'

function createDatabase() {
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
    return drizzleLibsql(client, { schema })
  }

  const dir = dirname(mode.path)
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }
  const sqlite = new Database(mode.path)
  return drizzleBun(sqlite, { schema })
}

export const db = createDatabase()

import { mkdirSync, existsSync } from 'fs'
import { dirname } from 'path'
import { drizzle } from 'drizzle-orm/bun-sqlite'
import { Database } from 'bun:sqlite'
import * as schema from './schema'

const dbPath = process.env.DB_PATH ?? './data/sqlite.db'
const dir = dirname(dbPath)
if (!existsSync(dir)) {
  mkdirSync(dir, { recursive: true })
}
const sqlite = new Database(dbPath)

export const db = drizzle(sqlite, { schema })

/**
 * Exits with code 1 if the DB is missing required tables (users, bookings).
 * Use after migrate in startCommand so the app never starts with an empty DB.
 */
import { join } from 'path'
import { Database } from 'bun:sqlite'
import { findMissingSqliteTables } from '../src/lib/findMissingSqliteTables'

const root = join(import.meta.dir, '..')
const dbPath = process.env.DB_PATH ?? join(root, 'data', 'sqlite.db')

const REQUIRED_TABLES = ['users', 'bookings'] as const

const db = new Database(dbPath)
const missing = findMissingSqliteTables(db, REQUIRED_TABLES)
db.close()

if (missing.length) {
  console.error(
    `[check-db] Required tables missing: ${missing.map((t) => `"${t}"`).join(', ')}.\n` +
      'Ensure the Start Command is "bun run migrate && bun run check-db && bun run start" ' +
      'and DB_PATH is set (e.g. /data/sqlite.db on Render), then redeploy.',
  )
  process.exit(1)
}

console.log('[check-db] OK — all required tables present.')

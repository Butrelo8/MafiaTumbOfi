/**
 * Exits with code 1 if the DB is missing required tables (e.g. users).
 * Use after migrate in startCommand so the app never starts with an empty DB.
 */
import { join } from 'path'
import { Database } from 'bun:sqlite'

const root = join(import.meta.dir, '..')
const dbPath = process.env.DB_PATH ?? join(root, 'data', 'sqlite.db')

const db = new Database(dbPath)
const row = db.query("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'").get()
db.close()

if (!row) {
  console.error(
    '[check-db] Table "users" not found. Ensure Start Command is "bun run migrate && bun run start" and DB_PATH is set (e.g. /data/sqlite.db on Render), then redeploy.'
  )
  process.exit(1)
}

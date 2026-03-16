import { readFileSync, mkdirSync, existsSync, readdirSync } from 'fs'
import { dirname, join } from 'path'
import { Database } from 'bun:sqlite'

const root = join(import.meta.dir, '..')
const dbPath = process.env.DB_PATH ?? join(root, 'data', 'sqlite.db')
console.log('[migrate] DB_PATH:', dbPath)
const dir = dirname(dbPath)
if (!existsSync(dir)) {
  mkdirSync(dir, { recursive: true })
}

const db = new Database(dbPath)
const drizzleDir = join(root, 'drizzle')
const files = readdirSync(drizzleDir)
  .filter((f) => f.endsWith('.sql'))
  .sort()

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
      const isIdempotent =
        msg.includes('already exists') || msg.includes('duplicate column name')
      if (!isIdempotent) throw e
    }
  }
  console.log(`Applied ${file}`)
}

db.close()
console.log('Migrations complete.')

import type { Database } from 'bun:sqlite'

const TABLE_EXISTS_SQL = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"

/**
 * Returns table names from `names` that are absent in `sqlite_master`.
 */
export function findMissingSqliteTables(db: Database, names: readonly string[]): string[] {
  const stmt = db.query(TABLE_EXISTS_SQL)
  return names.filter((name) => stmt.get(name) == null)
}

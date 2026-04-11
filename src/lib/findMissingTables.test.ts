import { Database } from 'bun:sqlite'
import { describe, expect, test } from 'bun:test'
import { findMissingTables } from './findMissingTables'

const REQUIRED = ['users', 'bookings'] as const

function bunSqliteGetFirstRow(db: Database) {
  return async (sql: string, args: readonly unknown[]) => {
    const stmt = db.query(sql)
    return stmt.get(args[0] as string) as unknown | undefined
  }
}

describe('findMissingTables', () => {
  test('reports all names when DB has no tables', async () => {
    const db = new Database(':memory:')
    try {
      const missing = await findMissingTables(bunSqliteGetFirstRow(db), REQUIRED)
      expect(missing).toEqual(['users', 'bookings'])
    } finally {
      db.close()
    }
  })

  test('reports only bookings when users exists', async () => {
    const db = new Database(':memory:')
    try {
      db.run('CREATE TABLE users (id INTEGER PRIMARY KEY)')
      const missing = await findMissingTables(bunSqliteGetFirstRow(db), REQUIRED)
      expect(missing).toEqual(['bookings'])
    } finally {
      db.close()
    }
  })

  test('returns empty when all names exist', async () => {
    const db = new Database(':memory:')
    try {
      db.run('CREATE TABLE users (id INTEGER PRIMARY KEY)')
      db.run('CREATE TABLE bookings (id INTEGER PRIMARY KEY)')
      const missing = await findMissingTables(bunSqliteGetFirstRow(db), REQUIRED)
      expect(missing).toEqual([])
    } finally {
      db.close()
    }
  })

  test('empty names list yields empty missing', async () => {
    const db = new Database(':memory:')
    try {
      const missing = await findMissingTables(bunSqliteGetFirstRow(db), [])
      expect(missing).toEqual([])
    } finally {
      db.close()
    }
  })
})

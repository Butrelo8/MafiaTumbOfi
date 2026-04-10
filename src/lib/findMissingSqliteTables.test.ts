import { describe, expect, test } from 'bun:test'
import { Database } from 'bun:sqlite'
import { findMissingSqliteTables } from './findMissingSqliteTables'

const REQUIRED = ['users', 'bookings'] as const

describe('findMissingSqliteTables', () => {
  test('reports all names when DB has no tables', () => {
    const db = new Database(':memory:')
    try {
      expect(findMissingSqliteTables(db, REQUIRED)).toEqual(['users', 'bookings'])
    } finally {
      db.close()
    }
  })

  test('reports only bookings when users exists', () => {
    const db = new Database(':memory:')
    try {
      db.run('CREATE TABLE users (id INTEGER PRIMARY KEY)')
      expect(findMissingSqliteTables(db, REQUIRED)).toEqual(['bookings'])
    } finally {
      db.close()
    }
  })

  test('returns empty when all names exist', () => {
    const db = new Database(':memory:')
    try {
      db.run('CREATE TABLE users (id INTEGER PRIMARY KEY)')
      db.run('CREATE TABLE bookings (id INTEGER PRIMARY KEY)')
      expect(findMissingSqliteTables(db, REQUIRED)).toEqual([])
    } finally {
      db.close()
    }
  })

  test('empty names list yields empty missing', () => {
    const db = new Database(':memory:')
    try {
      expect(findMissingSqliteTables(db, [])).toEqual([])
    } finally {
      db.close()
    }
  })
})

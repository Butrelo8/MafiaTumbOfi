import { defineConfig } from 'drizzle-kit'

const tursoUrl = process.env.TURSO_DATABASE_URL?.trim()
const tursoToken = process.env.TURSO_AUTH_TOKEN?.trim()
const useTurso = Boolean(tursoUrl && tursoToken)

export default defineConfig(
  useTurso
    ? {
        schema: './src/db/schema.ts',
        out: './drizzle',
        dialect: 'sqlite',
        driver: 'turso',
        dbCredentials: {
          url: tursoUrl!,
          authToken: tursoToken,
        },
      }
    : {
        schema: './src/db/schema.ts',
        out: './drizzle',
        dialect: 'sqlite',
        dbCredentials: {
          url: process.env.DB_PATH ?? './data/sqlite.db',
        },
      },
)

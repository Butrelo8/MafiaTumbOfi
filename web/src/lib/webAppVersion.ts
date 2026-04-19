import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

/** `web/package.json` (this Astro app), not the root API package. */
const webPackageJsonPath = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'package.json')

function readWebPackageJsonVersion(): string {
  const raw = readFileSync(webPackageJsonPath, 'utf-8')
  const parsed: unknown = JSON.parse(raw)
  if (
    typeof parsed !== 'object' ||
    parsed === null ||
    !('version' in parsed) ||
    typeof (parsed as { version: unknown }).version !== 'string' ||
    (parsed as { version: string }).version.trim().length === 0
  ) {
    throw new Error('web/package.json is missing a non-empty string "version"')
  }
  return (parsed as { version: string }).version.trim()
}

const webPackageJsonVersion = readWebPackageJsonVersion()

/**
 * Version for frontend GET /health and GET /api/health.
 * Override with APP_VERSION or RELEASE_VERSION (e.g. git SHA in CI), same semantics as the API `getAppVersion`.
 */
export function getWebAppVersion(): string {
  const fromApp = process.env.APP_VERSION?.trim()
  if (fromApp) return fromApp
  const fromRelease = process.env.RELEASE_VERSION?.trim()
  if (fromRelease) return fromRelease
  return webPackageJsonVersion
}

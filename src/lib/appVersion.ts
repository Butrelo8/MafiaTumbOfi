import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const packageJsonPath = join(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  'package.json',
)

function readPackageJsonVersion(): string {
  const raw = readFileSync(packageJsonPath, 'utf-8')
  const parsed: unknown = JSON.parse(raw)
  if (
    typeof parsed !== 'object' ||
    parsed === null ||
    !('version' in parsed) ||
    typeof (parsed as { version: unknown }).version !== 'string' ||
    (parsed as { version: string }).version.trim().length === 0
  ) {
    throw new Error('package.json is missing a non-empty string "version"')
  }
  return (parsed as { version: string }).version.trim()
}

const packageJsonVersion = readPackageJsonVersion()

/**
 * Version exposed by GET /health. Override with APP_VERSION or RELEASE_VERSION
 * (e.g. git SHA in CI) so deploys need not edit package.json.
 */
export function getAppVersion(): string {
  const fromApp = process.env.APP_VERSION?.trim()
  if (fromApp) return fromApp
  const fromRelease = process.env.RELEASE_VERSION?.trim()
  if (fromRelease) return fromRelease
  return packageJsonVersion
}

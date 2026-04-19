const TABLE_EXISTS_SQL = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"

export type GetFirstRow = (sql: string, args: readonly unknown[]) => Promise<unknown | undefined>

/**
 * Returns table names from `names` absent in `sqlite_master` (parameterized query).
 */
export async function findMissingTables(
  getFirstRow: GetFirstRow,
  names: readonly string[],
): Promise<string[]> {
  const missing: string[] = []
  for (const name of names) {
    const row = await getFirstRow(TABLE_EXISTS_SQL, [name])
    if (row == null) missing.push(name)
  }
  return missing
}

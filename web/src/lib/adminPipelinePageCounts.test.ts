import { describe, expect, test } from 'bun:test'
import { pipelineCountsForAdminRows } from './adminPipelinePageCounts'

describe('pipelineCountsForAdminRows', () => {
  test('empty list yields zeros', () => {
    expect(pipelineCountsForAdminRows([])).toEqual({
      new: 0,
      contacted: 0,
      closed: 0,
    })
  })

  test('counts each status and defaults unknown to new', () => {
    expect(
      pipelineCountsForAdminRows([
        { pipelineStatus: 'new' },
        { pipelineStatus: 'contacted' },
        { pipelineStatus: 'closed' },
        { pipelineStatus: null },
        { pipelineStatus: 'garbage' },
      ]),
    ).toEqual({ new: 3, contacted: 1, closed: 1 })
  })
})

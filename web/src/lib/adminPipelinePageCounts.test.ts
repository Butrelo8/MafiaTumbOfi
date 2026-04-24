import { describe, expect, test } from 'bun:test'
import {
  leadPriorityCountsForAdminRows,
  pipelineCountsForAdminRows,
} from './adminPipelinePageCounts'

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

describe('leadPriorityCountsForAdminRows', () => {
  test('empty list yields zeros', () => {
    expect(leadPriorityCountsForAdminRows([])).toEqual({ high: 0, medium: 0, low: 0 })
  })

  test('counts only valid stored priorities', () => {
    expect(
      leadPriorityCountsForAdminRows([
        { leadPriority: 'high' },
        { leadPriority: 'medium' },
        { leadPriority: 'low' },
        { leadPriority: null },
        { leadPriority: 'nope' },
      ]),
    ).toEqual({ high: 1, medium: 1, low: 1 })
  })
})

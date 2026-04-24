import { and, asc, gte, inArray } from 'drizzle-orm'
import { Hono } from 'hono'
import type { TourDateRow } from '../data/tourDates'
import { db } from '../db'
import { tourDates } from '../db/schema'
import { successResponse } from '../lib/errors'

export const toursRoutes = new Hono()

/** UTC calendar date `YYYY-MM-DD` for DB comparisons (stored dates are plain dates). */
function todayIsoDateUtc(): string {
  return new Date().toISOString().slice(0, 10)
}

function mapDbRowToTourDateRow(row: typeof tourDates.$inferSelect): TourDateRow {
  const ticket = row.ticketUrl?.trim() || null
  const cta = ticket
    ? { label: row.soldOut ? 'Agotado' : 'Boletos', href: ticket }
    : { label: 'Contratar', href: '/contratacion' }
  const out: TourDateRow = {
    date: row.date,
    city: row.city,
    venue: row.venue,
    cta,
  }
  if (row.soldOut) out.soldOut = true
  return out
}

toursRoutes.get('/tours/upcoming', async (c) => {
  c.header('Cache-Control', 'public, max-age=60, s-maxage=300')
  const today = todayIsoDateUtc()
  try {
    const rows = await db
      .select()
      .from(tourDates)
      .where(and(gte(tourDates.date, today), inArray(tourDates.status, ['confirmed', 'tentative'])))
      .orderBy(asc(tourDates.date))

    if (rows.length === 0) {
      return successResponse(c, [] as TourDateRow[])
    }
    return successResponse(c, rows.map(mapDbRowToTourDateRow))
  } catch {
    return successResponse(c, [] as TourDateRow[])
  }
})

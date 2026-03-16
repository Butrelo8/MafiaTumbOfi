import { Hono } from 'hono'
import { desc } from 'drizzle-orm'
import { authMiddleware } from '../middleware/auth'
import { adminAuth } from '../middleware/adminAuth'
import { errorResponse } from '../lib/errors'
import { db } from '../db'
import { bookings } from '../db/schema'

export const adminRoutes = new Hono()

adminRoutes.use('*', authMiddleware)
adminRoutes.use('*', adminAuth)

adminRoutes.get('/bookings', async (c) => {
  try {
    const allBookings = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))

    return c.json({
      data: allBookings,
      total: allBookings.length,
    })
  } catch (error) {
    console.error('Failed to fetch bookings:', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to fetch bookings')
  }
})

/** Admin-only export for debugging: full booking list + counts. Use to verify production data (e.g. missing submissions). */
adminRoutes.get('/export/bookings', async (c) => {
  try {
    const allBookings = await db
      .select()
      .from(bookings)
      .orderBy(desc(bookings.createdAt))

    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
    const last24h = allBookings.filter((b) => b.createdAt && b.createdAt >= oneDayAgo)

    return c.json({
      exportedAt: new Date().toISOString(),
      total: allBookings.length,
      last24hCount: last24h.length,
      bookings: allBookings,
    })
  } catch (error) {
    console.error('Failed to export bookings:', error)
    return errorResponse(c, 500, 'INTERNAL_ERROR', 'Failed to export bookings')
  }
})

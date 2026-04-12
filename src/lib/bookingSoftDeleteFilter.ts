import { isNull } from 'drizzle-orm'
import { bookings } from '../db/schema'

/** Use in `where(...)` so soft-deleted bookings stay hidden from operators and automation. */
export const bookingNotSoftDeleted = isNull(bookings.deletedAt)

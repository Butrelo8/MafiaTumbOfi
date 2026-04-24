import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  clerkId: text('clerk_id').notNull().unique(),
  email: text('email').notNull().unique(),
  name: text('name'),
  isAdmin: integer('is_admin', { mode: 'boolean' }).notNull().default(false),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .$defaultFn(() => new Date())
    .$onUpdateFn(() => new Date()),
})

export const bookings = sqliteTable('bookings', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
  email: text('email').notNull(),
  phone: text('phone'),
  eventDate: text('event_date'),
  city: text('city'),
  eventType: text('event_type'),
  duration: text('duration'),
  showType: text('show_type'),
  attendees: text('attendees'),
  venueSound: text('venue_sound'),
  budget: text('budget'),
  /** 0–1000; computed once at booking insert (`computeBookingLeadScore`). */
  leadScore: integer('lead_score'),
  /** `low` | `medium` | `high`; derived from `lead_score` bands at insert. */
  leadPriority: text('lead_priority'),
  message: text('message'),
  /** Follow-up: `new` | `contacted` | `closed` — not email delivery; see `status`. */
  pipelineStatus: text('pipeline_status').notNull().default('new'),
  status: text('status').notNull().default('pending'),
  confirmationLastError: text('confirmation_last_error'),
  confirmationAttempts: integer('confirmation_attempts').notNull().default(0),
  /** When Email 2 (nurture) should send; set at insert from `createdAt` + delay. */
  drip2DueAt: integer('drip2_due_at', { mode: 'timestamp' }),
  drip2SentAt: integer('drip2_sent_at', { mode: 'timestamp' }),
  /** When Email 3 (urgency) should send; set at insert from `createdAt` + delay. */
  drip3DueAt: integer('drip3_due_at', { mode: 'timestamp' }),
  drip3SentAt: integer('drip3_sent_at', { mode: 'timestamp' }),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
  /** Staff-only notes; never shown to the lead. */
  internalNotes: text('internal_notes'),
  /** When set, row is hidden from admin list/export and follow-up actions. */
  deletedAt: integer('deleted_at', { mode: 'timestamp' }),
})

export const tourDates = sqliteTable('tour_dates', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  date: text('date').notNull(),
  time: text('time'),
  city: text('city').notNull(),
  venue: text('venue').notNull(),
  status: text('status').notNull().default('confirmed'),
  ticketUrl: text('ticket_url'),
  soldOut: integer('sold_out', { mode: 'boolean' }).notNull().default(false),
  internalNotes: text('internal_notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .$defaultFn(() => new Date())
    .$onUpdateFn(() => new Date()),
})

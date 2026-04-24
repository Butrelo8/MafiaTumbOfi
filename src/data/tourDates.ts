/** Public tour row for `GET /api/tours/upcoming` (from DB only; empty array when none). */
export type TourDateRow = {
  /** ISO date (YYYY-MM-DD) or custom label string */
  date: string
  city: string
  venue: string
  cta: { label: string; href: string }
  soldOut?: boolean
}

/** Full row for admin panel (`GET /api/admin/tours`). */
export type AdminTourRow = {
  id: number
  date: string
  time: string | null
  city: string
  venue: string
  status: 'confirmed' | 'tentative' | 'cancelled'
  ticketUrl: string | null
  soldOut: boolean
  notes: string | null
}

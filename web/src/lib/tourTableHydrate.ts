import type { TourDateRow } from '../data/tourDates'
import { formatTourDateLabel } from './tourDateDisplay'

const EMPTY_MESSAGE = 'No hay fechas anunciadas por ahora.'

function buildEmptyRow(): HTMLTableRowElement {
  const tr = document.createElement('tr')
  tr.className = 'tour-table__empty'
  const td = document.createElement('td')
  td.colSpan = 4
  td.textContent = EMPTY_MESSAGE
  tr.appendChild(td)
  return tr
}

function buildRow(row: TourDateRow): HTMLTableRowElement {
  const tr = document.createElement('tr')
  if (row.soldOut) tr.classList.add('tour-table__soldout')

  const tdDate = document.createElement('td')
  tdDate.className = 'tour-table__date'
  tdDate.textContent = formatTourDateLabel(row.date)

  const tdCity = document.createElement('td')
  tdCity.textContent = row.city

  const tdVenue = document.createElement('td')
  tdVenue.textContent = row.venue

  const tdCta = document.createElement('td')
  tdCta.className = 'tour-table__cta'
  if (row.soldOut) {
    const span = document.createElement('span')
    span.className = 'tour-tag-soldout'
    span.textContent = 'SOLD OUT'
    tdCta.append(span)
  } else {
    const a = document.createElement('a')
    a.href = row.cta.href
    a.className = 'tour-ticket-btn'
    a.setAttribute('data-analytics-venue', row.venue)
    a.textContent = row.cta.label
    tdCta.append(a)
  }

  tr.append(tdDate, tdCity, tdVenue, tdCta)
  return tr
}

/**
 * After paint, replace tbody with GET /api/tours/upcoming payload when available.
 * Covers cases where SSR fetch failed (e.g. missing/wrong PUBLIC_API_URL on the server).
 */
export async function hydrateTourTablesFromApi(): Promise<void> {
  const wraps = document.querySelectorAll<HTMLElement>('[data-tour-upcoming-api]')
  await Promise.all(
    [...wraps].map(async (wrap) => {
      const url = wrap.dataset.tourUpcomingApi?.trim()
      if (!url) return
      try {
        const res = await fetch(url, { headers: { Accept: 'application/json' } })
        if (!res.ok) return
        const json = (await res.json()) as { data?: TourDateRow[] }
        const rows = json.data
        if (!Array.isArray(rows)) return
        const tbody = wrap.querySelector('tbody')
        if (!tbody) return
        if (rows.length === 0) {
          tbody.replaceChildren(buildEmptyRow())
          return
        }
        tbody.replaceChildren(...rows.map((r) => buildRow(r)))
      } catch {
        /* keep SSR markup */
      }
    }),
  )
}

export interface EstimatePriceInput {
  city?: string | null
  duration?: string | null
  attendees?: string | null
}

export const PRICE_CONSTANTS = {
  // Base price for a local, 1h show, <100 attendees
  baseLow: 15000,
  baseHigh: 25000,

  // Surcharge for non-local cities
  travelSurchargeLow: 5000,
  travelSurchargeHigh: 10000,

  // Cities considered "local" (case-insensitive)
  localCities: new Set([
    'monterrey',
    'san pedro',
    'san pedro garza garcia',
    'san pedro garza garcía',
    'santa catarina',
    'guadalupe',
    'apodaca',
    'escobedo',
    'general escobedo',
    'san nicolas',
    'san nicolás',
    'san nicolas de los garza',
    'san nicolás de los garza',
    'juarez',
    'juárez',
    'garcia',
    'garcía',
    'santiago',
  ]),

  // Duration multipliers: mapped from the form values
  durationMultipliers: {
    '1h': { low: 1.0, high: 1.0 },
    '2h': { low: 1.8, high: 1.8 },
    '3h_mas': { low: 2.5, high: 2.5 },
    no_definido: { low: 1.0, high: 2.0 },
  } as Record<string, { low: number; high: number }>,

  // Attendees multipliers: mapped from the form values
  attendeesMultipliers: {
    menos_100: { low: 1.0, high: 1.0 },
    '100_300': { low: 1.1, high: 1.2 },
    '300_500': { low: 1.2, high: 1.4 },
    '500_1000': { low: 1.4, high: 1.6 },
    mas_1000: { low: 1.6, high: 2.0 },
  } as Record<string, { low: number; high: number }>,
}

function normalizeCity(city?: string | null): string {
  return (city || '').trim().toLowerCase()
}

function formatRange(low: number, high: number): string {
  const lowK = Math.round(low / 1000)
  const highK = Math.round(high / 1000)

  if (lowK === highK) {
    return `${lowK}k MXN`
  }
  return `${lowK}k – ${highK}k MXN`
}

export function estimatedPriceRange(input: EstimatePriceInput): string {
  // If we have absolutely no inputs, we can't provide a meaningful estimate
  if (!input.city && !input.duration && !input.attendees) {
    return '-'
  }

  const cityNorm = normalizeCity(input.city)
  const isLocal = !cityNorm || PRICE_CONSTANTS.localCities.has(cityNorm)

  const travelLow = isLocal ? 0 : PRICE_CONSTANTS.travelSurchargeLow
  const travelHigh = isLocal ? 0 : PRICE_CONSTANTS.travelSurchargeHigh

  const durationMult = PRICE_CONSTANTS.durationMultipliers[input.duration || ''] || {
    low: 1.0,
    high: 1.5, // fallback for unknown/missing
  }

  const attendeesMult = PRICE_CONSTANTS.attendeesMultipliers[input.attendees || ''] || {
    low: 1.0,
    high: 1.2, // fallback for unknown/missing
  }

  const low = PRICE_CONSTANTS.baseLow * durationMult.low * attendeesMult.low + travelLow
  const high = PRICE_CONSTANTS.baseHigh * durationMult.high * attendeesMult.high + travelHigh

  // Ensure invariants
  const finalLow = Math.min(low, high)
  const finalHigh = Math.max(low, high)

  return formatRange(finalLow, finalHigh)
}

/**
 * Homepage testimonials (placeholder quotes). Replace with real client feedback when ready.
 */
export type Testimonial = {
  quote: string
  author: string
  event: string
}

export const testimonials: Testimonial[] = [
  {
    quote:
      'La banda llegó puntual, el sonido impecable y el público no dejó de bailar. Recomendamos sin duda para el próximo evento.',
    author: 'Organizador de evento',
    event: 'Evento privado (placeholder)',
  },
  {
    quote:
      'Profesionales de principio a fin. La comunicación fue clara y el show superó lo que prometieron en la cotización.',
    author: 'Promotor local',
    event: 'Bar / venue (placeholder)',
  },
  {
    quote:
      'Mezcla perfecta entre corridos tumbados y clásicos del regional. El cierre fue el momento más comentado de la noche.',
    author: 'Cliente',
    event: 'Celebración (placeholder)',
  },
]

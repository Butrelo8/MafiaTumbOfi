/**
 * Homepage “Repertorio” section. Edit copy here only — consumed by `index.astro`.
 */
export type RepertoireItem = {
  name: string
  description: string
}

export const repertoireItems: RepertoireItem[] = [
  {
    name: 'Corridos tumbados',
    description: 'Energía y actitud contemporánea; ideal para pista y barra.',
  },
  {
    name: 'Norteño',
    description: 'Clásicos y propios con acordeón y bajo sexto al frente.',
  },
  {
    name: 'Regional mexicano',
    description: 'Baladas y temas que conectan con público amplio.',
  },
  {
    name: 'Covers',
    description: 'Selección curada para levantar la fiesta sin perder identidad.',
  },
  {
    name: 'Canciones propias',
    description: 'Singles originales y material en crecimiento.',
  },
]

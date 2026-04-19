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
    description: 'Clásicos reinventados con su inconfundible estilo sólido.',
  },
  {
    name: 'Regional mexicano',
    description: 'Baladas y temas que conectan con público amplio.',
  },
  {
    name: 'Covers',
    description: 'Selección curada para levantar la fiesta sin perder la esencia.',
  },
  {
    name: 'Canciones propias',
    description: 'Singles originales y material en crecimiento.',
  },
]

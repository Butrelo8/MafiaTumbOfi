// Dos subtrazados con los mismos ocho puntos en el mismo orden: play y pausa se mezclan sin que GSAP tenga que adivinar.
export const FORMAS = {
  play: 'M6 4L12 7.43L12 16.57L6 20ZM12 7.43L20 12L20 12L12 16.57Z',
  pausa: 'M6 4L10 4L10 20L6 20ZM14 4L18 4L18 20L14 20Z',
} as const
export type Forma = keyof typeof FORMAS

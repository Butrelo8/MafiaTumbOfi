// Dos subtrazados con los mismos ocho puntos en el mismo orden: play y pausa se mezclan sin que GSAP tenga que adivinar.
export const FORMAS = {
  play: 'M6 4L12 7.43L12 16.57L6 20ZM12 7.43L20 12L20 12L12 16.57Z',
  pausa: 'M6 4L10 4L10 20L6 20ZM14 4L18 4L18 20L14 20Z',
} as const
// The designed middle shape of the morph: the two bars close their gap into one block (the halves share the edge at x=12, which
// play keeps, so the two halves never read as two triangles).
export const BLOQUE = 'M7 4L12 4L12 20L7 20ZM12 4L17 4L17 20L12 20Z'
export type Forma = keyof typeof FORMAS

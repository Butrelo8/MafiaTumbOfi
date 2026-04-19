import { z } from 'zod'

/**
 * Spanish error map for validation messages shown to users.
 * Use when parsing booking (or other user-facing) payloads.
 */
export const spanishErrorMap: z.ZodErrorMap = (issue, ctx) => {
  switch (issue.code) {
    case z.ZodIssueCode.invalid_type:
      if (issue.expected === 'string') {
        return { message: 'Debe ser texto' }
      }
      break
    case z.ZodIssueCode.too_small:
      if (issue.type === 'string' && issue.minimum === 1) {
        return { message: 'El nombre es obligatorio' }
      }
      if (issue.type === 'string') {
        return { message: `Mínimo ${issue.minimum} caracteres` }
      }
      break
    case z.ZodIssueCode.too_big:
      if (issue.type === 'string') {
        return { message: `Máximo ${issue.maximum} caracteres` }
      }
      break
    case z.ZodIssueCode.invalid_string:
      if (issue.validation === 'email') {
        return { message: 'Email no válido' }
      }
      break
  }
  return { message: ctx.defaultError }
}

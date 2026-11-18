# Aviso de privacidad (borrador)

`src/pages/aviso-de-privacidad.astro` es un **borrador** hecho para la lista de fans (LFPDPPP 2025, autoridad SABG).
Antes de producción, el titular llena tres campos al inicio del archivo: nombre o razón social del responsable,
domicilio y correo para derechos ARCO. No se inventaron. Conviene que un abogado lo revise.

- El consentimiento es una casilla sin marcar (la inacción no cuenta). La versión que aceptó cada persona queda en
  `mto_fans.consent_version` (`aviso-2026-11-18`, constante `CONSENT_VERSION` en `signup.js`): si cambias el texto, cambia la versión.
- Datos: correo o WhatsApp, ciudad opcional. Sin IP. Cloudflare (D1) los aloja y puede hacerlo fuera de México; el aviso lo dice.
- Cumplir una baja: `wrangler d1 execute mto_fans --remote --command "DELETE FROM mto_fans WHERE contact = '<correo o 52…>'"`.

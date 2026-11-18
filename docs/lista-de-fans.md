# Lista de fans — aparcada (2026-11-18)

Se construyó (formulario `#lista`, `POST /signup`, D1, aviso de privacidad) y el dueño decidió dejarla para después.
El código sigue en el historial: commits `c1f05f7` y `619c875` (rama `cc/validdrone`). Para retomarla, se restauran
`signup.js`, `signup.test.mjs`, `migrations/0001_mto_fans.sql`, `src/pages/aviso-de-privacidad.astro` y la sección `#lista`
de ese commit, más los bindings `DB` (D1) y `SIGNUP_LIMIT` en `wrangler.jsonc`. El aviso quedó en borrador con tres campos por completar.

La base D1 `mto_fans` (`591a5a08-44eb-4269-8c56-47827393aa2b`) sigue en la cuenta de Cloudflare, con la tabla creada y vacía, sin uso.

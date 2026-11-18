# Lista de fans

Formulario `#lista` → `POST /signup` (`signup.js`) → D1 `mto_fans` (id `591a5a08-44eb-4269-8c56-47827393aa2b`, esquema en `migrations/0001_mto_fans.sql`).
Cada alta escribe también un evento `signup` en Analytics Engine, sin el correo ni el número. Ver `docs/analytics.md` y `docs/aviso-de-privacidad.md`.

```bash
# leer la lista (--remote: sin él lee la base local vacía)
npx wrangler d1 execute mto_fans --remote --command "SELECT id, contact, kind, city, created_at FROM mto_fans ORDER BY id DESC"
# cuántos
npx wrangler d1 execute mto_fans --remote --command "SELECT kind, COUNT(*) AS n FROM mto_fans GROUP BY kind"
# dar de baja a alguien (derecho de cancelación)
npx wrangler d1 execute mto_fans --remote --command "DELETE FROM mto_fans WHERE contact = '<correo o 52…>'"
# migraciones nuevas
npx wrangler d1 migrations apply mto_fans --remote
```

Anti-spam: campo oculto `web` (si trae algo, responde ok y no guarda) y límite de 5 altas por minuto por IP y ubicación
(binding `SIGNUP_LIMIT`, no guarda la IP). Sin Turnstile; si aparece spam, se añade.
Un correo o número repetido responde ok y no duplica.

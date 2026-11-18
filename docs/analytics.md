# Medición de clics (Workers Analytics Engine)

`POST /e` (`e.js`) escribe un punto por clic en el dataset `mto_events` (binding `MTO_EVENTS`).
No se guarda IP, user agent, país ni cookie. Se ignoran bots (misma regex que `wa.js`), orígenes ajenos y nombres fuera de lista.

| Evento | Cuándo | `net` |
|---|---|---|
| `wa_click` | cualquier enlace a `/wa/…` | — |
| `contact_click` | enlaces `tel:` y `mailto:` | — |
| `follow_click` | enlaces a spotify, instagram, youtube, tiktok, facebook, apple_music | la red |

Columnas: `index1` = evento; `blob1` evento, `blob2` net, `blob3` página, `blob4` placement
(`header`, `menu`, `hero`, `musica`, `grupo`, `contratacion`, `footer`). El cliente es `src/lib/clickEvents.ts`
(un solo listener delegado, `sendBeacon`); el placement sale del `data-placement` más cercano.

## Consulta: clics por evento y por día

Los días son UTC. `SUM(_sample_interval)` y no `count()`: Analytics Engine muestrea y cada fila pesa lo que representa.
Token: Cloudflare → My Profile → API Tokens → Custom → *Account · Account Analytics · Read*.

```bash
curl -s "https://api.cloudflare.com/client/v4/accounts/5a69f76be617bb90c3098ee425031ae6/analytics_engine/sql" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" --data-binary \
  "SELECT toDate(timestamp) AS day, blob1 AS event, blob2 AS net, SUM(_sample_interval) AS clicks
   FROM mto_events WHERE timestamp > NOW() - INTERVAL '30' DAY
   GROUP BY day, event, net ORDER BY day DESC, event, net FORMAT JSON"
```

Por placement: cambia `blob2 AS net` por `blob4 AS placement` (y el `GROUP BY`).
Una fila tarda uno o dos minutos en aparecer.

## Page views

Plausible ya corre en el sitio (`PUBLIC_PLAUSIBLE_DOMAIN`). Los eventos `whatsapp_hero`, `whatsapp_contratacion` y
`whatsapp_footer` de Plausible se mantienen: esos tres enlaces disparan los dos sistemas (Plausible y `wa_click`).
Cloudflare Web Analytics no está activado (no hay beacon `cloudflareinsights` en el HTML en vivo).

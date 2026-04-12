# Guia de uso de la web app para manager (sin codigo)

Esta guia esta hecha para el manager de la banda.
No necesita saber programacion para usar el sistema.

---

## 1) Acceso rapido al inbox de la banda (Outlook)

Para revisar correos de solicitudes, el manager entra con:

1. Correo: `mafiatumbadaoficial@outlook.com`
2. Contrasena: `PEGAR_CONTRASENA_GENERICA_AQUI`

Pasos:

1. Entrar a [Outlook](https://outlook.live.com/).
2. Iniciar sesion con ese correo y contrasena.
3. Abrir Inbox para revisar nuevas cotizaciones.

Nota:

1. Esta cuenta debe usarse solo por personas autorizadas.
2. Si cambia la contrasena, actualizar esta guia el mismo dia.

---

## 2) Que pasa cuando una persona cotiza en la web

Flujo general:

1. La persona llena el formulario de contratacion.
2. El sistema guarda la solicitud.
3. La persona es enviada a una pagina de agradecimiento.
4. La solicitud aparece en el panel admin para seguimiento.

Pagina de agradecimiento:

1. Ruta: `/booking/gracias`
2. Tiene boton de WhatsApp (si esta configurado).
3. Muestra enlace/video principal:
`https://youtu.be/HTA31yUX41A?si=qduPw-9WioHKQlU4`

---

## 3) Correos que se envian (ejemplos para control de manager)

El manager debe conocer estos correos:

1. Correo al equipo/banda (aviso de nueva solicitud)
- Destino: inbox del equipo (correo configurado para notificaciones).
- Asunto ejemplo: `[Mafia Tumbada] Nueva solicitud de contratacion - {Nombre}`
- Objetivo: avisar rapido al equipo con los datos del cliente.

2. Correo de confirmacion al cliente (inmediato)
- Destino: correo que la persona escribio en el formulario.
- Asunto ejemplo: `Recibimos tu solicitud - Mafia Tumbada`
- Objetivo: confirmar que la solicitud si llego.

3. Correo de seguimiento con cancion/video
- Destino: cliente.
- Asunto ejemplo: `Asi sonamos - Mafia Tumbada`
- Incluye este enlace:
`https://www.youtube.com/watch?v=7Sx0yDjGoq0&list=RD7Sx0yDjGoq0&start_radio=1`
- Objetivo: mantener interes y reforzar confianza.

4. Correo final de seguimiento (urgencia)
- Destino: cliente.
- Asunto ejemplo: `Asegura tu fecha - Mafia Tumbada`
- Lleva a WhatsApp (si esta activo) o al formulario.
- Objetivo: empujar cierre de la contratacion.

5. Reenvio manual desde admin
- Se usa boton: **Reenviar confirmacion**.
- Sirve cuando una fila queda en estado `pending`.

---

## 4) Rutina diaria recomendada para el manager

1. Entrar a `/admin`.
2. Revisar solicitudes nuevas.
3. Actualizar **Seguimiento**: `Nuevo` -> `Contactado` -> `Cerrado`.
4. Abrir **Ver detalle** en leads importantes.
5. Guardar contexto en **Notas internas**.
6. Si hace falta, usar **Reenviar confirmacion**.
7. Exportar CSV para control diario/semanal.

---

## 5) Como leer los estados en admin

Hay 2 tipos de estado:

1. **Status (correo)**
- `sent`: correo al cliente enviado correctamente.
- `pending`: llego al equipo, pero hubo problema con correo al cliente.
- `failed`: fallo aviso al equipo.

2. **Seguimiento**
- `Nuevo`: aun no trabajado.
- `Contactado`: ya hubo contacto.
- `Cerrado`: ya se cerro ese lead.

Importante: son estados distintos e independientes.

---

## 6) Herramientas del panel admin (resumen rapido)

1. **Buscar**: filtra por nombre, correo o telefono.
2. **Todas / Nuevo / Contactado / Cerrado**: filtros rapidos.
3. **Descargar CSV (pagina visible)**: exporta lo que se esta viendo.
4. **Exportar JSON (depuracion)**: exportacion tecnica.
5. **Ver detalle**: abre panel lateral con toda la info.
6. **Notas internas + Guardar notas**: guarda seguimiento interno.
7. **Reenviar confirmacion**: reenvia correo al cliente.
8. **Eliminar**: oculta fila del panel (soft-delete).

---

## 7) Zona peligrosa: vaciar toda la base de solicitudes

Accion delicada:

1. Clic en **Vaciar todas las solicitudes...**
2. Opcional: **Vista previa (conteo)**
3. Escribir frase: `DELETE_ALL_BOOKINGS`
4. Clic en **Borrar todo (irreversible)**

Importante:

1. Borra todas las filas de solicitudes.
2. No se puede deshacer desde el panel.
3. Usar solo con autorizacion explicita.

---

## 8) Como pedir cambios de texto, botones, links o diseno (sin codigo)

Si el manager quiere cambios, solo tiene que pedirlos por mensaje claro.
No necesita explicacion tecnica.

Formato recomendado:

1. **Pagina o correo:** inicio / booking / gracias / Email 2 / Email 3, etc.
2. **Contenido actual:** texto o link actual exacto.
3. **Contenido nuevo:** texto o link final exacto.
4. **Tono:** formal / premium / directo / amigable.
5. **Prioridad:** urgente / esta semana / proxima actualizacion.

Ejemplo:

`Pagina o correo: Pagina de gracias (/booking/gracias)`
`Link actual: https://youtu.be/HTA31yUX41A?si=qduPw-9WioHKQlU4`
`Link nuevo: https://youtube.com/mi-video-nuevo`
`Tono: premium y directo`
`Prioridad: esta semana`

---

## 9) Cambiar canciones o subir video en vivo (si se puede)

Si, se puede.

El manager puede pedir:

1. Cambiar video/cancion de la pagina de gracias.
2. Cambiar cancion del correo de seguimiento.
3. Subir video en vivo y usarlo como principal.
4. Cambiar boton principal a WhatsApp o formulario.

Solo necesita mandar el/los links finales.

---

## 10) Cuando pedir ayuda tecnica

El manager debe pedir soporte si:

1. Admin no carga.
2. Puede entrar pero no ve solicitudes.
3. Reenviar confirmacion falla varias veces.
4. Exportaciones fallan.
5. Se requiere cambio grande en varias paginas/correos.

Al reportar, incluir:

1. Que paso.
2. Fecha y hora.
3. Captura de pantalla.
4. ID del lead (si lo tiene).

---

Si hace falta, esta guia se puede convertir en checklist de capacitacion de 1 pagina.
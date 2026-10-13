# Constraints

- No leer ni analizar el código de `rive-mcp` (su licencia lo prohíbe): usarlo solo por MCP.
- Personajes humanos o fotos de personas → skill `blender`, no Rive.
- No usar personajes con derechos (caricaturas, stock con marca de agua) en entregas a clientes.

## Known failure modes

- `rive` (oficial) no conecta si la app de escritorio no está abierta; no reintentar en bucle.
- `rive-mcp` sin Chromium → `RIVE_MCP_CHROME`.
- `headRatio` mal → la cabeza se deforma; ajustar al corte real de la cabeza en el PNG.

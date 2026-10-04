# Constraints

- Nunca entregar FBX de Mixamo ni `.blend` con ellos a un cliente: solo el render.
- Revisar qué archivo tiene abierto Blender antes de ejecutar código por MCP.

## Known failure modes

- Objetos emparentados a huesos diminutos → escala 0.01 de Mixamo; escalar ×100.
- Fondo gris en el render → `view_transform = 'Standard'`.
- `read_homefile` por MCP rompe el import FBX.

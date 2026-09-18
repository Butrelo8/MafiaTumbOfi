"""Escribe src/data/scene.json leyendo lo que hay en public/scene/.

El contrato con la capa web: estaciones, tramos y pesos. Se genera del disco y
no a mano, así que re-renderizar con otro número de frames no pide tocar nada.
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCENA = os.path.join(RAIZ, "public", "scene")
NOMBRES = ("nave", "altar", "sonido", "hornacinas", "reliquia", "retirada")
FORMATOS = {"mobile": (900, 1600), "desktop": (1920, 1080)}


def _peso(ruta):
    return os.path.getsize(ruta)


def formato(carpeta):
    base = os.path.join(ESCENA, carpeta)
    ancho, alto = FORMATOS[carpeta]
    estaciones = []
    for indice, nombre in enumerate(NOMBRES):
        archivo = "estacion-%d.avif" % indice
        ruta = os.path.join(base, archivo)
        if not os.path.exists(ruta):
            continue
        estacion = {"nombre": nombre,
                    "imagen": "/scene/%s/%s" % (carpeta, archivo),
                    "bytes": _peso(ruta)}

        # Capa con alfa de lo que va DELANTE del texto, y variante con el
        # relámpago encendido. Las dos son opcionales: si no están, la web se
        # comporta como antes de existir.
        for clave, sufijo, extension in (("capaFrente", "-frente", "webp"),
                                         ("relampago", "-relampago", "avif")):
            extra = "estacion-%d%s.%s" % (indice, sufijo, extension)
            ruta_extra = os.path.join(base, extra)
            if os.path.exists(ruta_extra):
                estacion[clave] = {"imagen": "/scene/%s/%s" % (carpeta, extra),
                                   "bytes": _peso(ruta_extra)}
        estaciones.append(estacion)

    tramos = []
    for indice in range(len(NOMBRES) - 1):
        carpeta_tramo = os.path.join(base, "tramo-%d" % indice)
        if not os.path.isdir(carpeta_tramo):
            continue
        # WebP y no AVIF: el decode de AVIF era el cuello del scrub, medido.
        archivos = sorted(f for f in os.listdir(carpeta_tramo) if f.endswith(".webp"))
        tramos.append({
            "desde": NOMBRES[indice],
            "hasta": NOMBRES[indice + 1],
            "frames": len(archivos),
            "patron": "/scene/%s/tramo-%d/%%03d.webp" % (carpeta, indice),
            "bytes": sum(_peso(os.path.join(carpeta_tramo, f)) for f in archivos),
        })

    total = sum(t["bytes"] for t in tramos)
    for e in estaciones:
        total += e["bytes"]
        for clave in ("capaFrente", "relampago"):
            if clave in e:
                total += e[clave]["bytes"]
    return {"ancho": ancho, "alto": alto, "estaciones": estaciones,
            "tramos": tramos, "bytes": total}


def main():
    datos = {"formatos": {c: formato(c) for c in FORMATOS if os.path.isdir(os.path.join(ESCENA, c))}}
    destino = os.path.join(RAIZ, "src", "data", "scene.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for nombre, datos_formato in datos["formatos"].items():
        print("%s: %d estaciones, %d tramos, %.2f MB"
              % (nombre, len(datos_formato["estaciones"]), len(datos_formato["tramos"]),
                 datos_formato["bytes"] / 1024 / 1024))


if __name__ == "__main__":
    main()

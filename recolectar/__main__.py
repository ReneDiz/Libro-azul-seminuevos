"""Recolecta los anuncios de todas las fuentes y guarda una captura fechada.

Uso:  python3 -m recolectar
Genera data/capturas/AAAA-MM-DD.json (una foto del mercado de ese día).
"""
import json, pathlib, collections, unicodedata
from .comun import HOY, guardar
from .fuentes import mercadolibre, zapata, otros

LECTORES = [mercadolibre.leer, zapata.leer_selectrucks, zapata.leer_goon, otros.leer_panamotors,
            otros.leer_nastrac, otros.leer_quality, otros.leer_scania, otros.leer_seminuevos]

def limpiar(a):
    for k, v in list(a.items()):
        if isinstance(v, str): a[k] = unicodedata.normalize("NFKC", v).strip()
    return a

def main():
    raiz = pathlib.Path(__file__).resolve().parent.parent
    todos, errores = [], {}
    for leer in LECTORES:
        nombre = f"{leer.__module__.rsplit('.', 1)[1]}.{leer.__name__}"
        print("Leyendo", nombre)
        try: todos += [limpiar(a) for a in leer()]
        except Exception as e:
            errores[nombre] = repr(e); print("  ERROR", e)
    destino = raiz / "data" / "capturas"; destino.mkdir(parents=True, exist_ok=True)
    guardar(destino / f"{HOY}.json", {"fecha": HOY, "errores": errores, "anuncios": todos})
    print("Listo:", len(todos), "anuncios", dict(collections.Counter((a["fuente"], a["producto"]) for a in todos)))

if __name__ == "__main__":
    main()

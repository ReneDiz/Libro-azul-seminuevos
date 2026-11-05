# Libro Azul de VC Seminuevos

Guía de mercado de vehículos comerciales seminuevos en México: valor de mercado con anuncios reales homologados, confianza, sensibilidad y precio de compra con margen.

- **Versión 1 (fija):** rama `version-1-fija`, también en `main`. No se modifica.
- **Versión 2 (prueba):** rama `v2-prueba`. Productos: Kenworth T680, Freightliner Cascadia e International LT.

## Cómo se actualiza

```bash
python3 -m recolectar   # lee las fuentes y guarda data/capturas/AAAA-MM-DD.json
python3 homologar.py    # junta capturas + Observatorio + correcciones en data/base.json
python3 build.py        # genera index.html y site/index.html
```

GitHub Actions corre estos tres pasos cada lunes (`.github/workflows/captura-semanal.yml`).

## Archivos

| Archivo | Qué es |
|---|---|
| `data/parametros.json` | Supuestos (IVA, vigencia, ventanas, descuentos, márgenes, gastos). Vienen del Observatorio 1.2. |
| `data/correcciones.json` | Correcciones manuales por anuncio: excluir, duplicado, tipo, nota, IVA. |
| `data/previas/` | Evidencia previa: Base de mercado del Observatorio 1.2 y captura de la versión 1. |
| `data/capturas/` | Una foto del mercado por fecha. No se borran: sirven para medir cambios de precio y rotación. |
| `recolectar/` | Un lector por fuente. |
| `plantilla.html` | Diseño y cálculos de la página. |
| `CAMBIOS.md` | Bitácora de cambios de método, parámetros y fuentes. |

Ningún resultado es una autorización de compra: se lleva al CR Sencillo V2 y sigue el procedimiento.

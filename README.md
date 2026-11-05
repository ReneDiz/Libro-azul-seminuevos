# Libro Azul de VC Seminuevos · Kenworth T680

Cotizador interactivo de vehículos comerciales (VC) seminuevos: valor de referencia por año, motor y kilometraje, a partir de anuncios reales en venta en México, y un precio propuesto de compra.

## Estructura

- `data/kenworth-t680.json`: anuncios, fuentes, tipo de cambio y fecha de corte.
- `build.py`: plantilla HTML, CSS y JS. Genera `index.html` y `site/index.html`.
- Al inicio de `build.py`: la paleta de colores (`PALETA = "azul"`, `"acero"` o `"petroleo"`), los supuestos de compra (`COMPRA`) y la dirección del sitio (`SITE_URL`).
- `site/`: carpeta que se publica (Netlify), con la imagen OG, el sticker y `_headers`.

## Uso

Edita los datos o la plantilla y regenera:

```bash
python3 build.py
```

No edites `index.html` a mano: se sobrescribe en cada build.

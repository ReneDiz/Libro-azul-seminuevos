# Libro Azul Advance · Kenworth T680

Cotizador interactivo de seminuevos de trabajo: valor de referencia por año, motor y kilometraje, a partir de anuncios reales en venta en México.

## Estructura

- `data/kenworth-t680.json`: anuncios, fuentes, tipo de cambio y fecha de corte.
- `build.py`: plantilla HTML, CSS y JS. Genera `index.html` y `site/index.html`.
- `site/`: carpeta que se publica (Netlify), con la imagen OG, el sticker y `_headers`.

## Uso

Edita los datos o la plantilla y regenera:

```bash
python3 build.py
```

No edites `index.html` a mano: se sobrescribe en cada build.

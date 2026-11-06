#!/usr/bin/env python3
"""Libro Azul de VC Seminuevos · versión 2 (prueba).

Lee data/base.json (generado por homologar.py) y genera index.html y site/index.html.
Todo el cálculo de mercado, confianza, sensibilidad y compra corre en el navegador,
con los supuestos de data/parametros.json (los mismos del Observatorio y Valuador 1.2).

Flujo completo:
  python3 -m recolectar   # lee las fuentes en internet y guarda data/capturas/AAAA-MM-DD.json
  python3 homologar.py    # junta capturas + Observatorio + correcciones -> data/base.json
  python3 build.py        # genera la página
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
BASE = json.load(open(ROOT / "data/base.json"))

# Dirección pública del sitio (para la vista previa al compartir el link).
SITE_URL = "https://libro-azul-advance.netlify.app"

# Paleta de colores activa: "marino" (actual), "azul", "acero" o "petroleo"
PALETA = "marino"
PALETAS = {
    # Marino y arena: azul marino profundo sobre fondo cálido, con acento dorado suave.
    "marino": dict(bg="#f6f4ef", bg2="#faf8f4", surface="#fff", line="#e4dfd4", text="#1b2a41", muted="#53607a", faint="#8b93a3", track="#ece7dc",
                   acc="#24507a", acc_ink="#1a3c5e", acc_on="#fff", acc_soft="rgba(36,80,122,.10)", acc_line="rgba(36,80,122,.38)",
                   alt="#c69a3c", tag="rgba(27,42,65,.86)", cum="#cfd5de", cum_ln="#8b93a3", sd_ln="#b9c0cb"),
    "azul": dict(bg="#f3f5f9", bg2="#f7f9fc", surface="#fff", line="#dde3ec", text="#14213d", muted="#4f5d75", faint="#8590a6", track="#e5e9f0",
                 acc="#2f6fed", acc_ink="#1d4fb8", acc_on="#fff", acc_soft="rgba(47,111,237,.13)", acc_line="rgba(47,111,237,.45)",
                 alt="#f2a541", tag="rgba(20,33,61,.84)", cum="#c7cfdc", cum_ln="#8590a6", sd_ln="#b3bccb"),
    "acero": dict(bg="#f4f4f1", bg2="#fafaf8", surface="#fff", line="#e2e1db", text="#132238", muted="#4d5867", faint="#8a919b", track="#e8e7e2",
                  acc="#ef7d22", acc_ink="#b5530c", acc_on="#fff", acc_soft="rgba(239,125,34,.14)", acc_line="rgba(239,125,34,.5)",
                  alt="#1f4e8c", tag="rgba(19,34,56,.86)", cum="#cfd3d9", cum_ln="#8a919b", sd_ln="#bcc0c6"),
    "petroleo": dict(bg="#f2f6f6", bg2="#f7fafa", surface="#fff", line="#dbe5e5", text="#122a2e", muted="#4a6266", faint="#839699", track="#e2eaea",
                     acc="#0f8a84", acc_ink="#0b6560", acc_on="#fff", acc_soft="rgba(15,138,132,.13)", acc_line="rgba(15,138,132,.45)",
                     alt="#e0a526", tag="rgba(18,42,46,.85)", cum="#c6d3d4", cum_ln="#839699", sd_ln="#b2c2c3"),
}
P = PALETAS[PALETA]
ROOT_CSS = (":root{" + ";".join(f"--{k.replace('_','-')}:{v}" for k, v in P.items()) +
            ";--good:#2e9b5f;--warn:#c9820b;--crit:#d63b3b;--shadow:0 1px 2px rgba(20,30,50,.05),0 10px 26px -16px rgba(20,35,70,.28)}")

# Solo se manda a la página lo que usa
CAMPOS = ("id", "fuente", "url", "producto", "modelo", "anio", "km", "motor", "trans", "cabina", "dormitorio_pulg", "traccion", "hp",
          "precio", "moneda", "precio_mxn", "iva", "iva_origen", "iva_presunto", "tipo_precio", "lugar", "vendedor", "tipo_vendedor", "tipo", "img", "img_url", "consulta",
          "dias_publicado", "publicado", "estado", "cambio_precio", "no_elegible", "dup_de", "nota")
DATA = json.dumps({**{k: BASE[k] for k in ("corte", "parametros", "productos", "fuentes", "capturas")},
                   "anuncios": [{k: a[k] for k in CAMPOS if a.get(k) not in (None, "", [])} for a in BASE["anuncios"]]},
                  ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

TEMPLATE = (ROOT / "plantilla.html").read_text(encoding="utf-8")
out = TEMPLATE.replace("__ROOT__", ROOT_CSS).replace("__SITE__", SITE_URL).replace("__DATA__", DATA)
(ROOT / "index.html").write_text(out, encoding="utf-8")
SITE = ROOT / "site"; SITE.mkdir(exist_ok=True)
assert (SITE / "og-libro-azul-t680-v3.jpg").exists(), "falta la miniatura OG en site/"
(SITE / "index.html").write_text(out, encoding="utf-8")
(SITE / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: no-referrer\n  X-Content-Type-Options: nosniff\n")
print("ok", len(BASE["anuncios"]), "anuncios")

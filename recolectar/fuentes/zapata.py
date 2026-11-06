"""Grupo Zapata: SelecTrucks Zapata (catálogo con VIN) y Go On Zapata (camiones)."""
import json, re
from ..comun import get, motor_normalizado, transmision_tipo, producto, HOY

def _lista(h, var):
    m = re.search(var + r"\s*=\s*(\[.*?\]);\s*\n", h, re.S)
    return json.loads(m.group(1)) if m else []

def _rango(prod, anio):
    return prod == "kenworth-t680" or (anio and 2021 <= anio <= 2025)

def leer_selectrucks(log=print):
    h = get("https://www.selectruckszapata.com/catalogo")
    out = []
    for a in _lista(h, r"let trucks"):
        marca = "International" if a.get("id_brand") == "4" else (a.get("id_brand") or "").title()
        prod = producto(marca, a.get("id_model"))
        if not prod or not _rango(prod, a.get("year")) or a.get("status") != "publicado": continue
        out.append({"id": "STZ-" + a["vin"], "fuente": "STZ", "url": "https://www.selectruckszapata.com/detalle/" + a["url"].replace("\\/", "/"),
            "producto": prod, "marca": marca, "modelo": a.get("id_model"), "anio": a.get("year"), "km": a.get("kms"),
            "motor_raw": a.get("engine_type") or "", "motor": motor_normalizado(a.get("engine_type")),
            "trans_raw": a.get("id_transmision") or "", "trans": transmision_tipo(a.get("id_transmision")),
            "precio": a.get("price"), "moneda": "MXN", "iva": "Incluido",  # catálogo SelecTrucks Zapata: contado con IVA incluido (Observatorio)
            "tipo_precio": "Contado publicado", "evidencia": "Ficha individual", "vin": a["vin"],
            "lugar": (a.get("id_location") or "").title(), "vendedor": "SelecTrucks Zapata", "tipo_vendedor": "distribuidor",
            "tipo": "tracto", "publicado": (a.get("created_at") or "")[:10], "actualizado": (a.get("updated_at") or "")[:10],
            "consulta": HOY, "img_url": (a.get("cover_image") or {}).get("picture", ""),
            "texto": " · ".join(str(a.get(k) or "") for k in ("id_model", "engine_type", "id_transmision", "sleeper_cab", "rear_axle", "description"))})
    log(f"  SelecTrucks Zapata: {len(out)} de interés")
    return out

def leer_goon(log=print):
    h = get("https://www.zapataseminuevos.mx/camiones")
    out = []
    for a in _lista(h, r"const cars"):
        prod = producto(a.get("brand"), a.get("model"))
        if not prod or not _rango(prod, a.get("year")): continue
        out.append({"id": "GOON-" + (a.get("vin") or str(a["id"])), "fuente": "GOON",
            "url": "https://www.zapataseminuevos.mx/" + (a.get("url") or "").replace("\\/", "/"),
            "producto": prod, "marca": a.get("brand"), "modelo": a.get("model"), "anio": a.get("year"), "km": a.get("km"),
            "motor_raw": a.get("engine") or "", "motor": motor_normalizado(a.get("engine")),
            "trans_raw": a.get("transmission") or "", "trans": transmision_tipo(a.get("transmission")),
            "precio": a.get("price"), "moneda": "MXN", "iva": "Desconocido", "tipo_precio": "Contado publicado",
            "evidencia": "Ficha individual", "vin": a.get("vin"), "lugar": a.get("location") or "", "vendedor": "Go On Zapata",
            "tipo_vendedor": "distribuidor", "tipo": "tracto", "consulta": HOY,
            "texto": " · ".join(str(a.get(k) or "") for k in ("title", "engine", "transmission", "sleeperCab", "type"))})
    log(f"  Go On Zapata: {len(out)} de interés")
    return out

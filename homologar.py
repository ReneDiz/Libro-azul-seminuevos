#!/usr/bin/env python3
"""Junta todas las evidencias en una sola base homologada: data/base.json.

Orden (lo más reciente gana para el mismo anuncio):
  1. data/previas/libro-azul-v1.json   (captura del 4 nov 2026 de la versión 1)
  2. data/previas/observatorio-1.2.json (Base de mercado del Observatorio 1.2)
  3. data/capturas/*.json              (capturas automáticas, de la más vieja a la más nueva)
Después aplica data/correcciones.json y marca duplicados entre portales (mismo VIN o misma unidad).
"""
import json, re, pathlib, datetime, collections

ROOT = pathlib.Path(__file__).parent
P = json.load(open(ROOT / "data/parametros.json"))

FUENTES = {
    "ML": ("Mercado Libre México", "https://vehiculos.mercadolibre.com.mx/camiones/", "portal"),
    "STZ": ("SelecTrucks Zapata", "https://www.selectruckszapata.com/catalogo", "distribuidor"),
    "GOON": ("Go On Zapata", "https://www.zapataseminuevos.mx/camiones", "distribuidor"),
    "PANA": ("Panamotors", "https://panamotors.com/tractocamiones", "distribuidor"),
    "NASTRAC": ("NASTRAC", "https://www.nastracseminuevos.com/", "distribuidor"),
    "QT": ("Quality Trucks", "https://qualitytrucks.com.mx/seminuevos/", "distribuidor"),
    "SCA": ("Scania Seminuevos", "https://seminuevos.scania.com/?s=kenworth&post_type=product", "distribuidor"),
    "SEM": ("Seminuevos.com", "https://www.seminuevos.com/usados/-/camiones", "portal"),
    "TRACTOS": ("Tractos", "https://www.tractos.com/seminuevos", "distribuidor"),
    "TTM": ("Tienda TTM Guadalajara", "https://tienda.ttmexico.mx/collections/vendors?q=kenworth", "distribuidor"),
    "DN": ("Del Norte TS", "https://delnortets.com/categoria-producto/tractocamiones/kenworth/", "distribuidor"),
    "DICAM": ("DICAM Texcoco", "https://dicamtexcoco.com.mx/", "distribuidor"),
    "ECC": ("Euro Centro Camionero", "https://eurocentrocamionero.com/seminuevos/", "distribuidor"),
}
PRODUCTOS = {"kenworth-t680": "Kenworth T680", "freightliner-cascadia": "Freightliner Cascadia", "international-lt": "International LT"}

def id_canonico(a):
    u = a.get("url") or ""
    for pat, pref in [(r"MLM-?(\d+)", "MLM-"), (r"nastracseminuevos\.com/vehiculo/(\d+)", "NAS-"),
                      (r"qualitytrucks\.com\.mx/seminuevos/[^/]+/([^/]+)/", "QT-"), (r"seminuevos\.scania\.com/p/([^/]+)/", "SCA-"),
                      (r"seminuevos\.com/vehicle/.*/(\d+)$", "SEM-"), (r"tractos\.com/seminuevos/.*/([A-Z]{2}-\d+)", "TRACTOS-")]:
        m = re.search(pat, u)
        if m:
            sufijo = m.group(1)
            if pref == "QT-" and not sufijo.startswith(("kenworth", "freightliner", "international")):
                sufijo = u.rstrip("/").split("/")[-2] + "-" + sufijo
            return pref + sufijo
    return a["id"]

def desde_v1(d):
    out = []
    for a in d["anuncios"]:
        prod = "kenworth-t680"
        mt = a.get("motor", "")
        from recolectar.comun import motor_normalizado, transmision_tipo
        out.append({"id": a["id"], "fuente": a["f"], "url": a.get("url") or (f"https://vehiculo.mercadolibre.com.mx/{a['id']}-_JM" if a["f"] == "ML" else ""),
            "producto": prod, "marca": "Kenworth", "modelo": "T680", "anio": a["anio"], "km": a["km"], "motor_raw": mt, "motor": motor_normalizado(mt),
            "trans_raw": a.get("trans", ""), "trans": transmision_tipo(a.get("trans", "")), "precio": a["precio"], "moneda": a["mon"],
            "iva": "Más IVA" if "IVA" in (a.get("nota") or "") and "Más" in (a.get("nota") or "") else "Desconocido",
            "tipo_precio": "Contado publicado", "evidencia": "Ficha individual", "lugar": a["lugar"], "vendedor": a.get("vend", ""),
            "tipo_vendedor": "distribuidor" if a["f"] != "ML" or a.get("vend") else "particular", "tipo": a.get("tipo", "tracto"),
            "img": a.get("img", ""), "consulta": d.get("corte", "2026-11-04")[:10] if a["f"] != "SCA" else "2026-11-05", "nota": a.get("nota", "")})
    return out

def main():
    v1 = desde_v1(json.load(open(ROOT / "data/previas/libro-azul-v1.json")))
    mapa_v1 = {a["id"]: id_canonico(a) for a in v1}  # IDs de la versión 1 -> ID canónico
    capas = [("v1", v1)]
    capas.append(("observatorio", json.load(open(ROOT / "data/previas/observatorio-1.2.json"))["anuncios"]))
    capturas = sorted((ROOT / "data/capturas").glob("*.json"))
    leidas_ok = {}  # fuente -> última fecha en que se leyó completa
    for c in capturas:
        d = json.load(open(c))
        capas.append((d["fecha"], d["anuncios"]))
        caidas = {k.split(".")[0] for k in d.get("errores", {})}
        for f in {a["fuente"] for a in d["anuncios"]}: leidas_ok[f] = d["fecha"]
    base, historia = {}, collections.defaultdict(list)
    for nombre, anuncios in capas:
        for a in anuncios:
            a = dict(a); a["id"] = id_canonico(a)
            previo = base.get(a["id"])
            if previo:
                a["primera_vista"] = previo.get("primera_vista") or previo.get("consulta")
                for k in ("img", "motor_raw", "trans_raw", "vin", "nota"):
                    if not a.get(k) and previo.get(k): a[k] = previo[k]
                if previo.get("iva") in ("Incluido", "Más IVA") and a.get("iva") == "Desconocido": a["iva"] = previo["iva"]
            else:
                a["primera_vista"] = a.get("publicado") or a.get("consulta")
            historia[a["id"]].append({"fecha": a.get("consulta"), "precio": a.get("precio"), "capa": nombre})
            base[a["id"]] = a
    corr = {mapa_v1.get(k, k): v for k, v in json.load(open(ROOT / "data/correcciones.json")).items() if not k.startswith("_")}
    corte = max(a.get("consulta") or "2000-01-01" for a in base.values())
    dcorte = datetime.date.fromisoformat(corte)
    salida = []
    for a in base.values():
        from recolectar.comun import motor_normalizado
        if a.get("motor_raw") or a.get("motor"): a["motor"] = motor_normalizado(a.get("motor_raw") or a.get("motor"))
        c = corr.get(a["id"], {})
        for k in ("tipo", "nota", "iva", "motor", "km"):
            if k in c: a[k] = c[k]
        h = historia[a["id"]]
        precios = [x["precio"] for x in h if x["precio"]]
        a["historial"] = [x for i, x in enumerate(h) if i == 0 or x["precio"] != h[i - 1]["precio"]]
        a["cambio_precio"] = (precios[-1] - precios[0]) if len(precios) > 1 and precios[-1] != precios[0] else 0
        ult = a.get("consulta") or corte
        # retirado: la fuente se leyó completa en la captura más reciente y este anuncio ya no apareció
        a["estado"] = "retirado" if (a["fuente"] in leidas_ok and ult < leidas_ok[a["fuente"]]) else "vigente"
        a["dias_desde_consulta"] = (dcorte - datetime.date.fromisoformat(ult)).days
        if a.get("km") and a["km"] > 5_000_000: a["km"] = None; a["nota"] = (a.get("nota", "") + " · km inválido en la ficha").strip(" ·")
        a["precio_mxn"] = round(a["precio"] * (P["tipo_cambio_mxn_usd"] if a.get("moneda") == "USD" else 1)) if a.get("precio") else None
        a["excluir"] = c.get("excluir", "")
        if "dup_de" in c: a["dup_de"] = mapa_v1.get(c["dup_de"], c["dup_de"])
        salida.append(a)
    # duplicados entre portales: mismo VIN, o mismo producto+año+km (+precio parecido)
    pref = {"STZ": 0, "QT": 1, "NASTRAC": 1, "SCA": 1, "TRACTOS": 1, "PANA": 2, "GOON": 2, "TTM": 2, "DN": 2, "SEM": 3, "ML": 4}
    salida.sort(key=lambda a: (pref.get(a["fuente"], 5), a["estado"] != "vigente", a["id"]))
    llaves = {}
    for a in salida:
        if a.get("dup_de"): continue
        ks = []
        if a.get("vin"): ks.append(("vin", a["vin"]))
        if a.get("km") and a["km"] not in (123456,):
            # km "redondos" (700,000) se repiten entre unidades distintas: ahí también debe coincidir el precio
            ks.append(("u", a["producto"], a["anio"], a["km"]) if a["km"] % 1000 else ("u", a["producto"], a["anio"], a["km"], a.get("precio_mxn")))
        for k in ks:
            if k in llaves and llaves[k] != a["id"]:
                a["dup_de"] = llaves[k]; break
        else:
            for k in ks: llaves[k] = a["id"]
    for a in salida:
        a.pop("_iid", None)
        motivos = []
        if a["excluir"]: motivos.append(a["excluir"])
        if a.get("tipo") != "tracto": motivos.append(f"No es tractocamión ({a.get('tipo')})")
        if a.get("dup_de"): motivos.append(f"Duplicado de {a['dup_de']}")
        if a["estado"] != "vigente": motivos.append("Ya no está publicado")
        if a["dias_desde_consulta"] > P["vigencia_dias"]: motivos.append("Consulta con más de 30 días")
        if a.get("tipo_precio") != "Contado publicado": motivos.append(f"Precio «{a.get('tipo_precio')}»")
        if not a.get("precio_mxn") or a["precio_mxn"] < 100000: motivos.append("Precio inválido")
        if a.get("moneda") == "USD": motivos.append("Precio en dólares (otro mercado)")
        a["no_elegible"] = motivos
    salida.sort(key=lambda a: (a["producto"], -(a["anio"] or 0), a["precio_mxn"] or 0))
    out = {"corte": corte, "parametros": P, "productos": PRODUCTOS,
           "fuentes": {k: {"nombre": v[0], "url": v[1], "tipo": v[2], "leida_automatica": k in leidas_ok, "ultima_lectura": leidas_ok.get(k)} for k, v in FUENTES.items()},
           "capturas": [c.stem for c in capturas], "anuncios": salida}
    json.dump(out, open(ROOT / "data/base.json", "w"), ensure_ascii=False, indent=1)
    cnt = collections.Counter((a["producto"], "elegible" if not a["no_elegible"] else "no") for a in salida)
    print("corte", corte, "anuncios", len(salida), dict(cnt))

if __name__ == "__main__":
    import sys; sys.path.insert(0, str(ROOT)); main()

"""Distribuidores con sitio propio: Panamotors, NASTRAC, Quality Trucks, Scania Seminuevos, Seminuevos.com."""
import json, re
from ..comun import get, texto, numero, iva_de_texto, motor_normalizado, transmision_tipo, producto, HOY

def _ok(prod, anio): return prod and (prod == "kenworth-t680" or (anio and 2021 <= anio <= 2025))

def leer_panamotors(log=print):
    out = []
    for pagina in ("https://panamotors.com/tractocamiones",):
        h = get(pagina).replace('\\"', '"')
        for m in re.finditer(r'"vehicle":(\{"id":\d+,"internal_id".*?"color":"?[^,}]*"?\})', h):
            try: v = json.loads(m.group(1))
            except Exception: continue
            prod = producto(v.get("make"), v.get("model"))
            if not _ok(prod, v.get("year")): continue
            grupo = v.get("is_group") and (v.get("group_count") or 0) > 1
            iid = f"PANA-{v['id']}"
            if any(o["id"] == iid for o in out): continue
            out.append({"id": iid, "fuente": "PANA", "url": pagina,
                "producto": prod, "marca": v.get("make", "").title(), "modelo": v.get("model"), "anio": v.get("year"),
                "km": v.get("odometer"), "motor_raw": "", "motor": "", "trans_raw": v.get("transmission") or "",
                "trans": {"AUTOMATIC": "Automática", "MANUAL": "Manual", "AUTOMATED": "Automatizada"}.get(v.get("transmission"), ""),
                "precio": v.get("price"), "moneda": "MXN", "iva": "Desconocido",
                "tipo_precio": "Desde" if grupo else "Contado publicado", "evidencia": "Inventario original" if grupo else "Ficha individual",
                "lugar": (v.get("location") or "") + ", Edo. Méx.", "vendedor": "Panamotors", "tipo_vendedor": "distribuidor", "tipo": "tracto",
                "nota": f"Grupo de {v['group_count']} unidades, km {v.get('odometer'):,}–{v.get('odometer_max'):,}" if grupo else "",
                "reacondicionado": v.get("is_reconditioned"), "consulta": HOY, "img_url": v.get("main_image", "")})
    log(f"  Panamotors: {len(out)} de interés")
    return out

def leer_nastrac(log=print):
    h = get("https://www.nastracseminuevos.com/")
    ligas = sorted(set(re.findall(r'href="(https://www\.nastracseminuevos\.com/vehiculo/\d+)"', h)))
    out = []
    for u in ligas:
        s = texto(get(u))
        m = re.search(r"Inventario > (.+?) \1? ?(.*?) • (\d{4}) • ([\d,]+) km", s) or re.search(r"Inventario > (\S+ \S+) .*? (\d{4}) • ([\d,]+) km", s)
        t = re.search(r"Inventario > ([^>]+?) \1", s)
        tit = re.search(r"^(.*?) \| NASTRAC", s)
        nombre = tit.group(1) if tit else ""
        marca, modelo = (nombre.split(" ", 1) + [""])[:2]
        anio = numero(re.search(r"Año (\d{4})", s).group(1)) if re.search(r"Año (\d{4})", s) else None
        prod = producto(marca, modelo)
        if not _ok(prod, anio): continue
        g = lambda p: (re.search(p, s).group(1).strip() if re.search(p, s) else "")
        out.append({"id": "NAS-" + u.rsplit("/", 1)[1], "fuente": "NASTRAC", "url": u, "producto": prod, "marca": marca, "modelo": modelo,
            "anio": anio, "km": numero(g(r"Kilometraje ([\d,]+) km")), "motor_raw": g(r"Motor (.+?) Transmisión"),
            "motor": motor_normalizado(g(r"Motor (.+?) Transmisión")), "trans_raw": g(r"Transmisión (\S+)"), "trans": transmision_tipo(g(r"Transmisión (\S+)")),
            "precio": numero(g(r"\$([\d,]+)")), "moneda": "MXN", "iva": iva_de_texto(s), "tipo_precio": "Contado publicado",
            "evidencia": "Ficha individual", "stock": g(r"Stock # (\S+)"), "lugar": "Zapopan, Jal.", "vendedor": "NASTRAC",
            "tipo_vendedor": "distribuidor", "tipo": "tracto", "consulta": HOY})
    log(f"  NASTRAC: {len(out)} de interés")
    return out

def leer_quality(log=print):
    h = get("https://qualitytrucks.com.mx/seminuevos/")
    ligas = sorted(set(re.findall(r'"url":"(https://qualitytrucks\.com\.mx/seminuevos/[^"]+/)"', h)))
    out = []
    for u in ligas:
        if not re.search(r"/(kenworth/t680|freightliner/(new-)?cascadia|international/lt)", u): continue
        s = get(u)
        ld = None
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                d = json.loads(m.group(1))
                if "Vehicle" in (d.get("@type") or []): ld = d
            except Exception: pass
        if not ld: continue
        anio = numero(ld.get("vehicleModelDate"))
        prod = producto(ld.get("brand", {}).get("name"), ld.get("model"))
        if not _ok(prod, anio): continue
        oferta = ld.get("offers") or {}
        eng = (ld.get("vehicleEngine") or {}).get("name", "")
        out.append({"id": "QT-" + ld.get("sku", u.rstrip("/").rsplit("/", 1)[1]), "fuente": "QT", "url": u, "producto": prod,
            "marca": ld["brand"]["name"], "modelo": ld.get("model"), "anio": anio, "km": numero((ld.get("mileageFromOdometer") or {}).get("value")),
            "motor_raw": eng, "motor": motor_normalizado(eng), "trans_raw": ld.get("vehicleTransmission", ""), "trans": transmision_tipo(ld.get("vehicleTransmission")),
            "precio": numero(oferta.get("price")), "moneda": oferta.get("priceCurrency", "MXN"), "iva": iva_de_texto(texto(s)),
            "tipo_precio": "Contado publicado", "evidencia": "Ficha individual", "lugar": "Querétaro, Qro.", "vendedor": "Quality Trucks",
            "tipo_vendedor": "distribuidor", "tipo": "tracto" if (ld.get("category") or "Tracto").lower().startswith("tracto") else ld.get("category", "").lower(),
            "consulta": HOY, "img_url": (ld.get("image") or [""])[0]})
    log(f"  Quality Trucks: {len(out)} de interés")
    return out

def leer_scania(log=print):
    h = get("https://seminuevos.scania.com/?s=kenworth&post_type=product")
    ligas = sorted(set(re.findall(r'href="(https://seminuevos\.scania\.com/p/[^"]+)"', h)))
    out = []
    for u in ligas:
        s = texto(get(u))
        g = lambda p: (re.search(p, s).group(1).strip() if re.search(p, s) else "")
        prod = producto(g(r"Marca: (\S+)"), g(r"Modelo: (.+?) Configuración"))
        anio = numero(g(r"Año: (\d{4})"))
        if not _ok(prod, anio): continue
        hp = g(r"Motor: (\d+)")
        out.append({"id": "SCA-" + u.rstrip("/").rsplit("/", 1)[1], "fuente": "SCA", "url": u, "producto": prod, "marca": "Kenworth",
            "modelo": "T680", "anio": anio, "km": numero(g(r"Kilometraje: (\d+)")), "motor_raw": (hp + " hp") if hp else "", "motor": "",
            "trans_raw": "", "trans": "", "precio": numero(g(r"\$ ?([\d,]+)(?:\.00)? \+ ?IVA")), "moneda": "MXN",
            "iva": "Más IVA" if "+ IVA" in s or "+IVA" in s else "Desconocido", "tipo_precio": "Contado publicado", "evidencia": "Ficha individual",
            "lugar": "México", "vendedor": "Scania Seminuevos", "tipo_vendedor": "distribuidor", "tipo": "tracto", "consulta": HOY})
    log(f"  Scania Seminuevos: {len(out)} de interés")
    return out

SEMI = ["https://www.seminuevos.com/usados/-/camiones/-/kenworth/t680",
        "https://www.seminuevos.com/usados/-/camiones/-/freightliner/cascadia",
        "https://www.seminuevos.com/usados/-/camiones/-/international/lt"]

def leer_seminuevos(log=print):
    ligas = []
    for base in SEMI:
        for p in range(1, 6):
            try: h = get(base + (f"?page={p}" if p > 1 else ""))
            except Exception: break
            nuevas = [l for l in dict.fromkeys(re.findall(r'href="(/vehicle/camiones-[^"]+)"', h)) if l not in ligas]
            if not nuevas: break
            ligas += nuevas
    out = []
    for l in ligas:
        u = "https://www.seminuevos.com" + l
        s = texto(get(u))
        g = lambda p: (re.search(p, s).group(1).strip() if re.search(p, s) else "")
        marca, modelo, anio = g(r"Marca (\S+) Modelo"), g(r"Modelo (.+?) Versión"), numero(g(r"Año (\d{4})"))
        prod = producto(marca, modelo)
        if not _ok(prod, anio): continue
        desc = g(r"Acerca de este vehículo (.+?) Especificaciones")
        vend = g(r"Extras .*? (\S[^$]{2,60}?) Ver más autos")
        out.append({"id": "SEM-" + l.rsplit("/", 1)[1], "fuente": "SEM", "url": u, "producto": prod, "marca": marca, "modelo": modelo,
            "anio": anio, "km": numero(g(r"Recorrido ([\d,]+) Kms")), "motor_raw": g(r"Motor (.{3,30}?)(?: \d[\d,]* km| Transmisión|$)"),
            "motor": motor_normalizado(desc), "trans_raw": g(r"Transmisión (\S+)"), "trans": transmision_tipo(desc + " " + g(r"Transmisión (\S+)")),
            "precio": numero(g(r"\$([\d,’']+) (?:Negociable|Precio|Este)")) or numero(g(r"\$([\d,’']+)")), "moneda": "MXN", "iva": iva_de_texto(desc),
            "tipo_precio": "Contado publicado", "evidencia": "Ficha individual", "lugar": g(r"Ciudad (.+?) Recorrido"),
            "vendedor": vend, "tipo_vendedor": "distribuidor" if vend else "particular",
            "tipo": "tracto" if re.search(r"Subtipo (Trailer|Tracto)", s) else "otro", "consulta": HOY})
    log(f"  Seminuevos.com: {len(out)} de interés")
    return out

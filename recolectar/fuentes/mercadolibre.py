"""Mercado Libre México: listados de búsqueda + ficha de cada anuncio."""
import json, re
from ..comun import get, numero, iva_de_texto, motor_normalizado, transmision_tipo, producto, HOY

BUSQUEDAS = [
    "https://vehiculos.mercadolibre.com.mx/camiones/kenworth/t680/",
    "https://vehiculos.mercadolibre.com.mx/camiones/freightliner/cascadia/2022/",
    "https://vehiculos.mercadolibre.com.mx/camiones/freightliner/cascadia/2023/",
    "https://vehiculos.mercadolibre.com.mx/camiones/freightliner/cascadia/2024/",
    "https://vehiculos.mercadolibre.com.mx/camiones/international/2022/",
    "https://vehiculos.mercadolibre.com.mx/camiones/international/2023/",
    "https://vehiculos.mercadolibre.com.mx/camiones/international/2024/",
]

def _tarjetas(h):
    out = []
    for m in re.finditer(r'"polycard":\{"unique_id"', h):
        # cada tarjeta es un objeto JSON; se recorta contando llaves
        i = m.start() + len('"polycard":'); prof = 0
        for j in range(i, min(len(h), i + 20000)):
            if h[j] == "{": prof += 1
            elif h[j] == "}":
                prof -= 1
                if prof == 0: break
        try: out.append(json.loads(h[i:j + 1]))
        except Exception: pass
    return out

def _atributo(h, nombre):
    m = re.search(r'\{"id":"' + re.escape(nombre) + r'","text":"([^"]*)"\}', h)
    return m.group(1).encode().decode("unicode_escape").encode("latin1").decode("utf-8", "ignore") if m else ""

def _tipo(titulo, desc):
    t = (titulo + " " + desc[:400]).lower()
    if re.search(r"volteo", t): return "volteo"
    if re.search(r"tort[oó]n|rab[oó]n|chasis cabina", t) and not re.search(r"tracto", titulo.lower()): return "torton"
    if re.search(r"\bgr[uú]a\b|pipa|revolvedora", titulo.lower()): return "otro"
    return "tracto"

def leer(log=print):
    vistos, anuncios = set(), []
    for base in BUSQUEDAS:
        for desde in (1, 49, 97, 145):
            url = base if desde == 1 else base + f"_Desde_{desde}_NoIndex_True"
            try: h = get(url)
            except Exception as e: log(f"  ML {url}: {e}"); break
            cards = _tarjetas(h)
            if not cards: break
            nuevos = 0
            for c in cards:
                md = c.get("metadata", {}); iid = md.get("id")
                if not iid or iid in vistos: continue
                vistos.add(iid); nuevos += 1
                comp = {x["type"]: x for x in c.get("components", [])}
                titulo = comp.get("title", {}).get("title", {}).get("text", "")
                attrs = comp.get("attributes_list", {}).get("attributes_list", {}).get("texts", [])
                precio = comp.get("price", {}).get("price", {}).get("current_price", {})
                anuncios.append({"_iid": iid, "_url": "https://" + md.get("url", "").replace("\\u002F", "/"),
                    "titulo": titulo, "anio": numero(attrs[0]) if attrs else None, "km": numero(attrs[1]) if len(attrs) > 1 else None,
                    "precio": precio.get("value"), "moneda": precio.get("currency_id") or precio.get("currency", "MXN"),
                    "lugar": comp.get("location", {}).get("location", {}).get("text", ""),
                    "img": (c.get("pictures", {}).get("pictures") or [{}])[0].get("id", "")})
            log(f"  ML {url}: {len(cards)} tarjetas, {nuevos} nuevas")
            if len(cards) < 48: break
    salida = []
    for a in anuncios:
        marca_modelo = a["titulo"]
        try: h = get(a["_url"].split("#")[0])
        except Exception as e:
            log(f"  ML ficha {a['_iid']}: {e}"); continue
        marca, modelo = _atributo(h, "Marca"), _atributo(h, "Modelo")
        prod = producto(marca or marca_modelo, (modelo + " " + marca_modelo))
        if not prod: continue
        anio = numero(_atributo(h, "Año")) or a["anio"]
        if prod != "kenworth-t680" and not (anio and 2021 <= anio <= 2025): continue
        dm = re.search(r'"id":"description","type":"description","state":"VISIBLE","title":"Descripción","content":"((?:[^"\\]|\\.)*)"', h)
        desc = json.loads('"' + dm.group(1) + '"') if dm else ""
        vend = re.search(r'"seller_name":\{"title":\{"text":"([^"]*)"[^}]*\},"label":\{"text":"([^"]*)"', h)
        pub = re.search(r'Publicado hace (\d+) (d[ií]as?|mes(?:es)?|años?|semanas?)', h)
        dias = None
        if pub:
            n = int(pub.group(1)); u = pub.group(2)
            dias = n * (30 if u.startswith("mes") else 365 if u.startswith("año") else 7 if u.startswith("sem") else 1)
        motor_raw = _atributo(h, "Marca del motor")
        trans_raw = _atributo(h, "Transmisión")
        mtx = re.search(r"(DT12|ULTRA ?SHIFT|I-?SHIFT|ENDURANT|MDRIVE|EATON FULLER[^,.]{0,25}|RTLO[\w-]*|ALLISON)", desc.upper())
        salida.append({
            "id": "MLM-" + a["_iid"][3:], "fuente": "ML", "url": a["_url"].split("#")[0], "titulo": a["titulo"],
            "producto": prod, "marca": marca, "modelo": modelo, "anio": anio, "km": numero(_atributo(h, "Kilómetros")) or a["km"],
            "motor_raw": motor_raw, "motor": motor_normalizado(motor_raw or desc[:300]),
            "trans_raw": (trans_raw + (" · " + mtx.group(1) if mtx else "")).strip(" ·"),
            "trans": transmision_tipo(mtx.group(1) if mtx else trans_raw),
            "precio": a["precio"], "moneda": a["moneda"], "iva": iva_de_texto(desc),
            "tipo_precio": "Contado publicado", "evidencia": "Ficha individual",
            "lugar": a["lugar"], "vendedor": vend.group(1) if vend else "",
            "tipo_vendedor": "distribuidor" if vend and re.search(r"Agencia|Concesionaria|Tienda|Profesional", vend.group(2), re.I) else "particular",
            "tipo": _tipo(a["titulo"], desc), "dias_publicado": dias, "consulta": HOY, "img": a["img"],
        })
        log(f"  ML ficha {salida[-1]['id']} {prod} {anio} {salida[-1]['precio']}")
    return salida

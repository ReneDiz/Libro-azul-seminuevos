"""Utilidades compartidas por los lectores de fuentes."""
import json, re, time, html, urllib.request, urllib.error, datetime

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
HOY = datetime.date.today().isoformat()
_ultimo = {}

def get(url, pausa=1.5, intentos=3):
    """Descarga una página con pausa entre peticiones al mismo sitio (para no saturarlo)."""
    host = url.split("/")[2]
    espera = pausa - (time.time() - _ultimo.get(host, 0))
    if espera > 0: time.sleep(espera)
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-MX,es;q=0.9"})
            with urllib.request.urlopen(req, timeout=40) as r:
                _ultimo[host] = time.time()
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410): raise
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"No se pudo leer {url}")

def texto(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", h, flags=re.S))).strip()

def numero(s):
    if s is None: return None
    if isinstance(s, (int, float)): return s
    d = re.sub(r"[^\d]", "", str(s))
    return int(d) if d else None

def iva_de_texto(t):
    """Busca en la descripción si el precio dice IVA incluido o más IVA."""
    t = (t or "").lower()
    if re.search(r"(m[aá]s|\+)\s*i\.?v\.?a|no incluye\s+(el\s+)?i\.?v\.?a|sin\s+i\.?v\.?a", t): return "Más IVA"
    if re.search(r"i\.?v\.?a\.?\s+incluido|incluye\s+(el\s+)?i\.?v\.?a|con\s+i\.?v\.?a\s+incluido|precio\s+con\s+i\.?v\.?a", t): return "Incluido"
    return "Desconocido"

def motor_normalizado(s):
    """Nombre corto y consistente del motor (MX-13, X15, ISX, DD13, DD15, S13...)."""
    u = (s or "").upper()
    if not u.strip(): return ""
    if "MX-13" in u or "MX13" in u or "MX 13" in u: return "PACCAR MX-13"
    if "PACCAR" in u: return "PACCAR"
    if "X15" in u or "X-15" in u: return "Cummins X15"
    if "ISX" in u: return "Cummins ISX"
    if "ISM" in u: return "Cummins ISM"
    if "DD16" in u: return "Detroit DD16"
    if "DD15" in u: return "Detroit DD15"
    if "DD13" in u: return "Detroit DD13"
    if "S13" in u: return "International S13"
    if "A26" in u: return "International A26"
    if "N13" in u or "MAXXFORCE" in u: return "Navistar N13"
    if "CUMMINS" in u or "CUMINS" in u or "CUMING" in u or "CUMMING" in u: return "Cummins"
    if "DETROIT" in u: return "Detroit"
    if "CATERPILLAR" in u or re.search(r"\bCAT\b", u): return "Caterpillar"
    return ""  # sin marca de motor reconocible: el texto original queda en motor_raw

def transmision_tipo(s):
    u = (s or "").upper()
    if not u.strip(): return ""
    if any(k in u for k in ("DT12", "ULTRASHIFT", "ULTRA SHIFT", "I-SHIFT", "MDRIVE", "ENDURANT", "AUTOMATIZ", "AMT", "TRAXON")): return "Automatizada"
    if "AUTOM" in u or "ALLISON" in u: return "Automática"
    if "MANUAL" in u or "ESTANDAR" in u or "ESTÁNDAR" in u or "FULLER" in u or "RTLO" in u or "VEL" in u: return "Manual"
    return ""

def producto(marca, modelo):
    """Agrupa el anuncio en uno de los productos del Libro Azul (o None si no aplica)."""
    m, mo = (marca or "").upper(), (modelo or "").upper()
    if "KENWORTH" in m and "T680" in mo.replace(" ", ""): return "kenworth-t680"
    if "FREIGHTLINER" in m and ("CASCADIA" in mo or "NEWCAS" in mo or "NEW CAS" in mo): return "freightliner-cascadia"
    if ("INTERNATIONAL" in m or m.strip() == "4") and re.search(r"\bLT\b|LT\s*HI|LT6", mo): return "international-lt"
    return None

def guardar(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)

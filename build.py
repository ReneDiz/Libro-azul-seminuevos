#!/usr/bin/env python3
"""Libro Azul Advance · cotizador interactivo de seminuevos de trabajo.
Lee data/*.json y genera index.html (toda la lógica de consulta corre en el navegador)."""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
D = json.load(open(ROOT / "data/kenworth-t680.json"))

def motor_tag(a):
    m = a["motor"].upper()
    if m.startswith("PACCAR") or "MX-13" in m: return "paccar"
    if m.startswith("CUMMINS"): return "cummins"
    return "sd"

anuncios = []
for a in D["anuncios"]:
    anuncios.append({
        "id": a["id"], "f": a["f"], "anio": a["anio"], "km": a["km"], "precio": a["precio"], "mon": a["mon"],
        "motor": a["motor"], "mt": motor_tag(a), "trans": a["trans"], "origen": a["origen"], "lugar": a["lugar"].replace("Nuevo León", "N.L.") if a["lugar"] == "Nuevo León" else a["lugar"],
        "vend": a["vend"], "dealer": a["f"] != "ML" or bool(a["vend"]), "tipo": a["tipo"], "dup": bool(a.get("dup")),
        "nota": a.get("nota", ""), "img": a.get("img", ""),
        "url": a.get("url") or (f"https://vehiculo.mercadolibre.com.mx/{a['id']}-_JM" if a["f"] == "ML" else D["fuentes"][a["f"]]["url"]),
    })

DATA = json.dumps({"modelo": D["modelo"], "corte": D["corte"], "fx": D["tipo_cambio_mxn_usd"],
                   "fuentes": D["fuentes"], "anuncios": anuncios}, ensure_ascii=False)

HTML = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Libro Azul Advance · Kenworth T680</title>
<meta name="robots" content="noindex,nofollow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Libro Azul Advance">
<meta property="og:title" content="Libro Azul Advance · Kenworth T680">
<meta property="og:description" content="Valor de referencia de seminuevos de trabajo por año, motor y kilometraje, con los anuncios reales en venta en México.">
<meta property="og:url" content="https://libro-azul-advance.netlify.app/">
<meta property="og:image" content="https://libro-azul-advance.netlify.app/og-libro-azul-t680-v2.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{--bg:#f3f5ef;--bg2:#f8f9f5;--surface:#fff;--line:#e0e4d7;--text:#1b2413;--muted:#5d6a4f;--faint:#8a957c;--track:#e6e9dd;
--lima:#C4D600;--lima-ink:#67750a;--lima-soft:rgba(196,214,0,.22);--lima-line:rgba(150,166,0,.5);
--good:#5c9a13;--warn:#c9820b;--crit:#d63b3b;--shadow:0 1px 2px rgba(30,40,20,.05),0 10px 26px -16px rgba(40,55,20,.28)}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-variant-numeric:tabular-nums}
a{color:var(--lima-ink)}
button{font:inherit;color:inherit}
.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,#fff 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:9px 24px;display:flex;align-items:center;gap:18px}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;letter-spacing:-.01em}
.brand img{height:40px;width:auto;display:block;margin:-6px 0}
.brand small{color:var(--faint);font-weight:500}
nav{display:flex;gap:6px;margin-left:auto}
nav a{text-decoration:none;color:var(--muted);padding:6px 12px;border-radius:9px;font-weight:500}
nav a.on{background:var(--lima-soft);color:var(--text);box-shadow:inset 2px 0 0 var(--lima)}
nav a.add{border:1px dashed var(--line)}
main{max-width:1180px;margin:0 auto;padding:26px 24px 70px}
.label{font-size:11px;text-transform:uppercase;letter-spacing:.14em;color:var(--faint);margin:0 0 8px}
h1{font-size:30px;line-height:1.1;margin:0 0 6px;letter-spacing:-.02em}
h1 b{color:var(--lima-ink);font-weight:600}
.sub{color:var(--muted);margin:0 0 20px}

/* consulta */
.consulta{display:grid;grid-template-columns:380px 1fr;gap:18px;margin-bottom:18px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:18px 20px;box-shadow:var(--shadow)}
.card h2{font-size:16px;margin:0 0 4px}
.card .hint{color:var(--muted);font-size:13px;margin:0 0 14px}
.field{margin:0 0 16px}
.field .label{margin-bottom:6px}
.seg{display:flex;flex-wrap:wrap;gap:4px}
.seg button{border:1px solid var(--line);background:#fff;border-radius:9px;padding:7px 0;min-width:46px;flex:1;cursor:pointer;color:var(--muted);font-weight:500}
.seg button.on{background:var(--lima-soft);border-color:var(--lima-line);color:var(--text);font-weight:600}
.seg button:disabled{opacity:.35;cursor:default}
.seg.years button{min-width:0;flex:1 1 calc(20% - 4px)}
input[type=range]{width:100%;accent-color:var(--lima-ink);margin:6px 0 2px}
.kmv{display:flex;justify-content:space-between;color:var(--muted);font-size:12.5px}
.kmv b{color:var(--text);font-size:15px}

.resultado{display:flex;flex-direction:column}
.resultado .big{font-size:48px;font-weight:700;letter-spacing:-.03em;line-height:1;margin:2px 0 4px}
.resultado .big small{font-size:16px;color:var(--muted);font-weight:500;letter-spacing:0;margin-left:6px}
.resultado .unit{color:var(--muted);margin-bottom:16px}
.unit b{color:var(--text)}
.bar{position:relative;height:14px;border-radius:7px;background:linear-gradient(90deg,#e4e8da 0%,var(--lima-soft) 50%,#e4e8da 100%);margin:28px 0 8px}
.bar .zona{position:absolute;top:0;bottom:0;background:var(--lima);opacity:.55;border-radius:7px}
.bar .pin{position:absolute;top:-8px;width:4px;height:30px;background:var(--text);border-radius:2px;transform:translateX(-2px)}
.bar .pin::after{content:attr(data-v);position:absolute;top:-24px;left:50%;transform:translateX(-50%);white-space:nowrap;font-size:12px;font-weight:600;background:var(--text);color:#fff;padding:2px 7px;border-radius:6px}
.barlbl{display:flex;justify-content:space-between;color:var(--faint);font-size:12px}
.barlbl span b{display:block;color:var(--text);font-size:13px}
.tres{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}
.mini{background:var(--bg2);border:1px solid var(--line);border-radius:11px;padding:10px 12px}
.mini .v{font-size:18px;font-weight:600;letter-spacing:-.02em}
.mini .label{margin:0 0 2px}
.mini .d{color:var(--muted);font-size:12px}
.aviso{margin-top:14px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:10px}

/* tabs */
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin:8px 0 18px}
.tabs button{border:0;background:none;padding:10px 14px;cursor:pointer;color:var(--muted);font-weight:500;border-bottom:2px solid transparent;margin-bottom:-1px}
.tabs button.on{color:var(--text);border-color:var(--lima);font-weight:600}
.pane{display:none}.pane.on{display:block}

/* comparables */
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.cmp{background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow);text-decoration:none;color:inherit;display:block;transition:transform .15s}
.cmp:hover{transform:translateY(-2px)}
.cmp .ph{aspect-ratio:4/3;background:var(--track) center/cover no-repeat;position:relative}
.cmp .ph .tag{position:absolute;left:10px;top:10px;background:rgba(27,36,19,.82);color:#fff;font-size:11px;padding:3px 8px;border-radius:20px;font-weight:600;letter-spacing:.04em}
.cmp .ph .tag.pac{background:var(--lima);color:#1b2413}
.cmp .ph .sim{position:absolute;right:10px;top:10px;background:rgba(255,255,255,.9);font-size:11px;padding:3px 8px;border-radius:20px;color:var(--muted);font-weight:600}
.cmp .b{padding:12px 14px}
.cmp .p{font-size:19px;font-weight:700;letter-spacing:-.02em}
.cmp .p small{font-weight:500;color:var(--faint);font-size:12px;margin-left:4px}
.cmp .t{font-weight:600;margin-top:2px}
.cmp .m{color:var(--muted);font-size:12.5px;margin-top:2px}
.cmp .m span{display:inline-block;margin-right:8px}
.cmp.dim{opacity:.55}
.more{margin-top:14px;text-align:center}
.more button{border:1px solid var(--line);background:#fff;border-radius:9px;padding:8px 16px;cursor:pointer;color:var(--muted)}

/* gráficos */
.chart-card{position:relative}
svg text{font-family:inherit}
.grid-l{stroke:var(--track);stroke-width:1}
.tick{fill:var(--faint);font-size:11px}
.curva{fill:none;stroke:var(--lima-ink);stroke-width:2.5}
.banda{fill:var(--lima);opacity:.16}
.pt{stroke-width:1;cursor:pointer}
.pt.pac{fill:var(--lima);stroke:var(--lima-ink)}
.pt.cum{fill:#c9cfc0;stroke:#8a957c}
.pt.sd{fill:#fff;stroke:#b7bfaa}
.pt.sel{stroke:var(--text);stroke-width:2}
.pt.dimp{opacity:.25}
.tip{position:absolute;pointer-events:none;background:var(--text);color:#fff;padding:8px 10px;border-radius:8px;font-size:12px;line-height:1.35;display:none;max-width:260px;z-index:3;box-shadow:var(--shadow)}
.tip b{display:block;font-size:13px}
.legend{display:flex;gap:16px;color:var(--muted);font-size:12.5px;margin:0 0 6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.plazas{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.row{display:grid;grid-template-columns:150px 1fr 90px 40px;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--line);font-size:13px}
.row:last-child{border:0}
.row .bg{height:10px;border-radius:5px;background:var(--track);overflow:hidden}
.row .bg i{display:block;height:100%;background:var(--lima);border-radius:5px}
.row .n{text-align:right;color:var(--faint)}
.row .v{text-align:right;font-weight:600}
.fuentes{margin-top:26px;color:var(--faint);font-size:12.5px}
.fuentes a{margin-right:14px}
.cmp .ph .sim{max-width:46%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media(max-width:600px){.cmp .ph .sim{display:none}}
@media(max-width:900px){.consulta{grid-template-columns:1fr}.grid{grid-template-columns:1fr 1fr}.plazas{grid-template-columns:1fr}.resultado .big{font-size:38px}main{padding:18px 16px}}
</style></head><body>
<header class="top">
  <div class="brand"><img src="sticker.png" alt="">Libro Azul Advance <small>· seminuevos de trabajo</small></div>
  <nav><a class="on" href="#">Kenworth T680</a><a class="add" href="#" title="Siguiente modelo">+ modelo</a></nav>
</header>
<main>
  <p class="label" id="corte"></p>
  <p class="sub">Elige la unidad y el valor se calcula al momento con los anuncios reales que hay en venta en México.</p>

  <section class="consulta">
    <div class="card">
      <h2>Tu unidad</h2>
      <p class="hint">Cada cambio recalcula el valor y los comparables.</p>
      <div class="field"><div class="label">Año modelo</div><div class="seg years" id="anio"></div></div>
      <div class="field"><div class="label">Motor</div><div class="seg" id="motor">
        <button data-v="paccar" class="on">PACCAR MX-13</button><button data-v="cummins">Cummins ISX / X15</button></div></div>
      <div class="field"><div class="label">Kilometraje</div>
        <input type="range" id="km" min="100000" max="1600000" step="25000" value="700000">
        <div class="kmv"><span>100 mil</span><b id="kmv">700 mil km</b><span>1.6 M</span></div></div>
      <div class="field"><div class="label">Quién vende</div><div class="seg" id="vend">
        <button data-v="0" class="on">Particular</button><button data-v="1">Distribuidor con garantía</button></div></div>
    </div>

    <div class="card resultado">
      <div class="label">Valor de referencia Advance</div>
      <div class="big" id="valor">—</div>
      <div class="unit" id="unidad"></div>
      <div class="bar" id="bar"><div class="zona" id="zona"></div><div class="pin" id="pin" data-v=""></div></div>
      <div class="barlbl"><span>Mínimo publicado<b id="bmin"></b></span><span style="text-align:center">Rango justo<b id="bjusto"></b></span><span style="text-align:right">Máximo publicado<b id="bmax"></b></span></div>
      <div class="tres">
        <div class="mini"><div class="label">Comparables</div><div class="v" id="ncmp">—</div><div class="d" id="ncmpd"></div></div>
        <div class="mini"><div class="label">Mediana comparables</div><div class="v" id="med">—</div><div class="d">lo que piden hoy</div></div>
        <div class="mini"><div class="label">Pierde por año</div><div class="v" id="dep">—</div><div class="d">entre un modelo y el anterior</div></div>
      </div>
      <div class="aviso" id="aviso"></div>
    </div>
  </section>

  <div class="tabs" id="tabs">
    <button class="on" data-t="cmp">Comparables</button>
    <button data-t="curva">Curva de valor</button>
    <button data-t="km">Por kilometraje</button>
    <button data-t="plazas">Por plaza</button>
    <button data-t="todos">Todos los anuncios</button>
  </div>

  <section class="pane on" id="p-cmp">
    <div class="grid" id="cmpgrid"></div>
    <div class="more"><button id="masbtn">Ver más anuncios parecidos</button></div>
  </section>

  <section class="pane" id="p-curva">
    <div class="card chart-card">
      <h2>Cómo se deprecia el T680</h2>
      <p class="hint">La línea es el valor de referencia para tu motor, kilometraje y tipo de vendedor en cada año. Los puntos son anuncios reales; pasa el cursor sobre ellos.</p>
      <div class="legend"><span><i style="background:var(--lima);border:1px solid var(--lima-ink)"></i>PACCAR</span><span><i style="background:#c9cfc0;border:1px solid #8a957c"></i>Cummins</span><span><i style="background:#fff;border:1px solid #b7bfaa"></i>Sin motor declarado</span></div>
      <div id="curva"></div><div class="tip" id="tip1"></div>
    </div>
  </section>

  <section class="pane" id="p-km">
    <div class="card chart-card">
      <h2>Precio contra kilometraje</h2>
      <p class="hint">Anuncios del año elegido y un año a cada lado. El kilometraje pesa menos que el año y que quién vende.</p>
      <div id="kmchart"></div><div class="tip" id="tip2"></div>
    </div>
  </section>

  <section class="pane" id="p-plazas">
    <div class="plazas">
      <div class="card"><h2>Dónde está la oferta</h2><p class="hint">Anuncios por estado, todos los años y motores.</p><div id="plazas-n"></div></div>
      <div class="card"><h2>Precio mediano por estado</h2><p class="hint">Solo estados con 3 anuncios o más.</p><div id="plazas-p"></div></div>
    </div>
  </section>

  <section class="pane" id="p-todos">
    <div class="grid" id="todosgrid"></div>
  </section>

  <p class="fuentes" id="fuentes"></p>
</main>
<script>
const DATA = __DATA__;
const fx = DATA.fx;
const fmt = n => '$' + Math.round(n).toLocaleString('es-MX');
const fmtk = n => !n ? 'km s/d' : (n >= 1e6 ? (n/1e6).toFixed(1).replace('.0','') + ' M km' : Math.round(n/1000).toLocaleString('es-MX') + ' mil km');
const img = a => a.img ? `https://http2.mlstatic.com/D_NQ_NP_2X_${a.img}-O.webp` : '';
const mxn = a => a.mon === 'MXN' ? a.precio : a.precio * fx;

// Universo comparable: tractocamiones, sin duplicados, en pesos
const BASE = DATA.anuncios.filter(a => a.tipo === 'tracto' && !a.dup && a.mon === 'MXN');
const YEARS = [...new Set(BASE.map(a => a.anio))].sort();

// Factores de ajuste (regresión log-lineal sobre los anuncios en pesos): +12 % por año modelo, +18 % distribuidor
const F_ANIO = 0.12, F_DEALER = 0.18;
const st = { anio: 2018, motor: 'paccar', km: 700000, vend: 0 };

function ajustar(a, s){ // trae el precio del anuncio a la unidad consultada
  let p = a.precio;
  p *= Math.exp(F_ANIO * (s.anio - a.anio));
  if (a.dealer && !s.vend) p /= Math.exp(F_DEALER);
  if (!a.dealer && s.vend) p *= Math.exp(F_DEALER);
  return p;
}
function similitud(a, s){
  let d = Math.abs(a.anio - s.anio) * 1.0;
  if (a.km) d += Math.min(Math.abs(a.km - s.km) / 400000, 1.5); else d += .5;
  if (a.mt !== s.motor) d += (a.mt === 'sd' ? .8 : 2.5);
  if (!!a.dealer !== !!s.vend) d += .6;
  return d;
}
function wmedian(items){ // items: [{v,w}]
  const xs = items.slice().sort((p,q)=>p.v-q.v); const tot = xs.reduce((s,x)=>s+x.w,0); let acc = 0;
  for (const x of xs){ acc += x.w; if (acc >= tot/2) return x.v; } return xs[xs.length-1].v;
}
function calcularCrudo(s){
  const ranked = BASE.map(a => ({a, d: similitud(a, s)})).sort((p,q)=>p.d-q.d);
  let cmp = ranked.filter(r => r.d <= 2.2);
  if (cmp.length < 5) cmp = ranked.slice(0, 5);
  const items = cmp.map(r => ({v: ajustar(r.a, s), w: 1/(0.4 + r.d)}));
  const est = wmedian(items);
  const vals = items.map(i=>i.v).sort((p,q)=>p-q);
  const q = p => vals[Math.min(vals.length-1, Math.floor((vals.length-1)*p))];
  const mismoAnio = BASE.filter(a => a.anio === s.anio);
  const todos = BASE.map(a=>a.precio);
  return { est, lo: Math.min(q(.25), est*.93), hi: Math.max(q(.75), est*1.07), cmp, ranked,
    medCmp: wmedian(cmp.map(r=>({v:r.a.precio,w:1}))), nAnio: mismoAnio.length,
    min: Math.min(...todos), max: Math.max(...todos) };
}

// La referencia por año no puede bajar al subir el año modelo: se suaviza con PAV (regresión isotónica)
// sobre la estimación cruda de cada año y se reparte el mismo ajuste al rango justo.
function calcular(s){
  const crudo = YEARS.map(y => calcularCrudo({...s, anio: y}));
  const v = crudo.map(c => c.est), w = crudo.map(c => c.cmp.length);
  const blocks = [];
  for (let i = 0; i < v.length; i++){
    let b = {sum: v[i]*w[i], w: w[i], n: 1};
    while (blocks.length && blocks[blocks.length-1].sum/blocks[blocks.length-1].w > b.sum/b.w){ const p = blocks.pop(); b = {sum: p.sum+b.sum, w: p.w+b.w, n: p.n+b.n}; }
    blocks.push(b);
  }
  const iso = []; for (const b of blocks) for (let k = 0; k < b.n; k++) iso.push(b.sum/b.w);
  const i = YEARS.indexOf(s.anio), c = crudo[i], k = iso[i] / c.est;
  return {...c, est: iso[i], lo: c.lo * k, hi: c.hi * k, curva: YEARS.map((y, j) => ({y, est: iso[j], lo: crudo[j].lo * iso[j]/crudo[j].est, hi: crudo[j].hi * iso[j]/crudo[j].est}))};
}

// ---------- UI de consulta ----------
const $ = id => document.getElementById(id);
function segs(id, values, cur, labels){
  const el = $(id); el.innerHTML = values.map(v => `<button data-v="${v}" class="${v==cur?'on':''}">${labels?labels(v):v}</button>`).join('');
}
segs('anio', YEARS, st.anio);
document.querySelectorAll('.seg').forEach(seg => seg.addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  seg.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  const k = seg.id; st[k] = k === 'anio' || k === 'vend' ? +b.dataset.v : b.dataset.v; render();
}));
$('km').addEventListener('input', e => { st.km = +e.target.value; $('kmv').textContent = fmtk(st.km); render(); });

let mostrar = 8;
$('masbtn').addEventListener('click', () => { mostrar += 8; render(); });

function card(a, extra){
  const tag = a.mt === 'paccar' ? '<span class="tag pac">PACCAR</span>' : a.mt === 'cummins' ? '<span class="tag">CUMMINS</span>' : '<span class="tag" style="background:#8a957c">MOTOR S/D</span>';
  const usd = a.mon === 'USD';
  return `<a class="cmp ${extra&&extra.dim?'dim':''}" href="${a.url}" target="_blank" rel="noopener">
    <div class="ph" style="background-image:url('${img(a)}')">${tag}${extra&&extra.sim!=null?`<span class="sim">${extra.sim}</span>`:''}</div>
    <div class="b"><div class="p">${usd?'US$ '+a.precio.toLocaleString('es-MX'):fmt(a.precio)}<small>${usd?'≈ '+fmt(mxn(a)):a.dealer?'distribuidor':'particular'}</small></div>
    <div class="t">${a.anio} · ${fmtk(a.km)}</div>
    <div class="m"><span>${a.motor || 'motor sin dato'}</span><span>${a.trans || ''}</span></div>
    <div class="m"><span>${a.lugar}</span>${a.origen?`<span>${a.origen}</span>`:''}${a.nota?`<span style="color:var(--warn)">${a.nota}</span>`:''}</div></div></a>`;
}

function render(){
  const r = calcular(st);
  $('valor').innerHTML = fmt(r.est) + '<small>MXN</small>';
  $('unidad').innerHTML = `Kenworth T680 <b>${st.anio}</b> · <b>${st.motor==='paccar'?'PACCAR MX-13':'Cummins'}</b> · <b>${fmtk(st.km)}</b> · ${st.vend?'distribuidor con garantía':'venta entre particulares'}`;
  const span = r.max - r.min, pct = v => Math.max(0, Math.min(100, (v - r.min) / span * 100));
  $('zona').style.left = pct(r.lo) + '%'; $('zona').style.width = (pct(r.hi) - pct(r.lo)) + '%';
  $('pin').style.left = pct(r.est) + '%'; $('pin').dataset.v = fmt(r.est);
  $('bmin').textContent = fmt(r.min); $('bmax').textContent = fmt(r.max); $('bjusto').textContent = fmt(r.lo) + ' – ' + fmt(r.hi);
  $('ncmp').textContent = r.cmp.length; $('ncmpd').textContent = `${r.nAnio} anuncios del ${st.anio}, ${BASE.length} del modelo`;
  $('med').textContent = fmt(r.medCmp);
  $('dep').textContent = Math.round((1 - Math.exp(-F_ANIO)) * 100) + ' %';
  const pacN = r.cmp.filter(x => x.a.mt === st.motor).length;
  $('aviso').textContent = pacN < 3 ? `Pocos anuncios con motor ${st.motor==='paccar'?'PACCAR':'Cummins'} para ${st.anio}: el valor se apoya en años vecinos y en el otro motor, ajustados. Tómalo como orientación.` : `Valor ajustado por año y tipo de vendedor a partir de ${r.cmp.length} anuncios publicados. Es precio pedido, no cerrado; el IVA depende de cada vendedor.`;
  $('cmpgrid').innerHTML = r.ranked.slice(0, mostrar).map(x => card(x.a, {sim: x.d <= .8 ? 'muy parecido' : x.d <= 2.2 ? 'parecido' : 'referencia', dim: x.d > 2.2})).join('');
  $('masbtn').style.display = mostrar >= r.ranked.length ? 'none' : '';
  drawCurva(r); drawKm(r);
}

// ---------- gráficos ----------
function tipOn(tipEl, host, a, ev){
  tipEl.style.display = 'block';
  tipEl.innerHTML = `<b>${a.anio} · ${fmt(a.precio)}</b>${a.motor||'motor s/d'} · ${fmtk(a.km)}<br>${a.lugar}${a.vend?' · '+a.vend:''}`;
  const rc = host.getBoundingClientRect();
  tipEl.style.left = (ev.clientX - rc.left + 14) + 'px'; tipEl.style.top = (ev.clientY - rc.top - 10) + 'px';
}
function bindTips(svg, tipEl, host, byId){
  svg.querySelectorAll('.pt').forEach(c => {
    c.addEventListener('mousemove', ev => tipOn(tipEl, host, byId[c.dataset.id], ev));
    c.addEventListener('mouseleave', () => tipEl.style.display = 'none');
    c.addEventListener('click', () => window.open(byId[c.dataset.id].url, '_blank'));
  });
}
const byId = Object.fromEntries(DATA.anuncios.map(a => [a.id, a]));

function drawCurva(r){
  const W = 1000, H = 380, PL = 70, PR = 20, PT = 20, PB = 40, ymin = 2013.5, ymax = 2024.5, pmax = 2600000;
  const sx = y => PL + (y - ymin) / (ymax - ymin) * (W - PL - PR), sy = p => PT + (1 - p / pmax) * (H - PT - PB);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%">`;
  for (let p = 0; p <= pmax; p += 500000) s += `<line class="grid-l" x1="${PL}" x2="${W-PR}" y1="${sy(p)}" y2="${sy(p)}"/><text class="tick" x="${PL-8}" y="${sy(p)+4}" text-anchor="end">${(p/1e6).toFixed(1)} M</text>`;
  for (let y = 2014; y <= 2024; y++) s += `<text class="tick" x="${sx(y)}" y="${H-14}" text-anchor="middle">${y}</text>`;
  // banda y línea de referencia por año
  const pts = r.curva;
  s += `<path class="banda" d="M${pts.map(p=>sx(p.y)+','+sy(p.hi)).join(' L')} L${pts.slice().reverse().map(p=>sx(p.y)+','+sy(p.lo)).join(' L')} Z"/>`;
  s += `<path class="curva" d="M${pts.map(p=>sx(p.y)+','+sy(p.est)).join(' L')}"/>`;
  let seed = 7; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  for (const a of BASE){ if (a.precio > pmax) continue;
    const sel = a.anio === st.anio && a.mt === st.motor;
    s += `<circle class="pt ${a.mt==='paccar'?'pac':a.mt==='cummins'?'cum':'sd'} ${sel?'sel':''} ${a.mt!==st.motor&&a.mt!=='sd'?'dimp':''}" data-id="${a.id}" cx="${sx(a.anio)+(rnd()-.5)*18}" cy="${sy(a.precio)}" r="${sel?7:5.5}"/>`; }
  const me = pts.find(p => p.y === st.anio);
  if (me) s += `<circle cx="${sx(me.y)}" cy="${sy(me.est)}" r="9" fill="none" stroke="var(--text)" stroke-width="2"/><text x="${sx(me.y)}" y="${sy(me.est)-16}" text-anchor="middle" font-size="12" font-weight="600" fill="var(--text)">${fmt(me.est)}</text>`;
  s += '</svg>';
  const host = $('curva').parentElement; $('curva').innerHTML = s; bindTips($('curva'), $('tip1'), host, byId);
}
function drawKm(r){
  const W = 1000, H = 340, PL = 70, PR = 20, PT = 20, PB = 40, kmax = 2100000, pmax = 2600000;
  const sx = k => PL + k / kmax * (W - PL - PR), sy = p => PT + (1 - p / pmax) * (H - PT - PB);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%">`;
  for (let p = 0; p <= pmax; p += 500000) s += `<line class="grid-l" x1="${PL}" x2="${W-PR}" y1="${sy(p)}" y2="${sy(p)}"/><text class="tick" x="${PL-8}" y="${sy(p)+4}" text-anchor="end">${(p/1e6).toFixed(1)} M</text>`;
  for (let k = 0; k <= kmax; k += 300000) s += `<text class="tick" x="${sx(k)}" y="${H-14}" text-anchor="middle">${k?fmtk(k):'0'}</text>`;
  s += `<line x1="${sx(st.km)}" x2="${sx(st.km)}" y1="${PT}" y2="${H-PB}" stroke="var(--lima-ink)" stroke-dasharray="4 4"/><text class="tick" x="${sx(st.km)+6}" y="${PT+12}" fill="var(--lima-ink)">tu kilometraje</text>`;
  const sub = BASE.filter(a => Math.abs(a.anio - st.anio) <= 1 && a.km && a.km > 5000);
  for (const a of sub){ const sel = a.anio === st.anio;
    s += `<circle class="pt ${a.mt==='paccar'?'pac':a.mt==='cummins'?'cum':'sd'} ${sel?'sel':''}" data-id="${a.id}" cx="${sx(Math.min(a.km,kmax))}" cy="${sy(a.precio)}" r="${sel?7:5.5}"/>`; }
  if (!sub.length) s += `<text x="${W/2}" y="${H/2}" text-anchor="middle" class="tick">Sin anuncios con kilometraje para estos años</text>`;
  s += '</svg>';
  const host = $('kmchart').parentElement; $('kmchart').innerHTML = s; bindTips($('kmchart'), $('tip2'), host, byId);
}
function drawPlazas(){
  const estado = a => (a.lugar.split(',').pop() || a.lugar).trim();
  const g = {}; for (const a of DATA.anuncios.filter(a=>a.tipo!=='excluido'&&!a.dup)) (g[estado(a)] = g[estado(a)] || []).push(a);
  const rows = Object.entries(g).map(([k,v]) => ({k, n: v.length, p: v.filter(a=>a.mon==='MXN').map(a=>a.precio).sort((x,y)=>x-y)})).sort((x,y)=>y.n-x.n);
  const maxn = rows[0].n;
  $('plazas-n').innerHTML = rows.map(r => `<div class="row"><span>${r.k}</span><div class="bg"><i style="width:${r.n/maxn*100}%"></i></div><span class="v">${r.n}</span><span class="n"></span></div>`).join('');
  const withMed = rows.filter(r => r.p.length >= 3).map(r => ({...r, med: r.p[Math.floor(r.p.length/2)]})).sort((x,y)=>y.med-x.med);
  const maxp = withMed[0].med;
  $('plazas-p').innerHTML = withMed.map(r => `<div class="row"><span>${r.k}</span><div class="bg"><i style="width:${r.med/maxp*100}%"></i></div><span class="v">${fmt(r.med)}</span><span class="n">${r.p.length}</span></div>`).join('');
}

// tabs
$('tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return;
  document.querySelectorAll('#tabs button').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('.pane').forEach(p => p.classList.toggle('on', p.id === 'p-' + b.dataset.t)); });

// todos los anuncios
$('todosgrid').innerHTML = DATA.anuncios.slice().sort((a,b)=>b.anio-a.anio||mxn(a)-mxn(b)).map(a => card(a, {dim: a.tipo==='excluido'||a.dup, sim: a.tipo==='tracto'?null:a.tipo==='excluido'?'excluido':a.dup?'duplicado':a.tipo})).join('');
$('corte').textContent = `Consulta de valor · corte ${DATA.corte.slice(8)} de noviembre de 2026 · ${BASE.length} tractocamiones comparables de ${DATA.anuncios.length} anuncios`;
$('fuentes').innerHTML = 'Fuentes · ' + Object.values(DATA.fuentes).map(f => `<a href="${f.url}" target="_blank" rel="noopener">${f.nombre}</a>`).join('') + ` · Dólares convertidos a ${fx.toFixed(2)} MXN.`;
drawPlazas(); render();
</script>
</body></html>'''

out = HTML.replace("__DATA__", DATA)
(ROOT / "index.html").write_text(out, encoding="utf-8")
SITE = ROOT / "site"; SITE.mkdir(exist_ok=True)
assert (SITE / "og-libro-azul-t680-v2.jpg").exists(), "falta la miniatura OG en site/"
(SITE / "index.html").write_text(out, encoding="utf-8")
(SITE / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: no-referrer\n  X-Content-Type-Options: nosniff\n")
print("ok", len(anuncios), "anuncios")

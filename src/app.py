# -*- coding: utf-8 -*-
# Flask žiniatinklio API – Išmanioji Hidratacija (LT)
from __future__ import annotations

import os, json
from pathlib import Path
from typing import Any, Dict, List

# .env palaikymui
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Modelis
from hidratacijos_prognoze import HidratacijosModelis

APP_NAME = "Išmanioji Hidratacija – Demo"

# ----- Failų vietos -----
ROOT = Path(__file__).resolve().parents[1]  # projekto šaknis
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
SCEN_FILE = DATA_DIR / "scenarios.json"

# ----- Numatyti scenarijai (seed) -----
DEFAULT_SCENARIOS: List[Dict[str, Any]] = [
    {
        "name": "Puikiai pailsėjęs",
        "payload": {
            "vandens_ml": 2300, "zingsniai": 9500, "sirdies_ritmas": 64,
            "stresas": 3, "miegas_val": 8, "temperatura_c": 21.0, "aktyvumas_min": 60
        }
    },
    {
        "name": "Po intensyvios treniruotės",
        "payload": {
            "vandens_ml": 2800, "zingsniai": 12000, "sirdies_ritmas": 82,
            "stresas": 6, "miegas_val": 6.5, "temperatura_c": 23.0, "aktyvumas_min": 90
        }
    },
    {
        "name": "Darbo dienos pabaiga",
        "payload": {
            "vandens_ml": 1600, "zingsniai": 4500, "sirdies_ritmas": 76,
            "stresas": 7, "miegas_val": 6.0, "temperatura_c": 24.0, "aktyvumas_min": 20
        }
    },
]

def _read_scenarios() -> List[Dict[str, Any]]:
    if not SCEN_FILE.exists():
        return []
    try:
        return json.loads(SCEN_FILE.read_text("utf-8"))
    except Exception:
        return []

def _write_scenarios(items: List[Dict[str, Any]]) -> None:
    SCEN_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def ensure_seed():
    """Jei failo nėra ARBA jis tuščias – įrašom numatytuosius scenarijus."""
    cur = _read_scenarios()
    if not cur:
        _write_scenarios(DEFAULT_SCENARIOS)

# ----- Stress insights (paprasta logika demo režimui) -----
def stress_insights(p: Dict[str, Any]) -> Dict[str, Any]:
    stresas = float(p.get("stresas", 5))
    hr = float(p.get("sirdies_ritmas", 70))
    miegas = float(p.get("miegas_val", 7))
    aktyv = float(p.get("aktyvumas_min", 45))

    if stresas >= 8 or hr >= 90:
        lygis = "aukštas"
    elif stresas >= 5 or hr >= 80:
        lygis = "vidutinis"
    else:
        lygis = "žemas"

    tips = []
    if lygis != "žemas":
        tips.append("3× po 1 min. gilaus kvėpavimo (4–4–6).")
    if miegas < 7:
        tips.append("Šiąnakt nusitaikyk į ≥7 val. miego.")
    if aktyv < 30:
        tips.append("Greitas 10–15 min. pasivaikščiojimas.")
    if hr > 85 and stresas >= 6:
        tips.append("Pertraukėlė be ekranų + stiklinė vandens.")

    return {"lygis": lygis, "rekomendacijos": tips}

# ----- Flask app -----
app = Flask(__name__)
CORS(app)

# Inicijuojame modelį paleidžiant serverį
MODEL = HidratacijosModelis()
DUOMENYS = MODEL.generuoti_demo_duomenis(dienos=30)
METR = MODEL.apmokyti(DUOMENYS)

# užsėklinam scenarijus
ensure_seed()

@app.get("/favicon.ico")
def favicon():
    # tuščias atsakymas, kad nelogintų 404
    return ("", 204)

@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "model": "LinearRegression + StandardScaler",
        "r2_test": round(METR.r2_test, 3)
    })

@app.post("/api/predict")
def predict():
    try:
        payload = request.get_json(force=True, silent=False) or {}
        ats = MODEL.prognozuoti(payload)
        ats["stress_insights"] = stress_insights(payload)
        return jsonify({"ok": True, "rezultatas": ats})
    except Exception as e:
        return jsonify({"ok": False, "klaida": str(e)}), 400

@app.get("/api/stats")
def stats():
    return jsonify(MODEL.statistika())

# ----- Scenarijų API -----
@app.get("/api/scenarios")
def get_scenarios():
    return jsonify({"scenarios": _read_scenarios()})

@app.post("/api/scenarios")
def save_scenario():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    payload = data.get("payload") or {}
    if not name:
        return jsonify({"ok": False, "error": "name required"}), 400
    items = [i for i in _read_scenarios() if i.get("name") != name]
    items.append({"name": name, "payload": payload})
    _write_scenarios(items)
    return jsonify({"ok": True})

@app.delete("/api/scenarios/<name>")
def delete_scenario(name):
    from urllib.parse import unquote
    name = unquote(name)
    items = [i for i in _read_scenarios() if i.get("name") != name]
    _write_scenarios(items)
    return jsonify({"ok": True})

@app.post("/api/scenarios/seed")
def reseed():
    _write_scenarios(DEFAULT_SCENARIOS)
    return jsonify({"ok": True, "count": len(DEFAULT_SCENARIOS)})

@app.get("/api/docs")
def docs():
    return jsonify({
        "endpoints": {
            "GET /": "Žiniatinklio forma ir demo",
            "GET /api/health": "Sveikatos patikra",
            "POST /api/predict": "Prognozė (JSON įvestys)",
            "GET /api/stats": "Aprašomoji statistika",
            "GET /api/scenarios": "Gauti scenarijus",
            "POST /api/scenarios": "Išsaugoti scenarijų {name, payload}",
            "DELETE /api/scenarios/<name>": "Ištrinti scenarijų",
            "POST /api/scenarios/seed": "Perrašyti į numatytuosius scenarijus"
        }
    })

# ----- Paprasta UI forma (demo) -----
INDEX_HTML = """
<!doctype html>
<html lang="lt">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{app_name}}</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial;
         margin:0;background:linear-gradient(180deg,#f8fbff 0%,#eef5ff 100%);}
    header{padding:24px 20px;background:#0b5cff;color:white}
    main{padding:24px;max-width:960px;margin:0 auto}
    .card{background:white;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.07);
          padding:20px;margin-bottom:20px}
    label{display:block;margin:8px 0 4px;font-weight:600}
    input,select{width:100%;padding:10px;border:1px solid #d7e0ef;border-radius:10px}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    .row > *{flex:1}
    button{margin-top:12px;padding:12px 16px;border:0;border-radius:12px;cursor:pointer}
    .primary{background:#0b5cff;color:#fff}
    .muted{background:#eef3ff;color:#234}
    pre{white-space:pre-wrap}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" referrerpolicy="no-referrer"></script>
</head>
<body>
  <header><h1>Išmanioji Hidratacija – demo</h1></header>
  <main>
    <div class="card">
      <h2>Realiojo laiko prognozė</h2>
      <form id="form">
        <label>Vanduo (ml)</label><input name="vandens_ml" type="number" value="2000" step="50">
        <label>Žingsniai</label><input name="zingsniai" type="number" value="8000" step="100">
        <label>Širdies ritmas (bpm)</label><input name="sirdies_ritmas" type="number" value="70" step="1">
        <label>Stresas (1–10)</label><input name="stresas" type="number" value="5" min="1" max="10">
        <label>Miegas (val.)</label><input name="miegas_val" type="number" value="7" step="0.1">
        <label>Temperatūra (°C)</label><input name="temperatura_c" type="number" value="22" step="0.1">
        <label>Aktyvumas (min)</label><input name="aktyvumas_min" type="number" value="45" step="5">

        <div class="row">
          <button class="primary" type="submit" id="btnPredict">Skaičiuoti prognozę</button>
          <button class="muted" type="button" id="btnDocs">API dokumentacija</button>
          <button class="muted" type="button" id="downloadJSON">Atsisiųsti JSON</button>
          <button class="muted" type="button" id="printPage">Spausdinti</button>
          <button class="muted" type="button" id="screenshot">Ekrano kopija</button>
        </div>

        <h3>Scenarijai:</h3>
        <div class="row">
          <select id="scenSelect"></select>
          <button type="button" id="saveScenario">Išsaugoti</button>
          <button type="button" id="applyScenario">Pritaikyti</button>
          <button type="button" id="deleteScenario">Ištrinti</button>
        </div>
      </form>
    </div>

    <div class="card"><h3>Rezultatas</h3><pre id="out">—</pre></div>
    <pre id="scenList" style="display:none"></pre>
  </main>

<script>
const $ = s => document.querySelector(s);
const out = $("#out");

function formToJSON(form){
  const obj = Object.fromEntries(new FormData(form).entries());
  for(const k in obj){ obj[k] = Number(obj[k]); }
  return obj;
}
async function api(url, method="GET", body=null){
  const r = await fetch(url, {
    method, headers: {"Content-Type":"application/json"},
    body: body ? JSON.stringify(body) : null
  });
  if(!r.ok){ throw new Error(await r.text()); }
  return await r.json();
}
async function predict(){
  const payload = formToJSON($("#form"));
  const j = await api("/api/predict","POST", payload);
  window.lastResult = j;
  out.textContent = JSON.stringify(j, null, 2);
}
async function loadScenarios(){
  const data = await api("/api/scenarios");
  const sel = $("#scenSelect");
  sel.innerHTML = "";
  data.scenarios.forEach(s=>{
    const opt = document.createElement("option");
    opt.value = s.name; opt.textContent = s.name;
    sel.appendChild(opt);
  });
  $("#scenList").textContent = JSON.stringify(data.scenarios, null, 2);
}
async function saveScenario(){
  const name = prompt("Scenarijaus pavadinimas:");
  if(!name) return;
  const payload = formToJSON($("#form"));
  await api("/api/scenarios","POST",{name, payload});
  await loadScenarios();
  alert("Išsaugota.");
}
function applyScenario(){
  const name = $("#scenSelect").value;
  if(!name) return;
  const list = JSON.parse($("#scenList").textContent || "[]");
  const found = list.find(x=>x.name===name);
  if(!found) return;
  const p = found.payload || {};
  Object.keys(p).forEach(k=>{
    const el = document.querySelector(`[name="${k}"]`);
    if(el) el.value = p[k];
  });
}
async function deleteScenario(){
  const name = $("#scenSelect").value;
  if(!name) return;
  if(!confirm(`Ištrinti „${name}“?`)) return;
  await fetch(`/api/scenarios/${encodeURIComponent(name)}`, {method:"DELETE"});
  await loadScenarios();
}
function downloadJSON(){
  const data = window.lastResult || { note:"Pirmiausia paskaičiuok prognozę." };
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "hidratacijos_demo_rezultatas.json";
  a.click();
}
function printPage(){ window.print(); }
function screenshot(){
  html2canvas(document.body).then(canvas=>{
    canvas.toBlob(b=>{
      const a = document.createElement("a");
      a.href = URL.createObjectURL(b);
      a.download = "hidratacijos_demo.png";
      a.click();
    });
  });
}
window.addEventListener("DOMContentLoaded", ()=>{
  $("#form").addEventListener("submit", (e)=>{ e.preventDefault(); predict().catch(e=>alert(e.message)); });
  $("#btnDocs").onclick = async ()=>{ const j = await api("/api/docs"); out.textContent = JSON.stringify(j, null, 2); };
  $("#saveScenario").onclick = ()=> saveScenario().catch(e=>alert(e.message));
  $("#applyScenario").onclick = applyScenario;
  $("#deleteScenario").onclick = ()=> deleteScenario().catch(e=>alert(e.message));
  $("#downloadJSON").onclick = downloadJSON;
  $("#printPage").onclick = printPage;
  $("#screenshot").onclick = screenshot;
  loadScenarios().catch(()=>{});
});
</script>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(INDEX_HTML, app_name=APP_NAME)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    debug = os.getenv("DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
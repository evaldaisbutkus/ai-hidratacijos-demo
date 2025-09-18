
# Išmanioji Hidratacija – LT Demo

Veikiantis prototipas su AI modeliu (LinearRegression + StandardScaler), 5 REST API galimybėmis ir paprasta žiniatinklio forma.

## Struktūra
```
AI-Hidratacijos-Demo/
├─ requirements.txt
├─ README.md
├─ test_demo.py
└─ src/
   ├─ app.py
   └─ hidratacijos_prognoze.py
```

## Greitas paleidimas

**Windows (PowerShell):**
```ps1
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pip install --upgrade pip
python src/app.py
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

Atidarykite naršyklę: http://localhost:5000

## API
- `GET /api/health` – gyvybingumo patikra
- `POST /api/predict` – prognozė (JSON laukeliai: `vandens_ml, zingsniai, sirdies_ritmas, stresas, miegas_val, temperatura_c, aktyvumas_min`)
- `GET /api/stats` – aprašomoji statistika
- `GET /api/docs` – endpoint aprašas
- `POST /api/retrain` – persimokyti (body: `{ "dienos": 30 }` pasirenkamai)

## Testai
```bash
pytest -q
```

## Pastabos
- Prototipas naudoja sintetinę duomenų generaciją demonstracijai. Realiems duomenims integruoti pritaikykite `generuoti_demo_duomenis` arba sukurkite duomenų įkėlimo funkciją.
- R² ~0.6–0.7 numatytas dirbtinai, kad atkartotų ~64% tikslumo pasakojimą demonstracijai.
- Visa sąsaja – lietuvių kalba.
```

# -*- coding: utf-8 -*-
"""
Pagrindinis AI prognozavimo modulis: 'HidratacijosModelis'
- Duomenų generavimas demonstracijai
- Modelio apmokymas
- Prognozavimas ir santraukos
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score

FEATURE_COLUMNS = [
    "vandens_ml","zingsniai","sirdies_ritmas","stresas",
    "miegas_val","temperatura_c","aktyvumas_min"
]

@dataclass
class Metrics:
    r2_train: float
    r2_test: float
    n_train: int
    n_test: int

class HidratacijosModelis:
    def __init__(self) -> None:
        self.pipeline: Pipeline | None = None
        self.metrics: Metrics | None = None
        self.tren_duomenys: pd.DataFrame | None = None

    def generuoti_demo_duomenis(self, dienos: int = 30, seed: int = 42) -> pd.DataFrame:
        rng = np.random.RandomState(seed)
        dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=dienos, freq="D")
        df = pd.DataFrame({
            "data": dates,
            "vandens_ml": rng.normal(2200, 350, size=dienos).clip(800, 4000),
            "zingsniai": rng.normal(8500, 3000, size=dienos).clip(0, 25000),
            "sirdies_ritmas": rng.normal(72, 8, size=dienos).clip(45, 120),
            "stresas": rng.randint(1, 11, size=dienos),  # 1–10
            "miegas_val": rng.normal(7.0, 1.2, size=dienos).clip(3, 11),
            "temperatura_c": rng.normal(21.5, 5.0, size=dienos).clip(10, 35),
            "aktyvumas_min": rng.normal(40, 30, size=dienos).clip(0, 240),
        })
        coeff = {
            "vandens_ml": 0.030, "zingsniai": 0.0012, "sirdies_ritmas": -0.60,
            "stresas": -1.50, "miegas_val": 2.5, "temperatura_c": -0.80, "aktyvumas_min": -0.06
        }
        Xc = pd.DataFrame({
            "vandens_ml": df["vandens_ml"] - 2000,
            "zingsniai": df["zingsniai"] - 8000,
            "sirdies_ritmas": df["sirdies_ritmas"] - 70,
            "stresas": df["stresas"] - 5,
            "miegas_val": df["miegas_val"] - 7,
            "temperatura_c": df["temperatura_c"] - 22,
            "aktyvumas_min": df["aktyvumas_min"] - 45,
        })
        noise = rng.normal(0, 8.0, size=dienos)
        raw = (
            coeff["vandens_ml"] * Xc["vandens_ml"] +
            coeff["zingsniai"]    * Xc["zingsniai"] +
            coeff["sirdies_ritmas"]* Xc["sirdies_ritmas"] +
            coeff["stresas"]      * Xc["stresas"] +
            coeff["miegas_val"]   * Xc["miegas_val"] +
            coeff["temperatura_c"]* Xc["temperatura_c"] +
            coeff["aktyvumas_min"]* Xc["aktyvumas_min"] +
            noise
        )
        idx = 60 + raw
        idx = np.clip(idx, 0, 100)
        df["hidratacijos_indeksas"] = idx
        return df

    def apmokyti(self, df: pd.DataFrame) -> Metrics:
        X = df[FEATURE_COLUMNS].copy()
        y = df["hidratacijos_indeksas"].astype(float).values
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=123)
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", LinearRegression())
        ])
        self.pipeline.fit(X_tr, y_tr)
        r2_tr = float(self.pipeline.score(X_tr, y_tr))
        y_pred = self.pipeline.predict(X_te)
        r2_te = float(r2_score(y_te, y_pred))
        self.tren_duomenys = df.copy()
        self.metrics = Metrics(r2_train=r2_tr, r2_test=r2_te, n_train=len(X_tr), n_test=len(X_te))
        return self.metrics

    def _interpretacija(self, indeksas: float) -> str:
        if indeksas < 40:
            return "Rizika dėl dehidratacijos – padidinkite skysčių suvartojimą."
        if indeksas < 60:
            return "Žemesnis nei optimalus – išgerkite stiklinę vandens ir peržiūrėkite dienos aktyvumą."
        if indeksas < 80:
            return "Normali būklė – palaikykite balansą."
        if indeksas <= 100:
            return "Puiku – hidratacija optimali."
        return "Nenurodyta."

    def prognozuoti(self, ivestis: Dict[str, Any]) -> Dict[str, Any]:
        if self.pipeline is None:
            raise RuntimeError("Modelis dar neapmokytas.")
        row = {
            "vandens_ml": float(ivestis.get("vandens_ml", 2000)),
            "zingsniai": float(ivestis.get("zingsniai", 8000)),
            "sirdies_ritmas": float(ivestis.get("sirdies_ritmas", 70)),
            "stresas": float(ivestis.get("stresas", 5)),
            "miegas_val": float(ivestis.get("miegas_val", 7)),
            "temperatura_c": float(ivestis.get("temperatura_c", 22)),
            "aktyvumas_min": float(ivestis.get("aktyvumas_min", 45)),
        }
        X = pd.DataFrame([row], columns=FEATURE_COLUMNS)  # suteikiam stulpelių pavadinimus
        pred = float(self.pipeline.predict(X)[0])
        pred = max(0.0, min(100.0, pred))
        return {
            "hidratacijos_indeksas": round(pred, 1),
            "ivestis": row,
            "interpretacija": self._interpretacija(pred),
        }

    def santrauka(self) -> Dict[str, Any]:
        m = self.metrics or Metrics(0.0, 0.0, 0, 0)
        return {
            "metrics": {
                "r2_train": round(m.r2_train, 3),
                "r2_test": round(m.r2_test, 3),
                "n_train": m.n_train,
                "n_test": m.n_test,
            },
            "features": FEATURE_COLUMNS,
        }

    def statistika(self) -> Dict[str, Any]:
        if self.tren_duomenys is None:
            return {"klaida": "Nėra treniravimo duomenų."}
        desc = self.tren_duomenys[FEATURE_COLUMNS + ["hidratacijos_indeksas"]].describe().to_dict()
        return {"aprasomoji_statistika": desc}

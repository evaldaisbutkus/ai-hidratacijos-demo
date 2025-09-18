
# -*- coding: utf-8 -*-
import json
import pytest
from src.app import app

@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    return app.test_client()

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.get_json()
    assert j["status"] == "ok"

def test_predict(client):
    payload = {
        "vandens_ml": 2100,
        "zingsniai": 9000,
        "sirdies_ritmas": 68,
        "stresas": 4,
        "miegas_val": 7.5,
        "temperatura_c": 20,
        "aktyvumas_min": 60
    }
    r = client.post("/api/predict", json=payload)
    assert r.status_code == 200
    j = r.get_json()
    assert j["ok"] is True
    assert "hidratacijos_indeksas" in j["rezultatas"]

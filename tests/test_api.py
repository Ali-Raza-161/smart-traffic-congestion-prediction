import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
os.environ["TRAFFIC_DB"] = _tmp.name

from api.main import app  # noqa: E402

client = TestClient(app)


def test_health_states_simulated_only():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["data"] == "simulated_only"


def test_sensors_and_congestion():
    assert client.get("/api/sensors").status_code == 200
    r = client.get("/api/congestion")
    assert r.status_code == 200
    assert len(r.json()["congestion"]) == 6


def test_predict_unknown_intersection_404():
    r = client.post("/api/predict", json={"intersection_id": "INT-Z", "horizon_minutes": 15})
    assert r.status_code == 404


def test_predict_bad_horizon_400():
    r = client.post("/api/predict", json={"intersection_id": "INT-A", "horizon_minutes": 45})
    assert r.status_code == 400


def test_predict_ok():
    r = client.post("/api/predict", json={"intersection_id": "INT-A", "horizon_minutes": 30})
    assert r.status_code == 200
    body = r.json()
    assert body["data_source"] == "simulated"
    assert body["congestion"] in ("Low", "Moderate", "High", "Severe")


def test_signals_are_advisory_only():
    r = client.get("/api/signals")
    assert r.status_code == 200
    assert r.json()["advisory_only"] is True
    assert all(s["advisory_only"] for s in r.json()["signals"])


def test_reports_and_export():
    r = client.get("/api/reports")
    assert r.status_code == 200
    assert r.json()["model_metrics"]["dataset"] == "simulated_only"
    r = client.get("/api/reports/export")
    assert r.status_code == 200
    assert "vehicle_count" in r.text


def test_support_ticket_flow():
    r = client.post("/api/support/tickets", json={"name": "Test", "subject": "Sensor", "message": "Help", "priority": "High"})
    assert r.status_code == 200
    tid = r.json()["id"]
    assert r.json()["status"] == "Open"
    r = client.patch(f"/api/support/tickets/{tid}", json={"status": "Resolved", "reply": "Checked."})
    assert r.status_code == 200
    assert r.json()["status"] == "Resolved"


def test_readings_unknown_intersection_404():
    assert client.get("/api/readings", params={"intersection_id": "INT-Z"}).status_code == 404

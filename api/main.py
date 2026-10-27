"""FastAPI backend — Smart Traffic Congestion Prediction (simulated data only).

Educational demo. No real IoT hardware, no real city traffic data, no real
signal control. Signal suggestions are advisory only.
"""
from __future__ import annotations

import csv
import io
import os
import sys
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import store  # noqa: E402
from api.schemas import PredictRequest, SettingsRequest, TicketRequest, TicketUpdate  # noqa: E402
from ml.model import ModelUnavailable, predict, train_models  # noqa: E402
from ml.simulator import INTERSECTIONS, SENSORS, congestion_level, generate_history, latest_reading  # noqa: E402

app = FastAPI(title="Smart Traffic Congestion Prediction API",
              description="Simulated IoT sensor data only. Educational demo, not a traffic-control system.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])

_MODELS: dict | None = None
_METRICS: dict | None = None


def _models():
    global _MODELS, _METRICS
    if _MODELS is None:
        try:
            _MODELS, _METRICS = train_models(days=7, n_estimators=60)
        except ModelUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc))
    return _MODELS


def _seed_if_empty() -> None:
    """Generate one day of synthetic history per intersection on first run."""
    store.init_db()
    if store.recent_readings(limit=1):
        return
    for inter in INTERSECTIONS:
        readings = [r.to_dict() for r in generate_history(inter["id"], days=1, seed=42)]
        store.save_readings(readings)
    # Seed demo alerts (simulated conditions, not real events).
    store.add_alert("INT-D", "sensor_offline", "Sensor SEN-D2 is offline (simulated). Check battery.", "High")
    store.add_alert("INT-A", "congestion", "Simulated evening congestion expected at Main Rd & Market Rd.", "Medium")


@app.on_event("startup")
def _startup():
    _seed_if_empty()


@app.get("/health")
def health():
    return {"ok": True, "service": "smart-traffic-congestion",
            "data": "simulated_only",
            "note": "Educational demo. No real IoT hardware, no real traffic data, no real signal control."}


@app.get("/api/intersections")
def intersections():
    _seed_if_empty()
    out = []
    for inter in INTERSECTIONS:
        latest = latest_reading(inter["id"])
        out.append({**inter, "latest": latest.to_dict()})
    return {"data_source": "simulated", "intersections": out}


@app.get("/api/sensors")
def sensors():
    return {"data_source": "simulated", "sensors": SENSORS}


@app.get("/api/readings")
def readings(intersection_id: str | None = None, limit: int = Query(default=50, ge=1, le=500)):
    _seed_if_empty()
    if intersection_id and intersection_id not in {i["id"] for i in INTERSECTIONS}:
        raise HTTPException(status_code=404, detail="Unknown intersection")
    return {"data_source": "simulated", "readings": store.recent_readings(intersection_id, limit)}


@app.get("/api/congestion")
def congestion():
    _seed_if_empty()
    out = []
    for inter in INTERSECTIONS:
        latest = latest_reading(inter["id"])
        out.append({"intersection_id": inter["id"], "name": inter["name"],
                    "congestion": latest.congestion, "occupancy_percent": latest.occupancy_percent,
                    "vehicle_count": latest.vehicle_count, "avg_speed_kmh": latest.avg_speed_kmh,
                    "queue_length": latest.queue_length, "timestamp": latest.timestamp})
    return {"data_source": "simulated", "congestion": out}


@app.post("/api/predict")
def predict_endpoint(body: PredictRequest):
    if body.intersection_id not in {i["id"] for i in INTERSECTIONS}:
        raise HTTPException(status_code=404, detail="Unknown intersection")
    if body.horizon_minutes not in (15, 30, 60):
        raise HTTPException(status_code=400, detail="horizon_minutes must be 15, 30 or 60")
    models = _models()
    history = generate_history(body.intersection_id, days=1, seed=42)
    counts = [r.vehicle_count for r in history]
    last = history[-1]
    weather = body.weather or last.weather
    event = body.event if body.event is not None else last.event
    ts = datetime.fromisoformat(last.timestamp.replace("Z", "+00:00"))
    result = predict(models, ts, weather, event, counts[-1], counts[-2], counts[-3],
                     sum(counts[-6:]) / 6, horizon_minutes=body.horizon_minutes)
    return {"data_source": "simulated", "intersection_id": body.intersection_id,
            "horizon_minutes": body.horizon_minutes, "based_on": last.to_dict(),
            "weather": weather, "event": event, **result,
            "note": "Prediction from a model trained on simulated data only."}


@app.get("/api/predict")
def predict_get(intersection_id: str, horizon_minutes: int = 15):
    return predict_endpoint(PredictRequest(intersection_id=intersection_id, horizon_minutes=horizon_minutes))


@app.get("/api/signals")
def signals():
    """Advisory green-time suggestions only. Nothing here controls a real signal."""
    _seed_if_empty()
    settings = store.get_settings()
    base = int(settings.get("green_time_base_seconds", "30"))
    suggestions = []
    for inter in INTERSECTIONS:
        latest = latest_reading(inter["id"])
        adj = {"Low": -5, "Moderate": 3, "High": 8, "Severe": 15}[latest.congestion]
        suggested = max(20, min(55, base + adj))
        suggestions.append({
            "intersection_id": inter["id"], "name": inter["name"],
            "congestion": latest.congestion, "current_green_seconds": base,
            "suggested_green_seconds": suggested, "adjustment_seconds": adj,
            "advisory_only": True,
            "reason": f"Simulated {latest.congestion} congestion (occupancy {latest.occupancy_percent}%).",
        })
    return {"data_source": "simulated", "advisory_only": True,
            "note": "Advisory suggestions only. This system does not control real traffic signals.",
            "signals": suggestions}


@app.get("/api/alerts")
def alerts():
    _seed_if_empty()
    return {"data_source": "simulated", "alerts": store.list_alerts()}


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: int):
    row = store.acknowledge_alert(alert_id)
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    return row


@app.get("/api/reports")
def reports():
    _seed_if_empty()
    models = _models()
    return {"data_source": "simulated", "summary": store.report_summary(),
            "model_metrics": models["metrics"],
            "note": "All figures are from simulated data only."}


@app.get("/api/reports/export")
def export_csv():
    _seed_if_empty()
    rows = store.recent_readings(limit=500)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["timestamp", "intersection_id", "sensor_id", "vehicle_count",
                                             "avg_speed_kmh", "occupancy_percent", "queue_length",
                                             "weather", "event", "congestion"])
    writer.writeheader()
    fields = ["timestamp", "intersection_id", "sensor_id", "vehicle_count",
              "avg_speed_kmh", "occupancy_percent", "queue_length",
              "weather", "event", "congestion"]
    writer.writerows([{k: r[k] for k in fields} for r in rows])
    return PlainTextResponse(buf.getvalue(), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=traffic-report.csv"})


@app.get("/api/support/tickets")
def tickets():
    store.init_db()
    return store.list_tickets()


@app.post("/api/support/tickets")
def create_ticket(body: TicketRequest):
    store.init_db()
    if body.priority not in ("Low", "Medium", "High"):
        raise HTTPException(status_code=400, detail="priority must be Low, Medium or High")
    return store.create_ticket(body.name, body.subject, body.message, body.priority)


@app.patch("/api/support/tickets/{ticket_id}")
def update_ticket(ticket_id: int, body: TicketUpdate):
    if body.status and body.status not in ("Open", "In Progress", "Resolved"):
        raise HTTPException(status_code=400, detail="Invalid status")
    row = store.update_ticket(ticket_id, body.status, body.reply)
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return row


@app.get("/api/settings")
def settings():
    store.init_db()
    return store.get_settings()


@app.put("/api/settings")
def update_settings(body: SettingsRequest):
    store.init_db()
    values = {k: v for k, v in body.model_dump().items() if v is not None}
    return store.set_settings(values)


@app.get("/api/model-info")
def model_info():
    models = _models()
    return {"trained_on": "simulated_data_only", "metrics": models["metrics"]}

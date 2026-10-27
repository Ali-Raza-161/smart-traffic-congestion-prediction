"""Congestion prediction models, trained ONLY on simulated data.

The models are trained at setup / first use from the synthetic generator in
simulator.py. No pre-trained model file is shipped, and no model here has
ever seen real traffic data. If scikit-learn is unavailable the training
functions raise ModelUnavailable instead of returning fake predictions.
"""
from __future__ import annotations

import os
from datetime import timedelta

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.metrics import accuracy_score, confusion_matrix, mean_absolute_error, mean_squared_error
    _SKLEARN_OK = True
except Exception:  # pragma: no cover - environment without sklearn
    np = None  # type: ignore
    _SKLEARN_OK = False


class ModelUnavailable(RuntimeError):
    pass


from .features import LEVELS, LEVEL_CODE, features_for  # noqa: E402
from .simulator import INTERSECTIONS, congestion_level, generate_history  # noqa: E402


def build_dataset(days: int = 14, seed: int = 42):
    """Return (X, y_level, y_count, timestamps, intersection_ids)."""
    if not _SKLEARN_OK:
        raise ModelUnavailable("scikit-learn is not installed; install requirements.txt to train the model.")
    X, y_level, y_count, stamps, ids = [], [], [], [], []
    for inter in INTERSECTIONS:
        readings = generate_history(inter["id"], days=days, seed=seed)
        counts = [r.vehicle_count for r in readings]
        for i in range(6, len(readings)):
            r = readings[i]
            # Predict the reading 3 steps (15 min) ahead from the current window.
            target = readings[i + 3] if i + 3 < len(readings) else None
            if target is None:
                continue
            ts = r.timestamp
            from datetime import datetime as _dt
            dt = _dt.fromisoformat(ts.replace("Z", "+00:00"))
            window = counts[i - 6:i]
            X.append(features_for(dt, r.weather, r.event, counts[i - 1], counts[i - 2], counts[i - 3],
                                  sum(window) / len(window)))
            y_level.append(LEVEL_CODE[target.congestion])
            y_count.append(target.vehicle_count)
            stamps.append(ts)
            ids.append(inter["id"])
    return np.array(X), np.array(y_level), np.array(y_count), stamps, ids


def train_models(days: int = 14, seed: int = 42, n_estimators: int = 80):
    """Train classifier + regressor on a chronological 80/20 split.

    Returns (models dict, metrics dict). Metrics are on synthetic data only.
    """
    if not _SKLEARN_OK:
        raise ModelUnavailable("scikit-learn is not installed; install requirements.txt to train the model.")
    X, y_level, y_count, _stamps, _ids = build_dataset(days=days, seed=seed)
    split = int(len(X) * 0.8)
    Xtr, Xte = X[:split], X[split:]
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1)
    reg = RandomForestRegressor(n_estimators=n_estimators, random_state=seed, n_jobs=-1)
    clf.fit(Xtr, y_level[:split])
    reg.fit(Xtr, y_count[:split])
    pred_level = clf.predict(Xte)
    pred_count = reg.predict(Xte)
    cm = confusion_matrix(y_level[split:], pred_level, labels=[0, 1, 2, 3]).tolist()
    metrics = {
        "dataset": "simulated_only",
        "rows": int(len(X)),
        "train_rows": int(split),
        "test_rows": int(len(X) - split),
        "classifier_accuracy": round(float(accuracy_score(y_level[split:], pred_level)), 4),
        "confusion_matrix_labels": LEVELS,
        "confusion_matrix": cm,
        "regressor_mae": round(float(mean_absolute_error(y_count[split:], pred_count)), 2),
        "regressor_rmse": round(float(mean_squared_error(y_count[split:], pred_count) ** 0.5), 2),
        "horizon_minutes": 15,
        "note": "Metrics are on synthetic simulated data only. They do not describe real traffic.",
    }
    return {"classifier": clf, "regressor": reg, "metrics": metrics}, metrics


def predict(models: dict, timestamp, weather: str, event: bool,
            lag1: float, lag2: float, lag3: float, rolling_mean: float, horizon_minutes: int = 15):
    """Predict congestion level + vehicle count for the next horizon.

    The trained models predict 15 minutes ahead. For 30/60 minutes the
    documented behaviour is: repeat the 15-minute model with the predicted
    count fed back as the newest lag (a simple rollout, stated in README).
    Horizon must be 15, 30 or 60.
    """
    if horizon_minutes not in (15, 30, 60):
        raise ValueError("horizon_minutes must be 15, 30 or 60")
    steps = horizon_minutes // 15
    lags = [float(lag1), float(lag2), float(lag3)]
    level_idx, count = 0, lags[0]
    for _ in range(steps):
        feats = features_for(timestamp, weather, event, lags[0], lags[1], lags[2], rolling_mean)
        level_idx = int(models["classifier"].predict([feats])[0])
        count = float(models["regressor"].predict([feats])[0])
        lags = [count, lags[0], lags[1]]
        rolling_mean = sum(lags) / len(lags)
        timestamp = timestamp + timedelta(minutes=15)
    return {"congestion": LEVELS[level_idx], "predicted_vehicle_count": int(round(count))}

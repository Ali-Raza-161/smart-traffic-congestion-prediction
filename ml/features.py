"""Feature engineering for the synthetic congestion model.

Features are computed only from simulated readings, timestamps, weather and
event flags. No real-world data is involved.
"""
from __future__ import annotations

import math
from datetime import datetime

WEATHER_CODE = {"clear": 0, "cloudy": 1, "rain": 2}
LEVEL_CODE = {"Low": 0, "Moderate": 1, "High": 2, "Severe": 3}
LEVELS = ["Low", "Moderate", "High", "Severe"]


def features_for(timestamp: datetime, weather: str, event: bool,
                 lag1: float, lag2: float, lag3: float, rolling_mean: float) -> list[float]:
    hour = timestamp.hour + timestamp.minute / 60.0
    return [
        math.sin(2 * math.pi * hour / 24.0),
        math.cos(2 * math.pi * hour / 24.0),
        float(timestamp.weekday()),
        1.0 if timestamp.weekday() >= 5 else 0.0,
        1.0 if (8 <= timestamp.hour < 10 or 17 <= timestamp.hour < 20) else 0.0,
        float(WEATHER_CODE.get(weather, 0)),
        1.0 if event else 0.0,
        float(lag1), float(lag2), float(lag3), float(rolling_mean),
    ]


FEATURE_NAMES = [
    "hour_sin", "hour_cos", "day_of_week", "is_weekend", "is_rush_hour",
    "weather_code", "event", "lag_5min", "lag_10min", "lag_15min", "rolling_mean_30min",
]

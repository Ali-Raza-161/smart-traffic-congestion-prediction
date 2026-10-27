import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml.simulator import INTERSECTIONS, congestion_level, generate_history, latest_reading


def test_six_fictional_intersections():
    assert len(INTERSECTIONS) == 6
    assert all(i["id"].startswith("INT-") for i in INTERSECTIONS)


def test_congestion_level_thresholds():
    assert congestion_level(10) == "Low"
    assert congestion_level(50) == "Moderate"
    assert congestion_level(75) == "High"
    assert congestion_level(95) == "Severe"


def test_rush_hour_higher_than_night():
    morning = [r.vehicle_count for r in generate_history("INT-A", days=1)
               if r.timestamp[11:13] == "09"]
    night = [r.vehicle_count for r in generate_history("INT-A", days=1)
             if r.timestamp[11:13] == "03"]
    assert morning and night
    assert sum(morning) / len(morning) > sum(night) / len(night)


def test_history_length_and_fields():
    rows = generate_history("INT-B", days=2)
    assert len(rows) == 2 * 24 * 12
    r = rows[-1]
    assert r.vehicle_count > 0
    assert 5 <= r.occupancy_percent <= 98
    assert r.congestion in ("Low", "Moderate", "High", "Severe")


def test_deterministic_with_same_seed():
    a = generate_history("INT-C", days=1, seed=7)
    b = generate_history("INT-C", days=1, seed=7)
    assert [r.vehicle_count for r in a] == [r.vehicle_count for r in b]


def test_latest_reading_is_recent():
    r = latest_reading("INT-A")
    ts = datetime.fromisoformat(r.timestamp.replace("Z", "+00:00"))
    assert (datetime.now(timezone.utc) - ts).total_seconds() < 48 * 3600

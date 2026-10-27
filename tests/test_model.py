import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml.model import predict, train_models


@pytest.fixture(scope="module")
def trained():
    models, metrics = train_models(days=7, n_estimators=30)
    return models, metrics


def test_metrics_are_synthetic_only(trained):
    _models, metrics = trained
    assert metrics["dataset"] == "simulated_only"
    assert 0 <= metrics["classifier_accuracy"] <= 1
    assert metrics["regressor_mae"] >= 0
    assert len(metrics["confusion_matrix"]) == 4


def test_predict_valid_horizons(trained):
    models, _m = trained
    from datetime import datetime, timezone
    out = predict(models, datetime.now(timezone.utc), "clear", False, 80, 75, 70, 75, 15)
    assert out["congestion"] in ("Low", "Moderate", "High", "Severe")
    assert out["predicted_vehicle_count"] > 0
    out60 = predict(models, datetime.now(timezone.utc), "rain", True, 80, 75, 70, 75, 60)
    assert out60["predicted_vehicle_count"] > 0


def test_predict_rejects_bad_horizon(trained):
    models, _m = trained
    from datetime import datetime, timezone
    with pytest.raises(ValueError):
        predict(models, datetime.now(timezone.utc), "clear", False, 80, 75, 70, 75, 45)

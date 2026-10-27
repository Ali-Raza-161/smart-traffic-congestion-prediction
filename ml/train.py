"""Train the synthetic-data models and save them locally (not committed).

Run:  python -m ml.train
Saves joblib files under ml/artifacts/ (gitignored). The API does not need
these files: it retrains in memory at startup from simulated data.
"""
from __future__ import annotations

from pathlib import Path

from .model import train_models


def main() -> None:
    try:
        import joblib
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"joblib is required to save models: {exc}")
    models, metrics = train_models()
    outdir = Path(__file__).resolve().parent / "artifacts"
    outdir.mkdir(exist_ok=True)
    joblib.dump(models["classifier"], outdir / "classifier.joblib")
    joblib.dump(models["regressor"], outdir / "regressor.joblib")
    print(f"Saved models to {outdir}")
    print(metrics)


if __name__ == "__main__":
    main()

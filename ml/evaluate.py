"""Evaluate the synthetic-data model and write a JSON report.

Run:  python -m ml.evaluate [--days 14]
Writes docs/evaluation_report.json. The model file itself is not committed;
re-running this script retrains from simulated data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import train_models


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14)
    args = parser.parse_args()
    _models, metrics = train_models(days=args.days)
    out = Path(__file__).resolve().parent.parent / "docs" / "evaluation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

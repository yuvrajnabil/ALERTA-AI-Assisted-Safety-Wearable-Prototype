#!/usr/bin/env python3
"""Run both saved desktop models on one example feature window."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


def predict(bundle_path: Path, values: dict[str, float]) -> tuple[float, bool]:
    bundle = joblib.load(bundle_path)
    row = pd.DataFrame([values], columns=bundle["features"])
    row = row.fillna(pd.Series(bundle["medians"]))
    probability = float(bundle["model"].predict_proba(row)[:, 1][0])
    return probability, probability >= float(bundle["threshold"])


def main() -> None:
    # Replace these values with a completed two-second firmware window.
    example = {
        "accel_mean_g": 1.08,
        "accel_std_g": 0.51,
        "accel_peak_g": 3.8,
        "gyro_peak_dps": 390.0,
        "posture_change_deg": 72.0,
        "immobility_s": 1.1,
        "heart_rate_bpm": 138.0,
        "spo2_percent": 87.0,
        "ppg_signal_quality": 0.72,
    }
    for task in ("fall", "health"):
        probability, alert = predict(
            Path("artifacts") / f"{task}_model.joblib", example
        )
        print(f"{task}: probability={probability:.3f}, alert={alert}")


if __name__ == "__main__":
    main()


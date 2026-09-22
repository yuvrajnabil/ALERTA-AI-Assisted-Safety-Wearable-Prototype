"""Reproducible synthetic feature-window generator.

The generator creates *feature-level simulations*, not real patient records.
Values overlap intentionally so the classification problem is not a perfect
lookup table. This data is useful for software integration and unit tests only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = np.array(
    [
        "rest",
        "walk",
        "sit_lie",
        "run",
        "stumble",
        "fall",
        "health_anomaly",
        "fall_health_anomaly",
    ]
)

SCENARIO_PROBABILITIES = np.array([0.22, 0.28, 0.16, 0.10, 0.09, 0.08, 0.05, 0.02])


@dataclass(frozen=True)
class SubjectProfile:
    subject_id: str
    baseline_hr: float
    baseline_spo2: float
    motion_scale: float
    ppg_quality: float


def _clipped_normal(
    rng: np.random.Generator, mean: float, sd: float, low: float, high: float
) -> float:
    return float(np.clip(rng.normal(mean, sd), low, high))


def _make_subjects(
    rng: np.random.Generator, number_of_subjects: int
) -> list[SubjectProfile]:
    subjects: list[SubjectProfile] = []
    for index in range(number_of_subjects):
        subjects.append(
            SubjectProfile(
                subject_id=f"SYN-{index + 1:03d}",
                baseline_hr=_clipped_normal(rng, 74, 9, 52, 105),
                baseline_spo2=_clipped_normal(rng, 97.2, 1.0, 94, 100),
                motion_scale=_clipped_normal(rng, 1.0, 0.12, 0.72, 1.35),
                ppg_quality=_clipped_normal(rng, 0.76, 0.14, 0.25, 1.0),
            )
        )
    return subjects


def _motion_features(
    rng: np.random.Generator, scenario: str, scale: float
) -> dict[str, float]:
    templates = {
        "rest": (1.00, 0.025, 1.10, 12, 4, 1.65),
        "walk": (1.04, 0.14, 1.65, 90, 13, 0.08),
        "sit_lie": (1.01, 0.09, 1.40, 105, 48, 0.55),
        "run": (1.15, 0.30, 2.45, 190, 18, 0.03),
        "stumble": (1.08, 0.25, 2.35, 235, 30, 0.24),
        "fall": (1.12, 0.48, 3.65, 355, 68, 1.05),
        "health_anomaly": (1.01, 0.09, 1.40, 75, 10, 0.75),
        "fall_health_anomaly": (1.13, 0.50, 3.80, 380, 72, 1.15),
    }
    mean_g, std_g, peak_g, gyro, posture, immobility = templates[scenario]
    return {
        "accel_mean_g": _clipped_normal(rng, mean_g, 0.05 * scale, 0.70, 1.60),
        "accel_std_g": _clipped_normal(
            rng, std_g * scale, max(0.025, std_g * 0.22), 0.005, 1.40
        ),
        "accel_peak_g": _clipped_normal(
            rng, peak_g * scale, max(0.10, peak_g * 0.14), 0.75, 7.50
        ),
        "gyro_peak_dps": _clipped_normal(
            rng, gyro * scale, max(7, gyro * 0.18), 1, 850
        ),
        "posture_change_deg": _clipped_normal(
            rng, posture, max(3, posture * 0.23), 0, 160
        ),
        "immobility_s": _clipped_normal(
            rng, immobility, max(0.04, immobility * 0.25), 0, 2.0
        ),
    }


def _health_features(
    rng: np.random.Generator, scenario: str, profile: SubjectProfile
) -> dict[str, float]:
    is_health_event = scenario in {"health_anomaly", "fall_health_anomaly"}
    motion_hr_addition = {"walk": 13, "run": 54, "stumble": 20, "fall": 24}.get(
        scenario, 0
    )

    if is_health_event:
        event = rng.choice(["bradycardia", "tachycardia", "low_spo2", "combined"])
        if event == "bradycardia":
            heart_rate = _clipped_normal(rng, 42, 7, 25, 62)
            spo2 = _clipped_normal(rng, profile.baseline_spo2 - 2, 2, 86, 100)
        elif event == "tachycardia":
            heart_rate = _clipped_normal(rng, 142, 18, 105, 205)
            spo2 = _clipped_normal(rng, profile.baseline_spo2 - 2, 2.5, 84, 100)
        elif event == "low_spo2":
            heart_rate = _clipped_normal(rng, profile.baseline_hr + 14, 15, 42, 165)
            spo2 = _clipped_normal(rng, 87.5, 3.2, 75, 94)
        else:
            heart_rate = _clipped_normal(rng, 134, 24, 35, 205)
            spo2 = _clipped_normal(rng, 86.5, 3.8, 72, 94)
    else:
        heart_rate = _clipped_normal(
            rng, profile.baseline_hr + motion_hr_addition, 7.5, 42, 190
        )
        spo2 = _clipped_normal(rng, profile.baseline_spo2 - (0.8 if scenario == "run" else 0), 1.0, 91, 100)

    quality_penalty = 0.20 if scenario in {"run", "fall", "fall_health_anomaly"} else 0
    ppg_quality = _clipped_normal(
        rng, profile.ppg_quality - quality_penalty, 0.10, 0.02, 1.0
    )
    return {
        "heart_rate_bpm": heart_rate,
        "spo2_percent": spo2,
        "ppg_signal_quality": ppg_quality,
    }


def generate_synthetic_dataset(
    rows: int = 6000,
    subjects: int = 80,
    seed: int = 42,
    missing_rate: float = 0.012,
) -> pd.DataFrame:
    """Return synthetic two-second feature windows.

    Args:
        rows: Number of feature windows.
        subjects: Number of independent synthetic subject profiles.
        seed: Reproducibility seed.
        missing_rate: Per-value probability of missing PPG fields.
    """
    if rows < 100:
        raise ValueError("rows must be at least 100")
    if subjects < 5 or subjects > rows:
        raise ValueError("subjects must be between 5 and rows")
    if not 0 <= missing_rate < 0.25:
        raise ValueError("missing_rate must be in [0, 0.25)")

    rng = np.random.default_rng(seed)
    profiles = _make_subjects(rng, subjects)
    records: list[dict[str, object]] = []

    for index in range(rows):
        profile = profiles[int(rng.integers(0, len(profiles)))]
        scenario = str(rng.choice(SCENARIOS, p=SCENARIO_PROBABILITIES))
        fall_label = int(scenario in {"fall", "fall_health_anomaly"})
        health_label = int(
            scenario in {"health_anomaly", "fall_health_anomaly"}
        )

        # Small independent label noise prevents unrealistic perfect separation.
        if rng.random() < 0.012:
            fall_label = 1 - fall_label
        if rng.random() < 0.012:
            health_label = 1 - health_label

        record: dict[str, object] = {
            "sample_id": f"SYN-W{index + 1:06d}",
            "subject_id": profile.subject_id,
            "scenario": scenario,
            **_motion_features(rng, scenario, profile.motion_scale),
            **_health_features(rng, scenario, profile),
            "label_fall": fall_label,
            "label_health_anomaly": health_label,
        }

        for column in ("heart_rate_bpm", "spo2_percent", "ppg_signal_quality"):
            if rng.random() < missing_rate:
                record[column] = np.nan
        records.append(record)

    dataframe = pd.DataFrame.from_records(records)
    ordered_columns = [
        "sample_id",
        "subject_id",
        "scenario",
        "accel_mean_g",
        "accel_std_g",
        "accel_peak_g",
        "gyro_peak_dps",
        "posture_change_deg",
        "immobility_s",
        "heart_rate_bpm",
        "spo2_percent",
        "ppg_signal_quality",
        "label_fall",
        "label_health_anomaly",
    ]
    return dataframe[ordered_columns]


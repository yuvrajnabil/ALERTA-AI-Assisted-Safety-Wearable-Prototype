from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
import re

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alerta_ml.export_cpp import export_models_to_header
from alerta_ml.schema import FALL_FEATURES, HEALTH_FEATURES, REQUIRED_COLUMNS
from alerta_ml.synthetic import generate_synthetic_dataset
from train_models import train_task


class SyntheticDataTests(unittest.TestCase):
    def test_schema_ranges_and_reproducibility(self) -> None:
        first = generate_synthetic_dataset(rows=800, subjects=20, seed=7)
        second = generate_synthetic_dataset(rows=800, subjects=20, seed=7)
        self.assertTrue(first.equals(second))
        self.assertTrue(set(REQUIRED_COLUMNS).issubset(first.columns))
        self.assertGreater(first["label_fall"].sum(), 20)
        self.assertGreater(first["label_health_anomaly"].sum(), 15)
        self.assertTrue(first["accel_peak_g"].between(0.7, 7.6).all())
        self.assertTrue(first["spo2_percent"].dropna().between(70, 100).all())

    def test_training_and_cpp_export(self) -> None:
        data = generate_synthetic_dataset(rows=1400, subjects=28, seed=11)
        fall = train_task(
            data,
            "fall",
            "label_fall",
            FALL_FEATURES,
            seed=11,
            estimators=5,
            max_depth=4,
        )
        health = train_task(
            data,
            "health",
            "label_health_anomaly",
            HEALTH_FEATURES,
            seed=12,
            estimators=5,
            max_depth=4,
        )
        self.assertTrue(0.0 <= fall.metrics["roc_auc"] <= 1.0)
        self.assertTrue(0.0 <= health.metrics["roc_auc"] <= 1.0)

        with tempfile.TemporaryDirectory() as temporary:
            header = Path(temporary) / "generated_models.h"
            export_models_to_header(
                header,
                fall.model,
                fall.features,
                fall.medians.tolist(),
                fall.threshold,
                health.model,
                health.features,
                health.medians.tolist(),
                health.threshold,
            )
            text = header.read_text(encoding="utf-8")
            self.assertIn("predict_fall_probability", text)
            self.assertIn("predict_health_probability", text)
            self.assertNotIn("nanF", text)
            self.assertIsNone(re.search(r"(?<![.\w])\d+F\b", text))


if __name__ == "__main__":
    unittest.main()

"""Reusable data and model utilities for the ALERTA prototype."""

from .schema import FALL_FEATURES, HEALTH_FEATURES, REQUIRED_COLUMNS
from .synthetic import generate_synthetic_dataset

__all__ = [
    "FALL_FEATURES",
    "HEALTH_FEATURES",
    "REQUIRED_COLUMNS",
    "generate_synthetic_dataset",
]


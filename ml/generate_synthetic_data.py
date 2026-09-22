#!/usr/bin/env python3
"""Command-line entry point for ALERTA synthetic feature data."""

from __future__ import annotations

import argparse
from pathlib import Path

from alerta_ml.synthetic import generate_synthetic_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--subjects", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--missing-rate", type=float, default=0.012)
    parser.add_argument(
        "--output", type=Path, default=Path("data/alerta_synthetic_v1.csv")
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = generate_synthetic_dataset(
        rows=args.rows,
        subjects=args.subjects,
        seed=args.seed,
        missing_rate=args.missing_rate,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, index=False)
    print(f"Saved {len(data):,} synthetic windows to {args.output}")
    print(data[["label_fall", "label_health_anomaly"]].mean().rename("rate"))


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""Train, evaluate and export ALERTA Random Forest prototype models."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit

from alerta_ml.export_cpp import export_models_to_header
from alerta_ml.schema import FALL_FEATURES, HEALTH_FEATURES, REQUIRED_COLUMNS


@dataclass
class TrainedTask:
    name: str
    target: str
    features: list[str]
    model: RandomForestClassifier
    medians: pd.Series
    threshold: float
    metrics: dict[str, object]
    predictions: pd.DataFrame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=Path("data/alerta_synthetic_v1.csv")
    )
    parser.add_argument("--outdir", type=Path, default=Path("artifacts"))
    parser.add_argument(
        "--header", type=Path, default=Path("include/generated_models.h")
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--estimators", type=int, default=24)
    parser.add_argument("--max-depth", type=int, default=6)
    return parser.parse_args()


def make_model(seed: int, estimators: int, max_depth: int) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=estimators,
        max_depth=max_depth,
        min_samples_leaf=4,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=-1,
    )


def choose_threshold(
    y_true: np.ndarray, probabilities: np.ndarray, minimum_recall: float = 0.90
) -> float:
    candidates: list[tuple[float, float, float]] = []
    for threshold in np.linspace(0.25, 0.85, 61):
        predicted = (probabilities >= threshold).astype(int)
        recall = recall_score(y_true, predicted, zero_division=0)
        f1 = f1_score(y_true, predicted, zero_division=0)
        candidates.append((float(threshold), float(recall), float(f1)))

    eligible = [item for item in candidates if item[1] >= minimum_recall]
    pool = eligible if eligible else candidates
    # Prefer F1, then recall, then the larger threshold to reduce false alarms.
    return max(pool, key=lambda item: (item[2], item[1], item[0]))[0]


def calculate_metrics(
    y_true: np.ndarray, probabilities: np.ndarray, threshold: float
) -> dict[str, object]:
    predicted = (probabilities >= threshold).astype(int)
    matrix = confusion_matrix(y_true, predicted, labels=[0, 1])
    return {
        "threshold": round(float(threshold), 4),
        "accuracy": round(float(accuracy_score(y_true, predicted)), 4),
        "balanced_accuracy": round(
            float(balanced_accuracy_score(y_true, predicted)), 4
        ),
        "precision": round(
            float(precision_score(y_true, predicted, zero_division=0)), 4
        ),
        "recall": round(float(recall_score(y_true, predicted, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predicted, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "confusion_matrix": matrix.tolist(),
        "test_negative": int((y_true == 0).sum()),
        "test_positive": int((y_true == 1).sum()),
    }


def train_task(
    dataframe: pd.DataFrame,
    name: str,
    target: str,
    features: list[str],
    seed: int,
    estimators: int,
    max_depth: int,
) -> TrainedTask:
    x = dataframe[features].copy()
    y = dataframe[target].astype(int)
    groups = dataframe["subject_id"].astype(str)

    outer_split = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=seed)
    train_full_idx, test_idx = next(outer_split.split(x, y, groups))
    x_train_full = x.iloc[train_full_idx].reset_index(drop=True)
    y_train_full = y.iloc[train_full_idx].reset_index(drop=True)
    groups_train_full = groups.iloc[train_full_idx].reset_index(drop=True)
    x_test = x.iloc[test_idx].reset_index(drop=True)
    y_test = y.iloc[test_idx].reset_index(drop=True)

    inner_split = GroupShuffleSplit(
        n_splits=1, test_size=0.22, random_state=seed + 101
    )
    train_idx, validation_idx = next(
        inner_split.split(x_train_full, y_train_full, groups_train_full)
    )
    x_train = x_train_full.iloc[train_idx]
    y_train = y_train_full.iloc[train_idx]
    x_validation = x_train_full.iloc[validation_idx]
    y_validation = y_train_full.iloc[validation_idx]

    threshold_medians = x_train.median(numeric_only=True)
    threshold_model = make_model(seed, estimators, max_depth)
    threshold_model.fit(x_train.fillna(threshold_medians), y_train)
    validation_probability = threshold_model.predict_proba(
        x_validation.fillna(threshold_medians)
    )[:, 1]
    threshold = choose_threshold(y_validation.to_numpy(), validation_probability)

    # Refit on all non-test subjects after choosing the threshold.
    final_medians = x_train_full.median(numeric_only=True)
    final_model = make_model(seed, estimators, max_depth)
    final_model.fit(x_train_full.fillna(final_medians), y_train_full)
    test_probability = final_model.predict_proba(x_test.fillna(final_medians))[:, 1]
    test_prediction = (test_probability >= threshold).astype(int)
    metrics = calculate_metrics(y_test.to_numpy(), test_probability, threshold)
    metrics.update(
        {
            "features": features,
            "train_subjects": int(groups_train_full.nunique()),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
            "estimators": estimators,
            "max_depth": max_depth,
        }
    )
    predictions = pd.DataFrame(
        {
            "row_index": test_idx,
            "subject_id": groups.iloc[test_idx].to_numpy(),
            "actual": y_test.to_numpy(),
            "probability": test_probability,
            "predicted": test_prediction,
        }
    )
    return TrainedTask(
        name=name,
        target=target,
        features=features,
        model=final_model,
        medians=final_medians,
        threshold=threshold,
        metrics=metrics,
        predictions=predictions,
    )


def save_task(task: TrainedTask, outdir: Path) -> None:
    bundle = {
        "model": task.model,
        "task": task.name,
        "target": task.target,
        "features": task.features,
        "medians": task.medians.to_dict(),
        "threshold": task.threshold,
        "training_data": "synthetic feature windows only",
    }
    joblib.dump(bundle, outdir / f"{task.name}_model.joblib")
    task.predictions.to_csv(outdir / f"{task.name}_test_predictions.csv", index=False)

    importance = pd.DataFrame(
        {"feature": task.features, "importance": task.model.feature_importances_}
    ).sort_values("importance", ascending=False)
    importance.to_csv(outdir / f"{task.name}_feature_importance.csv", index=False)

    matrix = np.asarray(task.metrics["confusion_matrix"])
    display = ConfusionMatrixDisplay(matrix, display_labels=["negative", "positive"])
    display.plot(cmap="Purples", colorbar=False)
    display.ax_.set_title(f"ALERTA {task.name.replace('_', ' ').title()}\nSynthetic test set")
    plt.tight_layout()
    plt.savefig(outdir / f"{task.name}_confusion_matrix.png", dpi=180)
    plt.close()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.data)
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    if data["subject_id"].nunique() < 10:
        raise ValueError("At least 10 subjects are required for grouped evaluation")

    args.outdir.mkdir(parents=True, exist_ok=True)
    fall = train_task(
        data,
        name="fall",
        target="label_fall",
        features=FALL_FEATURES,
        seed=args.seed,
        estimators=args.estimators,
        max_depth=args.max_depth,
    )
    health = train_task(
        data,
        name="health",
        target="label_health_anomaly",
        features=HEALTH_FEATURES,
        seed=args.seed + 1,
        estimators=args.estimators,
        max_depth=args.max_depth,
    )

    save_task(fall, args.outdir)
    save_task(health, args.outdir)
    export_models_to_header(
        args.header,
        fall_model=fall.model,
        fall_features=fall.features,
        fall_medians=fall.medians.tolist(),
        fall_threshold=fall.threshold,
        health_model=health.model,
        health_features=health.features,
        health_medians=health.medians.tolist(),
        health_threshold=health.threshold,
    )

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "data_file": str(args.data),
        "rows": int(len(data)),
        "subjects": int(data["subject_id"].nunique()),
        "seed": args.seed,
        "warning": (
            "Metrics use synthetic feature windows only and must not be interpreted "
            "as clinical or field performance."
        ),
        "fall": fall.metrics,
        "health": health.metrics,
    }
    (args.outdir / "metrics.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    print(f"Exported ESP32 header to {args.header}")


if __name__ == "__main__":
    main()


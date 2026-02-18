"""Evaluation metrics for burnout detection models."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compute a comprehensive set of evaluation metrics.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        y_proba: Predicted probabilities for the positive class (optional).

    Returns:
        Dict of metric name to value.
    """
    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
    }

    if y_proba is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
        except ValueError:
            # Can fail if only one class present in y_true
            metrics["roc_auc"] = None

    return metrics


def compute_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_feature: np.ndarray,
) -> dict[str, dict[str, float]]:
    """Compute per-group fairness metrics for bias auditing.

    Important for neurological burnout detection: different neurological
    conditions may lead to different base rates, and the model should
    not systematically disadvantage any group.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        sensitive_feature: Array of group labels (e.g., neurological condition).

    Returns:
        Nested dict: {group_value: {metric_name: value}}.
    """
    groups = np.unique(sensitive_feature)
    results: dict[str, dict[str, float]] = {}

    for group in groups:
        mask = sensitive_feature == group
        if mask.sum() == 0:
            continue

        group_true = y_true[mask]
        group_pred = y_pred[mask]

        results[str(group)] = {
            "n_samples": int(mask.sum()),
            "positive_rate": float(group_pred.mean()),
            "true_positive_rate": float(
                recall_score(group_true, group_pred, zero_division=0)
            ),
            "false_positive_rate": float(
                _false_positive_rate(group_true, group_pred)
            ),
            "precision": float(
                precision_score(group_true, group_pred, zero_division=0)
            ),
            "f1": float(f1_score(group_true, group_pred, zero_division=0)),
        }

    return results


def _false_positive_rate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute false positive rate."""
    negatives = (y_true == 0).sum()
    if negatives == 0:
        return 0.0
    false_positives = ((y_pred == 1) & (y_true == 0)).sum()
    return float(false_positives / negatives)

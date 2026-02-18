"""Tests for evaluation metrics and bias auditing."""

from __future__ import annotations

import numpy as np

from burnout_detection.evaluation.bias import audit_bias
from burnout_detection.evaluation.metrics import (
    compute_fairness_metrics,
    evaluate_model,
)


class TestEvaluateModel:
    def test_returns_all_metrics(self) -> None:
        y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 0, 1, 1, 0, 0, 1, 1])
        metrics = evaluate_model(y_true, y_pred)
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "confusion_matrix" in metrics

    def test_roc_auc_with_proba(self) -> None:
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 0, 1, 1])
        y_proba = np.array([0.1, 0.3, 0.7, 0.9])
        metrics = evaluate_model(y_true, y_pred, y_proba)
        assert "roc_auc" in metrics
        assert metrics["roc_auc"] is not None

    def test_perfect_predictions(self) -> None:
        y = np.array([0, 0, 1, 1])
        metrics = evaluate_model(y, y)
        assert metrics["accuracy"] == 1.0
        assert metrics["f1"] == 1.0


class TestFairnessMetrics:
    def test_per_group_metrics(self) -> None:
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred = np.array([0, 0, 1, 1, 1, 1])
        groups = np.array(["A", "A", "A", "B", "B", "B"])
        results = compute_fairness_metrics(y_true, y_pred, groups)
        assert "A" in results
        assert "B" in results
        assert "n_samples" in results["A"]
        assert "true_positive_rate" in results["A"]


class TestAuditBias:
    def test_detects_disparity(self) -> None:
        # Group A: 3 negatives, 3 positives — all predicted positive
        # Group B: 3 negatives, 3 positives — all predicted negative
        y_true = np.array([0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1])
        y_pred = np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
        groups = np.array(["A"] * 6 + ["B"] * 6)
        results = audit_bias(
            y_true,
            y_pred,
            {"condition": groups},
            disparity_threshold=0.1,
        )
        assert "condition" in results
        # Group A positive_rate=1.0, Group B positive_rate=0.0 → disparity=1.0
        assert results["condition"].max_disparity > 0
        assert not results["condition"].passed

    def test_passes_when_fair(self) -> None:
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])
        groups = np.array(["A", "A", "B", "B"])
        results = audit_bias(
            y_true,
            y_pred,
            {"condition": groups},
            disparity_threshold=0.1,
        )
        assert results["condition"].passed

"""Bias auditing for burnout detection models.

Neurological burnout detection requires careful attention to bias:
- Different conditions have different base rates of fatigue/burnout symptoms.
- Models must not systematically over- or under-predict for specific conditions.
- Demographic fairness (age, gender) must also be monitored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from burnout_detection.evaluation.metrics import compute_fairness_metrics


@dataclass
class BiasAuditResult:
    """Results of a bias audit across one sensitive attribute."""

    attribute_name: str
    group_metrics: dict[str, dict[str, float]]
    max_disparity: float
    flagged_groups: list[str] = field(default_factory=list)
    passed: bool = True

    def summary(self) -> str:
        """Human-readable summary of the bias audit."""
        lines = [f"Bias Audit: {self.attribute_name}"]
        lines.append(f"  Max disparity (positive rate): {self.max_disparity:.4f}")
        lines.append(f"  Status: {'PASSED' if self.passed else 'FLAGGED'}")
        if self.flagged_groups:
            lines.append(f"  Flagged groups: {self.flagged_groups}")
        for group, metrics in self.group_metrics.items():
            lines.append(f"  {group}: n={metrics['n_samples']:.0f}, "
                         f"TPR={metrics['true_positive_rate']:.3f}, "
                         f"FPR={metrics['false_positive_rate']:.3f}")
        return "\n".join(lines)


def audit_bias(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: dict[str, np.ndarray],
    disparity_threshold: float = 0.1,
) -> dict[str, BiasAuditResult]:
    """Run bias audits across multiple sensitive attributes.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        sensitive_features: Dict mapping attribute names to arrays of group labels.
            E.g., {"neurological_condition": [...], "gender": [...]}.
        disparity_threshold: Maximum allowed difference in positive prediction
            rates between any two groups before flagging.

    Returns:
        Dict mapping attribute names to BiasAuditResult objects.
    """
    results: dict[str, BiasAuditResult] = {}

    for attr_name, groups in sensitive_features.items():
        group_metrics = compute_fairness_metrics(y_true, y_pred, groups)

        # Compute max disparity in positive prediction rates
        positive_rates = [m["positive_rate"] for m in group_metrics.values()]
        max_disparity = max(positive_rates) - min(positive_rates) if positive_rates else 0.0

        # Flag groups with significantly different positive rates
        mean_rate = np.mean(positive_rates) if positive_rates else 0.0
        flagged = [
            group
            for group, m in group_metrics.items()
            if abs(m["positive_rate"] - mean_rate) > disparity_threshold
        ]

        passed = max_disparity <= disparity_threshold

        results[attr_name] = BiasAuditResult(
            attribute_name=attr_name,
            group_metrics=group_metrics,
            max_disparity=max_disparity,
            flagged_groups=flagged,
            passed=passed,
        )

    return results

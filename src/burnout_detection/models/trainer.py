"""Model training for burnout detection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

MODEL_REGISTRY: dict[str, type] = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
}

DEFAULT_PARAMS: dict[str, dict[str, Any]] = {
    "logistic_regression": {
        "max_iter": 1000,
        "random_state": 42,
        "class_weight": "balanced",
    },
    "random_forest": {
        "n_estimators": 200,
        "max_depth": 10,
        "random_state": 42,
        "class_weight": "balanced",
        "n_jobs": -1,
    },
    "gradient_boosting": {
        "n_estimators": 200,
        "max_depth": 5,
        "learning_rate": 0.1,
        "random_state": 42,
    },
}


def get_model(
    model_name: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """Instantiate a model by name with optional parameter overrides.

    Args:
        model_name: Key from MODEL_REGISTRY.
        params: Parameter overrides. Merged with DEFAULT_PARAMS.

    Returns:
        An instantiated sklearn-compatible estimator.

    Raises:
        ValueError: If model_name is not in the registry.
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model: '{model_name}'. Available: {list(MODEL_REGISTRY.keys())}"
        )

    merged_params = {**DEFAULT_PARAMS.get(model_name, {})}
    if params:
        merged_params.update(params)

    return MODEL_REGISTRY[model_name](**merged_params)


def train_model(
    X_train: pd.DataFrame | np.ndarray,
    y_train: pd.Series | np.ndarray,
    model_name: str = "gradient_boosting",
    params: dict[str, Any] | None = None,
) -> Any:
    """Train a burnout detection model.

    Args:
        X_train: Training features.
        y_train: Training labels (0 = no burnout, 1 = burnout).
        model_name: Name of the model to train (from MODEL_REGISTRY).
        params: Optional parameter overrides.

    Returns:
        A fitted model instance.
    """
    model = get_model(model_name, params)
    model.fit(X_train, y_train)
    return model


def cross_validate(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    model_name: str = "gradient_boosting",
    params: dict[str, Any] | None = None,
    n_folds: int = 5,
    scoring: str = "f1",
) -> dict[str, Any]:
    """Perform stratified k-fold cross-validation.

    Args:
        X: Feature matrix.
        y: Label vector.
        model_name: Name of the model to evaluate.
        params: Optional parameter overrides.
        n_folds: Number of cross-validation folds.
        scoring: Scoring metric (e.g., 'f1', 'accuracy', 'roc_auc').

    Returns:
        Dict with 'scores', 'mean', and 'std' of CV results.
    """
    model = get_model(model_name, params)
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)

    return {
        "model_name": model_name,
        "scoring": scoring,
        "n_folds": n_folds,
        "scores": scores.tolist(),
        "mean": float(scores.mean()),
        "std": float(scores.std()),
    }

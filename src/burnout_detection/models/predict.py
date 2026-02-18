"""Prediction and inference for burnout detection models."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def predict(
    model: Any,
    X: pd.DataFrame | np.ndarray,
) -> np.ndarray:
    """Generate burnout predictions from a trained model.

    Args:
        model: A fitted sklearn-compatible model.
        X: Feature matrix for prediction.

    Returns:
        Array of predicted labels (0 = no burnout, 1 = burnout).
    """
    return model.predict(X)


def predict_proba(
    model: Any,
    X: pd.DataFrame | np.ndarray,
) -> np.ndarray:
    """Generate burnout risk probabilities from a trained model.

    Args:
        model: A fitted sklearn-compatible model with predict_proba.
        X: Feature matrix for prediction.

    Returns:
        Array of shape (n_samples, 2) with probabilities for each class.

    Raises:
        AttributeError: If the model does not support predict_proba.
    """
    if not hasattr(model, "predict_proba"):
        raise AttributeError(
            f"Model {type(model).__name__} does not support predict_proba. "
            "Use predict() for hard predictions."
        )
    return model.predict_proba(X)


def predict_with_confidence(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Generate predictions with confidence scores and risk levels.

    Args:
        model: A fitted sklearn-compatible model with predict_proba.
        X: Feature matrix for prediction.
        threshold: Probability threshold for positive (burnout) class.

    Returns:
        DataFrame with columns: prediction, burnout_probability, risk_level.
    """
    probas = predict_proba(model, X)
    burnout_prob = probas[:, 1]

    predictions = (burnout_prob >= threshold).astype(int)

    risk_levels = np.where(
        burnout_prob >= 0.75,
        "high",
        np.where(burnout_prob >= 0.5, "moderate", np.where(burnout_prob >= 0.25, "low", "minimal")),
    )

    return pd.DataFrame(
        {
            "prediction": predictions,
            "burnout_probability": burnout_prob,
            "risk_level": risk_levels,
        }
    )

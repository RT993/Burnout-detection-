"""Tests for model training and prediction."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from burnout_detection.models.predict import predict, predict_proba, predict_with_confidence
from burnout_detection.models.trainer import (
    MODEL_REGISTRY,
    cross_validate,
    get_model,
    train_model,
)


class TestGetModel:
    def test_returns_known_models(self) -> None:
        for name in MODEL_REGISTRY:
            model = get_model(name)
            assert model is not None

    def test_raises_on_unknown_model(self) -> None:
        with pytest.raises(ValueError, match="Unknown model"):
            get_model("nonexistent_model")

    def test_param_override(self) -> None:
        model = get_model("random_forest", {"n_estimators": 50})
        assert model.n_estimators == 50


class TestTrainModel:
    def test_trains_and_predicts(self) -> None:
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
        y = pd.Series(np.random.randint(0, 2, size=100))
        model = train_model(X, y, model_name="logistic_regression")
        preds = predict(model, X)
        assert len(preds) == 100
        assert set(preds).issubset({0, 1})

    def test_predict_proba(self) -> None:
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
        y = pd.Series(np.random.randint(0, 2, size=100))
        model = train_model(X, y, model_name="logistic_regression")
        probas = predict_proba(model, X)
        assert probas.shape == (100, 2)
        assert (probas >= 0).all() and (probas <= 1).all()


class TestPredictWithConfidence:
    def test_returns_risk_levels(self) -> None:
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
        y = pd.Series(np.random.randint(0, 2, size=100))
        model = train_model(X, y, model_name="logistic_regression")
        result = predict_with_confidence(model, X)
        assert "prediction" in result.columns
        assert "burnout_probability" in result.columns
        assert "risk_level" in result.columns
        assert set(result["risk_level"].unique()).issubset(
            {"minimal", "low", "moderate", "high"}
        )


class TestCrossValidate:
    def test_returns_cv_results(self) -> None:
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
        y = pd.Series(np.random.randint(0, 2, size=100))
        results = cross_validate(X, y, model_name="logistic_regression", n_folds=3)
        assert "mean" in results
        assert "std" in results
        assert len(results["scores"]) == 3

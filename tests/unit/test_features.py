"""Tests for feature engineering."""

from __future__ import annotations

import pandas as pd

from burnout_detection.features.builder import (
    build_features,
    compute_burnout_composite,
    compute_neuro_fatigue_index,
    compute_work_strain_ratio,
)


class TestBurnoutComposite:
    def test_returns_series(self, sample_survey_df: pd.DataFrame) -> None:
        result = compute_burnout_composite(sample_survey_df)
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_survey_df)

    def test_higher_exhaustion_means_higher_score(self) -> None:
        df = pd.DataFrame(
            {
                "exhaustion_score": [1.0, 5.0],
                "depersonalization_score": [1.0, 1.0],
                "efficacy_score": [5.0, 5.0],
            }
        )
        result = compute_burnout_composite(df)
        assert result.iloc[1] > result.iloc[0]


class TestNeuroFatigueIndex:
    def test_returns_named_series(self, sample_survey_df: pd.DataFrame) -> None:
        result = compute_neuro_fatigue_index(sample_survey_df)
        assert result.name == "neuro_fatigue_index"
        assert len(result) == len(sample_survey_df)

    def test_handles_missing_columns(self) -> None:
        df = pd.DataFrame({"other": [1, 2, 3]})
        result = compute_neuro_fatigue_index(df)
        assert (result == 0.0).all()


class TestWorkStrainRatio:
    def test_computes_ratio(self) -> None:
        df = pd.DataFrame(
            {"work_hours_weekly": [40.0, 20.0], "fatigue_level": [8.0, 8.0]}
        )
        result = compute_work_strain_ratio(df)
        assert result.iloc[1] > result.iloc[0]  # Same fatigue, fewer hours = higher strain


class TestBuildFeatures:
    def test_adds_engineered_columns(self, sample_survey_df: pd.DataFrame) -> None:
        result = build_features(sample_survey_df)
        assert "burnout_composite" in result.columns
        assert "neuro_fatigue_index" in result.columns
        assert "work_strain_ratio" in result.columns
        assert "symptom_burnout_interaction" in result.columns

    def test_skip_neuro_features(self, sample_survey_df: pd.DataFrame) -> None:
        result = build_features(sample_survey_df, include_neuro_features=False)
        assert "neuro_fatigue_index" not in result.columns

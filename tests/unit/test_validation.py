"""Tests for data validation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from burnout_detection.data.validation import validate_dataframe


class TestValidateDataframe:
    def test_valid_data_passes(self, sample_survey_df: pd.DataFrame) -> None:
        result = validate_dataframe(sample_survey_df, require_all_columns=True)
        assert result.is_valid

    def test_empty_dataframe_fails(self) -> None:
        result = validate_dataframe(pd.DataFrame())
        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_missing_columns_detected(self) -> None:
        df = pd.DataFrame({"participant_id": [1], "age": [30]})
        result = validate_dataframe(df, require_all_columns=True)
        assert not result.is_valid
        assert any("Missing required columns" in e for e in result.errors)

    def test_negative_scores_flagged(self) -> None:
        df = pd.DataFrame(
            {
                "participant_id": [1],
                "age": [30],
                "gender": ["male"],
                "neurological_condition": ["none"],
                "exhaustion_score": [-1.0],
                "depersonalization_score": [3.0],
                "efficacy_score": [4.0],
            }
        )
        result = validate_dataframe(df, require_all_columns=True)
        assert not result.is_valid
        assert any("negative" in e.lower() for e in result.errors)

    def test_unknown_conditions_warned(self, sample_survey_df: pd.DataFrame) -> None:
        df = sample_survey_df.copy()
        df.loc[0, "neurological_condition"] = "unknown_rare_condition"
        result = validate_dataframe(df)
        assert any("Unknown neurological conditions" in w for w in result.warnings)

    def test_duplicate_ids_warned(self, sample_survey_df: pd.DataFrame) -> None:
        df = sample_survey_df.copy()
        df.loc[1, "participant_id"] = df.loc[0, "participant_id"]
        result = validate_dataframe(df)
        assert any("duplicate" in w.lower() for w in result.warnings)

    def test_high_missing_rate_flagged(self) -> None:
        df = pd.DataFrame(
            {
                "participant_id": [1, 2, 3],
                "age": [np.nan, np.nan, np.nan],
                "gender": [np.nan, np.nan, np.nan],
                "neurological_condition": [np.nan, np.nan, np.nan],
                "exhaustion_score": [np.nan, np.nan, np.nan],
                "depersonalization_score": [np.nan, np.nan, np.nan],
                "efficacy_score": [np.nan, np.nan, np.nan],
            }
        )
        result = validate_dataframe(df)
        has_missing_warning = any("missing" in (w + "").lower() for w in result.warnings)
        has_missing_error = any("missing" in (e + "").lower() for e in result.errors)
        assert has_missing_warning or has_missing_error

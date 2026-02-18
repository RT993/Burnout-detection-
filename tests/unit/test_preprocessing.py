"""Tests for data preprocessing utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from burnout_detection.data.preprocessing import (
    encode_categorical,
    handle_missing_values,
    preprocess_pipeline,
    remove_outliers,
    scale_features,
)


class TestHandleMissingValues:
    def test_imputes_numeric_median(self) -> None:
        df = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": [10.0, 20.0, np.nan]})
        result = handle_missing_values(df, numeric_strategy="median")
        assert result.isna().sum().sum() == 0
        assert result["a"].iloc[1] == 2.0  # median of [1, 3]

    def test_imputes_categorical(self) -> None:
        df = pd.DataFrame({"cat": ["a", "a", None, "b"]})
        result = handle_missing_values(df)
        assert result.isna().sum().sum() == 0
        assert result["cat"].iloc[2] == "a"  # most frequent


class TestEncodeCategorical:
    def test_encodes_object_columns(self) -> None:
        df = pd.DataFrame({"cat": ["a", "b", "c"], "num": [1, 2, 3]})
        result, encoders = encode_categorical(df)
        assert "cat" in encoders
        assert result["cat"].dtype in (np.int64, np.int32, int)

    def test_specific_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]})
        result, encoders = encode_categorical(df, columns=["a"])
        assert "a" in encoders
        assert "b" not in encoders


class TestScaleFeatures:
    def test_standardizes_to_zero_mean(self) -> None:
        df = pd.DataFrame({"a": [10.0, 20.0, 30.0], "b": [100.0, 200.0, 300.0]})
        result, scaler = scale_features(df)
        assert abs(result["a"].mean()) < 1e-10
        assert abs(result["b"].mean()) < 1e-10

    def test_reuse_scaler(self) -> None:
        df_train = pd.DataFrame({"a": [10.0, 20.0, 30.0]})
        _, scaler = scale_features(df_train)
        df_test = pd.DataFrame({"a": [15.0, 25.0]})
        result, _ = scale_features(df_test, scaler=scaler)
        assert result is not df_test


class TestRemoveOutliers:
    def test_iqr_removes_outliers(self) -> None:
        values = [1, 2, 3, 4, 5, 100]  # 100 is an outlier
        df = pd.DataFrame({"a": values})
        result = remove_outliers(df, method="iqr", threshold=1.5)
        assert 100 not in result["a"].values

    def test_zscore_removes_outliers(self) -> None:
        values = list(range(20)) + [1000]
        df = pd.DataFrame({"a": values})
        result = remove_outliers(df, method="zscore", threshold=3.0)
        assert 1000 not in result["a"].values


class TestPreprocessPipeline:
    def test_full_pipeline(self, sample_survey_df: pd.DataFrame) -> None:
        result, artifacts = preprocess_pipeline(sample_survey_df)
        assert not result.empty
        assert "scaler" in artifacts
        assert "encoders" in artifacts

"""Data preprocessing and cleaning for burnout detection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler


def handle_missing_values(
    df: pd.DataFrame,
    numeric_strategy: str = "median",
    categorical_strategy: str = "most_frequent",
) -> pd.DataFrame:
    """Impute missing values using specified strategies.

    Args:
        df: Input DataFrame.
        numeric_strategy: Strategy for numeric columns ('mean', 'median', 'most_frequent').
        categorical_strategy: Strategy for categorical columns ('most_frequent', 'constant').

    Returns:
        DataFrame with missing values imputed.
    """
    result = df.copy()

    numeric_cols = result.select_dtypes(include="number").columns.tolist()
    categorical_cols = result.select_dtypes(include=["object", "category"]).columns.tolist()

    if numeric_cols:
        imputer = SimpleImputer(strategy=numeric_strategy)
        result[numeric_cols] = imputer.fit_transform(result[numeric_cols])

    if categorical_cols:
        imputer = SimpleImputer(strategy=categorical_strategy)
        result[categorical_cols] = imputer.fit_transform(result[categorical_cols])

    return result


def encode_categorical(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    """Label-encode categorical columns.

    Args:
        df: Input DataFrame.
        columns: Specific columns to encode. If None, encodes all object/category columns.

    Returns:
        Tuple of (encoded DataFrame, dict mapping column names to fitted LabelEncoders).
    """
    result = df.copy()
    if columns is None:
        columns = result.select_dtypes(include=["object", "category"]).columns.tolist()

    encoders: dict[str, LabelEncoder] = {}
    for col in columns:
        if col in result.columns:
            le = LabelEncoder()
            # Handle NaN by converting to string temporarily
            mask = result[col].isna()
            result[col] = result[col].astype(str)
            result[col] = le.fit_transform(result[col])
            if mask.any():
                result.loc[mask, col] = np.nan
            encoders[col] = le

    return result, encoders


def scale_features(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    scaler: StandardScaler | None = None,
) -> tuple[pd.DataFrame, StandardScaler]:
    """Standardize numeric features to zero mean and unit variance.

    Args:
        df: Input DataFrame.
        columns: Columns to scale. If None, scales all numeric columns.
        scaler: Pre-fitted scaler for transform-only mode (e.g., for test data).

    Returns:
        Tuple of (scaled DataFrame, fitted StandardScaler).
    """
    result = df.copy()
    if columns is None:
        columns = result.select_dtypes(include="number").columns.tolist()

    if scaler is None:
        scaler = StandardScaler()
        result[columns] = scaler.fit_transform(result[columns])
    else:
        result[columns] = scaler.transform(result[columns])

    return result, scaler


def remove_outliers(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "iqr",
    threshold: float = 1.5,
) -> pd.DataFrame:
    """Remove outliers from numeric columns.

    Args:
        df: Input DataFrame.
        columns: Columns to check. If None, checks all numeric columns.
        method: Outlier detection method ('iqr' or 'zscore').
        threshold: IQR multiplier (default 1.5) or z-score threshold (default 3.0).

    Returns:
        DataFrame with outlier rows removed.
    """
    result = df.copy()
    if columns is None:
        columns = result.select_dtypes(include="number").columns.tolist()

    mask = pd.Series(True, index=result.index)

    for col in columns:
        if col not in result.columns:
            continue
        series = result[col].dropna()
        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            mask &= result[col].isna() | result[col].between(lower, upper)
        elif method == "zscore":
            mean = series.mean()
            std = series.std()
            if std > 0:
                z = (result[col] - mean).abs() / std
                mask &= result[col].isna() | (z <= threshold)

    return result[mask].reset_index(drop=True)


def preprocess_pipeline(
    df: pd.DataFrame,
    impute: bool = True,
    remove_outlier_cols: list[str] | None = None,
    encode: bool = True,
    scale: bool = True,
    scale_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run the full preprocessing pipeline.

    Args:
        df: Raw input DataFrame.
        impute: Whether to impute missing values.
        remove_outlier_cols: Columns to remove outliers from (None to skip).
        encode: Whether to label-encode categorical columns.
        scale: Whether to standardize numeric features.
        scale_columns: Specific columns to scale (None for all numeric).

    Returns:
        Tuple of (preprocessed DataFrame, dict of fitted artifacts for reuse).
    """
    artifacts: dict[str, Any] = {}
    result = df.copy()

    if impute:
        result = handle_missing_values(result)

    if remove_outlier_cols is not None:
        result = remove_outliers(result, columns=remove_outlier_cols)

    if encode:
        result, encoders = encode_categorical(result)
        artifacts["encoders"] = encoders

    if scale:
        result, scaler = scale_features(result, columns=scale_columns)
        artifacts["scaler"] = scaler

    return result, artifacts

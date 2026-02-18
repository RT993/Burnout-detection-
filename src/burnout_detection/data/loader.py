"""Data loading utilities for burnout detection datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


# Expected columns for the neurological burnout survey dataset
REQUIRED_COLUMNS: list[str] = [
    "participant_id",
    "age",
    "gender",
    "neurological_condition",
    "exhaustion_score",
    "depersonalization_score",
    "efficacy_score",
]

OPTIONAL_COLUMNS: list[str] = [
    "sleep_quality",
    "cognitive_load",
    "fatigue_level",
    "medication_adherence",
    "work_hours_weekly",
    "symptom_severity",
    "hrv_mean",
    "stress_self_report",
]

NEUROLOGICAL_CONDITIONS: list[str] = [
    "multiple_sclerosis",
    "epilepsy",
    "parkinsons",
    "traumatic_brain_injury",
    "chronic_fatigue_syndrome",
    "migraine_chronic",
    "adhd",
    "other",
    "none",
]


def load_survey_data(
    path: str | Path,
    drop_na: bool = False,
    validate: bool = True,
) -> pd.DataFrame:
    """Load burnout survey data from a CSV file.

    Args:
        path: Path to the CSV file.
        drop_na: Whether to drop rows with any missing values in required columns.
        validate: Whether to validate required columns exist.

    Returns:
        A DataFrame with the survey data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing and validate is True.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)

    if validate:
        missing = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}. "
                f"Expected: {REQUIRED_COLUMNS}"
            )

    if drop_na:
        present_required = [c for c in REQUIRED_COLUMNS if c in df.columns]
        df = df.dropna(subset=present_required)

    return df


def load_physiological_data(
    path: str | Path,
    resample_freq: str | None = None,
) -> pd.DataFrame:
    """Load physiological time-series data (HRV, sleep, activity).

    Args:
        path: Path to the CSV or Parquet file.
        resample_freq: Optional pandas frequency string for resampling (e.g., '1h', '1D').

    Returns:
        A DataFrame indexed by timestamp with physiological signals.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, parse_dates=["timestamp"])

    if "timestamp" in df.columns:
        df = df.set_index("timestamp").sort_index()

    if resample_freq and isinstance(df.index, pd.DatetimeIndex):
        df = df.resample(resample_freq).mean()

    return df


def load_dataset(
    survey_path: str | Path,
    physiological_path: str | Path | None = None,
    merge_on: str = "participant_id",
    **kwargs: Any,
) -> pd.DataFrame:
    """Load and optionally merge survey and physiological data.

    Args:
        survey_path: Path to the survey CSV.
        physiological_path: Optional path to physiological data.
        merge_on: Column to merge on if both datasets are provided.
        **kwargs: Additional keyword arguments passed to load_survey_data.

    Returns:
        A merged DataFrame or just the survey data if no physiological path given.
    """
    survey_df = load_survey_data(survey_path, **kwargs)

    if physiological_path is not None:
        phys_df = load_physiological_data(physiological_path)
        if merge_on in phys_df.columns or merge_on == phys_df.index.name:
            if merge_on == phys_df.index.name:
                phys_df = phys_df.reset_index()
            # Aggregate physiological data per participant before merging
            numeric_cols = phys_df.select_dtypes(include="number").columns.tolist()
            agg_cols = [c for c in numeric_cols if c != merge_on]
            if agg_cols:
                phys_agg = phys_df.groupby(merge_on)[agg_cols].mean().reset_index()
                survey_df = survey_df.merge(phys_agg, on=merge_on, how="left")

    return survey_df

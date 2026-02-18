"""Shared test fixtures for burnout detection tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_survey_df() -> pd.DataFrame:
    """Create a minimal valid survey DataFrame for testing."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame(
        {
            "participant_id": range(1, n + 1),
            "age": np.random.randint(22, 65, size=n),
            "gender": np.random.choice(["male", "female", "non_binary"], size=n),
            "neurological_condition": np.random.choice(
                [
                    "multiple_sclerosis",
                    "epilepsy",
                    "migraine_chronic",
                    "adhd",
                    "none",
                ],
                size=n,
            ),
            "exhaustion_score": np.random.uniform(0, 6, size=n).round(1),
            "depersonalization_score": np.random.uniform(0, 6, size=n).round(1),
            "efficacy_score": np.random.uniform(0, 6, size=n).round(1),
            "sleep_quality": np.random.uniform(1, 10, size=n).round(1),
            "cognitive_load": np.random.uniform(1, 10, size=n).round(1),
            "fatigue_level": np.random.uniform(1, 10, size=n).round(1),
            "medication_adherence": np.random.uniform(0, 1, size=n).round(2),
            "work_hours_weekly": np.random.uniform(20, 60, size=n).round(1),
            "symptom_severity": np.random.uniform(0, 10, size=n).round(1),
        }
    )


@pytest.fixture
def sample_survey_csv(tmp_path: object, sample_survey_df: pd.DataFrame) -> str:
    """Write sample survey data to a temp CSV and return the path."""
    path = str(tmp_path / "survey.csv")  # type: ignore[operator]
    sample_survey_df.to_csv(path, index=False)
    return path


@pytest.fixture
def binary_labels(sample_survey_df: pd.DataFrame) -> pd.Series:
    """Create binary burnout labels based on exhaustion score median split."""
    median = sample_survey_df["exhaustion_score"].median()
    return (sample_survey_df["exhaustion_score"] >= median).astype(int)

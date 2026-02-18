"""Tests for synthetic data generation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from burnout_detection.data.loader import NEUROLOGICAL_CONDITIONS, REQUIRED_COLUMNS
from burnout_detection.data.synthetic import (
    CONDITION_PROFILES,
    generate_cognitive_data,
    generate_full_dataset,
    generate_physiological_data,
    generate_survey_data,
)


# ---------------------------------------------------------------------------
# generate_survey_data
# ---------------------------------------------------------------------------

class TestGenerateSurveyData:
    def test_returns_dataframe(self) -> None:
        df = generate_survey_data(n_samples=50)
        assert isinstance(df, pd.DataFrame)

    def test_correct_row_count(self) -> None:
        df = generate_survey_data(n_samples=100)
        assert len(df) == 100

    def test_required_columns_present(self) -> None:
        df = generate_survey_data(n_samples=50)
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Missing required column: {col}"

    def test_optional_columns_present(self) -> None:
        df = generate_survey_data(n_samples=50)
        for col in ("sleep_quality", "cognitive_load", "fatigue_level",
                    "medication_adherence", "work_hours_weekly", "symptom_severity"):
            assert col in df.columns

    def test_burnout_label_present_and_binary(self) -> None:
        df = generate_survey_data(n_samples=100)
        assert "burnout_label" in df.columns
        assert set(df["burnout_label"].unique()).issubset({0, 1})

    def test_all_conditions_covered(self) -> None:
        # With enough samples, all 9 conditions should appear
        df = generate_survey_data(n_samples=500)
        generated = set(df["neurological_condition"].unique())
        # All known conditions should appear in a large enough sample
        for cond in CONDITION_PROFILES:
            assert cond in generated, f"Condition '{cond}' never generated"

    def test_scores_within_valid_range(self) -> None:
        df = generate_survey_data(n_samples=200)
        for col in ("exhaustion_score", "depersonalization_score", "efficacy_score"):
            assert (df[col] >= 0).all(), f"{col} has negative values"
            assert (df[col] <= 10).all(), f"{col} exceeds 10"

    def test_age_within_range(self) -> None:
        df = generate_survey_data(n_samples=200)
        assert (df["age"] >= 18).all()
        assert (df["age"] <= 80).all()

    def test_medication_adherence_in_0_1(self) -> None:
        df = generate_survey_data(n_samples=200)
        assert (df["medication_adherence"] >= 0).all()
        assert (df["medication_adherence"] <= 1).all()

    def test_reproducibility(self) -> None:
        df1 = generate_survey_data(n_samples=50, random_state=0)
        df2 = generate_survey_data(n_samples=50, random_state=0)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self) -> None:
        df1 = generate_survey_data(n_samples=50, random_state=1)
        df2 = generate_survey_data(n_samples=50, random_state=2)
        assert not df1["exhaustion_score"].equals(df2["exhaustion_score"])

    def test_condition_weights_applied(self) -> None:
        # Heavy weight for 'none' should produce many 'none' rows
        df = generate_survey_data(
            n_samples=500,
            condition_weights={"none": 100.0},
        )
        rate = (df["neurological_condition"] == "none").mean()
        assert rate > 0.5, f"Expected >50% 'none', got {rate:.2%}"

    def test_high_burden_condition_has_higher_burnout_rate(self) -> None:
        df = generate_survey_data(n_samples=1000, random_state=42)
        cfs_rate = df.loc[
            df["neurological_condition"] == "chronic_fatigue_syndrome", "burnout_label"
        ].mean()
        none_rate = df.loc[
            df["neurological_condition"] == "none", "burnout_label"
        ].mean()
        assert cfs_rate > none_rate, (
            f"CFS burnout rate ({cfs_rate:.2f}) should exceed "
            f"no-condition rate ({none_rate:.2f})"
        )

    def test_cfs_exhaustion_higher_than_none(self) -> None:
        df = generate_survey_data(n_samples=1000, random_state=42)
        cfs_mean = df.loc[
            df["neurological_condition"] == "chronic_fatigue_syndrome", "exhaustion_score"
        ].mean()
        none_mean = df.loc[
            df["neurological_condition"] == "none", "exhaustion_score"
        ].mean()
        assert cfs_mean > none_mean


# ---------------------------------------------------------------------------
# generate_physiological_data
# ---------------------------------------------------------------------------

class TestGeneratePhysiologicalData:
    def test_returns_dataframe(self) -> None:
        df = generate_physiological_data(["P00001", "P00002"], days=7)
        assert isinstance(df, pd.DataFrame)

    def test_correct_row_count(self) -> None:
        pids = [f"P{i:05d}" for i in range(10)]
        df = generate_physiological_data(pids, days=14)
        assert len(df) == 10 * 14

    def test_required_columns(self) -> None:
        df = generate_physiological_data(["P00001"], days=5)
        for col in ("participant_id", "timestamp", "hrv_mean", "resting_hr", "sleep_hours"):
            assert col in df.columns

    def test_hrv_positive(self) -> None:
        df = generate_physiological_data(["P00001", "P00002"], days=30)
        assert (df["hrv_mean"] > 0).all()

    def test_sleep_hours_reasonable(self) -> None:
        df = generate_physiological_data(["P00001"], days=100)
        assert (df["sleep_hours"] >= 2).all()
        assert (df["sleep_hours"] <= 12).all()

    def test_condition_map_affects_hrv(self) -> None:
        pids = [f"P{i:05d}" for i in range(100)]
        # CFS has lower HRV mean than none
        cfs_df = generate_physiological_data(
            pids, days=30,
            condition_map={p: "chronic_fatigue_syndrome" for p in pids},
            random_state=42,
        )
        none_df = generate_physiological_data(
            pids, days=30,
            condition_map={p: "none" for p in pids},
            random_state=42,
        )
        assert cfs_df["hrv_mean"].mean() < none_df["hrv_mean"].mean()

    def test_reproducibility(self) -> None:
        pids = ["P00001", "P00002"]
        df1 = generate_physiological_data(pids, days=10, random_state=0)
        df2 = generate_physiological_data(pids, days=10, random_state=0)
        pd.testing.assert_frame_equal(df1, df2)


# ---------------------------------------------------------------------------
# generate_cognitive_data
# ---------------------------------------------------------------------------

class TestGenerateCognitiveData:
    def test_returns_dataframe(self) -> None:
        df = generate_cognitive_data(["P00001"], assessments_per_participant=3)
        assert isinstance(df, pd.DataFrame)

    def test_correct_row_count(self) -> None:
        pids = [f"P{i:05d}" for i in range(20)]
        df = generate_cognitive_data(pids, assessments_per_participant=5)
        assert len(df) == 20 * 5

    def test_required_columns(self) -> None:
        df = generate_cognitive_data(["P00001"], assessments_per_participant=2)
        for col in ("participant_id", "session_id", "reaction_time_ms",
                    "task_completion_rate", "cognitive_load_score"):
            assert col in df.columns

    def test_reaction_time_positive(self) -> None:
        pids = [f"P{i:05d}" for i in range(50)]
        df = generate_cognitive_data(pids, assessments_per_participant=5)
        assert (df["reaction_time_ms"] > 0).all()

    def test_task_completion_in_0_1(self) -> None:
        pids = [f"P{i:05d}" for i in range(50)]
        df = generate_cognitive_data(pids, assessments_per_participant=5)
        assert (df["task_completion_rate"] >= 0).all()
        assert (df["task_completion_rate"] <= 1).all()

    def test_tbi_slower_than_none(self) -> None:
        pids = [f"P{i:05d}" for i in range(100)]
        tbi_df = generate_cognitive_data(
            pids,
            assessments_per_participant=5,
            condition_map={p: "traumatic_brain_injury" for p in pids},
            random_state=42,
        )
        none_df = generate_cognitive_data(
            pids,
            assessments_per_participant=5,
            condition_map={p: "none" for p in pids},
            random_state=42,
        )
        assert tbi_df["reaction_time_ms"].mean() > none_df["reaction_time_ms"].mean()

    def test_reproducibility(self) -> None:
        pids = ["P00001", "P00002"]
        df1 = generate_cognitive_data(pids, assessments_per_participant=3, random_state=0)
        df2 = generate_cognitive_data(pids, assessments_per_participant=3, random_state=0)
        pd.testing.assert_frame_equal(df1, df2)


# ---------------------------------------------------------------------------
# generate_full_dataset
# ---------------------------------------------------------------------------

class TestGenerateFullDataset:
    def test_returns_all_keys(self) -> None:
        datasets = generate_full_dataset(n_participants=50, physiological_days=7,
                                         cognitive_sessions=2)
        assert set(datasets.keys()) == {"survey", "physiological", "cognitive"}

    def test_participant_ids_consistent(self) -> None:
        datasets = generate_full_dataset(n_participants=50, physiological_days=7,
                                         cognitive_sessions=2, random_state=42)
        survey_ids = set(datasets["survey"]["participant_id"])
        phys_ids = set(datasets["physiological"]["participant_id"])
        cog_ids = set(datasets["cognitive"]["participant_id"])
        assert survey_ids == phys_ids == cog_ids

    def test_correct_sizes(self) -> None:
        n = 30
        days = 10
        sessions = 4
        datasets = generate_full_dataset(n_participants=n, physiological_days=days,
                                          cognitive_sessions=sessions, random_state=0)
        assert len(datasets["survey"]) == n
        assert len(datasets["physiological"]) == n * days
        assert len(datasets["cognitive"]) == n * sessions

"""Synthetic data generation for burnout detection development and testing.

Generates realistic multi-modal datasets covering:
- MBI survey sub-scales (exhaustion, depersonalization, efficacy)
- Physiological signals (HRV, sleep quality, resting heart rate)
- Cognitive / behavioural signals (cognitive load, reaction time, task completion)

Each neurological condition is parameterised with its own distribution profiles
based on the clinical literature on fatigue, sleep disruption, and cognitive
burden associated with each condition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Condition profiles
# ---------------------------------------------------------------------------

@dataclass
class ConditionProfile:
    """Statistical profile for a single neurological condition.

    All score ranges follow the conventions used in `loader.py`:
    - MBI sub-scales: 0-6 per item (we model the aggregate 0-54/0-30 range
      but keep values normalised to a 0-10 scale for simplicity)
    - Sleep quality, fatigue, cognitive load: 0-10 (higher = worse / more)
    - HRV (RMSSD, ms): higher values are healthier
    - Resting HR (bpm): lower is generally healthier
    - Reaction time (ms): lower is faster / healthier
    - Task completion rate: 0-1 (1 = fully completed tasks)
    - Symptom severity: 0-10
    - Medication adherence: 0-1
    - Work hours weekly: float
    """
    # MBI sub-scales (0-10 normalised scale; exhaustion/depersonalisation:
    # higher = worse; efficacy: higher = better)
    exhaustion_mean: float
    exhaustion_std: float
    depersonalization_mean: float
    depersonalization_std: float
    efficacy_mean: float          # higher = better capability / lower burnout
    efficacy_std: float

    # Physiological
    hrv_mean: float               # ms RMSSD
    hrv_std: float
    resting_hr_mean: float        # bpm
    resting_hr_std: float
    sleep_quality_mean: float     # 0-10, higher = worse
    sleep_quality_std: float
    sleep_hours_mean: float       # hours per night
    sleep_hours_std: float

    # Cognitive / behavioural
    cognitive_load_mean: float    # 0-10, higher = more burden
    cognitive_load_std: float
    reaction_time_mean: float     # ms; higher = slower
    reaction_time_std: float
    task_completion_mean: float   # 0-1
    task_completion_std: float

    # Work and general wellbeing
    fatigue_level_mean: float     # 0-10
    fatigue_level_std: float
    symptom_severity_mean: float  # 0-10
    symptom_severity_std: float
    work_hours_mean: float
    work_hours_std: float
    medication_adherence_mean: float  # 0-1
    medication_adherence_std: float

    # Probability that this participant is in the burnout class
    burnout_base_rate: float

    # Allowed age range for this condition
    age_min: int = 18
    age_max: int = 70


# ---------------------------------------------------------------------------
# Per-condition parameter tables
# ---------------------------------------------------------------------------
# Sources / rationale:
#   MS:  High fatigue (Krupp et al.), disrupted sleep, mild-moderate cog load.
#   Epilepsy: Sleep disruption, moderate fatigue, adherence varies.
#   Parkinson's: Progressive fatigue, autonomic dysfunction (lower HRV),
#                sleep disorders (REM behaviour disorder).
#   TBI: High cognitive load, slower reaction times, variable sleep.
#   CFS: Severe fatigue by definition, post-exertional malaise,
#         very poor sleep quality.
#   Migraine: Episodic high fatigue & disrupted sleep; inter-ictal normal.
#   ADHD: High cognitive load from compensation, variable sleep.
#   Other / none: General population baseline.

CONDITION_PROFILES: dict[str, ConditionProfile] = {
    "multiple_sclerosis": ConditionProfile(
        exhaustion_mean=7.0, exhaustion_std=1.5,
        depersonalization_mean=4.5, depersonalization_std=1.5,
        efficacy_mean=4.5, efficacy_std=1.5,
        hrv_mean=38.0, hrv_std=10.0,
        resting_hr_mean=76.0, resting_hr_std=8.0,
        sleep_quality_mean=6.5, sleep_quality_std=2.0,
        sleep_hours_mean=6.5, sleep_hours_std=1.2,
        cognitive_load_mean=6.5, cognitive_load_std=1.8,
        reaction_time_mean=310.0, reaction_time_std=50.0,
        task_completion_mean=0.72, task_completion_std=0.15,
        fatigue_level_mean=7.5, fatigue_level_std=1.5,
        symptom_severity_mean=6.0, symptom_severity_std=1.8,
        work_hours_mean=34.0, work_hours_std=8.0,
        medication_adherence_mean=0.75, medication_adherence_std=0.18,
        burnout_base_rate=0.60,
    ),
    "epilepsy": ConditionProfile(
        exhaustion_mean=5.5, exhaustion_std=2.0,
        depersonalization_mean=3.5, depersonalization_std=1.5,
        efficacy_mean=5.5, efficacy_std=1.5,
        hrv_mean=45.0, hrv_std=12.0,
        resting_hr_mean=72.0, resting_hr_std=8.0,
        sleep_quality_mean=5.5, sleep_quality_std=2.2,
        sleep_hours_mean=7.0, sleep_hours_std=1.3,
        cognitive_load_mean=5.5, cognitive_load_std=2.0,
        reaction_time_mean=295.0, reaction_time_std=55.0,
        task_completion_mean=0.78, task_completion_std=0.14,
        fatigue_level_mean=6.0, fatigue_level_std=2.0,
        symptom_severity_mean=5.0, symptom_severity_std=2.0,
        work_hours_mean=38.0, work_hours_std=8.0,
        medication_adherence_mean=0.70, medication_adherence_std=0.20,
        burnout_base_rate=0.45,
    ),
    "parkinsons": ConditionProfile(
        exhaustion_mean=7.5, exhaustion_std=1.5,
        depersonalization_mean=4.0, depersonalization_std=1.8,
        efficacy_mean=4.0, efficacy_std=1.8,
        hrv_mean=28.0, hrv_std=8.0,     # autonomic dysfunction
        resting_hr_mean=80.0, resting_hr_std=10.0,
        sleep_quality_mean=7.5, sleep_quality_std=1.8,
        sleep_hours_mean=5.8, sleep_hours_std=1.5,
        cognitive_load_mean=6.0, cognitive_load_std=2.0,
        reaction_time_mean=350.0, reaction_time_std=70.0,
        task_completion_mean=0.65, task_completion_std=0.18,
        fatigue_level_mean=7.8, fatigue_level_std=1.5,
        symptom_severity_mean=7.0, symptom_severity_std=2.0,
        work_hours_mean=28.0, work_hours_std=10.0,
        medication_adherence_mean=0.82, medication_adherence_std=0.15,
        burnout_base_rate=0.65,
        age_min=45, age_max=80,
    ),
    "traumatic_brain_injury": ConditionProfile(
        exhaustion_mean=6.5, exhaustion_std=2.0,
        depersonalization_mean=5.0, depersonalization_std=2.0,
        efficacy_mean=4.2, efficacy_std=1.8,
        hrv_mean=40.0, hrv_std=12.0,
        resting_hr_mean=74.0, resting_hr_std=9.0,
        sleep_quality_mean=6.8, sleep_quality_std=2.2,
        sleep_hours_mean=6.2, sleep_hours_std=1.5,
        cognitive_load_mean=8.0, cognitive_load_std=1.5,
        reaction_time_mean=380.0, reaction_time_std=80.0,
        task_completion_mean=0.62, task_completion_std=0.20,
        fatigue_level_mean=7.0, fatigue_level_std=1.8,
        symptom_severity_mean=6.5, symptom_severity_std=2.0,
        work_hours_mean=32.0, work_hours_std=10.0,
        medication_adherence_mean=0.72, medication_adherence_std=0.20,
        burnout_base_rate=0.62,
    ),
    "chronic_fatigue_syndrome": ConditionProfile(
        exhaustion_mean=9.0, exhaustion_std=1.0,
        depersonalization_mean=5.5, depersonalization_std=1.5,
        efficacy_mean=3.0, efficacy_std=1.5,
        hrv_mean=32.0, hrv_std=9.0,
        resting_hr_mean=82.0, resting_hr_std=10.0,
        sleep_quality_mean=8.0, sleep_quality_std=1.5,
        sleep_hours_mean=7.5, sleep_hours_std=2.0,   # long but non-restorative
        cognitive_load_mean=7.5, cognitive_load_std=1.8,
        reaction_time_mean=340.0, reaction_time_std=60.0,
        task_completion_mean=0.55, task_completion_std=0.20,
        fatigue_level_mean=9.2, fatigue_level_std=1.0,
        symptom_severity_mean=8.0, symptom_severity_std=1.5,
        work_hours_mean=22.0, work_hours_std=12.0,
        medication_adherence_mean=0.68, medication_adherence_std=0.22,
        burnout_base_rate=0.80,
    ),
    "migraine_chronic": ConditionProfile(
        exhaustion_mean=6.0, exhaustion_std=2.0,
        depersonalization_mean=3.8, depersonalization_std=1.8,
        efficacy_mean=5.0, efficacy_std=1.8,
        hrv_mean=42.0, hrv_std=12.0,
        resting_hr_mean=72.0, resting_hr_std=8.0,
        sleep_quality_mean=6.2, sleep_quality_std=2.2,
        sleep_hours_mean=6.8, sleep_hours_std=1.3,
        cognitive_load_mean=5.8, cognitive_load_std=2.0,
        reaction_time_mean=295.0, reaction_time_std=55.0,
        task_completion_mean=0.75, task_completion_std=0.15,
        fatigue_level_mean=6.5, fatigue_level_std=2.0,
        symptom_severity_mean=5.5, symptom_severity_std=2.0,
        work_hours_mean=36.0, work_hours_std=8.0,
        medication_adherence_mean=0.73, medication_adherence_std=0.18,
        burnout_base_rate=0.50,
    ),
    "adhd": ConditionProfile(
        exhaustion_mean=6.0, exhaustion_std=2.0,
        depersonalization_mean=4.0, depersonalization_std=2.0,
        efficacy_mean=5.0, efficacy_std=2.0,
        hrv_mean=48.0, hrv_std=13.0,
        resting_hr_mean=74.0, resting_hr_std=9.0,
        sleep_quality_mean=5.8, sleep_quality_std=2.2,
        sleep_hours_mean=6.5, sleep_hours_std=1.5,
        cognitive_load_mean=7.8, cognitive_load_std=1.5,
        reaction_time_mean=290.0, reaction_time_std=65.0,
        task_completion_mean=0.68, task_completion_std=0.20,
        fatigue_level_mean=6.2, fatigue_level_std=2.0,
        symptom_severity_mean=5.0, symptom_severity_std=2.0,
        work_hours_mean=40.0, work_hours_std=9.0,
        medication_adherence_mean=0.65, medication_adherence_std=0.25,
        burnout_base_rate=0.52,
        age_min=18, age_max=55,
    ),
    "other": ConditionProfile(
        exhaustion_mean=5.5, exhaustion_std=2.0,
        depersonalization_mean=3.5, depersonalization_std=1.8,
        efficacy_mean=5.5, efficacy_std=1.8,
        hrv_mean=50.0, hrv_std=14.0,
        resting_hr_mean=71.0, resting_hr_std=8.0,
        sleep_quality_mean=5.0, sleep_quality_std=2.5,
        sleep_hours_mean=7.0, sleep_hours_std=1.2,
        cognitive_load_mean=5.0, cognitive_load_std=2.0,
        reaction_time_mean=275.0, reaction_time_std=50.0,
        task_completion_mean=0.80, task_completion_std=0.15,
        fatigue_level_mean=5.5, fatigue_level_std=2.0,
        symptom_severity_mean=4.5, symptom_severity_std=2.2,
        work_hours_mean=38.0, work_hours_std=9.0,
        medication_adherence_mean=0.75, medication_adherence_std=0.20,
        burnout_base_rate=0.42,
    ),
    "none": ConditionProfile(
        exhaustion_mean=3.5, exhaustion_std=2.0,
        depersonalization_mean=2.0, depersonalization_std=1.5,
        efficacy_mean=7.0, efficacy_std=1.5,
        hrv_mean=60.0, hrv_std=15.0,
        resting_hr_mean=68.0, resting_hr_std=8.0,
        sleep_quality_mean=3.0, sleep_quality_std=2.0,
        sleep_hours_mean=7.5, sleep_hours_std=1.0,
        cognitive_load_mean=3.5, cognitive_load_std=1.8,
        reaction_time_mean=260.0, reaction_time_std=40.0,
        task_completion_mean=0.88, task_completion_std=0.10,
        fatigue_level_mean=3.0, fatigue_level_std=1.8,
        symptom_severity_mean=1.5, symptom_severity_std=1.2,
        work_hours_mean=40.0, work_hours_std=8.0,
        medication_adherence_mean=0.90, medication_adherence_std=0.12,
        burnout_base_rate=0.25,
    ),
}


# ---------------------------------------------------------------------------
# Core generator helpers
# ---------------------------------------------------------------------------

def _norm(rng: np.random.Generator, mean: float, std: float, n: int,
          lo: float, hi: float) -> np.ndarray:
    """Sample n values from N(mean, std), clip to [lo, hi], round to 1 dp."""
    return np.clip(rng.normal(mean, std, size=n), lo, hi).round(1)


def generate_survey_data(
    n_samples: int = 500,
    condition_weights: dict[str, float] | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic survey DataFrame with MBI sub-scales.

    Generates all values for each condition group as bulk numpy arrays to
    avoid per-row scalar conversion issues and for better performance.

    Args:
        n_samples: Total number of participant records to generate.
        condition_weights: Optional mapping of condition name to sampling weight.
            Defaults to equal weighting across all conditions.
        random_state: Seed for reproducibility.

    Returns:
        A DataFrame matching the required survey schema in loader.py.
    """
    rng = np.random.default_rng(random_state)
    conditions = list(CONDITION_PROFILES.keys())

    if condition_weights is None:
        weights = np.ones(len(conditions)) / len(conditions)
    else:
        weights = np.array([condition_weights.get(c, 1.0) for c in conditions], dtype=float)
        weights /= weights.sum()

    # Sample condition labels for all participants at once
    condition_labels: np.ndarray = rng.choice(conditions, size=n_samples, p=weights)

    # Pre-allocate output arrays
    ages = np.empty(n_samples, dtype=int)
    genders: list[str] = []
    exhaustion = np.empty(n_samples)
    depersonalization = np.empty(n_samples)
    efficacy = np.empty(n_samples)
    sleep_quality = np.empty(n_samples)
    cognitive_load = np.empty(n_samples)
    fatigue_level = np.empty(n_samples)
    medication_adherence = np.empty(n_samples)
    work_hours = np.empty(n_samples)
    symptom_severity = np.empty(n_samples)
    burnout_label = np.empty(n_samples, dtype=int)

    # Generate per-condition in vectorized batches
    for condition in conditions:
        mask = condition_labels == condition
        n = int(mask.sum())
        if n == 0:
            continue
        p = CONDITION_PROFILES[condition]

        ages[mask] = rng.integers(p.age_min, p.age_max + 1, size=n)
        exhaustion[mask] = _norm(rng, p.exhaustion_mean, p.exhaustion_std, n, 0, 10)
        depersonalization[mask] = _norm(
            rng, p.depersonalization_mean, p.depersonalization_std, n, 0, 10)
        efficacy[mask] = _norm(rng, p.efficacy_mean, p.efficacy_std, n, 0, 10)
        sleep_quality[mask] = _norm(rng, p.sleep_quality_mean, p.sleep_quality_std, n, 0, 10)
        cognitive_load[mask] = _norm(rng, p.cognitive_load_mean, p.cognitive_load_std, n, 0, 10)
        fatigue_level[mask] = _norm(rng, p.fatigue_level_mean, p.fatigue_level_std, n, 0, 10)
        medication_adherence[mask] = _norm(
            rng, p.medication_adherence_mean, p.medication_adherence_std, n, 0, 1)
        work_hours[mask] = _norm(rng, p.work_hours_mean, p.work_hours_std, n, 0, 80)
        symptom_severity[mask] = _norm(
            rng, p.symptom_severity_mean, p.symptom_severity_std, n, 0, 10)

        # Burnout probability: base rate shifted by how extreme exhaustion is
        burnout_prob = np.clip(
            p.burnout_base_rate + 0.05 * (exhaustion[mask] - p.exhaustion_mean), 0.0, 1.0
        )
        burnout_label[mask] = (rng.random(n) < burnout_prob).astype(int)

    # Sample gender for all participants at once
    genders = list(rng.choice(["female", "male", "non_binary"], size=n_samples, p=[0.52, 0.45, 0.03]))

    # Stress is derived from exhaustion + fatigue, add small noise
    stress_self_report = np.clip(
        (exhaustion + fatigue_level) / 2 + rng.normal(0, 1.0, n_samples), 0, 10
    ).round(1)

    participant_ids = [f"P{i + 1:05d}" for i in range(n_samples)]

    return pd.DataFrame(
        {
            "participant_id": participant_ids,
            "age": ages,
            "gender": genders,
            "neurological_condition": condition_labels,
            "exhaustion_score": exhaustion.round(1),
            "depersonalization_score": depersonalization.round(1),
            "efficacy_score": efficacy.round(1),
            "sleep_quality": sleep_quality.round(1),
            "cognitive_load": cognitive_load.round(1),
            "fatigue_level": fatigue_level.round(1),
            "medication_adherence": medication_adherence.round(2),
            "work_hours_weekly": work_hours.round(1),
            "symptom_severity": symptom_severity.round(1),
            "stress_self_report": stress_self_report,
            "burnout_label": burnout_label,
        }
    )


def generate_physiological_data(
    participant_ids: list[str],
    days: int = 30,
    condition_map: dict[str, str] | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate synthetic physiological time-series data per participant.

    Produces daily HRV, resting HR, and sleep hours records for each
    participant over the specified number of days.

    Args:
        participant_ids: List of participant identifiers.
        days: Number of consecutive days of data per participant.
        condition_map: Optional mapping of participant_id → neurological_condition.
            When provided, profiles are used to parameterise each participant's
            physiological signals. Falls back to the 'none' profile if unmapped.
        random_state: Seed for reproducibility.

    Returns:
        A long-format DataFrame with columns:
        participant_id, timestamp, hrv_mean, resting_hr, sleep_hours.
    """
    rng = np.random.default_rng(random_state)
    base_date = pd.Timestamp("2025-01-01")
    n_total = len(participant_ids) * days

    pid_col: list[str] = []
    ts_col: list[pd.Timestamp] = []

    hrv_col = np.empty(n_total)
    rhr_col = np.empty(n_total)
    slp_col = np.empty(n_total)

    timestamps = [base_date + pd.Timedelta(days=d) for d in range(days)]

    idx = 0
    for pid in participant_ids:
        condition = (condition_map or {}).get(pid, "none")
        p = CONDITION_PROFILES.get(condition, CONDITION_PROFILES["none"])

        hrv_col[idx: idx + days] = _norm(rng, p.hrv_mean, p.hrv_std * 0.6, days, 10, 120)
        rhr_col[idx: idx + days] = _norm(rng, p.resting_hr_mean, p.resting_hr_std * 0.4,
                                          days, 45, 110)
        slp_col[idx: idx + days] = _norm(rng, p.sleep_hours_mean, p.sleep_hours_std * 0.5,
                                          days, 2, 12)
        pid_col.extend([pid] * days)
        ts_col.extend(timestamps)
        idx += days

    return pd.DataFrame(
        {
            "participant_id": pid_col,
            "timestamp": ts_col,
            "hrv_mean": hrv_col,
            "resting_hr": rhr_col,
            "sleep_hours": slp_col,
        }
    )


def generate_cognitive_data(
    participant_ids: list[str],
    assessments_per_participant: int = 5,
    condition_map: dict[str, str] | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate synthetic cognitive assessment data.

    Simulates repeated cognitive tests capturing reaction time and task
    completion rates — key indicators of cognitive fatigue in neurological
    patients.

    Args:
        participant_ids: List of participant identifiers.
        assessments_per_participant: Number of assessment sessions per participant.
        condition_map: Optional mapping of participant_id → neurological_condition.
        random_state: Seed for reproducibility.

    Returns:
        DataFrame with columns:
        participant_id, session_id, reaction_time_ms, task_completion_rate,
        cognitive_load_score.
    """
    rng = np.random.default_rng(random_state)
    n_total = len(participant_ids) * assessments_per_participant
    sessions = list(range(1, assessments_per_participant + 1))

    pid_col: list[str] = []
    session_col: list[int] = []
    rt_col = np.empty(n_total)
    tc_col = np.empty(n_total)
    cl_col = np.empty(n_total)

    idx = 0
    for pid in participant_ids:
        condition = (condition_map or {}).get(pid, "none")
        p = CONDITION_PROFILES.get(condition, CONDITION_PROFILES["none"])

        for session in sessions:
            # Slight degradation across sessions for high-fatigue conditions
            ff = 1 + 0.02 * (session - 1) * (p.fatigue_level_mean / 10.0)

            rt_col[idx] = float(
                np.clip(rng.normal(p.reaction_time_mean * ff, p.reaction_time_std), 150, 800)
            )
            tc_col[idx] = float(
                np.clip(rng.normal(p.task_completion_mean / ff, p.task_completion_std), 0, 1)
            )
            cl_col[idx] = float(
                np.clip(rng.normal(p.cognitive_load_mean * ff, p.cognitive_load_std), 0, 10)
            )
            pid_col.append(pid)
            session_col.append(session)
            idx += 1

    return pd.DataFrame(
        {
            "participant_id": pid_col,
            "session_id": session_col,
            "reaction_time_ms": rt_col.round(0),
            "task_completion_rate": tc_col.round(3),
            "cognitive_load_score": cl_col.round(1),
        }
    )


def generate_full_dataset(
    n_participants: int = 500,
    physiological_days: int = 30,
    cognitive_sessions: int = 5,
    condition_weights: dict[str, float] | None = None,
    random_state: int = 42,
) -> dict[str, pd.DataFrame]:
    """Generate a complete multi-modal synthetic dataset.

    Args:
        n_participants: Number of participants.
        physiological_days: Days of physiological data per participant.
        cognitive_sessions: Cognitive assessment sessions per participant.
        condition_weights: Optional per-condition sampling weights.
        random_state: Seed for reproducibility.

    Returns:
        Dict with keys 'survey', 'physiological', 'cognitive' mapping to
        DataFrames.
    """
    survey_df = generate_survey_data(
        n_samples=n_participants,
        condition_weights=condition_weights,
        random_state=random_state,
    )

    condition_map = dict(
        zip(survey_df["participant_id"], survey_df["neurological_condition"])
    )
    participant_ids = survey_df["participant_id"].tolist()

    phys_df = generate_physiological_data(
        participant_ids=participant_ids,
        days=physiological_days,
        condition_map=condition_map,
        random_state=random_state + 1,
    )

    cog_df = generate_cognitive_data(
        participant_ids=participant_ids,
        assessments_per_participant=cognitive_sessions,
        condition_map=condition_map,
        random_state=random_state + 2,
    )

    return {
        "survey": survey_df,
        "physiological": phys_df,
        "cognitive": cog_df,
    }

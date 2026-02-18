"""Feature engineering for burnout detection in neurological populations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_burnout_composite(
    df: pd.DataFrame,
    exhaustion_col: str = "exhaustion_score",
    depersonalization_col: str = "depersonalization_score",
    efficacy_col: str = "efficacy_score",
    weights: tuple[float, float, float] = (0.4, 0.3, 0.3),
) -> pd.Series:
    """Compute a weighted composite burnout score from MBI sub-scales.

    Higher scores indicate greater burnout risk. Efficacy is inverted since
    low efficacy corresponds to higher burnout.

    Args:
        df: DataFrame containing the MBI sub-scale columns.
        exhaustion_col: Column name for emotional exhaustion.
        depersonalization_col: Column name for depersonalization.
        efficacy_col: Column name for personal efficacy.
        weights: Tuple of (exhaustion, depersonalization, inverse_efficacy) weights.

    Returns:
        A Series with composite burnout scores.
    """
    exhaustion = df[exhaustion_col].fillna(0)
    depersonalization = df[depersonalization_col].fillna(0)

    # Invert efficacy: higher score = lower burnout, so we flip it
    efficacy_max = df[efficacy_col].max()
    inverse_efficacy = (efficacy_max - df[efficacy_col].fillna(efficacy_max))

    composite = (
        weights[0] * exhaustion
        + weights[1] * depersonalization
        + weights[2] * inverse_efficacy
    )
    return composite


def compute_neuro_fatigue_index(
    df: pd.DataFrame,
    fatigue_col: str = "fatigue_level",
    sleep_col: str = "sleep_quality",
    cognitive_col: str = "cognitive_load",
) -> pd.Series:
    """Compute a neurological fatigue index combining multiple signals.

    This feature is specific to neurological populations where fatigue
    is a major confounder for burnout detection.

    Args:
        df: DataFrame with fatigue-related columns.
        fatigue_col: Self-reported fatigue level column.
        sleep_col: Sleep quality score column (higher = better sleep).
        cognitive_col: Cognitive load/difficulty column.

    Returns:
        A Series with the neurological fatigue index.
    """
    components = []
    weights = []

    if fatigue_col in df.columns:
        components.append(df[fatigue_col].fillna(0))
        weights.append(0.4)

    if sleep_col in df.columns:
        # Invert sleep quality: poor sleep contributes to fatigue
        sleep_max = df[sleep_col].max() if df[sleep_col].notna().any() else 1
        components.append(sleep_max - df[sleep_col].fillna(sleep_max))
        weights.append(0.3)

    if cognitive_col in df.columns:
        components.append(df[cognitive_col].fillna(0))
        weights.append(0.3)

    if not components:
        return pd.Series(0.0, index=df.index, name="neuro_fatigue_index")

    # Normalize weights to sum to 1
    total = sum(weights)
    weights = [w / total for w in weights]

    result = sum(w * c for w, c in zip(weights, components))
    return result.rename("neuro_fatigue_index")


def compute_symptom_burnout_interaction(
    df: pd.DataFrame,
    symptom_col: str = "symptom_severity",
    burnout_composite_col: str = "burnout_composite",
) -> pd.Series:
    """Compute interaction term between neurological symptom severity and burnout.

    This captures the compounding effect of neurological symptoms on burnout risk.

    Args:
        df: DataFrame with symptom and burnout columns.
        symptom_col: Neurological symptom severity column.
        burnout_composite_col: Composite burnout score column.

    Returns:
        A Series with the interaction feature.
    """
    if symptom_col not in df.columns or burnout_composite_col not in df.columns:
        return pd.Series(0.0, index=df.index, name="symptom_burnout_interaction")

    interaction = df[symptom_col].fillna(0) * df[burnout_composite_col].fillna(0)
    return interaction.rename("symptom_burnout_interaction")


def compute_work_strain_ratio(
    df: pd.DataFrame,
    work_hours_col: str = "work_hours_weekly",
    fatigue_col: str = "fatigue_level",
) -> pd.Series:
    """Compute work strain ratio: fatigue relative to work hours.

    Neurological patients may experience disproportionate fatigue for their
    work hours compared to the general population.

    Args:
        df: DataFrame with work and fatigue columns.
        work_hours_col: Weekly work hours column.
        fatigue_col: Fatigue level column.

    Returns:
        A Series with the work strain ratio.
    """
    if work_hours_col not in df.columns or fatigue_col not in df.columns:
        return pd.Series(np.nan, index=df.index, name="work_strain_ratio")

    hours = df[work_hours_col].replace(0, np.nan)
    ratio = df[fatigue_col] / hours
    return ratio.rename("work_strain_ratio")


def build_features(
    df: pd.DataFrame,
    include_neuro_features: bool = True,
    include_interaction_features: bool = True,
) -> pd.DataFrame:
    """Build the full feature set for burnout detection.

    Args:
        df: Input DataFrame with raw/preprocessed columns.
        include_neuro_features: Whether to include neurological-specific features.
        include_interaction_features: Whether to include interaction terms.

    Returns:
        DataFrame with all original columns plus engineered features.
    """
    result = df.copy()

    # Core burnout composite
    if all(
        c in result.columns
        for c in ("exhaustion_score", "depersonalization_score", "efficacy_score")
    ):
        result["burnout_composite"] = compute_burnout_composite(result)

    # Neurological-specific features
    if include_neuro_features:
        neuro_fatigue = compute_neuro_fatigue_index(result)
        result[neuro_fatigue.name] = neuro_fatigue

        work_strain = compute_work_strain_ratio(result)
        result[work_strain.name] = work_strain

    # Interaction features
    if include_interaction_features and "burnout_composite" in result.columns:
        interaction = compute_symptom_burnout_interaction(result)
        result[interaction.name] = interaction

    # Medication adherence as binary flag (if available)
    if "medication_adherence" in result.columns:
        result["low_med_adherence"] = (result["medication_adherence"] < 0.5).astype(int)

    return result

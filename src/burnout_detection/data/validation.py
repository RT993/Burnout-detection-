"""Data validation utilities for burnout detection datasets."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from burnout_detection.data.loader import NEUROLOGICAL_CONDITIONS, REQUIRED_COLUMNS


@dataclass
class ValidationResult:
    """Result of a data validation check."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        lines = [f"Validation: {status}"]
        for err in self.errors:
            lines.append(f"  ERROR: {err}")
        for warn in self.warnings:
            lines.append(f"  WARNING: {warn}")
        return "\n".join(lines)


def validate_dataframe(
    df: pd.DataFrame,
    require_all_columns: bool = False,
) -> ValidationResult:
    """Validate a burnout detection DataFrame for schema and value correctness.

    Args:
        df: DataFrame to validate.
        require_all_columns: If True, all REQUIRED_COLUMNS must be present.

    Returns:
        A ValidationResult with errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check for empty data
    if df.empty:
        errors.append("DataFrame is empty.")
        return ValidationResult(is_valid=False, errors=errors)

    # Check required columns
    if require_all_columns:
        missing = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            errors.append(f"Missing required columns: {sorted(missing)}")

    # Check participant_id uniqueness (if present)
    if "participant_id" in df.columns:
        dupes = df["participant_id"].duplicated().sum()
        if dupes > 0:
            warnings.append(f"Found {dupes} duplicate participant_id values.")

    # Validate score ranges (MBI sub-scales are typically 0-6 per item)
    score_columns = [c for c in df.columns if c.endswith("_score")]
    for col in score_columns:
        if col in df.columns and df[col].dtype in ("float64", "int64"):
            below = (df[col] < 0).sum()
            if below > 0:
                errors.append(f"Column '{col}' has {below} negative values.")

    # Validate neurological condition values
    if "neurological_condition" in df.columns:
        unique_conditions = set(df["neurological_condition"].dropna().unique())
        unknown = unique_conditions - set(NEUROLOGICAL_CONDITIONS)
        if unknown:
            warnings.append(
                f"Unknown neurological conditions: {sorted(unknown)}. "
                f"Known: {NEUROLOGICAL_CONDITIONS}"
            )

    # Check age ranges
    if "age" in df.columns:
        if (df["age"] < 0).any() or (df["age"] > 120).any():
            errors.append("Column 'age' has values outside valid range [0, 120].")

    # Check missing data percentage
    total_cells = df.shape[0] * df.shape[1]
    missing_pct = df.isna().sum().sum() / total_cells * 100 if total_cells > 0 else 0
    if missing_pct > 50:
        errors.append(f"Dataset has {missing_pct:.1f}% missing values (>50%).")
    elif missing_pct > 20:
        warnings.append(f"Dataset has {missing_pct:.1f}% missing values (>20%).")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

#!/usr/bin/env python
"""CLI script to generate synthetic burnout detection datasets.

Produces up to three CSV files in the specified output directory:
  - survey.csv           — MBI sub-scales + demographic + optional burnout label
  - physiological.csv    — Daily HRV, resting HR, and sleep hours per participant
  - cognitive.csv        — Repeated cognitive assessment scores per participant

Usage examples:
    # Minimal: survey data only, 500 participants
    python scripts/generate_synthetic_data.py

    # All modalities, 1000 participants, custom output path
    python scripts/generate_synthetic_data.py \\
        --n-participants 1000 \\
        --output-dir data/processed \\
        --physiological \\
        --cognitive

    # Oversample high-burden conditions
    python scripts/generate_synthetic_data.py \\
        --n-participants 800 \\
        --condition-weights multiple_sclerosis:2.0 chronic_fatigue_syndrome:2.0

    # Reproducible run with custom seed
    python scripts/generate_synthetic_data.py --seed 7
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_condition_weights(raw: list[str]) -> dict[str, float]:
    """Parse 'condition:weight' strings into a dict.

    Args:
        raw: List of strings like ['multiple_sclerosis:2.0', 'adhd:1.5'].

    Returns:
        Dict mapping condition names to weights.

    Raises:
        SystemExit: On malformed input.
    """
    weights: dict[str, float] = {}
    for token in raw:
        parts = token.split(":")
        if len(parts) != 2:
            print(f"Error: condition weight '{token}' must be in 'condition:weight' format.",
                  file=sys.stderr)
            sys.exit(1)
        name, value = parts
        try:
            weights[name.strip()] = float(value.strip())
        except ValueError:
            print(f"Error: weight '{value}' for condition '{name}' is not a valid float.",
                  file=sys.stderr)
            sys.exit(1)
    return weights


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic burnout detection datasets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--n-participants", type=int, default=500,
        help="Number of participant records to generate (default: 500).",
    )
    parser.add_argument(
        "--output-dir", type=str, default="data/processed",
        help="Directory to write output CSV files (default: data/processed).",
    )
    parser.add_argument(
        "--physiological", action="store_true",
        help="Also generate physiological time-series data.",
    )
    parser.add_argument(
        "--cognitive", action="store_true",
        help="Also generate cognitive assessment data.",
    )
    parser.add_argument(
        "--all-modalities", action="store_true",
        help="Shorthand for --physiological --cognitive.",
    )
    parser.add_argument(
        "--physiological-days", type=int, default=30,
        help="Days of physiological data per participant (default: 30).",
    )
    parser.add_argument(
        "--cognitive-sessions", type=int, default=5,
        help="Cognitive assessment sessions per participant (default: 5).",
    )
    parser.add_argument(
        "--condition-weights", nargs="+", default=[],
        metavar="CONDITION:WEIGHT",
        help=(
            "Override sampling weights for specific conditions. "
            "Repeat for multiple: --condition-weights ms:2.0 adhd:1.5"
        ),
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42).",
    )

    args = parser.parse_args()

    # Late import so the script is importable without side effects
    from burnout_detection.data.synthetic import (
        generate_cognitive_data,
        generate_full_dataset,
        generate_physiological_data,
        generate_survey_data,
        CONDITION_PROFILES,
    )

    condition_weights: dict[str, float] | None = None
    if args.condition_weights:
        condition_weights = parse_condition_weights(args.condition_weights)
        unknown = set(condition_weights) - set(CONDITION_PROFILES)
        if unknown:
            print(f"Warning: unknown conditions in weights: {sorted(unknown)}", file=sys.stderr)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    generate_phys = args.physiological or args.all_modalities
    generate_cog = args.cognitive or args.all_modalities

    if generate_phys or generate_cog:
        print(f"Generating full dataset ({args.n_participants} participants) …")
        datasets = generate_full_dataset(
            n_participants=args.n_participants,
            physiological_days=args.physiological_days,
            cognitive_sessions=args.cognitive_sessions,
            condition_weights=condition_weights,
            random_state=args.seed,
        )

        survey_path = out_dir / "survey.csv"
        datasets["survey"].to_csv(survey_path, index=False)
        print(f"  Survey data     → {survey_path}  "
              f"({len(datasets['survey'])} rows)")

        if generate_phys:
            phys_path = out_dir / "physiological.csv"
            datasets["physiological"].to_csv(phys_path, index=False)
            print(f"  Physiological   → {phys_path}  "
                  f"({len(datasets['physiological'])} rows)")

        if generate_cog:
            cog_path = out_dir / "cognitive.csv"
            datasets["cognitive"].to_csv(cog_path, index=False)
            print(f"  Cognitive       → {cog_path}  "
                  f"({len(datasets['cognitive'])} rows)")

    else:
        print(f"Generating survey data ({args.n_participants} participants) …")
        survey_df = generate_survey_data(
            n_samples=args.n_participants,
            condition_weights=condition_weights,
            random_state=args.seed,
        )
        survey_path = out_dir / "survey.csv"
        survey_df.to_csv(survey_path, index=False)
        print(f"  Survey data     → {survey_path}  ({len(survey_df)} rows)")

    # Print a brief condition distribution
    from burnout_detection.data.synthetic import generate_survey_data as _s  # noqa: F401

    print("\nCondition distribution:")
    # Reload survey to print distribution regardless of path taken
    import pandas as pd
    survey_check = pd.read_csv(out_dir / "survey.csv")
    dist = survey_check["neurological_condition"].value_counts()
    for cond, count in dist.items():
        pct = count / len(survey_check) * 100
        burnout_rate = survey_check.loc[
            survey_check["neurological_condition"] == cond, "burnout_label"
        ].mean()
        print(f"  {cond:<30} n={count:>4}  ({pct:4.1f}%)  burnout={burnout_rate:.0%}")

    print("\nDone.")


if __name__ == "__main__":
    main()

# CLAUDE.md — Burnout Detection Project

This file provides guidance for AI assistants (Claude Code and similar tools) working on this repository.

## Project Overview

**Burnout-detection-** detects burnout in individuals with neurological conditions (MS, epilepsy, Parkinson's, TBI, chronic fatigue syndrome, chronic migraine, ADHD). Standard burnout tools often miss the compounding effect of neurological symptoms on fatigue and cognitive load. This project builds neurological-aware ML models with built-in bias auditing.

**Current status:** Core pipeline implemented — data loading, preprocessing, feature engineering, model training, evaluation, and bias auditing are functional. 42 unit tests passing.

---

## Repository State

| Item | Status |
|------|--------|
| `pyproject.toml` | Configured with all dependencies and tool settings |
| `src/burnout_detection/` | Core package with 5 submodules + CLI |
| `tests/` | 42 unit tests (all passing) |
| `configs/default.yaml` | Default pipeline configuration |
| `.gitignore` | Configured for Python, data files, model artifacts |
| CI/CD | Not yet configured |
| Data | No datasets committed (raw data is gitignored) |

---

## Project Structure

```
Burnout-detection-/
├── CLAUDE.md
├── README.md
├── pyproject.toml            # Dependencies, tool config (black, ruff, pytest, mypy)
├── .gitignore
│
├── configs/
│   └── default.yaml          # Pipeline configuration
│
├── data/
│   ├── raw/                  # Raw datasets (gitignored, immutable)
│   ├── processed/            # Cleaned/engineered datasets
│   └── external/             # Third-party reference data
│
├── src/burnout_detection/
│   ├── __init__.py           # Package root, version
│   ├── cli.py                # CLI entry point (burnout-detect command)
│   ├── data/
│   │   ├── loader.py         # load_survey_data, load_physiological_data, load_dataset
│   │   ├── preprocessing.py  # handle_missing_values, encode, scale, remove_outliers, pipeline
│   │   └── validation.py     # validate_dataframe, ValidationResult
│   ├── features/
│   │   └── builder.py        # burnout_composite, neuro_fatigue_index, work_strain_ratio
│   ├── models/
│   │   ├── trainer.py        # train_model, cross_validate, MODEL_REGISTRY
│   │   └── predict.py        # predict, predict_proba, predict_with_confidence
│   ├── evaluation/
│   │   ├── metrics.py        # evaluate_model, compute_fairness_metrics
│   │   └── bias.py           # audit_bias, BiasAuditResult
│   └── utils/
│       ├── io.py             # save_artifact, load_artifact (joblib)
│       └── reproducibility.py # set_global_seed
│
├── tests/
│   ├── conftest.py           # Shared fixtures (sample_survey_df, sample_survey_csv)
│   ├── unit/
│   │   ├── test_loader.py
│   │   ├── test_preprocessing.py
│   │   ├── test_features.py
│   │   ├── test_models.py
│   │   ├── test_evaluation.py
│   │   └── test_validation.py
│   └── integration/          # (empty, for future end-to-end tests)
│
├── notebooks/                # (empty, for exploration and experiments)
├── scripts/                  # (empty, for CLI scripts)
└── outputs/                  # Model artifacts and reports (gitignored)
```

---

## Quick Reference Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src/burnout_detection --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_features.py

# Format code
black src/ tests/ --line-length 100
ruff check src/ tests/

# Type check
mypy src/

# Run the pipeline
burnout-detect --config configs/default.yaml
```

---

## Architecture & Key Modules

### Data Layer (`src/burnout_detection/data/`)

- **`loader.py`**: Loads CSV/Parquet survey and physiological data. Validates required columns (`participant_id`, `age`, `gender`, `neurological_condition`, MBI sub-scale scores). Supports merging survey + physiological data.
- **`preprocessing.py`**: Full pipeline with imputation (median/most_frequent), label encoding, StandardScaler, and IQR/z-score outlier removal. Returns fitted artifacts for reuse on test data.
- **`validation.py`**: Schema validation — checks required columns, score ranges (non-negative), valid neurological condition values, age bounds, missing data rates, duplicate IDs.

### Feature Engineering (`src/burnout_detection/features/`)

- **`builder.py`**: Neurological-specific features:
  - `burnout_composite` — weighted combination of MBI exhaustion, depersonalization, and inverse efficacy
  - `neuro_fatigue_index` — combines fatigue, inverted sleep quality, and cognitive load
  - `work_strain_ratio` — fatigue relative to work hours (captures disproportionate fatigue in neuro patients)
  - `symptom_burnout_interaction` — interaction between neurological symptom severity and burnout
  - `low_med_adherence` — binary flag for low medication adherence

### Models (`src/burnout_detection/models/`)

- **`trainer.py`**: Registry of sklearn-compatible models (logistic regression, random forest, gradient boosting). All use `random_state=42` and `class_weight="balanced"` where applicable. Supports cross-validation with stratified k-fold.
- **`predict.py`**: Hard predictions, probability outputs, and risk-level classification (minimal/low/moderate/high).

### Evaluation (`src/burnout_detection/evaluation/`)

- **`metrics.py`**: Standard metrics (accuracy, precision, recall, F1, ROC AUC, confusion matrix). Per-group fairness metrics (TPR, FPR, precision per sensitive group).
- **`bias.py`**: `audit_bias()` checks prediction rate disparity across neurological conditions and demographic groups. Returns `BiasAuditResult` with pass/fail and flagged groups.

### Configuration

`configs/default.yaml` controls the full pipeline — data paths, preprocessing options, feature flags, model choice, evaluation thresholds, and bias audit settings.

---

## Code Conventions

- **Python 3.10+** with `from __future__ import annotations`
- **Type hints** on all public functions
- **100-character line length** (black + ruff)
- **Docstrings**: Google style (Args/Returns/Raises)
- **Import order**: stdlib → third-party → local (enforced by ruff)
- **Random state**: Always `42` for reproducibility
- **Conventional Commits**: `feat`, `fix`, `data`, `model`, `refactor`, `test`, `docs`, `chore`

---

## Data Schema

### Required Survey Columns

| Column | Type | Description |
|--------|------|-------------|
| `participant_id` | str/int | Unique identifier |
| `age` | int | Participant age (0-120) |
| `gender` | str | Gender category |
| `neurological_condition` | str | One of: `multiple_sclerosis`, `epilepsy`, `parkinsons`, `traumatic_brain_injury`, `chronic_fatigue_syndrome`, `migraine_chronic`, `adhd`, `other`, `none` |
| `exhaustion_score` | float | MBI emotional exhaustion (>=0) |
| `depersonalization_score` | float | MBI depersonalization (>=0) |
| `efficacy_score` | float | MBI personal efficacy (>=0) |

### Optional Columns

`sleep_quality`, `cognitive_load`, `fatigue_level`, `medication_adherence`, `work_hours_weekly`, `symptom_severity`, `hrv_mean`, `stress_self_report`

---

## Key Decisions for AI Assistants

1. **Never modify files in `data/raw/`** — raw data is immutable.
2. **Prefer editing existing modules** over creating new files.
3. **Always add type hints** to new functions.
4. **All new functions need unit tests** — add to the appropriate `tests/unit/test_*.py` file.
5. **Run `pytest tests/`** after any code changes to verify nothing is broken.
6. **Use `random_state=42`** everywhere for reproducibility.
7. **Check `.gitignore`** before committing — no data files, model binaries, or secrets.
8. **Neurological context matters** — features and evaluations must account for condition-specific symptom overlaps with burnout.
9. **Bias audits are mandatory** — any new model or feature should be evaluated for fairness across neurological condition groups.
10. **Ethical considerations** — burnout predictions affect people's lives and clinical assessments. Flag any design decisions that could introduce bias or privacy risks. Model outputs must never be used as sole decision-makers.

---

## Privacy & Ethics

- All personal/health data must comply with GDPR, HIPAA, and applicable regulations
- Anonymize or pseudonymize data before processing
- Model outputs must never be sole basis for employment or clinical decisions
- Bias audits run by default across neurological condition groups and demographics
- Document data collection consent in `data/README.md`

---

## Useful References

- [Maslach Burnout Inventory](https://www.mindgarden.com/117-maslach-burnout-inventory-mbi)
- [WHO Burnout Definition](https://www.who.int/news/item/28-05-2019-burn-out-an-occupational-phenomenon-international-classification-of-diseases)
- [scikit-learn](https://scikit-learn.org/) — ML framework used for all models
- [pandas](https://pandas.pydata.org/) — tabular data
- [Conventional Commits](https://www.conventionalcommits.org/)

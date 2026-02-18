# CLAUDE.md — Burnout Detection Project

This file provides guidance for AI assistants (Claude Code and similar tools) working on this repository.

## Project Overview

**Burnout-detection-** is a project aimed at detecting employee/individual burnout using data-driven methods. Burnout is a state of chronic stress leading to physical and emotional exhaustion, cynicism, and feelings of ineffectiveness. The goal of this project is to build models, pipelines, and/or tools that can identify burnout signals from available data sources.

**Current status:** Early stage — initial repository with no code yet. The structure and conventions below should be followed as the project develops.

---

## Repository State

| Item | Status |
|------|--------|
| README.md | Minimal (title only) — needs expansion |
| Source code | Not yet created |
| Tests | Not yet created |
| Dependencies | Not yet defined |
| CI/CD | Not yet configured |

---

## Expected Project Structure

As this project grows, it should follow a structure appropriate for a data science / ML project:

```
Burnout-detection-/
├── CLAUDE.md               # This file — AI assistant guidance
├── README.md               # Project overview, setup instructions
├── requirements.txt        # Python dependencies (pip)
│   OR
├── pyproject.toml          # Modern Python packaging config (preferred)
├── .gitignore              # Ignore data files, model artifacts, venvs
│
├── data/
│   ├── raw/                # Raw, unprocessed datasets (never modify)
│   ├── processed/          # Cleaned, feature-engineered datasets
│   └── external/           # Third-party or reference data
│
├── notebooks/
│   ├── exploration/        # EDA and initial analysis notebooks
│   └── experiments/        # Model experiments and comparisons
│
├── src/
│   └── burnout_detection/  # Main Python package
│       ├── __init__.py
│       ├── data/           # Data loading and preprocessing
│       ├── features/       # Feature engineering
│       ├── models/         # Model definitions and training
│       ├── evaluation/     # Metrics and evaluation utilities
│       └── utils/          # Shared helper functions
│
├── tests/
│   ├── unit/               # Unit tests for individual functions
│   └── integration/        # End-to-end pipeline tests
│
├── configs/                # Configuration files (YAML/TOML)
├── scripts/                # CLI scripts and automation
└── outputs/                # Model artifacts, reports, figures (gitignored)
```

---

## Development Workflow

### Setting Up the Environment

```bash
# Clone the repository
git clone <repo-url>
cd Burnout-detection-

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies (once defined)
pip install -r requirements.txt
# or, for editable installs with pyproject.toml:
pip install -e ".[dev]"
```

### Git Workflow

This project uses feature branches. Development follows this pattern:

```bash
# Always branch from main
git checkout main
git pull origin main
git checkout -b feature/<short-description>

# Make changes, then commit
git add <files>
git commit -m "feat: brief description of what was added"

# Push and open a PR
git push -u origin feature/<short-description>
```

#### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

Types:
  feat      — new feature or model
  fix       — bug fix
  data      — changes to data pipelines or datasets
  model     — model architecture or training changes
  refactor  — code restructuring without behavior change
  test      — adding or updating tests
  docs      — documentation changes
  chore     — build system, dependencies, config
```

Examples:
```
feat(features): add rolling mean feature for work-hours signal
fix(data): handle missing values in survey dataset loader
model(lstm): tune dropout rate and learning rate schedule
test(preprocessing): add unit tests for outlier removal
```

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, reviewed code only |
| `feature/*` | New features under development |
| `fix/*` | Bug fixes |
| `experiment/*` | Model experiments (may not be merged) |
| `claude/*` | AI-assisted development branches |

---

## Code Conventions

### Language & Runtime

- **Primary language:** Python (3.10+ recommended)
- **Package manager:** pip with `requirements.txt` or `pyproject.toml`
- **Notebook format:** Jupyter `.ipynb` for exploration; convert stable code to `.py` modules

### Python Style

- Follow **PEP 8** for style
- Use **type hints** on all public functions and class methods
- Maximum line length: **100 characters**
- Formatter: **black** (preferred) or **ruff**
- Linter: **ruff** or **flake8**
- Import order: standard library → third-party → local (enforced by `isort` or `ruff`)

```python
# Good: typed, documented, single responsibility
def load_survey_data(path: str, drop_na: bool = True) -> pd.DataFrame:
    """Load burnout survey data from a CSV file.

    Args:
        path: Absolute or relative path to the CSV file.
        drop_na: Whether to drop rows with any missing values.

    Returns:
        A cleaned DataFrame ready for feature engineering.
    """
    df = pd.read_csv(path)
    if drop_na:
        df = df.dropna()
    return df
```

### Data Handling

- **Never commit raw data files** to the repository; use `.gitignore` to exclude `data/raw/` contents
- Document data sources, licenses, and access instructions in `data/README.md`
- Use deterministic random seeds (`random_state=42`) for reproducibility
- Store processed datasets with versioned filenames (e.g., `features_v1.parquet`)

### Machine Learning Conventions

- Log experiments with **MLflow** or **Weights & Biases** (to be decided)
- Always split data into train/validation/test before any feature engineering to prevent leakage
- Document model assumptions and limitations in code comments and README
- Save model artifacts with version tags, not just "latest"
- Evaluation metrics should include both technical metrics and fairness/bias checks where applicable

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/burnout_detection --cov-report=term-missing

# Run a specific test file
pytest tests/unit/test_preprocessing.py
```

**Expectations:**
- All new utility functions and data pipeline steps must have unit tests
- Target minimum 80% code coverage for `src/`
- Tests should use fixtures and not depend on real data files in `data/raw/`

---

## Key Decisions for AI Assistants

When working on this repository, AI assistants should:

1. **Ask before creating new top-level directories** — keep the structure above unless there is a clear reason to deviate.
2. **Never modify files in `data/raw/`** — treat raw data as immutable.
3. **Prefer editing existing modules** over creating new files when adding small features.
4. **Keep notebooks for exploration, modules for production logic** — do not put reusable logic inside notebook cells.
5. **Always add type hints** to new functions.
6. **Do not over-engineer** — implement exactly what is needed; avoid premature abstractions.
7. **Check for `.gitignore`** before committing — ensure no data files, model binaries, or secrets are staged.
8. **Use deterministic operations** wherever possible for reproducibility.
9. **Document data assumptions** — if a function expects specific columns or data types, assert or document them explicitly.
10. **Ethical considerations** — burnout detection models can affect people's employment or evaluation. Flag any design decisions that could introduce bias or privacy risks.

---

## Domain Context: Burnout Detection

### Common Data Sources

Burnout detection projects typically use one or more of:
- **Self-report surveys** (Maslach Burnout Inventory, WHO-5, PHQ-9)
- **Wearable / physiological data** (heart rate variability, sleep, activity)
- **Work behavior signals** (email/calendar metadata, hours logged, response times)
- **Text/NLP signals** (sentiment from written communications)

### Common Features

| Feature category | Examples |
|-----------------|---------|
| Work hours | Avg daily hours, overtime frequency, weekend work rate |
| Communication | Email response latency, after-hours messages, meeting load |
| Sentiment | NLP sentiment of written messages over time |
| Physiological | Sleep quality, HRV, resting heart rate trends |
| Survey scores | Exhaustion sub-scale, depersonalization, personal accomplishment |

### Common Models

- Logistic regression (baseline, interpretable)
- Gradient boosting (XGBoost, LightGBM) for tabular data
- LSTM / Transformer models for time-series signals
- Multi-modal fusion when combining survey + behavioral + physiological data

---

## Privacy & Ethics

- All personal data must be handled in compliance with applicable regulations (GDPR, HIPAA, etc.)
- Anonymize or pseudonymize data before processing where possible
- Model outputs should never be used as the sole basis for employment decisions
- Document data collection consent in the data README
- Bias audits should be performed segmented by demographic groups if demographic data is available

---

## Useful References

- [Maslach Burnout Inventory](https://www.mindgarden.com/117-maslach-burnout-inventory-mbi)
- [WHO Burnout Definition](https://www.who.int/news/item/28-05-2019-burn-out-an-occupational-phenomenon-international-classification-of-diseases)
- [scikit-learn](https://scikit-learn.org/) — general ML
- [pandas](https://pandas.pydata.org/) — tabular data
- [PyTorch](https://pytorch.org/) — deep learning
- [MLflow](https://mlflow.org/) — experiment tracking
- [Conventional Commits](https://www.conventionalcommits.org/)

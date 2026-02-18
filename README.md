# Burnout Detection for Neurological Populations

Burnout detection application targeting individuals with neurological conditions. Built with Python and scikit-learn, this project provides a modular pipeline for data loading, preprocessing, feature engineering, model training, evaluation, and bias auditing.

## Target Population

People with neurological conditions — including multiple sclerosis, epilepsy, Parkinson's disease, traumatic brain injury, chronic fatigue syndrome, chronic migraine, and ADHD — often experience compounding fatigue and cognitive difficulties that make them more susceptible to burnout. Standard burnout detection tools may not account for these overlapping symptoms. This project builds neurological-aware features and includes bias auditing across condition groups.

## Quick Start

```bash
# Clone and set up
git clone <repo-url>
cd Burnout-detection-
python -m venv .venv
source .venv/bin/activate

# Install (editable, with dev tools)
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run the pipeline (requires data in data/raw/)
burnout-detect --config configs/default.yaml
```

## Project Structure

```
src/burnout_detection/
├── data/           # Loading, preprocessing, validation
├── features/       # Neurological-aware feature engineering
├── models/         # Training (LogReg, RF, GBM) and prediction
├── evaluation/     # Metrics, fairness metrics, bias auditing
├── utils/          # I/O, reproducibility helpers
└── cli.py          # Command-line entry point
```

## Key Features

- **Data validation** with schema checks for required columns, score ranges, and neurological condition values
- **Preprocessing pipeline** with imputation, outlier removal, encoding, and scaling
- **Neurological-specific features**: neuro-fatigue index, work strain ratio, symptom-burnout interaction
- **Multiple models**: logistic regression (baseline), random forest, gradient boosting
- **Bias auditing**: per-group fairness metrics across neurological conditions and demographics
- **Risk-level predictions**: minimal / low / moderate / high burnout risk categories
- **YAML-configurable pipeline** via CLI

## Configuration

Edit `configs/default.yaml` to control:
- Data paths and train/test split ratios
- Preprocessing options (imputation strategy, outlier removal)
- Feature flags (neurological features, interaction terms)
- Model selection and hyperparameters
- Evaluation thresholds and bias audit settings

## Testing

```bash
pytest tests/ -v                                               # All tests
pytest tests/ --cov=src/burnout_detection --cov-report=term    # With coverage
pytest tests/unit/test_features.py                             # Specific module
```

## Privacy & Ethics

- All personal/health data must comply with GDPR, HIPAA, and applicable regulations
- Anonymize or pseudonymize participant data before processing
- Model outputs must never be used as the sole basis for employment or clinical decisions
- Bias audits are built into the pipeline and run by default across neurological condition groups

## License

MIT

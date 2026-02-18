"""Command-line interface for the burnout detection pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from burnout_detection.utils.reproducibility import set_global_seed


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Configuration dictionary.
    """
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict[str, Any]) -> None:
    """Execute the full burnout detection pipeline.

    Args:
        config: Configuration dictionary.
    """
    from burnout_detection.data.loader import load_survey_data
    from burnout_detection.data.preprocessing import preprocess_pipeline
    from burnout_detection.data.validation import validate_dataframe
    from burnout_detection.evaluation.bias import audit_bias
    from burnout_detection.evaluation.metrics import evaluate_model
    from burnout_detection.features.builder import build_features
    from burnout_detection.models.predict import predict, predict_proba
    from burnout_detection.models.trainer import cross_validate, train_model
    from burnout_detection.utils.io import save_artifact

    import numpy as np
    from sklearn.model_selection import train_test_split

    data_cfg = config["data"]
    preproc_cfg = config["preprocessing"]
    feat_cfg = config["features"]
    model_cfg = config["model"]
    eval_cfg = config["evaluation"]
    output_cfg = config["output"]

    set_global_seed(data_cfg.get("random_state", 42))

    # 1. Load data
    print("Loading data...")
    df = load_survey_data(data_cfg["survey_path"], validate=True)

    # 2. Validate
    print("Validating data...")
    validation = validate_dataframe(df, require_all_columns=True)
    print(validation)
    if not validation.is_valid:
        print("Data validation failed. Aborting.", file=sys.stderr)
        sys.exit(1)

    # 3. Preprocess
    print("Preprocessing...")
    df_processed, artifacts = preprocess_pipeline(
        df,
        impute=preproc_cfg.get("impute", True),
        remove_outlier_cols=preproc_cfg.get("outlier_columns"),
        encode=preproc_cfg.get("encode_categorical", True),
        scale=preproc_cfg.get("scale_features", True),
    )

    # 4. Feature engineering
    print("Building features...")
    df_features = build_features(
        df_processed,
        include_neuro_features=feat_cfg.get("include_neuro_features", True),
        include_interaction_features=feat_cfg.get("include_interaction_features", True),
    )

    # 5. Train/test split
    if "burnout_label" not in df_features.columns:
        # Derive binary label from composite if not present
        if "burnout_composite" in df_features.columns:
            median_val = df_features["burnout_composite"].median()
            df_features["burnout_label"] = (
                df_features["burnout_composite"] >= median_val
            ).astype(int)
        else:
            print("Error: No burnout_label or burnout_composite column.", file=sys.stderr)
            sys.exit(1)

    feature_cols = [
        c
        for c in df_features.columns
        if c not in ("participant_id", "burnout_label", "burnout_composite")
    ]
    # Keep only numeric features for modeling
    X = df_features[feature_cols].select_dtypes(include="number")
    y = df_features["burnout_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=data_cfg.get("test_size", 0.2),
        random_state=data_cfg.get("random_state", 42),
        stratify=y,
    )

    # 6. Cross-validation (optional)
    if model_cfg.get("cross_validate", True):
        print("Cross-validating...")
        cv_results = cross_validate(
            X_train,
            y_train,
            model_name=model_cfg["name"],
            params=model_cfg.get("params"),
            n_folds=model_cfg.get("cv_folds", 5),
            scoring=model_cfg.get("cv_scoring", "f1"),
        )
        print(f"  CV {cv_results['scoring']}: "
              f"{cv_results['mean']:.4f} (+/- {cv_results['std']:.4f})")

    # 7. Train final model
    print(f"Training {model_cfg['name']}...")
    model = train_model(
        X_train, y_train,
        model_name=model_cfg["name"],
        params=model_cfg.get("params"),
    )

    # 8. Evaluate
    print("Evaluating...")
    y_pred = predict(model, X_test)
    y_proba = None
    if hasattr(model, "predict_proba"):
        y_proba = predict_proba(model, X_test)[:, 1]

    metrics = evaluate_model(y_test.values, y_pred, y_proba)
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1:        {metrics['f1']:.4f}")
    if metrics.get("roc_auc") is not None:
        print(f"  ROC AUC:   {metrics['roc_auc']:.4f}")

    # 9. Bias audit
    if eval_cfg.get("bias_audit", True):
        print("Running bias audit...")
        sensitive = {}
        for attr in eval_cfg.get("bias_attributes", []):
            if attr in df_features.columns:
                test_indices = X_test.index
                sensitive[attr] = df_features.loc[test_indices, attr].values

        if sensitive:
            bias_results = audit_bias(
                y_test.values,
                y_pred,
                sensitive,
                disparity_threshold=eval_cfg.get("disparity_threshold", 0.1),
            )
            for attr_name, result in bias_results.items():
                print(result.summary())

    # 10. Save artifacts
    print("Saving artifacts...")
    model_dir = Path(output_cfg.get("model_dir", "outputs/models"))
    version = output_cfg.get("version")
    save_artifact(model, model_dir / f"{model_cfg['name']}.joblib", version=version)
    save_artifact(artifacts, model_dir / "preprocessing_artifacts.joblib", version=version)

    # Save metrics report
    reports_dir = Path(output_cfg.get("reports_dir", "outputs/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "evaluation_metrics.json"
    serializable_metrics = {
        k: v for k, v in metrics.items() if k != "classification_report"
    }
    with open(report_path, "w") as f:
        json.dump(serializable_metrics, f, indent=2)

    print(f"Done. Model saved to {model_dir}, report to {report_path}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Burnout Detection Pipeline for Neurological Populations",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to the YAML configuration file.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()

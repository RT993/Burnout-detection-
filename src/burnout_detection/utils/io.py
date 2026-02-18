"""I/O utilities for saving and loading artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


def save_artifact(obj: Any, path: str | Path, version: str | None = None) -> Path:
    """Save a model or preprocessing artifact to disk.

    Args:
        obj: The object to save (model, scaler, encoder, etc.).
        path: Destination file path.
        version: Optional version tag appended to the filename.

    Returns:
        The actual path the artifact was saved to.
    """
    path = Path(path)
    if version:
        path = path.with_stem(f"{path.stem}_v{version}")

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)
    return path


def load_artifact(path: str | Path) -> Any:
    """Load a saved artifact from disk.

    Args:
        path: Path to the saved artifact.

    Returns:
        The deserialized object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    return joblib.load(path)

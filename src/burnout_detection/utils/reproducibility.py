"""Reproducibility utilities for deterministic experiments."""

from __future__ import annotations

import random

import numpy as np


def set_global_seed(seed: int = 42) -> None:
    """Set random seeds for reproducibility across all libraries.

    Args:
        seed: The seed value to use.
    """
    random.seed(seed)
    np.random.seed(seed)

    # Set sklearn's global random state via numpy
    # If torch is available, seed it too
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

"""Model definitions, training, and inference."""

from burnout_detection.models.trainer import train_model
from burnout_detection.models.predict import predict

__all__ = ["train_model", "predict"]

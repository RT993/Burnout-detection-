"""Tests for data loading utilities."""

from __future__ import annotations

import pytest

from burnout_detection.data.loader import (
    REQUIRED_COLUMNS,
    load_survey_data,
)


class TestLoadSurveyData:
    def test_loads_valid_csv(self, sample_survey_csv: str) -> None:
        df = load_survey_data(sample_survey_csv)
        assert not df.empty
        assert len(df) == 50

    def test_validates_required_columns(self, sample_survey_csv: str) -> None:
        df = load_survey_data(sample_survey_csv, validate=True)
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

    def test_raises_on_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_survey_data("/nonexistent/path.csv")

    def test_raises_on_missing_columns(self, tmp_path: object) -> None:
        import pandas as pd

        path = str(tmp_path / "bad.csv")  # type: ignore[operator]
        pd.DataFrame({"col_a": [1, 2]}).to_csv(path, index=False)
        with pytest.raises(ValueError, match="Missing required columns"):
            load_survey_data(path, validate=True)

    def test_skip_validation(self, tmp_path: object) -> None:
        import pandas as pd

        path = str(tmp_path / "any.csv")  # type: ignore[operator]
        pd.DataFrame({"x": [1]}).to_csv(path, index=False)
        df = load_survey_data(path, validate=False)
        assert len(df) == 1

    def test_drop_na(self, tmp_path: object) -> None:
        import pandas as pd
        import numpy as np

        data = {col: [1.0, np.nan, 3.0] for col in REQUIRED_COLUMNS}
        data["participant_id"] = ["a", "b", "c"]
        path = str(tmp_path / "na.csv")  # type: ignore[operator]
        pd.DataFrame(data).to_csv(path, index=False)
        df = load_survey_data(path, drop_na=True, validate=False)
        assert df.isna().sum().sum() == 0

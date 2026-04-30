import pandas as pd

from app.application.service.dataset_service import DatasetService


def test_min_max_scale_column_applies_min_max_scaling():
    """La función debe escalar correctamente valores numéricos usando Min-Max."""
    column = pd.Series([10, 20, 30, 40])

    scaled = DatasetService.min_max_scale_column(column)

    assert scaled.tolist() == [0.0, 0.3333333333333333, 0.6666666666666666, 1.0]


def test_min_max_scale_column_handles_constant_column():
    """Si todos los valores son idénticos, debe devolver 0.0 para todos los elementos."""
    column = pd.Series([100, 100, 100])

    scaled = DatasetService.min_max_scale_column(column)

    assert scaled.tolist() == [0.0, 0.0, 0.0]


def test_min_max_scale_column_retains_nan_values():
    """Los valores NaN deben permanecer NaN y otros valores deben escalarse correctamente."""
    column = pd.Series([5, None, 15, float('nan'), 25])

    scaled = DatasetService.min_max_scale_column(column)

    assert scaled[0] == 0.0
    assert pd.isna(scaled[1])
    assert scaled[2] == 0.5
    assert pd.isna(scaled[3])
    assert scaled[4] == 1.0

"""Compute ARIMA features."""

import os

import joblib  # type: ignore
import pandas as pd
from sktime.forecasting import model_selection  # type: ignore
from sktime.forecasting.arima import AutoARIMA  # type: ignore
from sktime.forecasting.base import ForecastingHorizon  # type: ignore

from .cache import CACHE_FOLDER
from .feature import FEATURE_TYPE_ARIMA, Feature
from .sanitise import sanitise_dt_isoformat
from .transform import Transform

ARIMA_MODEL_EXT = "pkl"
ARIMA_MODEL_PREFIX = "arima_"
ARIMA_FOLDER_PREFIX = "arima"


def compute_arima(series: pd.Series, max_lag: int, min_lag: int) -> list[Feature]:
    """Compute ARIMA features."""
    model_name = "_".join(
        [ARIMA_FOLDER_PREFIX, str(series.name), str(max_lag), str(min_lag)]
    )
    model_folder = os.path.join(CACHE_FOLDER, model_name)
    os.makedirs(model_folder, exist_ok=True)

    splitter = model_selection.SlidingWindowSplitter(
        window_length=365, fh=min_lag, step_length=7, start_with_window=True
    )

    for train_idx, test_idx in splitter.split(series):
        y_train = series.iloc[train_idx]
        target_time = series.index[test_idx[0]]
        fh = ForecastingHorizon(range(1, min_lag + 1), is_relative=True)
        target_label = sanitise_dt_isoformat(str(target_time))
        model_path = os.path.join(
            model_folder, f"{ARIMA_MODEL_PREFIX}{target_label}.{ARIMA_MODEL_EXT}"
        )
        if os.path.exists(model_path):
            continue

        if len(y_train) < (max_lag + min_lag):
            continue

        model = AutoARIMA(suppress_warnings=True)  # weekly seasonality assumed
        model.fit(y=y_train, fh=fh)

        joblib.dump(model, model_path)

    return [
        Feature(
            feature_type=FEATURE_TYPE_ARIMA,
            columns=[str(series.name)],
            value1=model_name,
            value2=min_lag,
            transform=str(Transform.NONE),
        )
    ]

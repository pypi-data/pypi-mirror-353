"""Process the ARIMA features."""

import datetime
import os
from collections import defaultdict

import joblib  # type: ignore
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon  # type: ignore

from .cache import CACHE_FOLDER
from .columns import DELIMITER
from .compute_arima import ARIMA_MODEL_PREFIX
from .feature import FEATURE_TYPE_ARIMA, Feature
from .sanitise import DT_SANITISATION_REPLACEMENTS


def _desanitise_dt_isoformat(dt: str) -> str:
    for k, v in DT_SANITISATION_REPLACEMENTS.items():
        dt = dt.replace(v, k)
    return dt


def load_model_index(model_dir: str) -> list[tuple[datetime.datetime, str]]:
    """Loads the available ARIMA model timestamps from filenames."""
    model_files = os.listdir(model_dir)
    models = []
    for file in model_files:
        if not file.endswith(".pkl"):
            continue
        name = file.replace(ARIMA_MODEL_PREFIX, "").replace(".pkl", "")
        idx = pd.to_datetime(_desanitise_dt_isoformat(name))
        models.append((idx, os.path.join(model_dir, file)))
    return sorted(models, key=lambda x: x[0])


def find_closest_model(
    target_time: datetime.datetime, model_index: list[tuple[datetime.datetime, str]]
):
    """Find the most recent model before or at target_time."""
    candidates = [m for m in model_index if m[0] <= target_time]
    if not candidates:
        return None
    return candidates[-1][1]


def _predict_arima(series: pd.Series, model_dir: str, min_lag: int) -> pd.Series:
    model_index = load_model_index(model_dir)
    preds = pd.Series(index=series.index, dtype=float)

    sorted_index = sorted(series.index)
    model_index = sorted(model_index, key=lambda x: x[0])

    model_to_times = defaultdict(list)
    for t in sorted_index:
        model_path = find_closest_model(t, model_index)
        if model_path is not None:
            model_to_times[model_path].append(t)

    for model_path, times in model_to_times.items():
        model = joblib.load(model_path)

        # Assumes fh used in training is always range(1, min_lag+1)
        fh = ForecastingHorizon(range(1, min_lag + 1), is_relative=True)
        pred = model.predict(fh=fh)

        for t in times:
            preds.loc[t] = pred.values[0]

    return preds


def process_arima(
    df: pd.DataFrame, features: list[Feature], columns: list[str]
) -> pd.DataFrame:
    """Process ARIMA forecasting predictions."""
    if not features:
        return df
    for column in columns:
        for feature in features:
            if feature["feature_type"] != FEATURE_TYPE_ARIMA:
                continue
            if feature["columns"] and column not in feature["columns"]:
                continue
            model_name = feature["value1"]
            if not isinstance(model_name, str):
                continue
            min_lag = feature.get("value2")
            if not isinstance(min_lag, int):
                continue
            df[DELIMITER.join([column, model_name])] = _predict_arima(
                df[column], os.path.join(CACHE_FOLDER, model_name), min_lag
            )
    return df

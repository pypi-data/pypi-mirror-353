"""
Обертка для ETNA
"""

import time
from typing import Union

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from etna.datasets import TSDataset
from etna.models import CatBoostPerSegmentModel
from etna.models import CatBoostMultiSegmentModel
from etna.pipeline import Pipeline
from etna.analysis import plot_forecast

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class EtnaPipeline:
    """Pipeline wrapper for ETNA models.

    This class provides methods to fit, transform, forecast, and visualize
    time series data using ETNA models.

    Args:
        dev_ts (TSDataset): Development time series dataset.
        train_ts (TSDataset): Training time series dataset.
        test_ts (TSDataset): Testing time series dataset.
        oot_ts (TSDataset): Out-of-time time series dataset.
        horizon: Forecast horizon.
        transforms: List of transformations to apply.
        frequency: Frequency of the time series data.
        model_type (str, optional): Type of ETNA model to use. Defaults to "multi_segment".
        use_etna (bool, optional): Flag to indicate whether to use ETNA for plotting. Defaults to False.
    """

    def __init__(
        self,
        dev_ts: TSDataset,
        train_ts: TSDataset,
        test_ts: TSDataset,
        oot_ts: TSDataset,
        horizon,
        transforms,
        frequency,
        model_type="multi_segment",
        use_etna: bool = False,
    ):
        self.model_name = "ETNA"
        self.dev_ts = dev_ts
        self.train_ts = train_ts
        self.test_ts = test_ts
        self.oot_ts = oot_ts
        self.horizon = horizon
        self.transforms = transforms
        self.frequency = frequency
        self.model_type = model_type
        self.pipeline = self._get_pipeline()
        self.frequency = frequency
        self.use_etna = use_etna
        self.fitted = False

    def _get_estimator(
        self, model_type: str
    ) -> Union[CatBoostPerSegmentModel, CatBoostMultiSegmentModel]:
        """Retrieve the appropriate ETNA estimator based on model type.

        Args:
            model_type (str): Type of model to instantiate.

        Returns:
            Union[CatBoostPerSegmentModel, CatBoostMultiSegmentModel]: Initialized ETNA model.
        """
        if model_type == "per_segment":
            return CatBoostPerSegmentModel()
        elif model_type == "multi_segment":
            return CatBoostMultiSegmentModel()

    def _get_pipeline(self) -> Pipeline:
        """Create and return the ETNA pipeline.

        Returns:
            Pipeline: Configured ETNA pipeline.
        """
        model = self._get_estimator(self.model_type)
        pipeline = Pipeline(
            model=model, transforms=self.transforms, horizon=self.horizon
        )
        return pipeline

    def fit(self, train_ts: TSDataset) -> None:
        """Fit the ETNA pipeline on the training data.

        Args:
            train_ts (TSDataset): Training time series dataset.

        Raises:
            Exception: If fitting fails.
        """
        _logger.info(f"{time.ctime()}, start fitting ETNA")
        self.pipeline.fit(train_ts)
        self.fitted = True

    def transform(
        self, data: Union[TSDataset, pd.DataFrame], return_dataset: bool = False
    ) -> np.ndarray:
        """Transform the input data using the fitted ETNA pipeline.

        Args:
            data (Union[TSDataset, pd.DataFrame]): Input data to transform.
            return_dataset (bool, optional): Whether to return the full dataset. Defaults to False.

        Returns:
            np.ndarray: Transformed target values if return_dataset is False.
            pd.DataFrame: Transformed dataset if return_dataset is True.

        Raises:
            ValueError: If data transformation fails.
        """
        if isinstance(data, pd.DataFrame):
            try:
                data, _ = self.dev_ts.train_test_split(
                    train_start=data["timestamp"].min(),
                    train_end=data["timestamp"].max(),
                )
            except:
                _, data = self.dev_ts.train_test_split(
                    train_start=data["timestamp"].min(),
                    train_end=data["timestamp"].max(),
                )
        prediction = self.pipeline.predict(ts=data, return_components=False)
        pred_df = prediction.to_pandas(True)
        return pred_df if return_dataset else pred_df["target"]

    def forecast(
        self,
        data: Union[TSDataset, pd.DataFrame],
        return_dataset: bool = False,
    ) -> np.ndarray:
        """Generate forecasts using the fitted ETNA pipeline.

        Args:
            data (Union[TSDataset, pd.DataFrame]): Input data for forecasting.
            return_dataset (bool, optional): Whether to return the full forecast dataset. Defaults to False.

        Returns:
            np.ndarray: Forecasted target values if return_dataset is False.
            pd.DataFrame: Forecasted dataset if return_dataset is True.

        Raises:
            ValueError: If forecasting fails.
        """
        if isinstance(data, pd.DataFrame):
            try:
                data, _ = self.dev_ts.train_test_split(
                    train_start=data["timestamp"].min(),
                    train_end=data["timestamp"].max(),
                )
            except:
                _, data = self.dev_ts.train_test_split(
                    test_start=data["timestamp"].min(), test_end=data["timestamp"].max()
                )
        forecast = self.pipeline.forecast(ts=data, return_components=False)
        forecast_df = forecast.to_pandas(True)
        return forecast_df if return_dataset else forecast_df["target"]

    def plot_forecast(self, train_ts: TSDataset, test_ts: TSDataset) -> None:
        """Plot the forecasted results against the test data.

        Args:
            train_ts (TSDataset): Training time series dataset.
            test_ts (TSDataset): Testing time series dataset.

        Raises:
            ValueError: If plotting fails.
        """
        if self.use_etna:
            train_data = self.train_ts.to_pandas(True).copy()
            if train_data["segment"].nunique() < 10:
                plot_forecast(
                    self.pipeline.forecast(train_ts),
                    test_ts,
                    train_ts,
                    n_train_samples=20,
                )
            else:
                _logger.info("Selected random 10 segments to plot.")
                segments = np.random.choice(
                    train_data["segment"].unique(), size=10, replace=False
                )
                plot_forecast(
                    self.pipeline.forecast(train_ts),
                    test_ts,
                    train_ts,
                    n_train_samples=20,
                    segments=segments,
                )
            plt.show()

    def get_etna_eval_set(self) -> dict:
        """Retrieve the evaluation datasets used by the pipeline.

        Returns:
            dict: Dictionary containing development, training, testing, and out-of-time datasets.
        """
        eval_set = {
            "dev_ts": self.dev_ts,
            "train_ts": self.train_ts,
            "test_ts": self.test_ts,
            "oot_ts": self.oot_ts,
        }
        return eval_set
from typing import Tuple, Any
from copy import deepcopy
import pandas as pd

from etna.pipeline import Pipeline
from etna.datasets import TSDataset

from dreamml.utils.prepare_artifacts_config import RegressionArtifactsConfig
from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.feature_enrichment.timeseries_enrichment import (
    get_time_column_frequency,
)
from dreamml.logging import get_logger
from dreamml.modeling.models.estimators.boosting_base import BoostingBaseModel
from dreamml.features.categorical.categorical_encoder import (
    CategoricalFeaturesTransformer,
)


_logger = get_logger(__name__)


def prepare_artifacts_config_timeseries(config: dict) -> Tuple[Any, Any]:
    """
    Prepare the artifacts configuration for passing to the ValidationReport object.

    Args:
        config (dict): Configuration dictionary specifying the final model name and
                       the directory containing the artifacts of the computational experiment.

    Returns:
        Tuple[Any, Any]: A tuple containing the artifacts configuration and associated data.

    Raises:
        KeyError: If required keys are missing in the configuration dictionary.
        ValueError: If the configuration is invalid or incomplete.
    """
    prepare_artifacts = RegressionArtifactsConfig(config=config)
    artifacts_config, data = prepare_artifacts.prepare_artifacts_config()
    return artifacts_config, data


class TimeSeriesPrediction:
    """
    A class for performing time series predictions using provided configurations and pipelines.

    Attributes:
        artifacts_config (dict): Configuration for artifacts.
        dml_transforms (dict): Dictionary of DML transformations.
        etna_pipeline (Pipeline): Etna pipeline for forecasting.
        etna_eval_sets (dict): Dictionary of evaluation sets.
        model (BoostingBaseModel): The estimator model used for predictions.
        used_features (list): List of features used by the model.
        config_storage (ConfigStorage): Configuration storage object.
        transformer (CategoricalFeaturesTransformer): Transformer for categorical features.
        horizon (int): Forecast horizon.
        frequency (str): Frequency of the time series data.
        use_etna (bool): Flag indicating whether to use Etna for forecasting.
        dml_predictions (pd.DataFrame or None): Predictions from DML transformations.
        etna_predictions (pd.DataFrame or None): Predictions from Etna pipeline.
    """

    def __init__(
        self,
        artifacts_config,
        dml_transforms,
        etna_pipeline,
        etna_eval_sets,
    ):
        """
        Initialize the TimeSeriesPrediction class with necessary configurations and pipelines.

        Args:
            artifacts_config (dict): Configuration for artifacts including model and transformers.
            dml_transforms (dict): Dictionary of DML transformations to be applied.
            etna_pipeline (Pipeline): Etna pipeline used for forecasting.
            etna_eval_sets (dict): Dictionary containing evaluation datasets.

        Raises:
            KeyError: If required keys are missing in artifacts_config.
            AttributeError: If expected attributes are not found in the provided objects.
        """
        self.artifacts_config = artifacts_config
        self.dml_transforms: dict = dml_transforms
        self.etna_pipeline: Pipeline = etna_pipeline
        self.etna_transforms = self.etna_pipeline.transforms
        self.etna_eval_sets: dict = etna_eval_sets

        self.model: BoostingBaseModel = artifacts_config["estimator"]
        self.used_features: list = self.model.used_features
        self.config_storage: ConfigStorage = artifacts_config["config_storage"]
        self.transformer: CategoricalFeaturesTransformer = artifacts_config["encoder"]

        self.horizon = self.config_storage.pipeline.task_specific.time_series.horizon
        self.frequency = get_time_column_frequency(
            self.config_storage.data.columns.time_column_period
        )
        self.use_etna = self.config_storage.pipeline.alt_mode.use_etna
        self.dml_predictions = None
        self.etna_predictions = None

    def get_forecast(self) -> pd.DataFrame:
        """
        Generate forecasted data using the Etna pipeline or by creating future steps.

        Returns:
            pd.DataFrame: Forecasted data as a pandas DataFrame.

        Raises:
            ValueError: If neither 'oot_ts' nor 'test_ts' datasets are available in etna_eval_sets.
            RuntimeError: If forecasting fails due to pipeline issues.
        """
        if (
            "oot_ts" in self.etna_eval_sets
            and self.etna_eval_sets["oot_ts"] is not None
        ):
            data: TSDataset = self.etna_eval_sets["oot_ts"]
        elif "test_ts" in self.etna_eval_sets and self.etna_eval_sets["test_ts"] is not None:
            data: TSDataset = self.etna_eval_sets["test_ts"]
        else:
            raise ValueError("No valid evaluation dataset found in etna_eval_sets.")

        if self.use_etna is True:
            try:
                predictions = self.etna_pipeline.forecast(data)
            except Exception as e:
                _logger.error("Etna pipeline forecasting failed.", exc_info=True)
                raise RuntimeError("Forecasting with Etna pipeline failed.") from e
        else:
            predictions = data.make_future(
                future_steps=self.horizon, transforms=self.etna_transforms
            )
        return predictions.to_pandas(True)

    def _dml_feature_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich features with DML transformations.

        Args:
            data (pd.DataFrame): Input data to be transformed.

        Returns:
            pd.DataFrame: Transformed data after applying DML feature transformations.

        Raises:
            RuntimeError: If transformation fails for any DML transform.
        """
        if len(self.dml_transforms) > 0:
            for transform in self.dml_transforms:
                try:
                    _, data = transform.transform(data)
                except Exception as e:
                    _logger.error("DML feature transformation failed.", exc_info=True)
                    raise RuntimeError("DML feature transformation failed.") from e
        return data

    def transform(self) -> None:
        """
        Perform the transformation process to generate predictions.

        This method obtains the forecast, optionally stores Etna predictions, and
        generates DML predictions.

        Raises:
            RuntimeError: If the forecasting or transformation process fails.
        """
        data = self.get_forecast()
        if self.use_etna:
            self.etna_predictions = deepcopy(data[["target", "timestamp", "segment"]])
        self.dml_predictions = self._get_dml_predict(data)

    def _get_dml_predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate DML-based predictions from the provided data.

        Args:
            data (pd.DataFrame): Data used for generating predictions.

        Returns:
            pd.DataFrame: DataFrame containing the DML predictions.

        Raises:
            RuntimeError: If prediction generation fails at any step.
        """
        try:
            predictions = self._dml_feature_transform(data)
            predictions = self.transformer.transform(predictions)
            predictions["target"] = self.model.transform(predictions[self.used_features])
            predictions = predictions[["target", "timestamp", "segment"]]
            predictions = self.transformer.inverse_transform(predictions)
            predictions = TSDataset.to_dataset(predictions)
            predictions = TSDataset(df=predictions, freq=self.frequency)
            predictions.inverse_transform(transforms=self.etna_transforms)
            predictions = predictions.to_pandas(True)
            return predictions
        except Exception as e:
            _logger.error("DML prediction generation failed.", exc_info=True)
            raise RuntimeError("DML prediction generation failed.") from e
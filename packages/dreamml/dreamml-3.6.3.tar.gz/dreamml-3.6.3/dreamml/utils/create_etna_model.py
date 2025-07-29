from etna.datasets import TSDataset

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._dataset import DataSet
from dreamml.modeling.models.estimators._etna_model import EtnaPipeline
from dreamml.features.feature_enrichment.timeseries_enrichment import (
    get_time_column_frequency,
)
from dreamml.logging import get_logger

_logger = get_logger(__name__)


class ETNA:
    """Wrapper for the ETNA framework used in the modeling pipeline.

    This class integrates the ETNA framework with the existing data storage and configuration
    to facilitate time series forecasting tasks. It handles data preparation, model training,
    and pipeline management.
    """

    def __init__(
        self,
        config_storage: ConfigStorage,
        data_storage: DataSet,
    ):
        """Initializes the ETNA wrapper with configuration and data storage.

        Args:
            config_storage (ConfigStorage): Configuration storage containing pipeline settings.
            data_storage (DataSet): Data storage containing datasets and ETNA artifacts.
        """
        self.data_storage = data_storage
        self.drop_features = config_storage.data.columns.drop_features
        self.etna_transforms = data_storage.etna_artifacts["etna_transforms"]
        self.dev_ts: TSDataset = data_storage.etna_artifacts["dev_ts"]
        self.horizon = config_storage.pipeline.task_specific.time_series.horizon
        self.frequency = get_time_column_frequency(
            config_storage.data.columns.time_column_period
        )
        self.known_future = (
            config_storage.pipeline.task_specific.time_series.known_future
        )
        self.eval_set = data_storage.get_clean_eval_set()
        self.use_etna = config_storage.pipeline.alt_mode.use_etna

    def _prepare_eval_set(self):
        """Prepares the evaluation set by splitting the development time series.

        This method processes the evaluation samples to determine date ranges for training,
        testing, and out-of-time (OOT) evaluation. It then splits the development time series
        accordingly.

        Returns:
            tuple of TSDataset:
                - train_ts: Training time series dataset.
                - test_ts: Testing time series dataset.
                - oot_ts: Out-of-time evaluation time series dataset, or None if not applicable.

        Raises:
            KeyError: If expected keys are not present in the evaluation set.
            IndexError: If samples in the evaluation set are empty.
        """
        sample_dates = {}
        for sample_name, sample in self.eval_set.items():
            sample_dates[sample_name] = (
                sample[0]["timestamp"].min(),
                sample[0]["timestamp"].max(),
            )

        train_ts, test_ts, oot_ts = self._train_test_oot_split(
            self.dev_ts, sample_dates
        )
        return train_ts, test_ts, oot_ts

    def _train_test_oot_split(self, dev_ts: TSDataset, sample_dates: dict):
        """Splits the development time series into training, testing, and OOT datasets.

        Args:
            dev_ts (TSDataset): The full development time series dataset.
            sample_dates (dict): Dictionary containing date ranges for different sample splits.

        Returns:
            tuple of TSDataset:
                - train_ts: Training time series dataset.
                - test_ts: Testing time series dataset.
                - oot_ts: Out-of-time evaluation time series dataset, or None if not applicable.

        Raises:
            KeyError: If required keys ('train', 'valid', 'test') are missing in sample_dates.
        """
        train_ts, test_ts = dev_ts.train_test_split(
            train_start=sample_dates["train"][0],
            train_end=sample_dates["valid"][1],
            test_start=sample_dates["test"][0],
            test_end=sample_dates["test"][1],
        )
        oot_ts = None
        if "OOT" in sample_dates:
            _, oot_ts = dev_ts.train_test_split(
                train_start=sample_dates["train"][0],
                train_end=sample_dates["valid"][1],
                test_start=sample_dates["OOT"][0],
                test_end=sample_dates["OOT"][1],
            )
        return train_ts, test_ts, oot_ts

    def add_etna_model(self, model_type: str = "multi_segment"):
        """Adds and fits an ETNA model to the pipeline.

        This method initializes an ETNA pipeline with the prepared training, testing, and
        optional out-of-time datasets. It fits the model if ETNA usage is enabled in the
        configuration and stores the pipeline in the data storage.

        Args:
            model_type (str, optional): The type of ETNA model to use. Defaults to "multi_segment".

        Returns:
            EtnaPipeline: The instantiated ETNA pipeline.

        Raises:
            KeyError: If required ETNA artifacts are missing in the data storage.
            Exception: If fitting the ETNA pipeline fails.
        """
        train_ts, test_ts, oot_ts = self._prepare_eval_set()

        etna_pipeline = EtnaPipeline(
            dev_ts=self.dev_ts,
            horizon=self.horizon,
            transforms=self.etna_transforms,
            frequency=self.frequency,
            model_type=model_type,
            train_ts=train_ts,
            test_ts=test_ts,
            oot_ts=oot_ts,
            use_etna=self.use_etna,
        )

        if self.use_etna:
            etna_pipeline.fit(train_ts)

        self.data_storage.etna_pipeline = etna_pipeline
        return etna_pipeline
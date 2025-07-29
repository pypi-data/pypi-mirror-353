import re
import sys
import time
import warnings
from typing import Tuple, Dict, Optional
from pathlib import Path

import numpy as np
import pandas as pd

from dreamml.logging import get_logger
from dreamml.logging.monitoring import DataTransformedLogData
from pandas.core.dtypes.common import is_datetime64_any_dtype
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin

from dreamml.pipeline.fitter.utils import choose_validation_type_by_data_size
from dreamml.utils.errors import ConfigurationError
from dreamml.utils.temporary_directory import TempDirectory
from dreamml.utils.warnings import DMLWarning
from dreamml.utils import ValidationType
from dreamml.data import DataSet, AMTSDataset
from dreamml.data.store import get_input
from dreamml.data.exceptions import ZeroDataFrameException, ColumnDoesntExist
from dreamml.data._enums import FrequencyEnums
from dreamml.configs.config_storage import ConfigStorage
from dreamml.utils.encode_categorical import encode_categorical
from dreamml.utils.encode_text import encode_text
from dreamml.utils.splitter import DataSplitter
from dreamml.features.feature_extraction._base import drop_features
from dreamml.data._hadoop import create_spark_session, stop_spark_session
from dreamml.features.feature_enrichment import TimeSeriesEnrichment
from dreamml.features.feature_enrichment.timeseries_transforms import (
    RusHolidayTransform,
)

_logger = get_logger(__name__)


class DataTransformer(BaseEstimator, TransformerMixin):
    """Transformer for input data in the dreamml_base training pipeline.

    The pipeline reads and processes data for model training and testing
    (Out-Of-Time selection). It performs splitting of the training set into
    train-valid-test parts, selection of a subset for PSI analysis, removal of
    garbage features, and processing of categorical features.

    Args:
        config (ConfigStorage): Global dreamml_base configuration file.
        spark_config (pyspark.conf.SparkConf, optional): Spark session configuration.
            Defaults to None. If not provided, a session with spark.driver.maxResultSize=32g
            and spark.executor.memory=16g is used.
        seed (int, optional): Random seed for reproducibility. Defaults to 27.

    Attributes:
        config (ConfigStorage): Configuration storage.
        spark_config: Spark configuration.
        seed (int): Random seed.
        cat_transformer: Transformer for categorical features.
        text_transformer: Transformer for text features.
        log_target: Target for logging.
        target_name (str): Name of the target column.
        task (str): Type of the pipeline task.
        subtask (str): Subtask of the pipeline task.
        shuffle (bool): Whether to shuffle the data.
        text_augs: Text augmentations.
        aug_p: Augmentation probability.
        _custom_data_split (bool): Indicates if custom data split is used.
        etna_artifacts (dict): Artifacts for ETNA.
        train_indexes_before_augmentations: Train indexes before augmentations.
    """

    def __init__(
        self, config: ConfigStorage, spark_config=None, seed: int = 27
    ) -> None:
        """
        Initializes the DataTransformer.

        Args:
            config (ConfigStorage): Global dreamml_base configuration file.
            spark_config (pyspark.conf.SparkConf, optional): Spark session configuration.
                Defaults to None.
            seed (int, optional): Random seed for reproducibility. Defaults to 27.
        """
        self.config = config
        self.spark_config = spark_config
        self.seed = seed
        self.cat_transformer = None
        self.text_transformer = None
        self.log_target = config.pipeline.preprocessing.log_target
        self.target_name = config.data.columns.target_name
        self.task = config.pipeline.task
        self.subtask = config.pipeline.subtask
        self.shuffle = config.data.splitting.shuffle
        self.text_augs = config.data.augmentation.text_augmentations
        self.aug_p = config.data.augmentation.aug_p
        self._custom_data_split = self.config.data.dev_path is None
        self._check_dev_train_val_test_path()
        self.etna_artifacts = {}
        self.train_indexes_before_augmentations = None

    def _is_spark_needed(self) -> bool:
        """Determines whether Spark is required based on data paths.

        Returns:
            bool: True if Spark is needed, False otherwise.
        """
        local_file_types = ["csv", "pkl", "pickle", "parquet", "xlsx"]

        data_paths = [
            self.config.data.dev_path,
            self.config.data.oot_path,
            self.config.data.train_path,
            self.config.data.valid_path,
            self.config.data.test_path,
            self.config.pipeline.task_specific.time_series.path_to_exog_data,
        ]

        for path in data_paths:
            if path is None:
                continue

            data_ext = Path(path).suffix[1:]
            if data_ext not in local_file_types:
                return True

        return False

    def _get_data(self) -> Dict[str, pd.DataFrame]:
        """Retrieves and processes the data based on configuration.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing processed data splits.

        Raises:
            ZeroDataFrameException: If any of the data splits are empty.
            Exception: If validation type requirements are not met.
        """
        data_dict = {}

        if self._is_spark_needed():
            temp_dir = TempDirectory(path=self.config.data.spark.temp_dir_path)
            spark = create_spark_session(
                spark_config=self.spark_config, temp_dir=temp_dir
            )
        else:
            temp_dir = None
            spark = None

        if self._custom_data_split:
            df_train = self._get_train_data(spark)
            data_dict["train"] = df_train
            self._calculate_time_frequency(data_dict["train"])

            df_test = self._get_test_data(spark)
            data_dict["test"] = df_test

            df_valid = self._get_valid_data(spark)

            if not df_valid.empty:
                data_dict["valid"] = df_valid
            else:
                validation_type = self._get_validation_type(data_dict)
                self._check_validation_type(validation_type, data_dict)
        else:
            data_dict["dev"] = self._get_dev_data(spark)
            self._calculate_time_frequency(data_dict["dev"])

        if self.config.data.oot_path:
            data_dict["oot"] = self._get_oot_data(spark)

        if self.config.pipeline.task == "timeseries":
            if (
                self.config.pipeline.task_specific.time_series.path_to_exog_data
                is not None
            ):
                data_dict["exog"] = self._get_exog_data(spark)

            data_dict = self._rename_timeseries_dataset(data_dict)
            data_dict = self._check_group_column(data_dict)

            self.config.data.columns.time_column = "timestamp"
            self.config.data.columns.group_column = "segment"
            self.config.data.columns.target_name = "target"

        for key, df in data_dict.items():
            if len(df) == 0:
                _logger.exception(f"Input data with {key=} is empty.")
                raise ZeroDataFrameException()

        if spark is not None:
            stop_spark_session(spark=spark, temp_dir=temp_dir)

        self.config.check_data(data_dict)

        return data_dict

    def _rename_timeseries_dataset(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Renames columns in the datasets to comply with ETNA requirements.

        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of data splits.

        Returns:
            Dict[str, pd.DataFrame]: Updated data dictionary with renamed columns.
        """
        self.etna_artifacts["original_columns"] = {
            "timestamp": self.config.data.columns.time_column,
            "target": self.config.data.columns.target_name,
            "segment": self.config.data.columns.group_column,
        }

        etna_required_columns = ["timestamp", "target", "segment"]
        original_columns = [
            self.config.data.columns.time_column,
            self.config.data.columns.target_name,
            self.config.data.columns.group_column,
        ]

        for sample_name, sample in data_dict.items():
            for original_column, etna_column in zip(
                original_columns, etna_required_columns
            ):
                if original_column is not None and original_column in sample.columns:
                    sample.rename({original_column: etna_column}, axis=1, inplace=True)
                    data_dict[sample_name] = sample
        return data_dict

    def _check_group_column(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Checks and ensures the presence of a group column in the datasets.

        If the group column is not specified and multiple time series are detected,
        it raises an error. Otherwise, it adds a default 'segment' column.

        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of data splits.

        Returns:
            Dict[str, pd.DataFrame]: Updated data dictionary with group columns.

        Raises:
            ValueError: If multiple time series are detected without a group column.
        """
        for sample_name, sample in data_dict.items():
            if (
                sample["timestamp"].nunique() != len(sample)
                and self.config.data.columns.group_column is None
            ):
                raise ValueError(
                    "The dataset contains duplicate timestamps, indicating multiple time series.\n"
                    'Specify a group column in the config parameter "group_column".'
                )
            elif (
                sample["timestamp"].nunique() == len(sample)
                and self.config.data.columns.group_column is None
            ):
                sample["segment"] = "main"

            data_dict[sample_name] = sample
        return data_dict

    def _get_dev_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the development (dev) dataset.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: Development dataset.
        """
        df, _ = get_input(data_path="dev_data_path", config=self.config, spark=spark)

        return df

    def _get_oot_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the Out-Of-Time (OOT) dataset.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: OOT dataset.
        """
        df, _ = get_input(data_path="oot_data_path", config=self.config, spark=spark)

        return df

    def _get_exog_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the exogenous (exog) dataset for time series tasks.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: Exogenous dataset.
        """
        df, _ = get_input(
            data_path="path_to_exog_data", config=self.config, spark=spark
        )

        return df

    def _get_train_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the training dataset.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: Training dataset.
        """
        df, _ = get_input(data_path="train_data_path", config=self.config, spark=spark)

        return df

    def _get_valid_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the validation dataset.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: Validation dataset or empty DataFrame if not provided.
        """
        if not self.config.data.valid_path:
            df = pd.DataFrame()
        else:
            df, _ = get_input(
                data_path="valid_data_path", config=self.config, spark=spark
            )

        return df

    def _get_test_data(self, spark=None) -> pd.DataFrame:
        """Retrieves the test dataset.

        Args:
            spark: Spark session if needed.

        Returns:
            pd.DataFrame: Test dataset.
        """
        df, _ = get_input(data_path="test_data_path", config=self.config, spark=spark)

        return df

    def _get_validation_type(self, data_dict) -> ValidationType:
        """Determines the validation type based on configuration and data size.

        Args:
            data_dict: Dictionary of data splits.

        Returns:
            ValidationType: The chosen validation type.
        """
        validation = self.config.pipeline.validation_type

        if validation == "auto":
            assert "valid" not in data_dict
            data_size = data_dict["train"].shape[0] + data_dict["test"].shape[0]

            return choose_validation_type_by_data_size(data_size)
        else:
            return ValidationType(validation)

    def _check_validation_type(self, validation_type: ValidationType, data_dict):
        """Validates the selected validation type against the data splits.

        Args:
            validation_type (ValidationType): The selected validation type.
            data_dict: Dictionary of data splits.

        Raises:
            Exception: If hold-out validation is selected without a validation split.
            ValueError: If an unsupported validation type is selected.
        """
        if validation_type == ValidationType.HOLDOUT:
            msg = (
                "Validation type is set to hold-out. "
                "A separate validation split is required. Specify the path in data.valid_path."
            )
            raise Exception(msg)
        elif validation_type == ValidationType.CV:
            data_dict["train"], data_dict["valid"] = train_test_split(
                data_dict["train"], test_size=0.2, shuffle=False
            )
        else:
            raise ValueError(
                f"Can't transform data with validation type = {validation_type.value}."
            )

    def _split_oot_from_dev(self, data_dict: Dict[str, pd.DataFrame]):
        """Splits the Out-Of-Time (OOT) data from the development dataset.

        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of data splits.
        """
        split_column = self.config.data.columns.time_column

        if self._custom_data_split:
            split_values = pd.concat(
                [data_dict.get(key)[split_column] for key in ["train", "valid", "test"]]
            ).unique()
        else:
            split_values = data_dict["dev"][split_column].unique()
        self.config.data.splitting.oot_split_n_values = (
            self.config.pipeline.task_specific.time_series.horizon
            if self.task == "timeseries"
            else self.config.data.splitting.oot_split_n_values
        )
        last_n_values = sorted(split_values)[
            -self.config.data.splitting.oot_split_n_values :
        ]

        oot_parts = []
        for key, df in data_dict.items():
            if key in ["dev", "train", "valid", "test"]:
                mask = df[split_column].isin(last_n_values)

                oot_parts.append(df[mask])
                data_dict[key] = df[~mask].reset_index(drop=True)

        data_dict["oot"] = pd.concat(oot_parts, ignore_index=True)

    @staticmethod
    def _merge_train_valid_test(data_dict: Dict[str, pd.DataFrame]):
        """Merges the train, valid, and test datasets into the development dataset.

        Args:
            data_dict (Dict[str, pd.DataFrame]): Dictionary of data splits.
        """
        merged_data = pd.concat(
            [data_dict.get(key) for key in ["train", "valid", "test"]],
            ignore_index=True,
        )

        data_dict["dev"] = merged_data

    def _get_train_valid_test_indexes(self, data_dict) -> Tuple[pd.Index, ...]:
        """Obtains the indexes for train, valid, and test splits.

        Args:
            data_dict: Dictionary of data splits.

        Returns:
            Tuple[pd.Index, ...]: Tuple containing indexes for train, valid, and test.
        """
        if self._custom_data_split:
            dev_indexes = data_dict["dev"].index
            valid_start = len(data_dict["train"])
            valid_end = valid_start + len(data_dict.get("valid", []))

            indexes = (
                dev_indexes[:valid_start],
                dev_indexes[valid_start:valid_end],
                dev_indexes[valid_end:],
            )
        else:
            splitter = DataSplitter(
                split_fractions=self.config.data.splitting.split_params,
                shuffle=self.shuffle,
                group_column=self.config.data.columns.group_column,
                target_name=self.config.data.columns.target_name,
                stratify=self.config.data.splitting.stratify,
                task=self.task,
                time_column=self.config.data.columns.time_column,
                split_by_group=self.config.data.splitting.split_by_group,
            )
            indexes = splitter.transform(data_dict["dev"])

        return indexes

    def _check_dev_train_val_test_path(self):
        """Checks for conflicts in data paths within the configuration.

        Raises:
            Exception: If there are conflicts or missing required paths based on the data split strategy.
        """
        if self._custom_data_split:
            if not (self.config.data.train_path and self.config.data.test_path):
                msg = (
                    "When data.dev_path is not provided, "
                    "data.train_path and data.test_path must be specified."
                )
                raise Exception(msg)
        else:
            if (
                self.config.data.train_path
                or self.config.data.valid_path
                or self.config.data.test_path
            ):
                msg = (
                    "When data.dev_path is provided, "
                    "data.train_path, data.valid_path, and data.test_path must be empty."
                )
                raise Exception(msg)

    def _check_feature_names(self, data: Dict[str, Tuple[pd.DataFrame, pd.Series]]):
        """Validates the feature names for compatibility with LightGBM and WhiteBox AutoML.

        Removes models from the training pipeline if feature names contain invalid characters.

        Args:
            data (Dict[str, Tuple[pd.DataFrame, pd.Series]]): Dictionary with training data.

        Raises:
            None
        """
        features_names = data["train"][0].columns
        invalid_column_list = []
        # List of unsupported characters
        for col in features_names:
            if re.search(r'[",:\[\]{}]', col):
                invalid_column_list.append(col)

        if invalid_column_list:
            if "lightgbm" in self.config.pipeline.model_list:
                self.config.pipeline.model_list.remove("lightgbm")
                warnings.warn(
                    "LightGBM model removed from the training list due to invalid feature names. "
                    'Invalid characters detected: ",:[]{}',
                    DMLWarning,
                    stacklevel=2,
                )
            if self.config.pipeline.alt_mode.use_whitebox_automl:
                self.config.pipeline.alt_mode.use_whitebox_automl = False
                warnings.warn(
                    "WhiteBox AutoML removed from the training list due to invalid feature names. "
                    'Invalid characters detected: ",:[]{}',
                    DMLWarning,
                    stacklevel=2,
                )
            warnings.warn(
                f"Features with invalid names: {invalid_column_list}",
                DMLWarning,
                stacklevel=2,
            )

    def _check_model_availability(self):
        """Ensures that there are models available for training.

        Raises:
            Exception: If no models are available for training.
        """
        msg = "No models available for training!"
        if (
            not self.config.pipeline.model_list
            and not self.config.pipeline.alt_mode.use_whitebox_automl
        ):
            raise Exception(msg)

    def _transform_time_column_to_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms the time column to datetime format.

        Args:
            df (pd.DataFrame): DataFrame containing the time column.

        Returns:
            pd.DataFrame: DataFrame with the transformed time column.

        Raises:
            Exception: If the time column is missing.
            ValueError: If the time format is incorrect or conversion fails.
        """
        if self.config.data.columns.time_column not in df.columns:
            raise Exception(
                f"Column {self.config.data.columns.time_column} is missing in the DataFrame."
            )

        if is_datetime64_any_dtype(df[self.config.data.columns.time_column].dtype):
            df = self._remove_timezone(df)
            return df

        try:
            df[self.config.data.columns.time_column] = pd.to_datetime(
                df[self.config.data.columns.time_column],
                format=self.config.data.columns.time_column_format,
                utc=True,
            )
            df = self._remove_timezone(df)
        except ValueError as e:
            raise ValueError(
                f"Incorrect date format or the column does not contain dates. {e}"
            )
        return df

    def _remove_timezone(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes timezone information from the time column if present.

        Args:
            df (pd.DataFrame): DataFrame containing the time column.

        Returns:
            pd.DataFrame: DataFrame with timezone information removed.
        """
        if df[self.config.data.columns.time_column].dt.tz:
            df[self.config.data.columns.time_column] = df[
                self.config.data.columns.time_column
            ].dt.tz_localize(None)
        return df

    def _add_segment_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds a default 'segment' column to the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to which the segment column will be added.

        Returns:
            pd.DataFrame: Updated DataFrame with the segment column.
        """
        self.config.data.columns.group_column = "segment"
        df[self.config.data.columns.group_column] = 1
        return df

    def transform(self) -> DataSet:
        """Executes the full pipeline for data retrieval and processing.

        Returns:
            DataSet: An object containing the training data and related information.

        Raises:
            Various exceptions based on internal method validations.
        """
        np.random.seed(self.seed)

        data_dict = self._get_data()
        start_time = time.time()

        if self._custom_data_split:
            self._merge_train_valid_test(data_dict)

        if self.task == "timeseries":
            timeseries_feature_enrichment = TimeSeriesEnrichment(
                data_dict, self.config, self.cat_transformer
            )
            timeseries_feature_enrichment.transform()
            data_dict = timeseries_feature_enrichment.return_data_dict()
            etna_artifacts = data_dict.pop("etna_artifacts")
            self.etna_artifacts.update(etna_artifacts)

        dev_data = data_dict["dev"]
        oot_data = data_dict.get("oot")

        if (
            self.task in ["amts", "amts_ad"]
            and self.config.pipeline.task_specific.time_series.time_column_frequency
            == FrequencyEnums.DAYS
        ):
            holiday_transform_atms = RusHolidayTransform(
                in_column=self.config.data.columns.time_column
            )
            if not self.config.data.splitting.split_by_group:
                dev_data = self._add_segment_column(dev_data)
            added_features, dev_data = holiday_transform_atms.transform(data=dev_data)

        if (
            data_dict.get("oot") is None
            and self.config.data.columns.time_column is not None
            and self.config.data.oot_path is not None
        ):
            self._split_oot_from_dev(data_dict)
            dev_data = data_dict["dev"]
            oot_data = data_dict["oot"]

        indexes = self._get_train_valid_test_indexes(data_dict)
        self.train_indexes_before_augmentations = indexes[0]
        del data_dict

        # Apply transformations to the data
        dev_data, oot_data, self.cat_transformer = self.encode_categorical_compat(
            dev_data, oot_data, indexes
        )
        self.config.data.columns.categorical_features = (
            self.cat_transformer.cat_features
        )

        if self.subtask == "nlp":
            (
                dev_data,
                oot_data,
                indexes,
                self.config.data.columns.text_features_preprocessed,
                self.text_transformer,
            ) = encode_text(self.config, dev_data, oot_data, indexes)

        if self.config.data.columns.time_column is not None:
            dev_data = self._transform_time_column_to_datetime(dev_data)
            if oot_data is not None:
                oot_data = self._transform_time_column_to_datetime(oot_data)

        if self.config.pipeline.task == "amts":
            self.config.data.columns.categorical_features = [
                features
                for features in self.config.data.columns.categorical_features
                if features != self.config.data.columns.time_column
            ]

        if self.config.pipeline.task in ("amts", "amts_ad"):
            dataset = AMTSDataset(
                dev_data,
                oot_data,
                self.config,
                indexes,
                self.config.data.columns.categorical_features,
                self.config.data.columns.text_features,
                self.config.data.columns.text_features_preprocessed,
                self.text_transformer,
            )
        else:
            dataset = DataSet(
                dev_data,
                oot_data,
                self.config,
                indexes,
                self.config.data.columns.categorical_features,
                self.config.data.columns.text_features,
                self.config.data.columns.text_features_preprocessed,
                self.text_transformer,
            )
        dataset.etna_artifacts = self.etna_artifacts
        dataset.train_indexes_before_augmentations = (
            self.train_indexes_before_augmentations
        )

        if self.task == "binary":
            self.config.pipeline.metric_params["labels"] = [0, 1]
        elif self.task == "multiclass":
            self.config.pipeline.metric_params["labels"] = (
                self.cat_transformer.encoders[self.target_name].encoder.classes_
            )
        else:
            self.config.pipeline.metric_params["labels"] = None

        data = dataset.get_eval_set(drop_service_fields=False)

        if self.task not in ["amts", "amts_ad"]:
            self._check_feature_names(data)
            self._check_nan_values_and_zero_columns(data)

        self._check_model_availability()

        # Logging
        elapsed_time = time.time() - start_time
        _logger.monitor(
            f"Data transformed in {elapsed_time:.1f} seconds.",
            extra={
                "log_data": DataTransformedLogData(
                    name="dev_data",
                    length=len(dev_data),
                    features_num=dev_data.shape[1],
                    nan_count=dev_data.isna().sum().sum(),
                    elapsed_time=elapsed_time,
                )
            },
        )

        if self.config.data.columns.categorical_features:
            _logger.debug(
                f"Categorical features: {self.config.data.columns.categorical_features}"
            )

        if self.subtask == "nlp":
            _logger.debug(f"Text features: {self.config.data.columns.text_features}")
            _logger.debug(
                f"Text features preprocessed: {self.config.data.columns.text_features_preprocessed}"
            )

        return dataset

    def _check_nan_values_and_zero_columns(self, data: dict):
        """Checks for NaN values and entirely zero columns in the target.

        Args:
            data (dict): Dictionary containing the evaluation set.

        Raises:
            ValueError: If NaN values or zero columns are found in the target.
        """
        if (
            self.task == "multilabel"
            and self.config.pipeline.task_specific.multilabel.target_with_nan_values
            is False
        ):
            for sample_name, sample in data.items():
                df_targets = sample[1]

                nan_columns = df_targets.columns[df_targets.isna().any()].tolist()
                if nan_columns:
                    raise ValueError(
                        f"Target contains NaN values in sample '{sample_name}' in columns: {', '.join(nan_columns)}.\n"
                        f"Set config option 'pipeline.task_specific.multilabel.target_with_nan_values = True' or handle NaN values in targets."
                    )

                zero_columns = df_targets.columns[(df_targets == 0).all()].tolist()
                if zero_columns:
                    raise ValueError(
                        f"Target contains columns with all zeros in sample '{sample_name}'"
                        f" in columns: {', '.join(zero_columns)}.\n"
                        f"The number of classes must be greater than 1. Please handle all-zero columns in targets."
                    )

    def get_compat_dataframes(
        self, dev_data: pd.DataFrame, oot_data: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], dict]:
        """Ensures backward compatibility with dreamml_base versions before 2.0.

        Prepares dataframes for encoding categorical features without drop_features.

        Args:
            dev_data (pd.DataFrame): Development dataset.
            oot_data (Optional[pd.DataFrame]): Out-Of-Time dataset.

        Returns:
            Tuple[pd.DataFrame, Optional[pd.DataFrame], dict]: Compatible development and OOT datasets, and dropped data.
        """
        compat_set = {}
        target_name = self.config.data.columns.target_name

        compat_set["dev"] = (
            (dev_data, dev_data[target_name])
            if target_name
            else (dev_data, target_name)
        )
        if isinstance(oot_data, pd.DataFrame):
            compat_set["oot"] = (
                (oot_data, oot_data[target_name])
                if target_name
                else (oot_data, target_name)
            )

        compat_conf = {
            "task": self.config.pipeline.task,
            "drop_features": self.config.data.columns.drop_features,
            "target_name": self.config.data.columns.target_name,
            "multitarget": [],
            "time_column": self.config.data.columns.time_column,
            "oot_data_path": self.config.data.oot_path,
            "never_used_features": self.config.data.columns.never_used_features,
        }
        compat_set, dropped_data = drop_features(compat_conf, compat_set)

        if self.config.data.columns.target_name is None:
            compat_dev_data = compat_set["dev"][0]
        else:
            compat_dev_data = compat_set["dev"][0].join(compat_set["dev"][1])

        if compat_set.get("oot"):
            if self.config.data.columns.target_name is None:
                compat_oot_data = compat_set["oot"][0]
            else:
                compat_oot_data = compat_set["oot"][0].join(compat_set["oot"][1])
            return (
                compat_dev_data,
                compat_oot_data,
                dropped_data,
            )
        return compat_dev_data, None, dropped_data

    def encode_categorical_compat(self, dev_data, oot_data, indexes) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[TransformerMixin]]:
        """Encodes categorical features with compatibility adjustments.

        Args:
            dev_data (pd.DataFrame): Development dataset.
            oot_data (Optional[pd.DataFrame]): Out-Of-Time dataset.
            indexes: Indexes for splitting.

        Returns:
            Tuple[pd.DataFrame, Optional[pd.DataFrame], TransformerMixin]: Encoded development and OOT datasets, and the transformer.
        """
        compat_dev_data, compat_oot_data, dropped_data = self.get_compat_dataframes(
            dev_data, oot_data
        )

        dev_data, oot_data, transformer = encode_categorical(
            self.config, compat_dev_data, compat_oot_data, indexes
        )

        if dropped_data:
            dev_data = dev_data.join(dropped_data["dev"])
            if isinstance(oot_data, pd.DataFrame):
                oot_data = oot_data.join(dropped_data["oot"])

        return dev_data, oot_data, transformer

    def _calculate_time_frequency(self, data: pd.DataFrame):
        """Calculates and sets the time column frequency based on the data.

        Args:
            data (pd.DataFrame): Dataset for which to calculate frequency.
        """
        if self.task not in ("amts", "amts_ad"):
            return

        if self.config.data.splitting.split_by_group:
            try:
                group = data[self.config.data.columns.group_column][0]
            except Exception as e:
                raise ColumnDoesntExist(
                    column_name=self.config.data.columns.group_column, data=data
                )
            df = data[data[self.config.data.columns.group_column] == group]
            data = df

        try:
            time_column: pd.Series = pd.to_datetime(
                data[self.config.data.columns.time_column]
            )
        except Exception as e:
            raise ColumnDoesntExist(
                column_name=self.config.data.columns.time_column, data=data
            )

        diff = time_column.diff().dropna()
        most_common_freq = diff.mode()[0]

        seconds = most_common_freq.total_seconds()
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        months, days = divmod(days, 5)

        components = {
            FrequencyEnums.SECONDS: int(seconds),
            FrequencyEnums.MINUTES: int(minutes),
            FrequencyEnums.HOURS: int(hours),
            FrequencyEnums.DAYS: int(days),
            FrequencyEnums.MONTHS: int(months),
        }

        for unit, value in components.items():
            if value > 0:
                try:
                    self.config.models.prophet.params["time_column_frequency"] = unit
                except Exception:
                    pass
                try:
                    self.config.models.nbeats_revin.params["time_column_frequency"] = (
                        unit
                    )
                except Exception:
                    pass
                self.config.pipeline.task_specific.time_series.time_column_frequency = (
                    unit
                )
                self.config.models.nbeats_revin.params["time_column_frequency"] = unit
                self.config.models.prophet.params["time_column_frequency"] = unit
        return
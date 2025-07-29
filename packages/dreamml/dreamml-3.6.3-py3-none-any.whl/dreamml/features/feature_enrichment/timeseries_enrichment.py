"""
Модуль с реализацией feature enrichment for timeseries
"""

from copy import deepcopy
from typing import Optional, List, Dict
import pandas as pd

from etna.datasets import TSDataset
from etna.transforms import HolidayTransform, LabelEncoderTransform

from dreamml.configs.config_storage import ConfigStorage
from dreamml.features.categorical import CategoricalFeaturesTransformer
from dreamml.features.feature_enrichment.timeseries_transforms import (
    RusHolidayTransform,
)
from dreamml.logging import get_logger


_logger = get_logger(__name__)

DML_TRANSFORMS = [RusHolidayTransform]
ETNA_FORBIDDEN_TRANSFORMS = [
    HolidayTransform
]  # PicklingError when using "Holiday" library


def split_dml_transforms(transforms: List):
    """Splits the provided transforms into ETNA and DML transforms.

    Args:
        transforms (List): A list of transform instances.

    Returns:
        Tuple[List, List]: A tuple containing two lists - ETNA transforms and DML transforms.
    """
    etna_transforms = [
        transform
        for transform in transforms
        if not isinstance(transform, tuple(DML_TRANSFORMS))
        and not isinstance(transform, tuple(ETNA_FORBIDDEN_TRANSFORMS))
    ]
    dml_transforms = [
        transform
        for transform in transforms
        if isinstance(transform, tuple(DML_TRANSFORMS))
    ]
    return etna_transforms, dml_transforms


def get_time_column_frequency(time_column_period: str):
    """Determines the pandas frequency string based on the provided time column period.

    Args:
        time_column_period (str): The period of the time column (e.g., 'day', 'W', 'M').

    Returns:
        str: The corresponding pandas frequency string.

    Raises:
        None: This function logs a debug message if the frequency is non-standard.
    """
    if time_column_period in ["day", "D"]:
        info = "calendar day frequency"
        freq = "D"
    elif time_column_period in ["week", "W"]:
        info = "weekly frequency"
        freq = "W"
    elif time_column_period in ["month", "M"]:
        info = "monthly frequency"
        freq = "M"
    elif time_column_period in ["quarter", "Q"]:
        info = "quarterly frequency"
        freq = "Q"
    elif time_column_period in ["quarter_start", "QS"]:
        info = "quarter-start frequency"
        freq = "QS"
    elif time_column_period in ["month_start", "MS"]:
        info = "month-start frequency"
        freq = "MS"
    elif time_column_period in ["semi_month", "SM"]:
        info = "semi-month frequency (15th of months)"
        freq = "SM"
    elif time_column_period in ["semi_month_start", "SMS"]:
        info = "semi-month start frequency (15th and start of months)"
        freq = "SMS"
    elif time_column_period in ["year", "Y"]:
        info = "yearly frequency"
        freq = "Y"
    elif time_column_period in ["year_end", "YE"]:
        info = "year-end frequency"
        freq = "YE"
    elif time_column_period in ["year_start", "YS"]:
        info = "year-start frequency"
        freq = "YS"
    elif time_column_period in ["hour", "h"]:
        info = "hourly frequency"
        freq = "H"
    elif time_column_period in ["min", "m", "T"]:
        info = "minutely frequency"
        freq = "min"
    elif time_column_period in ["sec", "s"]:
        info = "secondly frequency"
        freq = "S"
    elif time_column_period in ["millisec", "ms"]:
        info = "milliseconds"
        freq = "ms"
    elif time_column_period in ["microsec", "us"]:
        info = "microseconds"
        freq = "us"
    elif time_column_period in ["nanosec", "ns", "N"]:
        info = "nanoseconds"
        freq = "N"
    # elif time_column_period in ["month_end", "ME"]:  # pandas >= 2.*
    #     info = "month-end frequency"
    #     freq = "ME"
    # elif time_column_period in ["semi_month_end", "SME"]:  # pandas >= 2.*
    #     info = "semi-month end frequency (15th and end of months)"
    #     freq = "SME"
    else:
        info = "nonstandard frequency"
        freq = time_column_period
        debug_msg = f"Частота временного столбца: {freq} не из списка стандартных."
        _logger.debug(debug_msg)

    info_msg = f"Time column frequency: {freq} ({info})."
    _logger.info(info_msg)
    return freq


class TimeSeriesEnrichment:
    """Handles the enrichment of dreamml_base input data with features from configuration parameters.

    This class processes the input data dictionaries, applies ETNA and DML transformations,
    and prepares the data for subsequent time series analysis.

    Attributes:
        config (ConfigStorage): Configuration storage containing pipeline and data settings.
        data_dict (dict): Dictionary containing different data splits (e.g., 'dev', 'oot').
        transformer (Optional[CategoricalFeaturesTransformer]): Transformer for categorical features.
        etna_required_columns (List[str]): Required columns for ETNA transformations.
        drop_features (List[str]): List of feature columns to drop.
        etna_transforms (List): List of ETNA transform instances.
        dml_transforms (List): List of DML transform instances.
        frequency (str): Frequency of the time column.
        known_future (Any): Configuration for known future values in the pipeline.
        horizon (int): Forecast horizon.
        use_etna (bool): Flag indicating whether to use ETNA transformations.
        dev_data (Optional[pd.DataFrame]): Development data after preprocessing.
        dev_ts (Optional[TSDataset]): Development time series dataset.
        exog_data (Optional[pd.DataFrame]): Exogenous data.
    """

    def __init__(
        self,
        data_dict: dict,
        config: ConfigStorage,
        transformer: Optional[CategoricalFeaturesTransformer] = None,
    ):
        """
        Initializes the TimeSeriesEnrichment instance with data and configuration.

        Args:
            data_dict (dict): Dictionary containing different data splits (e.g., 'dev', 'oot').
            config (ConfigStorage): Configuration storage containing pipeline and data settings.
            transformer (Optional[CategoricalFeaturesTransformer], optional): 
                Transformer for categorical features. Defaults to None.
        """
        self.config = config
        self.data_dict = data_dict
        self.transformer = transformer
        self.etna_required_columns = ["target", "segment", "timestamp"]
        self.drop_features = config.data.columns.drop_features
        self.etna_transforms, self.dml_transforms = split_dml_transforms(
            config.pipeline.task_specific.time_series.ts_transforms
        )
        self.config.pipeline.task_specific.time_series.ts_transforms = (
            self.dml_transforms
        )
        self.frequency = get_time_column_frequency(
            config.data.columns.time_column_period
        )
        self.known_future = self.config.pipeline.task_specific.time_series.known_future
        self.horizon = config.pipeline.task_specific.time_series.horizon
        self.use_etna = self.config.pipeline.alt_mode.use_etna
        self.dev_data, self.dev_ts, self.exog_data = None, None, None

    def preprocessing_data(self):
        """Preprocesses the input data by transforming and validating datasets.

        Returns:
            Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]: 
                A tuple containing the preprocessed development data and exogenous data.
                
        Raises:
            None
        """
        preprocess = PreprocessDataset(self.data_dict, self.config)
        preprocess.transform()
        return preprocess.dev_data, preprocess.exog_data

    def transform(self):
        """Executes the pipeline to enrich data with additional features.

        Processes the development data through ETNA and DML transformations.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        dev_data, self.exog_data = self.preprocessing_data()
        dev_data, self.dev_ts = self._etna_feature_transform(dev_data)
        self.dev_data = self._dml_feature_transform(dev_data)

    def _etna_feature_transform(self, data: pd.DataFrame):
        """Enriches the data with ETNA transformations.

        Converts the input DataFrame to a TSDataset, applies ETNA transformations,
        and converts it back to a DataFrame.

        Args:
            data (pd.DataFrame): The input development data.

        Returns:
            Tuple[pd.DataFrame, TSDataset]: 
                A tuple containing the transformed development data and the TSDataset.

        Raises:
            None
        """
        dev_ts: TSDataset = self._transform_to_ts_dataset(
            deepcopy(data).drop(columns=self.drop_features, axis=1)
        )
        dev_data: TSDataset = self._transform_to_ts_dataset(data)
        dev_data.fit_transform(transforms=self.etna_transforms)
        dev_data: pd.DataFrame = dev_data.to_pandas(True)
        return dev_data, dev_ts

    def _dml_feature_transform(self, data: pd.DataFrame):
        """Enriches the data with DML transformations.

        Applies each DML transform to the data sequentially.

        Args:
            data (pd.DataFrame): The input data after ETNA transformations.

        Returns:
            pd.DataFrame: The data enriched with DML features.

        Raises:
            None
        """
        if len(self.dml_transforms) > 0:
            for transform in self.dml_transforms:
                _, data = transform.transform(data)
        return data

    def _transform_to_ts_dataset(self, data: pd.DataFrame):
        """Converts a pandas DataFrame to a TSDataset object.

        Includes exogenous data if available.

        Args:
            data (pd.DataFrame): The input DataFrame to convert.

        Returns:
            TSDataset: The resulting time series dataset.

        Raises:
            None
        """
        ts_data = TSDataset.to_dataset(data)

        if self.exog_data is not None:
            regressor_ts = TSDataset.to_dataset(self.exog_data)
            ts_dataset = TSDataset(
                df=ts_data,
                freq=self.frequency,
                df_exog=regressor_ts,
                known_future=self.known_future,
            )
        else:
            ts_dataset = TSDataset(df=ts_data, freq=self.frequency)
        return ts_dataset

    def return_data_dict(self):
        """Finalizes and returns the enriched data dictionaries.

        Constructs dictionaries containing the enriched development data and ETNA artifacts.

        Args:
            None

        Returns:
            dict: A dictionary with keys 'dev' and 'etna_artifacts' containing the enriched data.

        Raises:
            None
        """
        etna_artifacts = {
            "dev_ts": self.dev_ts,
            "etna_transforms": self.etna_transforms,
        }
        data_dict = {
            "dev": self.dev_data,
            "etna_artifacts": etna_artifacts,
        }
        return data_dict


class PreprocessDataset:
    """Prepares datasets for ETNA compatibility and validates them for time series tasks.

    This class handles the concatenation of development and out-of-time (OOT) data,
    checks the integrity of exogenous data, and processes categorical columns.

    Attributes:
        config (ConfigStorage): Configuration storage containing pipeline and data settings.
        horizon (int): Forecast horizon.
        dev_data (pd.DataFrame): Development data.
        oot_data (Optional[pd.DataFrame]): Out-of-time data, if available.
        exog_data (Optional[pd.DataFrame]): Exogenous data, if available.
    """

    def __init__(self, data_dict: Dict[str, pd.DataFrame], config: ConfigStorage):
        """
        Initializes the PreprocessDataset instance with data and configuration.

        Args:
            data_dict (Dict[str, pd.DataFrame]): 
                Dictionary containing different data splits (e.g., 'dev', 'oot', 'exog').
            config (ConfigStorage): Configuration storage containing pipeline and data settings.
        """
        self.config = config
        self.horizon = config.pipeline.task_specific.time_series.horizon
        self.dev_data = data_dict["dev"]
        self.oot_data = data_dict["oot"] if "oot" in data_dict else None
        self.exog_data = data_dict["exog"] if "exog" in data_dict else None

    def transform(self):
        """Transforms and validates the datasets.

        Performs concatenation of development and OOT data,
        checks the exogenous data, and encodes categorical columns.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If validation checks fail.
        """
        # Объединяем dev_data и oot_data
        self.dev_data = self._concat_dev_oot_data(self.dev_data, self.oot_data)
        self.oot_data = None

        # Проверяем датасет с экзогенными данными
        if self.exog_data is not None:
            self._check_exog_data()

        # Обрабатываем категориальные столбцы
        self.transform_categorical_columns(self.dev_data)

    def _concat_dev_oot_data(
        self, dev_data: pd.DataFrame, oot_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Concatenates development and OOT data after validation.

        Validates the presence of required columns, ensures matching group counts,
        checks the size against the forecast horizon, and verifies non-overlapping dates.

        Args:
            dev_data (pd.DataFrame): Development data.
            oot_data (Optional[pd.DataFrame], optional): OOT data. Defaults to None.

        Returns:
            pd.DataFrame: Concatenated development and OOT data.

        Raises:
            ValueError: If required columns are missing, group counts don't match,
                        data sizes are incorrect, or dates overlap.
        """
        for etna_column in ["timestamp", "target", "segment"]:
            if etna_column not in dev_data or (
                oot_data is not None and etna_column not in oot_data
            ):
                raise ValueError(
                    "Для dev_data и oot_data обязательны столбцы 'timestamp', 'target' и 'segment'."
                )

        if oot_data is not None:
            if oot_data["segment"].nunique() != dev_data["segment"].nunique():
                raise ValueError(
                    "Количество групп в oot выборке должно равняться количеству групп в dev выборке."
                )

            min_required_len_per_group = self.horizon
            min_required_len_oot_data = (
                min_required_len_per_group * oot_data["segment"].nunique()
            )
            if len(oot_data) != min_required_len_oot_data:
                raise ValueError(
                    "Размер oot_data должен равняться горизонту предсказаний по всем группам."
                )

            dev_unique_dates = set(dev_data["timestamp"].unique().tolist())
            oot_unique_dates = set(oot_data["timestamp"].unique().tolist())
            if len(dev_unique_dates & oot_unique_dates) > 0:
                raise ValueError(
                    "Даты в oot_data не должны пересекаться с датами в dev_data."
                )

            dev_data = pd.concat([dev_data, oot_data], axis=0, ignore_index=True)
        return dev_data

    def _check_exog_data(self):
        """Validates the exogenous data for consistency and correctness.

        Ensures required columns are present, the target column is absent,
        there is appropriate temporal coverage, and there are no overlapping columns
        with the development data.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If validation checks fail.
        """
        for etna_column in ["timestamp", "segment"]:
            if etna_column not in self.exog_data.columns:
                raise ValueError(
                    "Для exog_data обязательны столбцы 'timestamp' и 'segment'."
                )

        if "target" in self.exog_data.columns:
            raise ValueError(
                "Целевой столбец не должен быть в датасете с экзогенными данными."
            )

        for column in self.exog_data.columns:
            if column in self.dev_data.columns and column not in [
                "timestamp",
                "target",
                "segment",
            ]:
                raise ValueError(
                    f"Столбец {column} присутствует в dev_data и exog_data."
                )

    def transform_categorical_columns(self, data: pd.DataFrame):
        """Encodes categorical features using label encoding.

        Identifies categorical columns and adds corresponding
        LabelEncoderTransform instances to the transformation pipeline.

        Args:
            data (pd.DataFrame): The input DataFrame with potential categorical columns.

        Returns:
            pd.DataFrame: The DataFrame with categorical columns processed.

        Raises:
            None
        """
        category_columns = data.select_dtypes(include=["category"]).columns.tolist()
        for column in set(category_columns):
            transform = LabelEncoderTransform(
                in_column=column, out_column="auto", return_type="numeric"
            )
            self.config.pipeline.task_specific.time_series.ts_transforms.extend(
                transform
            )
        return data
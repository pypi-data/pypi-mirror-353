import os
import pickle
import time
from typing import Union, Tuple, Optional

import pandas as pd
import pyspark
from pandas import DataFrame
from pyspark.sql import SparkSession

from dreamml.configs.config_storage import ConfigStorage
from dreamml.data._hadoop import (
    get_hadoop_input,
    get_hadoop_sql_input,
    get_hadoop_parquet_input,
)
from dreamml.logging import get_logger
from dreamml.logging.monitoring import DataLoadedLogData

_logger = get_logger(__name__)


def _compress_datatypes(X: pd.DataFrame) -> pd.DataFrame:
    """
    Compresses the data types in the input DataFrame to reduce memory usage.

    Integer columns with dtype int64 are converted to int32 if their values fit within the int32 range.
    Float columns with dtype float64 are converted to float32.

    Args:
        X (pd.DataFrame): The input DataFrame to compress.

    Returns:
        pd.DataFrame: The compressed DataFrame with reduced memory usage.

    Raises:
        None
    """
    usage_before = X.memory_usage(deep=True).sum()
    usage_before = round(usage_before / 1024 / 1024, 2)
    int64 = X.dtypes[X.dtypes == "int64"].index  # int32: (-2147483648; 2147483647)
    int64 = X[int64].max()[X[int64].max() <= 2147483647].index
    int64 = X[int64].min()[X[int64].min() >= -2147483648].index
    float64 = X.dtypes[X.dtypes == "float64"].index  # float32: (-3,4e+38; 3.4e+38)

    X[int64] = X[int64].astype("int32")
    X[float64] = X[float64].astype("float32")
    usage_after = X.memory_usage(deep=True).sum()
    usage_after = round(usage_after / 1024 / 1024, 2)

    _logger.info("Data is compressed to 32bit types.")
    _logger.debug(
        f"Memory usage before compression = {usage_before} Mb, after compression = {usage_after} Mb."
    )
    return X


def create_old_dict_compat(config: ConfigStorage) -> dict:
    """
    Creates a compatibility dictionary from a ConfigStorage object to maintain backward compatibility
    with older dreamml_base modules that do not use ConfigStorage.

    Args:
        config (ConfigStorage): The experiment configuration object.

    Returns:
        dict: A dictionary containing the experiment configurations.

    Raises:
        None
    """
    compat_config = {
        "dev_data_path": config.data.dev_path,
        "oot_data_path": config.data.oot_path,
        "train_data_path": config.data.train_path,
        "valid_data_path": config.data.valid_path,
        "test_data_path": config.data.test_path,
        "multitarget": [],
        "target_name": config.data.columns.target_name,
        "drop_features": config.data.columns.drop_features,
        "never_used_features": config.data.columns.never_used_features,
        "time_column": config.data.columns.time_column,
        "task": config.pipeline.task,
        "path_to_exog_data": config.pipeline.task_specific.time_series.path_to_exog_data,
        "use_compression": config.data.use_compression,
    }

    return compat_config


def get_input(
    spark: Optional[SparkSession], data_path: str, config: Union[ConfigStorage, dict]
) -> Tuple[DataFrame, Optional[None]]:
    """
    Loads input data from the specified data_path. Supports loading data from various sources
    including disk files (.csv, .pkl, .pickle, .parquet, .xlsx), TeraData, and Hadoop.

    Args:
        spark (Optional[SparkSession]): The current Spark session object.
        data_path (str): The key in the config that specifies the path to the data sample.
        config (Union[ConfigStorage, dict]): The main dreamml_base configuration object.
            For backward compatibility, a dictionary can be provided for modules not updated to release 2.0.

    Returns:
        Tuple[pd.DataFrame, Optional[None]]:
            - pd.DataFrame: The DataFrame containing the training data.
            - Optional[None]: The target data as pd.Series or pd.DataFrame if multitarget is configured.

    Raises:
        ValueError: If the data_path key is incorrect or points to an unsupported file format.
        NameError: If the data format is unsupported or there is an issue with Hadoop input.

    """
    start_time = time.time()

    if isinstance(config, ConfigStorage):
        config = create_old_dict_compat(config)

    drop_features = config.get("drop_features", []) + config.get(
        "never_used_features", []
    )

    file_name = config.get(data_path)

    if file_name is None:
        raise ValueError(f"Incorrect path to {data_path} data.")
    elif file_name.rsplit(".", 1)[-1] == "csv":
        data = pd.read_csv(file_name)
    elif file_name.rsplit(".", 1)[-1] in {"pkl", "pickle"}:
        data = pd.read_pickle(file_name)
    elif file_name.rsplit(".", 1)[-1] == "parquet":
        data = pd.read_parquet(file_name)
    elif file_name.rsplit(".", 1)[-1] == "xlsx":
        data = pd.read_excel(file_name)
    elif "select " in file_name.lower():
        data = get_hadoop_sql_input(
            spark=spark, path=file_name, drop_features=drop_features
        )
    elif file_name.rsplit(":", 1)[0] == "hdfs":
        data = get_hadoop_parquet_input(
            spark=spark, path=file_name, drop_features=drop_features
        )
    else:
        try:
            data = get_hadoop_input(
                spark=spark, path=file_name, drop_features=drop_features
            )
        except (NameError, FileNotFoundError) as e:
            raise NameError(
                f"dreamml_base supports only formats: .csv, .pkl, .pickle, .parquet, database.table or sql ("
                f"HiveQl)\n"
            ) from e

    if config["use_compression"]:
        data = _compress_datatypes(data)

    if config.get("path_to_exog_data") is not None:
        return data, None

    target_name = config.get("target_name")

    # train_data_path -> train_data
    data_type_name = data_path
    if data_type_name.endswith("_path"):
        data_type_name = data_type_name[: -len("_path")]

    elapsed_time = time.time() - start_time
    _logger.monitor(
        f"Loaded {data_type_name} with shape {data.shape}.",
        extra={
            "log_data": DataLoadedLogData(
                name=data_type_name,
                length=len(data),
                features_num=data.shape[1],
                nan_count=data.isna().sum().sum(),
                elapsed_time=elapsed_time,
            )
        },
    )

    if "data_path" in config:
        save_data(
            data,
            data_type_name=data_type_name,
            target_name=target_name,
            save_path=config["data_path"],
            task=config["task"],
            target_label_encoder=config.get("target_label_encoder", True),
        )

    # У валидаторов есть тест на наличие столбца index
    # этот столбец нужен, так как при загрузке-выгрузке с hadoop бывало, что терялись некоторые строчки
    if "index" in data.columns:
        data = data.reset_index(drop=True)
    else:
        data = data.reset_index()

    multitarget = config.get("multitarget")
    if multitarget:
        target_name = [target_name] + multitarget
    #     В таком случае будет возвращён DataFrame

    if target_name is None:
        return data, None

    return data, data[target_name]


def save_data(
    data,
    data_type_name: str,
    target_name: Optional[str],
    save_path: str,
    task: str,
    target_label_encoder: bool,
):
    """
    Saves the dataset and its metadata to the specified directory.

    The saving mechanism attempts to create a `raw` folder within `save_path`. If the folder already exists,
    it checks existing metadata to determine if the current data has been saved before based on its shape and
    target mean. If the data is new, it is saved along with its metadata.

    Args:
        data (pd.DataFrame): The dataset to be saved.
        data_type_name (str): The name of the dataset.
        target_name (Optional[str]): The name of the target column.
        save_path (str): The directory path where data should be saved.
        task (str): The name of the task (e.g., binary, multiclass, regression).
        target_label_encoder (bool): Flag indicating whether to apply label encoding to the target.

    Returns:
        None

    Raises:
        None
    """
    if task in ("binary", "multiclass", "multilabel"):
        target_mean = 0
    else:
        if target_name is None or data[target_name].dtype not in [int, float]:
            target_mean = 0
        else:
            target_mean = round(data[target_name].values.mean(), 4)

    raw_data_path = os.path.join(save_path, "raw")
    os.makedirs(raw_data_path, exist_ok=True)

    metadata_postfix = "_metadata"

    metadata = {
        "shape": data.shape,
        "target_mean": target_mean,
    }

    is_already_saved_data = False
    saved_metadata_names = [
        filename
        for filename in os.listdir(raw_data_path)
        if data_type_name in filename and metadata_postfix in filename
    ]
    for filename in saved_metadata_names:
        saved_metadata_path = os.path.join(raw_data_path, filename)

        try:
            with open(saved_metadata_path, "rb") as f:
                meta_data = pickle.load(f)

            if meta_data == metadata:
                is_already_saved_data = True
                break
        except (ValueError, pickle.UnpicklingError):
            pass
        except Exception as e:
            _logger.exception(
                f"Unexpected error occured while processing {saved_metadata_path}: {e}"
            )

    if not is_already_saved_data:
        numeration_postfix = f"_{len(saved_metadata_names) + 1}"

        data_save_path = os.path.join(
            raw_data_path, data_type_name + numeration_postfix + ".pkl"
        )
        data.to_pickle(data_save_path)

        metadata_path = os.path.join(
            raw_data_path,
            data_type_name + metadata_postfix + numeration_postfix + ".pkl",
        )
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata, f)
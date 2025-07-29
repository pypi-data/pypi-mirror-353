"""
Модуль с реализацией сущностей для взаимодействия с Hadoop.

Доступные сущности:
- create_spark_session: функция для создания Hive-сессии.
- get_hadoop_input: функция для получения данных из Hadoop в pandas.DataFrame
- prepare_dtypes: функция для приведения типов данных из pyspark.DataFrame в pandas.DataFrame.

============================================================================
"""

import pandas as pd
import sys
from pyspark import SparkConf
from pyspark.sql import SparkSession

from dreamml.logging import get_logger
from ..utils.spark_session_configuration import spark_conf
from ..utils.spark_init import init_spark_env
from ..utils.temporary_directory import TempDirectory

_logger = get_logger(__name__)


def create_spark_session(
    spark_config: SparkConf = None, temp_dir: TempDirectory = None
) -> SparkSession:
    """
    Create a SparkSession.

    Initializes a default Spark session with predefined parameters if no configuration is provided.
    Otherwise, it configures the Spark session based on the provided SparkConf and temporary directory.

    Args:
        spark_config (SparkConf, optional): Configuration object to set Spark properties. Defaults to None.
        temp_dir (TempDirectory, optional): Temporary directory for storing intermediate files. Defaults to None.

    Returns:
        SparkSession: A configured SparkSession instance for interacting with Hive and HDFS.

    Raises:
        None
    """
    _logger.info("Starting Spark session...")

    init_spark_env()

    if "user-venvs" in sys.executable:  # DataLab
        spark = (
            SparkSession.builder.config("spark.ui.enabled", "true")
            .config("spark.driver.memory", "2g")
            .config("spark.executor.instances", "2")
            .config("spark.executor.cores", "2")
            .config("spark.kubernetes.executor.limit.cores", "2")
            .config("spark.kubernetes.executor.request.cores", "1800m")
            .config("spark.executor.memory", "2g")
            .config("spark.executor.memoryOverhead", "100m")
            .config("spark.sql.parquet.compression.codec", "snappy")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .getOrCreate()
        )
    else:
        if spark_config is None:
            spark_config = spark_conf

        if temp_dir is not None:
            tmp_dir_path = temp_dir.name
        else:
            tmp_dir_path = "dml_spark_temp_dir"

        spark_config.set("spark.local.dir", tmp_dir_path)
        spark = (
            SparkSession.builder.enableHiveSupport()
            .config(conf=spark_config)
            .getOrCreate()
        )

    _logger.info("Spark session is started!")

    return spark


def stop_spark_session(spark: SparkSession, temp_dir: TempDirectory = None):
    """
    Stop the SparkSession and clean up the temporary directory.

    Terminates the active Spark session and removes the temporary directory if provided.

    Args:
        spark (SparkSession): The active SparkSession to be stopped.
        temp_dir (TempDirectory, optional): The temporary directory to be cleared. Defaults to None.

    Returns:
        None

    Raises:
        None
    """
    spark.stop()

    if temp_dir is not None:
        temp_dir.clear()

    _logger.info("Spark session is stopped.")


def get_hadoop_input(spark, path: str, drop_features=None) -> pd.DataFrame:
    """
    Retrieve data from Hadoop as a pandas DataFrame.

    Loads data from a specified Hive table or HDFS path and converts it to a pandas DataFrame,
    optionally dropping specified features and adjusting data types.

    Args:
        spark: The active SparkSession for data retrieval.
        path (str): The Hive table name or HDFS path to load data from.
        drop_features (list, optional): List of feature names to exclude from the DataFrame. Defaults to None.

    Returns:
        pd.DataFrame: The resulting pandas DataFrame containing the loaded data.

    Raises:
        None
    """
    data = spark.table(path)
    data = data.toPandas()
    data = prepare_dtypes(data, drop_features)

    return data


def get_hadoop_sql_input(spark, path: str, drop_features=None) -> pd.DataFrame:
    """
    Retrieve data from Hadoop using an SQL query as a pandas DataFrame.

    Executes a given SQL query on the SparkSession and converts the result to a pandas DataFrame,
    optionally dropping specified features and adjusting data types.

    Args:
        spark: The active SparkSession for executing the SQL query.
        path (str): The SQL query string to execute.
        drop_features (list, optional): List of feature names to exclude from the DataFrame. Defaults to None.

    Returns:
        pd.DataFrame: The resulting pandas DataFrame containing the query results.

    Raises:
        None
    """
    path = path.replace(";", "")
    data = spark.sql(path)
    data = data.toPandas()
    data = prepare_dtypes(data, drop_features)

    return data


def get_hadoop_parquet_input(spark, path: str, drop_features=None) -> pd.DataFrame:
    """
    Retrieve data from a Hadoop directory containing Parquet files as a pandas DataFrame.

    Loads Parquet files from the specified HDFS directory and converts them to a pandas DataFrame,
    optionally dropping specified features and adjusting data types.

    Args:
        spark: The active SparkSession for reading Parquet files.
        path (str): The HDFS path to the directory containing Parquet files.
        drop_features (list, optional): List of feature names to exclude from the DataFrame. Defaults to None.

    Returns:
        pd.DataFrame: The resulting pandas DataFrame containing the loaded Parquet data.

    Raises:
        None
    """
    data = spark.read.format("parquet").load(path)
    data = data.toPandas()
    data = prepare_dtypes(data, drop_features)

    return data


def prepare_dtypes(df: pd.DataFrame, drop_features=None) -> pd.DataFrame:
    """
    Convert data types of DataFrame columns from object to float where possible.

    Iterates through object-type columns in the DataFrame and attempts to cast them to float.
    Columns that cannot be cast are recorded and a warning is logged.

    Args:
        df (pd.DataFrame): The pandas DataFrame to process.
        drop_features (list, optional): List of feature names to exclude from type conversion. Defaults to None.

    Returns:
        pd.DataFrame: The transformed DataFrame with updated data types.

    Raises:
        None
    """
    if drop_features is None:
        drop_features = []
    obj_features = df.dtypes[df.dtypes == "object"].index

    cannot_cast_features = []
    for feature in obj_features:
        if feature in drop_features:
            continue

        try:
            df[feature] = df[feature].astype(float)
        except (ValueError, TypeError) as e:
            cannot_cast_features.append(feature)

    _logger.warning(
        f"Can't cast to float the following 'object' features: {cannot_cast_features}"
    )

    return df
from pyspark import SparkConf
from pyspark.sql import SparkSession

from dreamml.utils.spark_session_configuration import spark_conf


def create_spark_session(conf: SparkConf = None) -> SparkSession:
    """
    Creates and returns a SparkSession with Hive support enabled.

    Args:
        conf (SparkConf, optional): 
            The Spark configuration to use for the session. 
            If not provided, the default `spark_conf` is used.

    Returns:
        SparkSession: 
            An active SparkSession instance configured with the provided or default settings.

    Raises:
        Exception: 
            If the SparkSession cannot be created or configured properly.
    """
    if conf is None:
        conf = spark_conf

    spark = SparkSession.builder.enableHiveSupport().config(conf=conf).getOrCreate()

    return spark
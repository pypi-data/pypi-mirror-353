from pyspark import SparkConf
from ..utils.spark_session_configuration import spark_conf


def get_hyperopt_spark_conf(local_dir: str) -> SparkConf:
    """
    Creates a Spark configuration for the distributed Hyperopt optimizer.

    Args:
        local_dir (str): Path to the temporary directory.

    Returns:
        SparkConf: Configuration for initiating a Spark session for the distributed optimizer.
    """
    hyperopt_spark_conf = spark_conf
    hyperopt_spark_conf.set("spark.local.dir", local_dir)
    return hyperopt_spark_conf
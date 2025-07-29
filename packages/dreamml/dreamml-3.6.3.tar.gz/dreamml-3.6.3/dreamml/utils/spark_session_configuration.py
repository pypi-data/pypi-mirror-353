from pyspark import SparkConf

shared_cache_dir = "/tmp"

spark_conf = (
    SparkConf()
    .setAppName("DML_SPARK")
    .setMaster("yarn")
    .set("spark.executorEnv.NUMBA_CACHE_DIR", shared_cache_dir)
    .set("spark.driverEnv.NUMBA_CACHE_DIR", shared_cache_dir)
    .set("spark.dynamicAllocation.enabled", "true")
    .set("spark.shuffle.service.enabled", "true")
    .set("spark.dynamicAllocation.minExecutors", "5")
    .set("spark.dynamicAllocation.maxExecutors", "14")
    .set("spark.executor.memory", "10g")
    .set("spark.executor.cores", "5")
    .set("spark.driver.memory", "12g")
    .set("spark.driver.cores", "5")
    .set("spark.driver.maxResultSize", "23g")
    .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .set("spark.kryoserializer.buffer.max", "2047m")
    .set("spark.executor.memoryOverhead", "2g")
    .set("spark.sql.execution.arrow.pyspark.enabled", "true")
)
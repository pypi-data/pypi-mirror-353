from pyspark.sql import SparkSession
import pytest


@pytest.fixture(scope="session")
def spark_session():
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("unit_test_suite") \
        .enableHiveSupport() \
        .config('spark.sql.debug.maxToStringFields', 2000) \
        .getOrCreate()
    sc = spark.sparkContext

    return spark, sc

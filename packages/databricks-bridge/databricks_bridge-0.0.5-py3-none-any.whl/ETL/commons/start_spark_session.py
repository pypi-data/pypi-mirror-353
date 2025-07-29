from pyspark import SparkContext
from pyspark.sql import SparkSession
import os


def get_or_create_spark_session(env=locals()) -> (SparkSession, SparkContext, str):
    """
    Added this config: .config('spark.sql.debug.maxToStringFields', 2000), to prevent the following WARNING Message
    WARN package: Truncated the string representation of a plan since it was too large. This behavior can be adjusted by setting 'spark.sql.debug.maxToStringFields'.
    Added this config: .config("spark.driver.memory", "9g"), to prevent the following WARNING Message
    WARN MemoryManager: Total allocation exceeds 95.00% (1,020,054,720 bytes) of heap memory Scaling row group sizes to 95.00% for 8 writers
    Without the config, the executor only has 434.4 MiB storage memory (as shown in the spark UI)
    With the config, the executor has up to 3.4 GiB for 6gb and 5.2 GiB for 9gb (as shown in the spark UI)
    :return: session, context, and spark_ui_url
    """
    # check if its in databricks or local
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        spark = env["spark"]
        sc = env["sc"]
        spark_ui_url = sc.uiWebUrl
    else:
        spark = SparkSession.builder \
            .appName("Data Normalization Task") \
            .enableHiveSupport() \
            .config('spark.sql.debug.maxToStringFields', 2000) \
            .config("spark.driver.memory", "9g") \
            .getOrCreate()
            # .config("spark.sql.jsonGenerator.ignoreNullFields", "false") \

        sc = spark.sparkContext
        spark_ui_url = sc.uiWebUrl

    return spark, sc, spark_ui_url
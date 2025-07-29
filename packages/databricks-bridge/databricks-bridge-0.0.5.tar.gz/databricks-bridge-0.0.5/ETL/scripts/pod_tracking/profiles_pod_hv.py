# Databricks notebook source
import os
from typing import Tuple
import traceback
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import lag, when, lit, sum, min, max

from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.logging.logging_decorators import log_general_info

from ETL.scripts.pod_tracking.df_utils.profiles_pod_hv_df_utils import PodHVTable

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/profiles_pod_hv.py"
etl_data_name = "profiles_pod_hv"

def query_from_databricks(spark, query):
    # Allows the ability to query directly from databricks hive metastore 
    return spark.sql(query)


def calculating_date_range(df):
    # Define a window specification for ordering by client_id and date
    window_spec = Window.partitionBy("client_id").orderBy("data_dt")
    # Create columns to check for changes in pod_id and pod
    df = df.withColumn("pod_id_change", when(lag("pod_id").over(window_spec) != df["pod_id"], lit(1)).otherwise(lit(0)))
    df = df.withColumn("pod_change", when(lag("pod").over(window_spec) != df["pod"], lit(1)).otherwise(lit(0)))

    # Use the cumulative sum to create a group identifier when changes occur
    df = df.withColumn("pod_id_group", sum("pod_id_change").over(window_spec))
    df = df.withColumn("pod_group", sum("pod_change").over(window_spec))

    # Group by client_id, pod_id, pod, and the group identifiers
    df = df.groupBy("client_id", "pod_id", "pod", "pod_id_group", "pod_group") \
        .agg(min("data_dt").alias("start_date"), max("data_dt").alias("end_date")) \
        .orderBy("client_id", "start_date").drop("pod_id_group", "pod_group")

    return df


def write_list_to_table(df, table_name):
    # Write the Spark DataFrame to the table
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table_name)


def etl_steps(spark, query, data_sources_duration_s):
    # Running databricks query and returning a dataframe 
    start_time = datetime.now()
    df = query_from_databricks(spark, query)
    query_duration_sec = (datetime.now() - start_time).total_seconds()
    data_sources_duration_s += query_duration_sec

    # Adding a column with timestamp named data_dt
    df = calculating_date_range(df)

    # Write to table
    table_class = PodHVTable()
    write_list_to_table(df, table_class.table_name)
    
    return data_sources_duration_s


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    query = """SELECT * from profiles.pod_pt"""
    print(f"Spark UI Url: {spark_ui_url}")

    data_sources_duration_s = 0.0
    data_source_n_status = []
    logger_helper = LoggerHelper(source='profiles.pod_pt')
    try:
        data_sources_duration_s = etl_steps(spark, query, data_sources_duration_s)
        logger_helper.log_status()

    except Exception:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())
# Databricks notebook source
import os
from typing import Tuple
import traceback
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, date_format

from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.logging.logging_decorators import log_general_info

from ETL.scripts.pod_tracking.df_utils.profiles_pod_pt_df_utils import PodPTTable

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/profiles_pod_pt.py"
etl_data_name = "profiles_pod_pt"

def query_from_databricks(spark, query):
    # Allows the ability to query directly from databricks hive metastore 
    return spark.sql(query)


def adding_timestamp(df):
    # additional column data_dt was requested to include a timestamp
    return df.withColumn("data_dt", date_format(current_timestamp(),"yyyy-MM-dd"))


def write_list_to_table(df, table_name):
    # Write the Spark DataFrame to the table
    df.write.mode('append').option("overwriteSchema", "true").saveAsTable(table_name)


def etl_steps(spark, query, data_sources_duration_s):
    # Running databricks query and returning a dataframe 
    start_time = datetime.now()
    df = query_from_databricks(spark, query)
    query_duration_sec = (datetime.now() - start_time).total_seconds()
    data_sources_duration_s += query_duration_sec
    # Adding a column with timestamp named data_dt
    df = adding_timestamp(df)

    # Write to table
    table_class = PodPTTable()
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
    query = """SELECT A.CLIENT_ID
			            ,A.POD_ID
			            ,B.NAME AS POD
	            FROM PROFILES.POD_CLIENT_RELATIONS	a
		        inner join profiles.pod	b
                on a.pod_id = b.id"""
    print(f"Spark UI Url: {spark_ui_url}")

    data_sources_duration_s = 0.0
    data_source_n_status = []
    logger_helper = LoggerHelper(source='profiles.pod_client_relations')
    try:
        data_sources_duration_s = etl_steps(spark, query, data_sources_duration_s)
        logger_helper.log_status()

    except Exception:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())